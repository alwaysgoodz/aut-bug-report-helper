"""BR-01 creation service; persistence uses only the Python standard library."""
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

SEVERITIES = ("low", "medium", "high", "critical")


class ReportStore:
    """A file-backed store. Each operation closes its connection deterministically."""

    def __init__(self, database: str | Path):
        self.database = str(database)
        if self.database == ":memory:":
            raise ValueError("Use a file-backed database for persistent reports")
        with self._connect() as connection:
            connection.execute("""CREATE TABLE IF NOT EXISTS reports (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL CHECK(length(trim(title)) > 0),
                description TEXT NOT NULL,
                steps TEXT NOT NULL,
                expected TEXT NOT NULL,
                actual TEXT NOT NULL,
                environment TEXT NOT NULL,
                severity TEXT NOT NULL CHECK(severity IN ('low','medium','high','critical')),
                status TEXT NOT NULL CHECK(status IN ('Open','In progress','Resolved')),
                created_at TEXT NOT NULL
            )""")

    def _connect(self):
        # The context manager commits/rolls back; closing is explicit through wrapper.
        return _Connection(self.database)

    def create(self, *, title: str, severity: str = "", description: str = "",
               steps: str = "", expected: str = "", actual: str = "",
               environment: str = "") -> dict:
        title = title.strip()
        if not title:
            raise ValueError("title must contain non-whitespace text")
        if severity not in SEVERITIES:
            raise ValueError("severity must be low, medium, high or critical")
        report = dict(id=str(uuid4()), title=title, description=description, steps=steps,
                      expected=expected, actual=actual, environment=environment,
                      severity=severity, status="Open",
                      created_at=datetime.now(timezone.utc).isoformat())
        with self._connect() as connection:
            connection.execute("""INSERT INTO reports
                (id, title, description, steps, expected, actual, environment, severity, status, created_at)
                VALUES (:id, :title, :description, :steps, :expected, :actual, :environment,
                        :severity, :status, :created_at)""", report)
        return report

    def get(self, report_id: str) -> dict | None:
        with self._connect() as connection:
            connection.row_factory = sqlite3.Row
            row = connection.execute("SELECT * FROM reports WHERE id = ?", (report_id,)).fetchone()
            return dict(row) if row is not None else None


class _Connection:
    """Compose SQLite's transaction context with guaranteed connection closure."""

    def __init__(self, database):
        self.connection = sqlite3.connect(database)

    def __enter__(self):
        return self.connection.__enter__()

    def __exit__(self, exc_type, exc_value, traceback):
        try:
            return self.connection.__exit__(exc_type, exc_value, traceback)
        finally:
            self.connection.close()
