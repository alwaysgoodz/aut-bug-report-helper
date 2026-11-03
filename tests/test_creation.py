"""BR-01 acceptance cases: validation, persistence, and real CLI behaviour."""
import json
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from contextlib import closing
from datetime import datetime
from pathlib import Path

from bugreport.service import ReportStore


class CreationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.db = Path(self.temp.name) / "reports.db"
        self.store = ReportStore(self.db)
        self.payload = dict(title="Login fails", description="Blank page", steps="Open login",
                            expected="Dashboard", actual="Blank", environment="Firefox / Windows",
                            severity="high")

    def count(self):
        with closing(sqlite3.connect(self.db)) as connection:
            return connection.execute("SELECT COUNT(*) FROM reports").fetchone()[0]

    def test_persists_all_fields_across_new_connection(self):
        created = self.store.create(**self.payload)
        saved = ReportStore(self.db).get(created["id"])
        for key, value in self.payload.items():
            self.assertEqual(saved[key], value)
        self.assertEqual(saved, created)

    def test_generated_metadata_is_unique_open_and_utc(self):
        first = self.store.create(**self.payload)
        second = self.store.create(**self.payload)
        self.assertNotEqual(first["id"], second["id"])
        self.assertEqual(first["status"], "Open")
        self.assertEqual(datetime.fromisoformat(first["created_at"]).utcoffset().total_seconds(), 0)

    def test_title_is_trimmed(self):
        self.payload["title"] = "  Login fails\n"
        self.assertEqual(self.store.create(**self.payload)["title"], "Login fails")

    def test_empty_title_rejected_without_insert(self):
        self.payload["title"] = ""
        with self.assertRaisesRegex(ValueError, "title"):
            self.store.create(**self.payload)
        self.assertEqual(self.count(), 0)

    def test_whitespace_title_rejected_without_insert(self):
        self.payload["title"] = " \t\n"
        with self.assertRaisesRegex(ValueError, "title"):
            self.store.create(**self.payload)
        self.assertEqual(self.count(), 0)

    def test_invalid_severity_rejected_without_insert(self):
        self.payload["severity"] = "urgent"
        with self.assertRaisesRegex(ValueError, "severity"):
            self.store.create(**self.payload)
        self.assertEqual(self.count(), 0)

    def test_missing_severity_rejected_without_insert(self):
        self.payload.pop("severity")
        with self.assertRaisesRegex(ValueError, "severity"):
            self.store.create(**self.payload)
        self.assertEqual(self.count(), 0)

    def test_all_supported_severities(self):
        for severity in ("low", "medium", "high", "critical"):
            with self.subTest(severity=severity):
                self.payload["severity"] = severity
                self.assertEqual(self.store.create(**self.payload)["severity"], severity)

    def test_optional_fields_can_remain_blank(self):
        created = self.store.create(title="Intermittent failure", severity="low")
        for field in ("description", "steps", "expected", "actual", "environment"):
            self.assertEqual(created[field], "")

    def test_unicode_multiline_and_sql_text_are_preserved_as_data(self):
        self.payload["description"] = "缺陷\n'; DROP TABLE reports; --"
        created = self.store.create(**self.payload)
        self.assertEqual(self.store.get(created["id"])["description"], self.payload["description"])
        self.assertEqual(self.count(), 1)

    def test_unknown_id_returns_no_record(self):
        self.assertIsNone(self.store.get("not-an-id"))

    def test_invalid_submission_preserves_existing_record(self):
        created = self.store.create(**self.payload)
        self.payload["severity"] = "invalid"
        with self.assertRaises(ValueError):
            self.store.create(**self.payload)
        self.assertEqual(self.count(), 1)
        self.assertEqual(self.store.get(created["id"]), created)

    def run_cli(self, *args):
        return subprocess.run([sys.executable, "-m", "bugreport", "--db", str(self.db), *args],
                              capture_output=True, text=True, encoding="utf-8", check=False)

    def test_cli_create_then_read_from_separate_process(self):
        result = self.run_cli("create", "--title", "CLI defect", "--severity", "medium")
        self.assertEqual(result.returncode, 0, result.stderr)
        created = json.loads(result.stdout)
        read = self.run_cli("show", created["id"])
        self.assertEqual(read.returncode, 0, read.stderr)
        self.assertEqual(json.loads(read.stdout), created)

    def test_cli_invalid_title_exits_nonzero_without_insert(self):
        result = self.run_cli("create", "--title", "   ", "--severity", "low")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("title", result.stderr)
        self.assertEqual(self.count(), 0)

    def test_cli_unknown_id_has_explicit_error(self):
        result = self.run_cli("show", "missing")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("not found", result.stderr)
