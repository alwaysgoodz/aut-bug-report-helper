"""Local, consent-based product study; never generates human observations."""
import argparse
from contextlib import closing
from datetime import datetime, timezone
import csv
import hashlib
import json
import os
import platform
from pathlib import Path
import re
import secrets
import shutil
import sqlite3
import statistics
import subprocess
import sys
import tempfile
import threading
import time
from http.server import ThreadingHTTPServer
from urllib.parse import parse_qs, urlsplit
from uuid import uuid4

from bugreport import views
from bugreport.service import FIELDS, LABELS, ReportStore, ValidationError, has_text
from bugreport.web import MAX_BODY, STATIC, ReportHandler

SCHEDULE = {
    "P01": (("baseline", "A"), ("guided", "B")),
    "P02": (("guided", "A"), ("baseline", "B")),
    "P03": (("baseline", "B"), ("guided", "A")),
    "P04": (("guided", "B"), ("baseline", "A")),
}
TASKS = {"A": ("Study Planner", "Active", "Completed", "Send project outline"),
         "B": ("Supply List", "Urgent", "Normal", "Buy printer paper")}


def utc():
    return datetime.now(timezone.utc).isoformat()


def fingerprint():
    root = Path(__file__).resolve().parents[1]
    source = [root/"tools/peer_study.py", *[p for p in (root/"bugreport").rglob("*") if p.is_file() and "__pycache__" not in p.parts]]
    git = subprocess.run([shutil.which("git"), "rev-parse", "HEAD"], cwd=root, capture_output=True, text=True, check=False) if shutil.which("git") else None
    return dict(git_sha=git.stdout.strip() if git and git.returncode == 0 else "unavailable",
                python=sys.version, sqlite=sqlite3.sqlite_version, platform=platform.platform(),
                source_sha256={p.relative_to(root).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(source)})


