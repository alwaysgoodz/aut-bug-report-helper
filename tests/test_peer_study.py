"""Tool verification uses simulated data in temporary directories, never human evidence."""
import http.client
import json
from pathlib import Path
import re
import tempfile
import threading
import unittest
from unittest.mock import patch
from urllib.parse import urlencode

from bugreport.service import FIELDS, ValidationError
from tools.peer_study import SCHEDULE, StudyServer, StudyStore


class PeerStudyTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.now = 100.0
        self.store = StudyStore(self.root/"data", test_only=True, clock=lambda: self.now)
        self.addCleanup(self.store.close)

    def finish(self, row):
        self.now += 20 if row["condition"] == "baseline" else 25
        values = dict(title="Synthetic report", severity="low", steps="Select the view") if row["condition"] == "guided" else dict(body="Synthetic test-only free report")
        return self.store.submit(row["id"], values)

    def marks(self, condition="guided"):
        return dict({field: "1" if condition == "guided" else "0" for field in FIELDS},
                    reviewer="R01", ack="yes", outcome="reproduced", clarifications="0")

    def test_counterbalance_covers_every_order_and_task_condition_twice(self):
        self.assertEqual(len(SCHEDULE), 4)
        for condition in ("baseline", "guided"):
            for task in ("A", "B"):
                self.assertEqual(sum((condition, task) in sequence for sequence in SCHEDULE.values()), 2)
            self.assertEqual(sum(sequence[0][0] == condition for sequence in SCHEDULE.values()), 2)

    def test_consent_is_explicit_and_invalid_codes_cannot_start(self):
        for participant, consent in (("P01", "no"), ("P99", "yes")):
            with self.assertRaises(ValueError):
                self.store.consent(participant, consent)
        with self.assertRaises(ValueError):
            self.store.start("P01")
        self.assertEqual(self.store.summary()["consenting"], 0)

    def test_repeated_start_keeps_id_and_timer_and_invalid_submit_does_not_finish(self):
        self.store.consent("P01", "yes")
        row = self.store.start("P01")
        self.now += 10
        self.assertEqual(self.store.start("P01")["id"], row["id"])
        with self.assertRaises(ValueError):
            self.store.submit(row["id"], dict(body=" "))
        finished = self.finish(row)
        self.assertEqual(finished["duration_seconds"], 30)
        with self.assertRaises(ValueError):
            self.store.submit(row["id"], dict(body="Duplicate"))

    def test_guided_uses_product_validation_and_actual_stored_fields(self):
        self.store.consent("P02", "yes")
        row = self.store.start("P02")
        with self.assertRaises(ValidationError):
            self.store.submit(row["id"], dict(title=" ", severity="low", steps="Keep"))
        self.assertEqual(self.store.get(row["id"])["state"], "active")
        finished = self.finish(row)
        self.assertEqual(self.store.product.get(finished["report"]["id"])["steps"], "Select the view")

    def test_both_tasks_follow_fixed_schedule_and_no_third_task(self):
        self.store.consent("P03", "yes")
        for condition, task in SCHEDULE["P03"]:
            row = self.store.start("P03")
            self.assertEqual((row["condition"], row["task"]), (condition, task))
            self.finish(row)
        with self.assertRaises(ValueError):
            self.store.start("P03")

    def test_reviews_require_explicit_marks_and_independence_is_not_assumed(self):
        self.store.consent("P01", "yes")
        row = self.finish(self.store.start("P01"))
        values = self.marks()
        del values["environment"]
        with self.assertRaises(ValueError):
            self.store.review(row["review_key"], values)
        values = dict(self.marks(), clarifications="1")
        self.store.review(row["review_key"], values)
        self.assertFalse(self.store.get(row["id"])["review"]["independent_success"])
        with self.assertRaises(ValueError):
            self.store.review(row["review_key"], self.marks())

    def test_four_simulated_pairs_have_expected_deltas_but_are_never_human_completion(self):
        for participant in SCHEDULE:
            self.store.consent(participant, "yes")
            for _ in range(2):
                row = self.finish(self.store.start(participant))
                self.store.review(row["review_key"], self.marks(row["condition"]))
        result = self.store.export(self.root/"export")
        self.assertEqual(result["complete_pairs"], 4)
        self.assertEqual(result["submitted"], 8)
        self.assertFalse(result["human_study_complete"])
        self.assertTrue(result["test_only"])
        self.assertTrue(all(pair["delta_seconds"] == 5 and pair["delta_completeness"] == 100 for pair in result["pairs"]))
        self.assertEqual(result["aggregate"]["guided"]["median_seconds"], 25)
        self.assertEqual(len((self.root/"export/paired-results.csv").read_text(encoding="utf-8-sig").splitlines()), 5)

    def test_read_only_export_does_not_interrupt_active_timer_and_writer_lock_is_enforced(self):
        self.store.consent("P01", "yes")
        row = self.store.start("P01")
        original = self.store.path.read_bytes()
        with StudyStore(self.root/"data", test_only=True, read_only=True) as reader:
            reader.export(self.root/"snapshot")
        self.assertEqual(self.store.path.read_bytes(), original)
        with self.assertRaises(ValueError):
            StudyStore(self.root/"data", test_only=True)
        self.finish(row)

    def test_restart_marks_active_trial_interrupted_and_repeated_attempt_is_excluded(self):
        self.store.consent("P01", "yes")
        row = self.store.start("P01")
        self.store.close()
        with StudyStore(self.root/"data", test_only=True) as reopened:
            self.assertEqual(reopened.get(row["id"])["state"], "interrupted")
            self.assertEqual(reopened.start("P01")["attempt"], 2)
            self.assertEqual(reopened.summary()["complete_pairs"], 0)

    def test_withdrawal_removes_guided_data_and_excludes_participant(self):
        self.store.consent("P02", "yes")
        row = self.finish(self.store.start("P02"))
        report_id = row["report"]["id"]
        self.store.withdraw("P02")
        self.assertEqual(self.store.summary()["consenting"], 0)
        self.assertIsNone(self.store.product.get(report_id))
        self.assertEqual(self.store.data["trials"], [])
        with self.assertRaises(ValueError):
            self.store.consent("P02", "yes")

    def test_empty_real_study_has_no_results_or_invented_medians(self):
        with StudyStore(self.root/"real") as real:
            result = real.export(self.root/"empty-export")
        self.assertEqual(result["consenting"], 0)
        self.assertEqual(result["complete_pairs"], 0)
        self.assertIsNone(result["aggregate"]["baseline"]["median_seconds"])
        self.assertFalse(result["human_study_complete"])

    def test_corrupt_data_is_preserved_and_failed_open_releases_writer_lock(self):
        original = self.store.path.read_bytes()
        self.store.close()
        self.store.path.write_text("{broken", encoding="utf-8")
        with self.assertRaises(json.JSONDecodeError):
            StudyStore(self.root/"data", test_only=True)
        self.assertEqual(self.store.path.read_text(encoding="utf-8"), "{broken")
        self.store.path.write_bytes(original)
        with StudyStore(self.root/"data", test_only=True) as recovered:
            self.assertEqual(recovered.summary()["consenting"], 0)

    def test_source_change_blocks_mixed_collection_but_old_snapshot_can_be_exported(self):
        self.store.consent("P01", "yes")
        self.store.close()
        original = self.store.path.read_bytes()
        changed = dict(self.store.data["software"], source_sha256={"changed": "source"})
        with patch("tools.peer_study.fingerprint", return_value=changed):
            with self.assertRaisesRegex(ValueError, "source changed"):
                StudyStore(self.root/"data", test_only=True)
        self.assertEqual(self.store.path.read_bytes(), original)
        with StudyStore(self.root/"data", test_only=True, read_only=True) as reader:
            self.assertEqual(reader.export(self.root/"old-snapshot")["consenting"], 1)

    def test_http_guided_flow_preserves_errors_and_masks_review_metadata(self):
        server = StudyServer(("127.0.0.1", 0), self.store)
        worker = threading.Thread(target=server.serve_forever, kwargs={"poll_interval": .01}, daemon=True)
        worker.start()
        self.addCleanup(server.server_close)
        self.addCleanup(worker.join, 2)
        self.addCleanup(server.shutdown)

        def request(method="GET", path="/", values=None, origin=None):
            connection = http.client.HTTPConnection("127.0.0.1", server.server_address[1], timeout=5)
            self.addCleanup(connection.close)
            headers = {"Content-Type": "application/x-www-form-urlencoded"}
            if origin:
                headers["Origin"] = origin
            body = urlencode(dict(_csrf=server.csrf_token, **values)).encode() if values is not None else None
            connection.request(method, path, body, headers)
            response = connection.getresponse()
            return response.status, dict(response.getheaders()), response.read().decode()

        self.assertEqual(request("POST", "/consent/P02", dict(consent="yes"), "https://foreign.example")[0], 403)
        self.assertEqual(request("POST", "/consent/P02", dict(consent="yes"))[0], 303)
        _, headers, _ = request("POST", "/start/P02", {})
        trial_id = headers["Location"].rsplit("/", 1)[1]
        code, _, page = request(path=headers["Location"])
        self.assertEqual(code, 200)
        self.assertIn(f'action="/submit/{trial_id}"', page)
        self.assertIn('data-completeness', page)
        code, _, page = request("POST", f"/submit/{trial_id}", dict(title=" ", severity="low", steps="Retain"))
        self.assertEqual(code, 422)
        self.assertIn("Retain", page)
        self.assertEqual(request("POST", f"/submit/{trial_id}", dict(title="Safe <script> report", severity="low"))[0], 303)
        key = self.store.get(trial_id)["review_key"]
        code, _, page = request(path=f"/review/{key}")
        self.assertEqual(code, 200)
        self.assertIn("Safe &lt;script&gt; report", page)
        self.assertNotIn("P02", page)
        self.assertNotIn('"condition"', page)
        self.assertEqual(request(path="/health")[0], 200)
        self.assertEqual(request(path="/static/../peer-study.json")[0], 404)


if __name__ == "__main__":
    unittest.main()
