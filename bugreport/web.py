"""Loopback-only HTTP adapter for the course prototype, not public hosting."""
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import re
import secrets
from urllib.parse import parse_qs, urlsplit

from . import views
from .service import FIELDS, LIMITS, SEVERITIES, STATUSES, ReportStore, StatusConflict, ValidationError

# A Unicode scalar can occupy four UTF-8 bytes, each percent-encoded as %XX.
# Allow every field's valid maximum plus form names/CSRF overhead, still bounded.
MAX_BODY = 12*sum(LIMITS.values()) + 4096
STATIC = Path(__file__).with_name("static")


def navigation_context(query):
    parsed = parse_qs(query, keep_blank_values=True, max_num_fields=8)
    if any(len(values) != 1 for values in parsed.values()):
        raise ValueError("Duplicate navigation parameters")
    params = {key: values[0] for key, values in parsed.items()}
    severity, status = params.get("severity", ""), params.get("status", "")
    page = int(params.get("page", "1"))
    if (severity and severity not in SEVERITIES) or (status and status not in STATUSES) or page < 1:
        raise ValueError("Invalid report filter or page")
    return views.list_context(severity=severity, status=status, page=page), params


class ReportServer(ThreadingHTTPServer):
    daemon_threads = True

    def __init__(self, address, store):
        if address[0] != "127.0.0.1":
            raise ValueError("This prototype supports loopback hosting only")
        self.store = store
        self.csrf_token = secrets.token_urlsafe(32)
        super().__init__(address, ReportHandler)


class ReportHandler(BaseHTTPRequestHandler):
    server_version = "BugReportHelper"
    sys_version = ""

    def setup(self):
        super().setup()
        self.connection.settimeout(5)

    def _send(self, status, body="", *, content_type="text/html; charset=utf-8", location=None):
        data = body.encode("utf-8") if isinstance(body, str) else body
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Referrer-Policy", "same-origin")
        self.send_header("Content-Security-Policy", "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; base-uri 'none'; frame-ancestors 'none'; form-action 'self'")
        if location:
            self.send_header("Location", location)
        self.end_headers()
        self.wfile.write(data)

    def _error(self, status, message):
        self._send(status, views.error_page(status, message))

    def _valid_host(self):
        port = self.server.server_address[1]
        hosts = {f"127.0.0.1:{port}", f"localhost:{port}"}
        if port == 80:
            hosts.update(("127.0.0.1", "localhost"))
        if len(self.headers.get_all("Host", [])) != 1 or self.headers.get("Host", "") not in hosts:
            self._error(400, "Unrecognised host")
            return False
        return True

    def do_GET(self):
        if not self._valid_host():
            return
        url = urlsplit(self.path)
        store = self.server.store
        if url.path == "/health":
            self._send(200, "ok", content_type="text/plain; charset=utf-8")
        elif url.path in ("/static/app.css", "/static/app.js", "/static/mark.svg"):
            mime = {"css": "text/css", "js": "text/javascript", "svg": "image/svg+xml"}[url.path.rsplit(".", 1)[1]]
            self._send(200, (STATIC / url.path.rsplit("/", 1)[1]).read_bytes(), content_type=mime+"; charset=utf-8")
        elif url.path == "/":
            try:
                context, _ = navigation_context(url.query)
                listing = store.list_page(**context)
            except ValueError:
                self._error(400, "Invalid report filter or page")
                return
            self._send(200, views.report_list(listing["reports"], store.counts(), severity=context.get("severity", ""),
                                              status=context.get("status", ""), pagination=listing))
        elif url.path == "/reports/new":
            self._send(200, views.report_form(self.server.csrf_token, store.counts()["total"]))
        elif re.fullmatch(r"/reports/[0-9a-f-]{36}", url.path):
            try:
                context, params = navigation_context(url.query)
            except ValueError:
                self._error(400, "Invalid report filter or page")
                return
            report = store.get(url.path.split("/")[2])
            if report is None:
                self._error(404, "Report not found")
            else:
                self._send(200, views.report_detail(report, self.server.csrf_token, store.counts()["total"],
                                                    created=params.get("created") == "1", updated=params.get("updated") == "1",
                                                    context=context))
        else:
            self._error(404, "Page not found")

    def do_POST(self):
        self.close_connection = True
        if not self._valid_host():
            return
        origin = self.headers.get("Origin")
        if origin is not None and origin != "http://" + self.headers["Host"]:
            self._error(403, "Request origin is not allowed")
            return
        if self.headers.get("Content-Type", "").split(";", 1)[0] != "application/x-www-form-urlencoded":
            self._error(415, "Use a form submission")
            return
        if "Transfer-Encoding" in self.headers:
            self._error(400, "Unsupported request encoding")
            return
        try:
            length = int(self.headers["Content-Length"])
        except (TypeError, ValueError):
            self._error(411, "A valid content length is required")
            return
        if length < 0:
            self._error(400, "Invalid content length")
            return
        if length > MAX_BODY:
            self._error(413, "Report submission is too large")
            return
        try:
            raw = self.rfile.read(length)
            if len(raw) != length:
                self._error(400, "Incomplete form submission")
                return
            parsed = parse_qs(raw.decode("utf-8"), keep_blank_values=True, strict_parsing=True,
                              max_num_fields=12, encoding="utf-8", errors="strict")
        except (UnicodeError, ValueError):
            self._error(400, "Invalid form submission")
            return
        if any(len(values) != 1 for values in parsed.values()):
            self._error(400, "Duplicate form fields are not supported")
            return
        data = {key: values[0] for key, values in parsed.items()}
        if not secrets.compare_digest(data.get("_csrf", "").encode("utf-8"), self.server.csrf_token.encode("ascii")):
            self._error(403, "This form has expired. Reload the page and try again.")
            return
        path = urlsplit(self.path).path
        store = self.server.store
        if path == "/reports":
            values = {field: data.get(field, "") for field in FIELDS}
            try:
                report = store.create(**values)
            except ValidationError as error:
                self._send(422, views.report_form(self.server.csrf_token, store.counts()["total"], values, error.errors))
                return
            self._send(303, location=f"/reports/{report['id']}?created=1")
        elif re.fullmatch(r"/reports/[0-9a-f-]{36}/status", path):
            report_id = path.split("/")[2]
            try:
                context, _ = navigation_context(urlsplit(self.path).query)
            except ValueError:
                self._error(400, "Invalid report filter or page")
                return
            try:
                if data.get("expected_status", "") not in ("Open", "In progress", "Resolved"):
                    raise ValueError("Reload the report before changing its status.")
                store.update_status(report_id, data.get("status", ""), expected_status=data["expected_status"])
            except KeyError:
                self._error(404, "Report not found")
                return
            except ValueError as error:
                report = store.get(report_id)
                if report is None:
                    self._error(404, "Report not found")
                    return
                self._send(409 if isinstance(error, StatusConflict) else 422,
                           views.report_detail(report, self.server.csrf_token, store.counts()["total"], error=str(error),
                                               context=context))
                return
            self._send(303, location=views.context_url(f"/reports/{report_id}", context, notice="updated"))
        else:
            self._error(404, "Page not found")


def serve(database, port=8765):
    with ReportServer(("127.0.0.1", port), ReportStore(database)) as server:
        print(f"Bug Report Helper: http://127.0.0.1:{server.server_address[1]}", flush=True)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print("\nServer stopped.", flush=True)