class StudyStore:
    def __init__(self, directory, *, test_only=False, clock=time.perf_counter, read_only=False):
        self.directory = Path(directory)
        self.directory.mkdir(parents=True, exist_ok=True)
        self.path = self.directory / "peer-study.json"
        self.read_only, self.file_lock = read_only, None
        self.lock, self.clock, self.active = threading.RLock(), clock, {}
        if not read_only:
            self.file_lock = (self.directory/"study.lock").open("a+b")
            if self.file_lock.tell() == 0:
                self.file_lock.write(b"0")
                self.file_lock.flush()
            self.file_lock.seek(0)
            try:
                if os.name == "nt":
                    import msvcrt
                    msvcrt.locking(self.file_lock.fileno(), msvcrt.LK_NBLCK, 1)
                else:
                    import fcntl
                    fcntl.flock(self.file_lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except OSError as error:
                self.close()
                raise ValueError("Study data is in use; stop the server before opening another writer") from error
        try:
            self._load(test_only)
        except BaseException:
            self.close()
            raise

    def _load(self, test_only):
        if self.path.exists():
            self.data = json.loads(self.path.read_text(encoding="utf-8"))
            if self.data.get("schema") != 1 or self.data.get("test_only") is not test_only:
                self.close()
                raise ValueError("Existing study schema/mode differs; choose a separate directory")
            for trial in self.data["trials"] if not self.read_only else []:
                if trial["state"] == "active":
                    trial.update(state="interrupted", interrupted_at=utc())
        else:
            if self.read_only:
                raise ValueError("Study data does not exist yet")
            self.data = dict(schema=1, protocol="peer-study-v1", test_only=test_only,
                             created_at=utc(), participants={}, trials=[], withdrawals=[])
        if not self.read_only:
            software = fingerprint()
            previous = self.data.get("software")
            if self.data["participants"] and previous and previous["source_sha256"] != software["source_sha256"]:
                raise ValueError("Study source changed during collection; restore the recorded source or use a new directory")
            if not self.data["participants"]:
                self.data["software"] = software
        self.product = None if self.read_only else ReportStore(self.directory / "guided-reports.db")
        if not self.read_only:
            self.save()

    def close(self):
        if self.file_lock is not None:
            self.file_lock.close()
            self.file_lock = None

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()

    def save(self):
        if self.read_only:
            raise ValueError("Cannot change a read-only study snapshot")
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=self.directory,
                                         suffix=".json.tmp", delete=False) as file:
            json.dump(self.data, file, ensure_ascii=False, indent=2)
            file.write("\n")
            temporary = Path(file.name)
        try:
            temporary.replace(self.path)
        finally:
            temporary.unlink(missing_ok=True)

    def consent(self, participant, agreed):
        with self.lock:
            if participant not in SCHEDULE or agreed != "yes":
                raise ValueError("Valid participant code and explicit consent are required")
            if any(row["participant"] == participant for row in self.data["withdrawals"]):
                raise ValueError("This participant withdrew; do not reuse the code")
            self.data["participants"].setdefault(participant, dict(consented_at=utc(), protocol="peer-study-v1"))
            self.save()

    def start(self, participant, browser="not_recorded"):
        with self.lock:
            if participant not in self.data["participants"]:
                raise ValueError("Consent is required before timing starts")
            previous = [row for row in self.data["trials"] if row["participant"] == participant]
            for row in previous:
                if row["state"] == "active":
                    return dict(row)
            slot = sum(row["state"] == "submitted" for row in previous)
            if slot >= 2:
                raise ValueError("Both tasks have already been submitted")
            condition, task = SCHEDULE[participant][slot]
            row = dict(id=str(uuid4()), participant=participant, slot=slot+1,
                       attempt=1+sum(item["slot"] == slot+1 for item in previous),
                       condition=condition, task=task, state="active", started_at=utc(),
                       review_key=secrets.token_hex(12), review=None, browser=browser)
            self.active[row["id"]] = self.clock()
            self.data["trials"].append(row)
            self.save()
            return dict(row)

    def get(self, trial_id):
        with self.lock:
            row = next((row for row in self.data["trials"] if row["id"] == trial_id), None)
            if row is None:
                raise KeyError("Unknown trial")
            return json.loads(json.dumps(row))

    def submit(self, trial_id, values):
        with self.lock:
            row = next((row for row in self.data["trials"] if row["id"] == trial_id), None)
            if row is None or row["state"] != "active" or trial_id not in self.active:
                raise ValueError("This timed trial is no longer active")
            if row["condition"] == "guided":
                report = self.product.create(**{field: values.get(field, "") for field in FIELDS})
            else:
                body = values.get("body", "")
                if not has_text(body) or len(body) > 20000 or "\x00" in body:
                    raise ValueError("Enter a nonblank report, up to 20,000 characters, without null characters")
                report = dict(body=body)
            row.update(state="submitted", submitted_at=utc(), report=report,
                       duration_seconds=round(self.clock()-self.active.pop(trial_id), 4))
            self.save()
            return dict(row)

    def review(self, key, values):
        with self.lock:
            row = next((row for row in self.data["trials"] if row["review_key"] == key), None)
            if row is None or row["state"] != "submitted" or row["review"] is not None:
                raise ValueError("Report is unavailable or already reviewed")
            if values.get("ack") != "yes" or not re.fullmatch(r"R\d{2}", values.get("reviewer", "")):
                raise ValueError("An independent reviewer code and acknowledgement are required")
            if any(values.get(field) not in ("0", "1") for field in FIELDS):
                raise ValueError("Explicitly mark every information element present or absent")
            outcome = values.get("outcome", "")
            if outcome not in ("reproduced", "needs_clarification", "not_reproduced"):
                raise ValueError("Choose the observed reproduction outcome")
            clarifications = int(values.get("clarifications", ""))
            if not 0 <= clarifications <= 99:
                raise ValueError("Clarifications must be between 0 and 99")
            marks = {field: int(values[field]) for field in FIELDS}
            row["review"] = dict(reviewer=values["reviewer"], reviewed_at=utc(), marks=marks,
                                 completeness=round(100*sum(marks.values())/7, 2), outcome=outcome,
                                 clarifications=clarifications,
                                 independent_success=outcome == "reproduced" and clarifications == 0,
                                 notes=values.get("notes", ""))
            self.save()

    def withdraw(self, participant):
        with self.lock:
            if participant not in self.data["participants"]:
                raise ValueError("Unknown consenting participant")
            removed = [row for row in self.data["trials"] if row["participant"] == participant]
            with closing(sqlite3.connect(self.product.database)) as connection, connection:
                for row in removed:
                    report_id = row.get("report", {}).get("id")
                    if report_id:
                        connection.execute("DELETE FROM reports WHERE id = ?", (report_id,))
                    self.active.pop(row["id"], None)
            self.data["trials"] = [row for row in self.data["trials"] if row["participant"] != participant]
            del self.data["participants"][participant]
            self.data["withdrawals"].append(dict(participant=participant, at=utc(), removed=len(removed)))
            self.save()

    def summary(self):
        with self.lock:
            pairs = []
            for participant in self.data["participants"]:
                rows = [row for row in self.data["trials"] if row["participant"] == participant]
                if len(rows) != 2 or any(row["state"] != "submitted" or row["review"] is None or row["attempt"] != 1 for row in rows):
                    continue
                baseline = next(row for row in rows if row["condition"] == "baseline")
                guided = next(row for row in rows if row["condition"] == "guided")
                pairs.append(dict(participant=participant,
                                  baseline_seconds=baseline["duration_seconds"], guided_seconds=guided["duration_seconds"],
                                  delta_seconds=round(guided["duration_seconds"]-baseline["duration_seconds"], 4),
                                  baseline_completeness=baseline["review"]["completeness"],
                                  guided_completeness=guided["review"]["completeness"],
                                  delta_completeness=round(guided["review"]["completeness"]-baseline["review"]["completeness"], 2),
                                  baseline_independent=int(baseline["review"]["independent_success"]),
                                  guided_independent=int(guided["review"]["independent_success"])))
            aggregate = {}
            for condition in ("baseline", "guided"):
                aggregate[condition] = dict(n=len(pairs),
                    median_seconds=statistics.median(p[condition+"_seconds"] for p in pairs) if pairs else None,
                    median_completeness=statistics.median(p[condition+"_completeness"] for p in pairs) if pairs else None,
                    independent_successes=sum(p[condition+"_independent"] for p in pairs))
            return dict(test_only=self.data["test_only"], consenting=len(self.data["participants"]),
                        submitted=sum(row["state"] == "submitted" for row in self.data["trials"]),
                        reviewed=sum(row["review"] is not None for row in self.data["trials"]),
                        complete_pairs=len(pairs), human_study_complete=len(pairs) == 4 and not self.data["test_only"],
                        pairs=pairs, aggregate=aggregate,
                        limits="Four-person convenience sample; descriptive paired results only. Incomplete/repeated/interrupted pairs excluded. Report format may reveal condition to reviewers.")

    def export(self, destination):
        with self.lock:
            destination = Path(destination)
            destination.mkdir(parents=True, exist_ok=True)
            result = self.summary()
            (destination/"summary.json").write_text(json.dumps(result, indent=2)+"\n", encoding="utf-8")
            (destination/"raw-study.json").write_text(json.dumps(self.data, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
            columns = ("participant", "baseline_seconds", "guided_seconds", "delta_seconds",
                       "baseline_completeness", "guided_completeness", "delta_completeness", "baseline_independent", "guided_independent")
            with (destination/"paired-results.csv").open("w", newline="", encoding="utf-8-sig") as file:
                writer = csv.DictWriter(file, fieldnames=columns)
                writer.writeheader()
                writer.writerows(result["pairs"])
            return result


def fixture(task):
    title, selected, other, defect_item = TASKS[task]
    # Intentional fixture defect: changing the view never excludes the third row.
    content = f'''<p class="eyebrow">CONTROLLED STUDY FIXTURE {task} / BUILD 1.0</p><h1>{title}</h1>
<p class="subtitle">Choose a view. Only items matching that view should appear.</p>
<section class="panel status-card"><label for="fixture-filter">View</label><select id="fixture-filter"><option>All</option><option>{selected}</option></select>
<p id="fixture-view">Current view: All</p><ul id="fixture-items"><li>Prepare project notes - {selected}</li><li>Check the next deadline - {selected}</li><li>{defect_item} - {other}</li></ul></section>
<script src="/fixture.js"></script>'''
    return f'<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>{title} - Study fixture {task}</title><link rel="stylesheet" href="/static/app.css"><link rel="stylesheet" href="/fixture.css"></head><body><main class="fixture-layout">{content}</main></body></html>'


class StudyServer(ThreadingHTTPServer):
    daemon_threads = True

    def __init__(self, address, store):
        if address[0] != "127.0.0.1":
            raise ValueError("Study tool supports loopback only")
        self.store, self.csrf_token = store, secrets.token_urlsafe(32)
        super().__init__(address, StudyHandler)


class StudyHandler(ReportHandler):
    def _form(self, action, body):
        return f'<form action="{action}" method="post"><input type="hidden" name="_csrf" value="{self.server.csrf_token}">{body}</form>'

    def _page(self, title, content):
        self._send(200, views.shell(title, content, self.server.store.product.counts()["total"]))

    def _error(self, status, message):
        self._send(status, views.shell("Study feedback", f'<section class="panel status-card"><h1>{views.e(message)}</h1><a href="/">Study dashboard</a></section>'))

    def do_GET(self):
        if not self._valid_host():
            return
        path = urlsplit(self.path).path
        store = self.server.store
        if path.startswith("/static/") or path == "/health":
            return super().do_GET()
        if path == "/fixture.js":
            return self._send(200, "document.querySelector('#fixture-filter').addEventListener('change',e=>{document.querySelector('#fixture-view').textContent='Current view: '+e.target.value;});", content_type="text/javascript; charset=utf-8")
        if path == "/fixture.css":
            return self._send(200, '.fixture-layout{max-width:760px;margin:0 auto;padding:32px 20px}.fixture-layout .panel{margin-top:28px}.fixture-layout li{padding:12px 0;border-bottom:1px solid var(--line)}', content_type="text/css; charset=utf-8")
        if path in ("/fixture/A", "/fixture/B"):
            return self._send(200, fixture(path[-1]))
        if path == "/":
            result = store.summary()
            links = "".join(f'<p><a class="button secondary" href="/participant/{pid}">{pid}</a></p>' for pid in SCHEDULE)
            return self._page("Peer study", f'<h1>Peer product study</h1><p class="subtitle">{"TEST-ONLY PILOT - not human evidence" if result["test_only"] else "Prepared for real participants"}</p><section class="panel status-card"><p>{result["consenting"]}/4 consented; {result["submitted"]}/8 reports; {result["reviewed"]}/8 reviewed; {result["complete_pairs"]}/4 complete pairs.</p>{links}<a href="/review">Independent reviewer</a></section>')
        if path == "/reports/new":
            return self._send(303, location="/")
        match = re.fullmatch(r"/participant/(P0[1-4])", path)
        if match:
            pid = match[1]
            if pid not in store.data["participants"]:
                body = f'<h1>{pid}: consent</h1><p>Voluntary, anonymous study using fictional defects. Two tasks, about 10-15 minutes. You may stop or ask the facilitator to withdraw your code and delete reports. No student ID or name is collected.</p><label><input type="checkbox" name="consent" value="yes" required> I agree to anonymous timing/report collection and independent reproduction review.</label><button class="button primary" type="submit">Consent and continue</button>'
                return self._page("Consent", self._form(f"/consent/{pid}", body))
            submitted = sum(row["participant"] == pid and row["state"] == "submitted" for row in store.data["trials"])
            if submitted == 2:
                return self._page("Tasks submitted", '<h1>Both reports submitted</h1><p>Thank you. Independent review is still required; no result is inferred yet.</p><a href="/">Dashboard</a>')
            return self._page("Ready", self._form(f"/start/{pid}", f'<h1>{pid}: task {submitted+1} of 2</h1><p>Inspect the linked fixture and report the observed problem so another developer can reproduce it. Use only the fictional task. Timing begins after you select Start.</p><button class="button primary" type="submit">Start timed task</button>'))
        match = re.fullmatch(r"/trial/([0-9a-f-]{36})", path)
        if match:
            try:
                row = store.get(match[1])
            except KeyError:
                return self._error(404, "Unknown trial")
            if row["state"] != "active":
                return self._error(409, "This task is no longer active; return to your participant page")
            return self._trial(row)
        if path == "/review":
            rows = sorted((row for row in store.data["trials"] if row["state"] == "submitted" and row["review"] is None), key=lambda row: row["review_key"])
            links = "".join(f'<p><a href="/review/{row["review_key"]}">Report {index+1}</a></p>' for index, row in enumerate(rows))
            return self._page("Independent review", '<h1>Independent review queue</h1><p>Review only reports you did not author. Condition, participant and timing are hidden here. The writing format may still suggest the condition.</p>'+links)
        match = re.fullmatch(r"/review/([0-9a-f]{24})", path)
        if match:
            row = next((row for row in store.data["trials"] if row["review_key"] == match[1] and row["state"] == "submitted" and row["review"] is None), None)
            if row is None:
                return self._error(404, "Review not available")
            report = row["report"]
            text = report.get("body") if row["condition"] == "baseline" else "\n\n".join(f'{LABELS[field]}: {report[field]}' for field in FIELDS)
            marks = "".join(f'<label>{LABELS[field]}<select name="{field}" required><option value="">Choose</option><option value="1">Present</option><option value="0">Absent</option></select></label>' for field in FIELDS)
            body = f'<section class="panel status-card"><h1>Report review</h1><p class="report-text">{views.e(text)}</p><p>Available fixtures: <a href="/fixture/A" target="_blank">A</a> / <a href="/fixture/B" target="_blank">B</a>. Try to reproduce using the report alone, before checking element presence.</p><label>Reviewer code (R01)<input name="reviewer" pattern="R[0-9]{{2}}" required></label><label><input type="checkbox" name="ack" value="yes" required> I did not author this report and recorded an actual reproduction attempt.</label>{marks}<label>Observed outcome<select name="outcome" required><option value="">Choose</option><option value="reproduced">Reproduced</option><option value="needs_clarification">Needs clarification</option><option value="not_reproduced">Not reproduced</option></select></label><label>Clarifications requested<input type="number" name="clarifications" min="0" max="99" required></label><label>Observation notes<textarea name="notes" rows="3"></textarea></label><button class="button primary" type="submit">Save actual review</button></section>'
            return self._page("Review", self._form(path, body))
        self._error(404, "Study page not found")

    def _trial(self, row, values=None, errors=None):
        banner = f'<div class="notice" role="status">Timed task {row["slot"]}/2. Inspect <a href="/fixture/{row["task"]}" target="_blank">{TASKS[row["task"]][0]} / build 1.0</a>, then report the problem. Timer continues through reloads and validation errors.</div>'
        if row["condition"] == "guided":
            page = views.report_form(self.server.csrf_token, self.server.store.product.counts()["total"], values, errors)
            marker = 'action="/reports"'
            if page.count(marker) != 1:
                raise RuntimeError("Product form integration changed; update the study adapter")
            page = page.replace(marker, f'action="/submit/{row["id"]}"', 1)
            page = page.replace('<main id="main" tabindex="-1">', '<main id="main" tabindex="-1">'+banner, 1)
            return self._send(422 if errors else 200, page)
        body = self._form(f'/submit/{row["id"]}', f'<section class="panel status-card"><h1>Write a bug report</h1><label for="body">Describe the problem in your own words</label><textarea id="body" name="body" rows="14" required>{views.e((values or {}).get("body", ""))}</textarea><button class="button primary" type="submit">Submit report</button></section>')
        error = f'<div class="error-summary" id="form-errors" tabindex="-1" role="alert">{views.e(errors["body"])}</div>' if errors else ""
        self._send(422 if errors else 200, views.shell("Write a report", banner+error+body))

    def do_POST(self):
        self.close_connection = True
        if not self._valid_host():
            return
        if self.headers.get("Origin") not in (None, "http://"+self.headers["Host"]):
            return self._error(403, "Request origin is not allowed")
        if self.headers.get("Content-Type", "").split(";", 1)[0] != "application/x-www-form-urlencoded":
            return self._error(415, "Use a form submission")
        if "Transfer-Encoding" in self.headers:
            return self._error(400, "Unsupported request encoding")
        try:
            length = int(self.headers.get("Content-Length", "-1"))
            if length < 0 or length > MAX_BODY:
                return self._error(413, "Study submission size is invalid")
            raw = self.rfile.read(length)
            if len(raw) != length:
                return self._error(400, "Incomplete form")
            parsed = parse_qs(raw.decode("utf-8"), keep_blank_values=True, strict_parsing=True, max_num_fields=20, errors="strict")
            if any(len(values) != 1 for values in parsed.values()):
                return self._error(400, "Duplicate fields")
            values = {key: entries[0] for key, entries in parsed.items()}
        except (ValueError, UnicodeError):
            return self._error(400, "Invalid form")
        if not secrets.compare_digest(values.get("_csrf", "").encode("utf-8"), self.server.csrf_token.encode("ascii")):
            return self._error(403, "Reload the study form")
        path, store = urlsplit(self.path).path, self.server.store
        try:
            match = re.fullmatch(r"/(consent|start)/(P0[1-4])", path)
            if match:
                action, pid = match.groups()
                if action == "consent":
                    store.consent(pid, values.get("consent"))
                    return self._send(303, location=f"/participant/{pid}")
                row = store.start(pid, browser=self.headers.get("User-Agent", "not_recorded"))
                return self._send(303, location=f'/trial/{row["id"]}')
            match = re.fullmatch(r"/submit/([0-9a-f-]{36})", path)
            if match:
                row = store.submit(match[1], values)
                return self._send(303, location=f'/participant/{row["participant"]}')
            match = re.fullmatch(r"/review/([0-9a-f]{24})", path)
            if match:
                store.review(match[1], values)
                return self._send(303, location="/review")
        except ValidationError as error:
            return self._trial(store.get(path.rsplit("/", 1)[1]), values, error.errors)
        except (ValueError, KeyError) as error:
            if re.fullmatch(r"/submit/[0-9a-f-]{36}", path):
                try:
                    row = store.get(path.rsplit("/", 1)[1])
                except KeyError:
                    return self._error(422, str(error))
                if row["state"] == "active" and row["condition"] == "baseline":
                    return self._trial(row, values, dict(body=str(error)))
            return self._error(422, str(error))
        self._error(404, "Study action not found")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("serve", "export", "withdraw"))
    parser.add_argument("--data-dir", default="study-data")
    parser.add_argument("--port", type=int, default=8766)
    parser.add_argument("--output", default="study-export")
    parser.add_argument("--participant")
    parser.add_argument("--test-only", action="store_true")
    args = parser.parse_args()
    with StudyStore(args.data_dir, test_only=args.test_only, read_only=args.action == "export") as store:
        if args.action == "export":
            print(json.dumps(store.export(args.output), indent=2))
        elif args.action == "withdraw":
            store.withdraw(args.participant)
            print("Participant reports removed")
        else:
            with StudyServer(("127.0.0.1", args.port), store) as server:
                print(f'Peer study: http://127.0.0.1:{server.server_address[1]} (test_only={args.test_only})', flush=True)
                try:
                    server.serve_forever()
                except KeyboardInterrupt:
                    print("Study stopped. An unfinished timed task is excluded after restart.")


if __name__ == "__main__":
    main()
