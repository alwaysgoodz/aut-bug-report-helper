"""BR-02/03 persistence contract and defensive validation."""
import tempfile
import unittest
from pathlib import Path

from bugreport.service import ReportStore, StatusConflict, ValidationError


class LifecycleTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.db = Path(temp.name) / "reports.db"
        self.store = ReportStore(self.db)

    def test_empty_list_and_counts(self):
        self.assertEqual(self.store.list_reports(), [])
        self.assertEqual(self.store.counts(), {"Open": 0, "In progress": 0, "Resolved": 0, "total": 0})

    def test_create_list_survives_reopen_and_newest_first(self):
        first = self.store.create(title="First", severity="low")
        second = self.store.create(title="Second", severity="high")
        self.assertEqual(ReportStore(self.db).list_reports(), [second, first])

    def test_full_status_cycle_persists(self):
        report = self.store.create(title="Lifecycle", severity="critical")
        for old, new in (("Open", "In progress"), ("In progress", "Resolved"), ("Resolved", "Open")):
            with self.subTest(new=new):
                self.store.update_status(report["id"], new, expected_status=old)
                self.assertEqual(ReportStore(self.db).get(report["id"])["status"], new)

    def test_unknown_id_and_invalid_status_leave_existing_report_unchanged(self):
        report = self.store.create(title="Keep me", severity="medium")
        with self.assertRaises(KeyError):
            self.store.update_status("unknown", "In progress")
        with self.assertRaises(ValueError):
            self.store.update_status(report["id"], "Closed")
        self.assertEqual(self.store.get(report["id"]), report)

    def test_cannot_skip_in_progress(self):
        report = self.store.create(title="Open", severity="low")
        with self.assertRaisesRegex(ValueError, "directly"):
            self.store.update_status(report["id"], "Resolved")
        self.assertEqual(self.store.get(report["id"]), report)

    def test_stale_update_is_rejected_without_lost_update(self):
        report = self.store.create(title="Shared state", severity="low")
        self.store.update_status(report["id"], "In progress", expected_status="Open")
        with self.assertRaises(StatusConflict):
            self.store.update_status(report["id"], "In progress", expected_status="Open")
        self.assertEqual(self.store.get(report["id"])["status"], "In progress")

    def test_non_text_and_overlong_fields_are_rejected_before_insert(self):
        for payload in (dict(title=42, severity="low"), dict(title="x"*161, severity="low"),
                        dict(title="Valid", severity="low", steps="x"*5001)):
            with self.subTest(payload=str(payload)[:80]), self.assertRaises(ValidationError):
                self.store.create(**payload)
        self.assertEqual(self.store.counts()["total"], 0)
