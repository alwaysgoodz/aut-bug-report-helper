"""BR-01 creation service; persistence uses only the Python standard library."""
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

SEVERITIES = ("low", "medium", "high", "critical")
STATUSES = ("Open", "In progress", "Resolved")
TRANSITIONS = {"Open": ("In progress",), "In progress": ("Resolved",), "Resolved": ("Open",)}
FIELDS = ("title", "description", "steps", "expected", "actual", "environment", "severity")
LABELS = {"title": "Title", "description": "Description", "steps": "Steps to reproduce",
          "expected": "Expected behaviour", "actual": "Actual behaviour",
          "environment": "Environment", "severity": "Severity"}
LIMITS = {field: 5000 for field in FIELDS}
LIMITS.update(title=160, environment=240, severity=16)
PAGE_SIZE = 25
# Shared with the browser form: Unicode whitespace plus BOM and legacy separators.
BLANK_CODEPOINTS = (*range(9, 14), *range(28, 33), 133, 160, 5760,
                    *range(8192, 8203), 8232, 8233, 8239, 8287, 12288, 65279)
TEXT_BLANK = "".join(chr(value) for value in BLANK_CODEPOINTS)


def has_text(value) -> bool:
    return isinstance(value, str) and bool(value.strip(TEXT_BLANK))


class ValidationError(ValueError):
    """Field-specific feedback shared by the CLI and web adapter."""

    def __init__(self, errors):
        self.errors = errors
        super().__init__("; ".join(f"{key}: {value}" for key, value in errors.items()))


class StatusConflict(ValueError):
    """The displayed report state is stale; no update has been applied."""


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
            connection.execute("CREATE INDEX IF NOT EXISTS reports_created_idx ON reports(created_at DESC, id DESC)")
            connection.execute("CREATE INDEX IF NOT EXISTS reports_filter_idx ON reports(severity, status, created_at DESC, id DESC)")

    def _connect(self):
        # The context manager commits/rolls back; closing is explicit through wrapper.
        return _Connection(self.database)

    def create(self, *, title: str, severity: str = "", description: str = "",
               steps: str = "", expected: str = "", actual: str = "",
               environment: str = "") -> dict:
        payload = dict(title=title, severity=severity, description=description, steps=steps,
                       expected=expected, actual=actual, environment=environment)
        errors = {}
        for field, value in payload.items():
            if not isinstance(value, str):
                errors[field] = "Enter text."
            elif len(value) > LIMITS[field]:
                errors[field] = f"Use {LIMITS[field]} characters or fewer."
        if isinstance(title, str) and not has_text(title):
            errors["title"] = "Enter a title that contains more than whitespace."
        if not isinstance(severity, str) or severity not in SEVERITIES:
            errors["severity"] = "Choose low, medium, high or critical severity."
        if errors:
            raise ValidationError(errors)
        title = title.strip(TEXT_BLANK)
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

    def list_reports(self, *, severity: str = "", status: str = "") -> list[dict]:
        where, values = self._filters(severity, status)
        query = "SELECT * FROM reports" + where + " ORDER BY created_at DESC, id DESC"
        with self._connect() as connection:
            connection.row_factory = sqlite3.Row
            return [dict(row) for row in connection.execute(query, values).fetchall()]

    @staticmethod
    def _filters(severity, status):
        if severity and severity not in SEVERITIES:
            raise ValueError("Invalid severity filter")
        if status and status not in STATUSES:
            raise ValueError("Invalid status filter")
        conditions, values = [], []
        for field, value in (("severity", severity), ("status", status)):
            if value:
                conditions.append(field + " = ?")
                values.append(value)
        return (" WHERE " + " AND ".join(conditions) if conditions else ""), values

    def list_page(self, *, severity: str = "", status: str = "", page: int = 1) -> dict:
        """Bound UI rendering while preserving a consistent count/row snapshot."""
        if type(page) is not int or page < 1:
            raise ValueError("Page must be a positive integer")
        where, values = self._filters(severity, status)
        with self._connect() as connection:
            connection.row_factory = sqlite3.Row
            connection.execute("BEGIN")
            total = connection.execute("SELECT COUNT(*) FROM reports" + where, values).fetchone()[0]
            pages = max(1, (total + PAGE_SIZE - 1)//PAGE_SIZE)
            page = min(page, pages)
            rows = connection.execute("SELECT * FROM reports" + where +
                                      " ORDER BY created_at DESC, id DESC LIMIT ? OFFSET ?",
                                      (*values, PAGE_SIZE, (page-1)*PAGE_SIZE)).fetchall()
        return dict(reports=[dict(row) for row in rows], total=total,
                    page=page, pages=pages, page_size=PAGE_SIZE)

    def counts(self) -> dict:
        result = {status: 0 for status in STATUSES}
        with self._connect() as connection:
            for status, count in connection.execute("SELECT status, COUNT(*) FROM reports GROUP BY status"):
                result[status] = count
        result["total"] = sum(result.values())
        return result

    def update_status(self, report_id: str, status: str, *, expected_status: str | None = None) -> dict:
        if status not in STATUSES:
            raise ValueError("Invalid status")
        report = self.get(report_id)
        if report is None:
            raise KeyError(report_id)
        old_status = report["status"]
        if expected_status is not None and old_status != expected_status:
            raise StatusConflict("This report changed. Reload it before updating the status.")
        if status != old_status and status not in TRANSITIONS[old_status]:
            raise ValueError(f"Cannot change {old_status} directly to {status}")
        with self._connect() as connection:
            changed = connection.execute("UPDATE reports SET status = ? WHERE id = ? AND status = ?",
                                         (status, report_id, old_status)).rowcount
            if changed != 1:
                raise StatusConflict("This report changed. Reload it before updating the status.")
        report["status"] = status
        return report


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
