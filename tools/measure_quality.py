"""Single-client list latency on a controlled synthetic database, with raw timings."""
import argparse
from contextlib import redirect_stderr
from datetime import datetime, timezone
import hashlib
import http.client
import io
import json
import math
from pathlib import Path
import platform
import sqlite3
import statistics
import subprocess
import sys
import tempfile
import threading
import time

from bugreport.service import ReportStore, SEVERITIES
from bugreport.web import ReportServer


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="docs/a2/evidence/performance.json")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    source = {str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
              for p in sorted((root/"bugreport").rglob("*")) if p.is_file() and "__pycache__" not in p.parts}
    sha = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip()
    status = subprocess.check_output(["git", "status", "--porcelain"], cwd=root, text=True)
    with tempfile.TemporaryDirectory(prefix="bugreport-quality-") as directory:
        db = Path(directory)/"quality.db"
        store = ReportStore(db)
        setup_start = time.perf_counter()
        for index in range(500):
            store.create(title=f"Synthetic defect {index:04d}", severity=SEVERITIES[index % 4],
                         description="Synthetic course benchmark, no personal information.",
                         steps="1. Open app\n2. Open settings", expected="Controls appear",
                         actual="Panel is blank", environment="Synthetic build / browser")
        setup_seconds = time.perf_counter()-setup_start
        server = ReportServer(("127.0.0.1", 0), store)
        worker = threading.Thread(target=server.serve_forever, kwargs={"poll_interval": .01}, daemon=True)
        worker.start()
        durations, response_bytes = [], []
        try:
            with redirect_stderr(io.StringIO()):
                for index in range(55):
                    start = time.perf_counter()
                    connection = http.client.HTTPConnection("127.0.0.1", server.server_address[1], timeout=5)
                    try:
                        connection.request("GET", "/")
                        response = connection.getresponse()
                        body = response.read()
                        if response.status != 200:
                            raise RuntimeError(f"Unexpected benchmark status {response.status}")
                    finally:
                        connection.close()
                    elapsed = (time.perf_counter()-start)*1000
                    if index >= 5:
                        durations.append(round(elapsed, 4))
                        response_bytes.append(len(body))
        finally:
            server.shutdown()
            worker.join(timeout=2)
            server.server_close()
        db_bytes = db.stat().st_size
    p95 = sorted(durations)[math.ceil(.95*len(durations))-1]
    result = dict(measured_at=datetime.now(timezone.utc).isoformat(), git_sha=sha,
                  working_tree_status_before_measurement=status,
                  environment=dict(python=sys.version, sqlite=sqlite3.sqlite_version,
                                   platform=platform.platform(), processor=platform.processor(), machine=platform.machine()),
                  scenario=dict(records=500, concurrent_clients=1, warmups=5, samples=50,
                                method="HTTP GET / including connection, render and full-body read; warm local file cache"),
                  target=dict(p95_ms_less_than=250, established_in="docs/a2/quality-plan.md"),
                  observations=dict(median_ms=round(statistics.median(durations), 4), p95_ms=p95,
                                    min_ms=min(durations), max_ms=max(durations),
                                    setup_seconds=round(setup_seconds, 4), database_bytes=db_bytes,
                                    response_bytes=response_bytes, durations_ms=durations),
                  target_met=p95 < 250, source_sha256=source,
                  limits="Single local machine and client, warm cache, fixed synthetic data; no cold-start/concurrency/network generalisation")
    output = root/args.output
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2)+"\n", encoding="utf-8")
    print(json.dumps({k: result[k] for k in ("git_sha", "environment", "target", "target_met")}, indent=2))
    print(json.dumps(result["observations"], indent=2))
    return 0 if result["target_met"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
