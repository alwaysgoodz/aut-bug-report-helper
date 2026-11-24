"""Offline demo entry point: isolated data, safe reset and native browser launch."""
import argparse
from contextlib import closing, redirect_stderr
from datetime import datetime, timezone
import errno
import http.client
import json
import os
from pathlib import Path
import sqlite3
import socket
import sys
import tempfile
import time
import traceback
from urllib.parse import urlsplit
import webbrowser

from bugreport.service import ReportStore
from bugreport.web import ReportServer, STATIC
from tools.seed_demo import seed_database

VERSION = "1.0.0-demo"


class WorkspaceBusy(RuntimeError):
    pass


class WorkspaceLock:
    def __init__(self, directory):
        self.path = Path(directory) / ".demo.lock"
        self.handle = None

    def __enter__(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.handle = self.path.open("a+b")
        if self.handle.tell() == 0:
            self.handle.write(b"0")
            self.handle.flush()
        self.handle.seek(0)
        try:
            if os.name == "nt":
                import msvcrt
                msvcrt.locking(self.handle.fileno(), msvcrt.LK_NBLCK, 1)
            else:
                import fcntl
                fcntl.flock(self.handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError as error:
            self.handle.close()
            self.handle = None
            raise WorkspaceBusy("Demo workspace is already open") from error
        return self

    def __exit__(self, *_):
        if self.handle is not None:
            self.handle.close()
            self.handle = None


def default_directory():
    source = Path(__file__).resolve().parents[1]
    base = source.parent if (source.parent / "runtime" / "python.exe").exists() else source
    return base / "demo-data"


def prepare_database(directory):
    database = Path(directory) / "demo-reports.db"
    if ReportStore(database).counts()["total"] == 0:
        seed_database(database)
    return database


def reset_demo(directory):
    """Caller holds the workspace lock and has confirmed; keep a SQLite backup."""
    directory = Path(directory)
    database = directory / "demo-reports.db"
    backup = None
    if database.exists():
        backups = directory / "backups"
        backups.mkdir(exist_ok=True)
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
        backup = backups / f"demo-reports-{stamp}.db"
        with closing(sqlite3.connect(database)) as source, closing(sqlite3.connect(backup)) as target:
            source.backup(target)
    # Build a complete replacement before replacing the old database.
    with tempfile.TemporaryDirectory(prefix="reset-", dir=directory) as temporary:
        fresh = Path(temporary) / "fresh.db"
        seed_database(fresh)
        os.replace(fresh, database)
    return backup


class DemoServer(ReportServer):
    allow_reuse_address = False

    def server_bind(self):
        if os.name == "nt":
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_EXCLUSIVEADDRUSE, 1)
        super().server_bind()


def create_server(database, port):
    store = ReportStore(database)
    try:
        return DemoServer(("127.0.0.1", port), store)
    except OSError as error:
        if port == 0 or (error.errno not in (errno.EADDRINUSE, 10048) and getattr(error, "winerror", None) != 10013):
            raise
        return DemoServer(("127.0.0.1", 0), store)


def write_ready(directory, server):
    payload = dict(schema=1, version=VERSION, pid=os.getpid(),
                   url=f"http://127.0.0.1:{server.server_address[1]}/",
                   database="demo-reports.db", fictional_data=True)
    path = Path(directory) / "workspace.json"
    temporary = path.with_suffix(".tmp")
    temporary.write_text(json.dumps(payload, indent=2)+"\n", encoding="utf-8")
    os.replace(temporary, path)
    return payload


def running_workspace(directory):
    path = Path(directory) / "workspace.json"
    for _ in range(15):
        try:
            record = json.loads(path.read_text(encoding="utf-8"))
            url = urlsplit(record["url"])
            if record.get("schema") != 1 or url.scheme != "http" or url.hostname != "127.0.0.1" or url.path != "/":
                return None
            connection = http.client.HTTPConnection("127.0.0.1", url.port, timeout=.3)
            try:
                connection.request("GET", "/health")
                response = connection.getresponse()
                if response.status == 200 and response.read() == b"ok" and response.getheader("Server", "").startswith("BugReportHelper"):
                    return record["url"]
            finally:
                connection.close()
        except (OSError, ValueError, KeyError, http.client.HTTPException):
            pass  # A second launch can race the first server's ready-file write.
        time.sleep(.1)
    return None


def self_check():
    for asset in ("app.css", "app.js", "mark.svg"):
        if not (STATIC / asset).is_file():
            raise FileNotFoundError(f"Missing packaged resource: {asset}")
    with tempfile.TemporaryDirectory(prefix="bug-report-check-") as directory:
        database = prepare_database(directory)
        assert ReportStore(database).counts()["total"] == 4
    return dict(version=VERSION, python=sys.version.split()[0], sqlite=sqlite3.sqlite_version,
                static_assets=True, sqlite_write=True, fictional_seed_count=4)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Bug Report Helper offline demonstration")
    parser.add_argument("--data-dir", type=Path, default=default_directory())
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--no-browser", action="store_true")
    parser.add_argument("--reset-demo", action="store_true", help="Back up and reset only this demo workspace")
    parser.add_argument("--yes", action="store_true", help="Confirm an explicitly requested reset")
    parser.add_argument("--check", action="store_true", help="Check assets and temporary SQLite without starting a server")
    args = parser.parse_args(argv)
    if not 0 <= args.port <= 65535:
        parser.error("Port must be between 0 and 65535")
    if args.yes and not args.reset_demo:
        parser.error("--yes requires --reset-demo")
    if args.check:
        print(json.dumps(self_check(), indent=2))
        return 0
    directory = args.data_dir.resolve()
    try:
        with WorkspaceLock(directory):
            if args.reset_demo:
                if not args.yes and input("Close the server first. Back up and reset demo data? Type RESET: ") != "RESET":
                    print("Reset cancelled; data unchanged.")
                    return 0
                backup = reset_demo(directory)
                print(f"Demo reset to four fictional examples. Backup: {backup or 'No previous data'}")
                return 0
            database = prepare_database(directory)
            with create_server(database, args.port) as server:
                ready = write_ready(directory, server)
                print(f"\nBUG REPORT HELPER | {VERSION} | OFFLINE DEMO\n")
                print("Fictional Study Planner examples; not human evaluation results.")
                print(f"Workspace: {ready['url']}\nData: {database}\n")
                print("Keep this window open. Press Ctrl+C to stop; your reports are retained.")
                print("If the browser did not open, copy the workspace address above.\n", flush=True)
                if not args.no_browser:
                    webbrowser.open(ready["url"])
                with (directory / "server.log").open("a", encoding="utf-8") as log, redirect_stderr(log):
                    try:
                        server.serve_forever(poll_interval=.2)
                    except KeyboardInterrupt:
                        print("\nDemo stopped. Data retained.")
            return 0
    except WorkspaceBusy:
        if args.reset_demo:
            print("Reset refused: the demo is running. Stop its window first.", file=sys.stderr)
            return 2
        url = running_workspace(directory)
        if not url:
            print("Workspace is busy. Wait for its startup or close the original demo window.", file=sys.stderr)
            return 2
        print(f"Demo already running: {url}")
        if not args.no_browser:
            webbrowser.open(url)
        return 0
    except (OSError, sqlite3.Error) as error:
        print(f"Demo could not start: {error}\nExtract the whole ZIP into a writable folder and retry.", file=sys.stderr)
        return 2


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception:
        traceback.print_exc()
        raise SystemExit(1)
