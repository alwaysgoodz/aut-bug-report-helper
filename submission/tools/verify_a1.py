"""Recheck the exact A1 reference without changing the active application checkout."""
from __future__ import annotations

import io
import json
import platform
import subprocess
import sys
import tarfile
from datetime import datetime
from pathlib import Path
from urllib.request import Request, urlopen
from zoneinfo import ZoneInfo

REPO = Path(__file__).resolve().parents[2]
SHA = "03fb9c5e41f80026c0ec66c28a92b09ed6f1251e"
SLUG = "alwaysgoodz/aut-bug-report-helper"
OUT = REPO / "submission/evidence"
SNAPSHOT = REPO / "tmp/a1-reference-recheck"


def gh_json(endpoint):
    result = subprocess.run(["gh", "api", endpoint], check=True, capture_output=True, text=True, encoding="utf-8")
    return json.loads(result.stdout)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    SNAPSHOT.mkdir(parents=True, exist_ok=True)
    archive = subprocess.run(["git", "archive", SHA], cwd=REPO, check=True, capture_output=True).stdout
    # Only an immutable, locally tracked Git tree is extracted here.
    with tarfile.open(fileobj=io.BytesIO(archive)) as source:
        source.extractall(SNAPSHOT, filter="data")
    checks = []
    for label, arguments in [
        ("acceptance", ["-m", "unittest", "discover", "-s", "tests", "-v"]),
        ("compile", ["-m", "compileall", "-q", "bugreport", "tests"]),
    ]:
        result = subprocess.run([sys.executable, *arguments], cwd=SNAPSHOT, capture_output=True, text=True, encoding="utf-8")
        (OUT / f"a1-{label}-recheck.log").write_text(result.stdout + result.stderr, encoding="utf-8")
        checks.append({"name": label, "command": [sys.executable, *arguments], "exit_code": result.returncode})
        if result.returncode:
            raise RuntimeError(f"{label} failed; inspect preserved log")

    metadata = gh_json(f"repos/{SLUG}")
    pull = gh_json(f"repos/{SLUG}/pulls/7")
    reviews = gh_json(f"repos/{SLUG}/pulls/7/reviews")
    inline = gh_json(f"repos/{SLUG}/pulls/7/comments")
    discussion = gh_json(f"repos/{SLUG}/issues/7/comments")
    run = gh_json(f"repos/{SLUG}/actions/runs/41675675123")
    jobs = gh_json(f"repos/{SLUG}/actions/runs/41675675123/jobs")
    issue = gh_json(f"repos/{SLUG}/issues/1")
    unauthenticated = []
    for suffix in ["", "/issues/1", "/pull/7", "/actions/runs/41675675123", f"/blob/{SHA}/README.md"]:
        url = f"https://github.com/{SLUG}{suffix}"
        request = Request(url, headers={"User-Agent": "A1-evidence-verification"})
        with urlopen(request, timeout=30) as response:
            unauthenticated.append({"url": url, "status": response.status, "final_url": response.url})
    output = {
        "verified_at": datetime.now(ZoneInfo("Asia/Shanghai")).isoformat(),
        "assessment_code_reference": SHA,
        "local_environment": {"python": sys.version, "platform": platform.platform()},
        "checks": checks,
        "repository": {"url": metadata["html_url"], "private": metadata["private"], "default_branch": metadata["default_branch"]},
        "requirement": {key: issue[key] for key in ("number", "title", "html_url", "created_at", "state")},
        "pull_request": {"url": pull["html_url"], "state": pull["state"], "draft": pull["draft"], "head_sha": pull["head"]["sha"], "merged": pull["merged"]},
        "reviews": [{"author": r["user"]["login"], **{key: r[key] for key in ("state", "body", "submitted_at", "commit_id", "html_url")}} for r in reviews],
        "inline_review_comment_count": len(inline),
        "discussion_comment_count": len(discussion),
        "ci": {key: run[key] for key in ("id", "html_url", "head_sha", "status", "conclusion", "created_at")},
        "ci_jobs": [{key: j[key] for key in ("name", "conclusion", "html_url")} for j in jobs["jobs"]],
        "unauthenticated_access": unauthenticated,
        "limits": ["Approval has an empty body; no substantive review finding or reviewer test is established.", "Reviewer-to-member mapping and individual contributions require human confirmation.", "This verifier is AI-assisted execution, not an independent teammate test."],
    }
    (OUT / "verification.json").write_text(json.dumps(output, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"reference": SHA, "checks": checks, "public_access": unauthenticated, "reviews": output["reviews"]}, indent=2))


if __name__ == "__main__":
    main()
