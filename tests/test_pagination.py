"""Bounded browsing keeps every report reachable and filters/counts consistent."""
import tempfile
import unittest
from pathlib import Path

from bugreport.rules import completeness
from bugreport.service import BLANK_CODEPOINTS, PAGE_SIZE, ReportStore, ValidationError


class PaginationTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.store = ReportStore(Path(temp.name)/"pages.db")

    def test_empty_page_is_well_defined(self):
        self.assertEqual(self.store.list_page(), dict(reports=[], total=0, page=1, pages=1, page_size=25))

    def test_all_pages_are_stable_without_duplicates_or_omissions(self):
        for index in range(53):
            self.store.create(title=f"Report {index:03d}", severity="high" if index % 2 else "low")
        all_reports = self.store.list_reports()
        pages = [self.store.list_page(page=n) for n in (1, 2, 3)]
        self.assertEqual([len(x["reports"]) for x in pages], [25, 25, 3])
        self.assertTrue(all(x["total"] == 53 and x["pages"] == 3 for x in pages))
        self.assertEqual([r for x in pages for r in x["reports"]], all_reports)
        self.assertEqual(self.store.list_page(page=999), pages[-1])

    def test_filtered_count_page_and_order_match_legacy_query(self):
        for index in range(60):
            self.store.create(title=f"Filter {index:03d}", severity="high" if index % 2 else "low")
        expected = self.store.list_reports(severity="high", status="Open")
        first = self.store.list_page(severity="high", status="Open")
        last = self.store.list_page(severity="high", status="Open", page=2)
        self.assertEqual(first["total"], 30)
        self.assertEqual(first["reports"]+last["reports"], expected)
        self.assertEqual(self.store.counts()["total"], 60)

    def test_invalid_pages_and_filters_are_rejected(self):
        for page in (0, -1, "1", True, 1.5):
            with self.subTest(page=page), self.assertRaises(ValueError):
                self.store.list_page(page=page)
        with self.assertRaises(ValueError):
            self.store.list_page(status="Closed")


class WhitespaceContractTests(unittest.TestCase):
    def test_every_shared_blank_character_has_identical_server_meaning(self):
        for point in BLANK_CODEPOINTS:
            with self.subTest(codepoint=point):
                self.assertEqual(completeness(dict(title=chr(point)))["score"], 0)
        self.assertEqual(completeness(dict(title="缺陷", severity="high"))["score"], 29)

    def test_bom_and_nel_only_titles_cannot_be_persisted(self):
        with tempfile.TemporaryDirectory() as directory:
            store = ReportStore(Path(directory)/"blank.db")
            for title in ("\ufeff", "\u0085", "\u001c\u00a0\ufeff"):
                with self.subTest(title=repr(title)), self.assertRaises(ValidationError):
                    store.create(title=title, severity="low")
            created = store.create(title="\ufeff Login fails \u0085", severity="low")
            self.assertEqual(created["title"], "Login fails")
            self.assertEqual(store.counts()["total"], 1)
