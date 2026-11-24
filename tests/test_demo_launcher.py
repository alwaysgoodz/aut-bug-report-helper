"""Demo data integrity, exclusive launch and occupied-port recovery."""
from contextlib import redirect_stderr
import io
from pathlib import Path
import tempfile
import threading
import unittest

from bugreport.service import ReportStore
from tools.demo_launcher import (WorkspaceBusy, WorkspaceLock, create_server, main,
                                 prepare_database, reset_demo, running_workspace, self_check, write_ready)


class DemoLauncherTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="demo-tests-")
        self.addCleanup(self.temporary.cleanup)
        self.directory = Path(self.temporary.name) / "演示 data"
        self.directory.mkdir()

    def test_repeat_prepare_preserves_added_report_and_status(self):
        database = prepare_database(self.directory)
        store = ReportStore(database)
        report = store.create(title="Retained 演示 report", severity="high")
        store.update_status(report["id"], "In progress")
        self.assertEqual(prepare_database(self.directory), database)
        self.assertEqual(store.counts()["total"], 5)
        self.assertEqual(store.get(report["id"])["status"], "In progress")

    def test_reset_creates_readable_backup_before_replacing_demo_only(self):
        database = prepare_database(self.directory)
        report = ReportStore(database).create(title="Preserve in backup", severity="low")
        unrelated = ReportStore(self.directory / "other.db")
        unrelated.create(title="Unrelated data", severity="medium")
        with WorkspaceLock(self.directory):
            backup = reset_demo(self.directory)
        self.assertTrue(backup.is_file())
        self.assertEqual(ReportStore(backup).counts()["total"], 5)
        self.assertEqual(ReportStore(backup).get(report["id"])["title"], "Preserve in backup")
        self.assertEqual(ReportStore(database).counts()["total"], 4)
        self.assertEqual(unrelated.counts()["total"], 1)

    def test_exclusive_lock_rejects_another_writer_and_releases(self):
        with WorkspaceLock(self.directory):
            with self.assertRaises(WorkspaceBusy):
                with WorkspaceLock(self.directory):
                    self.fail("A second writer acquired the live workspace")
        with WorkspaceLock(self.directory):
            pass

    def test_reset_is_refused_while_workspace_is_running(self):
        database = prepare_database(self.directory)
        before = database.read_bytes()
        with WorkspaceLock(self.directory), redirect_stderr(io.StringIO()):
            self.assertEqual(main(["--data-dir", str(self.directory), "--reset-demo", "--yes"]), 2)
        self.assertEqual(database.read_bytes(), before)
        self.assertFalse((self.directory / "backups").exists())

    def test_occupied_port_uses_another_listener(self):
        database = prepare_database(self.directory)
        with create_server(database, 0) as original:
            with create_server(database, original.server_address[1]) as fallback:
                self.assertNotEqual(original.server_address[1], fallback.server_address[1])
                self.assertEqual(fallback.server_address[0], "127.0.0.1")

    def test_ready_file_finds_only_live_loopback_workspace(self):
        database = prepare_database(self.directory)
        with create_server(database, 0) as server:
            worker = threading.Thread(target=server.serve_forever, kwargs={"poll_interval": .02}, daemon=True)
            worker.start()
            try:
                record = write_ready(self.directory, server)
                self.assertTrue(record["fictional_data"])
                self.assertEqual(running_workspace(self.directory), record["url"])
                (self.directory / "workspace.json").write_text('{"schema":1,"url":"https://example.com/"}', encoding="utf-8")
                self.assertIsNone(running_workspace(self.directory))
            finally:
                server.shutdown()
                worker.join(timeout=2)

    def test_self_check_checks_real_assets_and_temporary_sqlite(self):
        result = self_check()
        self.assertTrue(result["static_assets"])
        self.assertTrue(result["sqlite_write"])
        self.assertEqual(result["fictional_seed_count"], 4)


if __name__ == "__main__":
    unittest.main()
