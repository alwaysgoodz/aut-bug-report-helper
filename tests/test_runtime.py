"""Check the required storage runtime in the initial scaffold."""
import sqlite3
import unittest


class RuntimeTest(unittest.TestCase):
    def test_sqlite_transactions_are_available(self):
        with sqlite3.connect(":memory:") as connection:
            self.assertEqual(connection.execute("SELECT 1").fetchone(), (1,))
