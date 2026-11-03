"""BR-04/05 acceptance: exact scoring, precise omissions and non-mutating filters."""
import tempfile
import unittest
from pathlib import Path

from bugreport.rules import completeness
from bugreport.service import FIELDS, ReportStore


class GuidanceTests(unittest.TestCase):
    def test_empty_report_has_zero_and_all_seven_missing(self):
        self.assertEqual(completeness({}), dict(score=0, completed=0, total=7, missing=list(FIELDS)))

    def test_each_present_field_and_six_of_seven_rounding(self):
        values = dict.fromkeys(FIELDS, "detail")
        values["severity"] = "high"
        self.assertEqual(completeness(values)["score"], 100)
        for missing in FIELDS:
            with self.subTest(missing=missing):
                partial = {**values, missing: " \t\n"}
                result = completeness(partial)
                self.assertEqual(result["score"], 86)
                self.assertEqual(result["missing"], [missing])

    def test_invalid_severity_and_nontext_are_missing(self):
        result = completeness(dict(title=7, severity="urgent"))
        self.assertEqual(result["score"], 0)
        self.assertEqual(len(result["missing"]), 7)

    def test_function_does_not_mutate_input_or_count_metadata(self):
        values = dict(title="Defect", severity="low", status="Resolved", id="abc", created_at="now")
        original = values.copy()
        self.assertEqual(completeness(values)["score"], 29)
        self.assertEqual(values, original)


class FilterTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.store = ReportStore(Path(temp.name)/"filters.db")
        self.high_open = self.store.create(title="High open", severity="high")
        self.low_open = self.store.create(title="Low open", severity="low")
        self.high_resolved = self.store.create(title="High resolved", severity="high")
        self.store.update_status(self.high_resolved["id"], "In progress")
        self.store.update_status(self.high_resolved["id"], "Resolved")

    def test_combined_filters_use_and(self):
        rows = self.store.list_reports(severity="high", status="Open")
        self.assertEqual([x["id"] for x in rows], [self.high_open["id"]])

    def test_each_filter_empty_result_and_clear_preserve_data(self):
        original = self.store.list_reports()
        self.assertEqual(len(self.store.list_reports(severity="high")), 2)
        self.assertEqual(len(self.store.list_reports(status="Open")), 2)
        self.assertEqual(self.store.list_reports(severity="critical", status="Resolved"), [])
        self.assertEqual(self.store.list_reports(), original)

    def test_invalid_filter_rejected_without_mutation(self):
        original = self.store.list_reports()
        for args in (dict(severity="' OR 1=1 --"), dict(status="Closed")):
            with self.assertRaises(ValueError):
                self.store.list_reports(**args)
        self.assertEqual(self.store.list_reports(), original)
