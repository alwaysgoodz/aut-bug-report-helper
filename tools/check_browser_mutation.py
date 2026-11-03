"""PI-01 controlled experiment; restore original JavaScript even if a runner fails."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="docs/a2/evidence/i2-focus-mutant.json")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    target = root/"bugreport/static/app.js"
    original = target.read_bytes()
    marker = b"if (summary) summary.focus();"
    if original.count(marker) != 1:
        raise RuntimeError("Expected exactly one error-focus statement; mutation was not applied")
    command = ["node", str(root/"node_modules/@playwright/test/cli.js"), "test", "--grep", "C1:"]
    env = {**os.environ, "BUGREPORT_PYTHON": sys.executable}
    start = time.perf_counter()
    try:
        target.write_bytes(original.replace(marker, b"// PI-01 controlled mutant: focus disabled."))
        result = subprocess.run(command, cwd=root, env=env, capture_output=True, text=True,
                                encoding="utf-8", errors="replace", timeout=90, check=False)
        results_path = root/"test-results/browser-results.json"
        report = json.loads(results_path.read_text(encoding="utf-8")) if results_path.exists() else {}
    finally:
        target.write_bytes(original)
    log = result.stdout + "\n" + result.stderr
    output = root/args.output
    output.parent.mkdir(parents=True, exist_ok=True)
    output.with_suffix(".log").write_text(log, encoding="utf-8")
    restored = target.read_bytes() == original
    caught = result.returncode != 0 and "toBeFocused" in log and report.get("stats", {}).get("unexpected") == 1
    observation = dict(experiment="PI-01 identical missing-focus mutation", command=command,
                       duration_seconds=round(time.perf_counter()-start, 3),
                       browser_exit_code=result.returncode, caught_by_focus_assertion=caught,
                       original_restored=restored, original_sha256=hashlib.sha256(original).hexdigest(),
                       stats=report.get("stats", {}), interpretation="One targeted controlled mutation; not a general defect-detection rate")
    output.write_text(json.dumps(observation, indent=2)+"\n", encoding="utf-8")
    print(json.dumps(observation, indent=2))
    return 0 if caught and restored else 1


if __name__ == "__main__":
    raise SystemExit(main())
