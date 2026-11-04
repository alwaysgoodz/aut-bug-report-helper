"""BR-02/03 HTTP acceptance and local security boundaries; no browser dependency."""
import http.client
import re
import tempfile
import threading
import unittest
from pathlib import Path
from urllib.parse import urlencode

from bugreport.service import ReportStore
from bugreport.web import MAX_BODY, ReportServer


class WebTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        cls.store = ReportStore(Path(cls.temp.name) / "web.db")
        cls.server = ReportServer(("127.0.0.1", 0), cls.store)
        cls.port = cls.server.server_address[1]
        cls.worker = threading.Thread(target=cls.server.serve_forever, kwargs={"poll_interval": .02}, daemon=True)
        cls.worker.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.worker.join(timeout=2)
        cls.server.server_close()
        cls.temp.cleanup()

    def request(self, method="GET", path="/", data=None, headers=None, raw=None):
        connection = http.client.HTTPConnection("127.0.0.1", self.port, timeout=5)
        self.addCleanup(connection.close)
        request_headers = dict(headers or {})
        body = raw
        if data is not None:
            body = urlencode(data).encode("utf-8")
            request_headers.setdefault("Content-Type", "application/x-www-form-urlencoded")
        connection.request(method, path, body, request_headers)
        response = connection.getresponse()
        return response.status, dict(response.getheaders()), response.read().decode("utf-8")

    def form_data(self, **values):
        return dict(_csrf=self.server.csrf_token, title="HTTP defect", severity="medium", **values)

    def test_form_has_seven_visible_labels_and_empty_explicit_severity(self):
        code, _, body = self.request(path="/reports/new")
        self.assertEqual(code, 200)
        for field in ("title", "description", "steps", "expected", "actual", "environment", "severity"):
            self.assertIn(f'for="{field}"', body)
        self.assertIn('<option value="">Select severity</option>', body)
        self.assertNotIn('value="medium" selected', body)

    def test_full_valid_unicode_payload_fits_transport_and_preserves_all_fields(self):
        values = dict(_csrf=self.server.csrf_token, title="\U0001f41b"*160,
                      severity="critical", environment="\U0001f310"*240)
        values.update({field: "\U0001f41b"*5000 for field in ("description", "steps", "expected", "actual")})
        code, headers, _ = self.request("POST", "/reports", values)
        self.assertEqual(code, 303)
        saved = self.store.get(headers["Location"].split("/")[2].split("?")[0])
        for field, value in values.items():
            if field != "_csrf":
                self.assertEqual(saved[field], value)

    def test_browser_create_redirect_reload_and_status_cycle(self):
        code, headers, _ = self.request("POST", "/reports", self.form_data(steps="Open settings"))
        self.assertEqual(code, 303)
        location = headers["Location"]
        report_id = location.split("/")[2].split("?")[0]
        _, _, page = self.request(path=location)
        self.assertIn("HTTP defect", page)
        self.assertIn("Open settings", page)
        count = self.store.counts()["total"]
        self.request(path=location)
        self.assertEqual(self.store.counts()["total"], count)
        for old, new in (("Open", "In progress"), ("In progress", "Resolved"), ("Resolved", "Open")):
            code, _, _ = self.request("POST", f"/reports/{report_id}/status",
                                      dict(_csrf=self.server.csrf_token, status=new, expected_status=old))
            self.assertEqual(code, 303)
            self.assertEqual(self.store.get(report_id)["status"], new)

    def test_invalid_form_retains_input_and_has_linked_inline_errors_without_insert(self):
        before = self.store.counts()["total"]
        data = self.form_data(steps="Keep this useful detail")
        data["title"] = "  "
        data["severity"] = ""
        code, _, body = self.request("POST", "/reports", data)
        self.assertEqual(code, 422)
        self.assertIn("Keep this useful detail", body)
        self.assertIn('href="#title"', body)
        self.assertIn('id="title-error"', body)
        self.assertIn('aria-describedby="title-help title-error"', body)
        self.assertEqual(self.store.counts()["total"], before)

    def test_report_markup_is_escaped_and_security_headers_present(self):
        report = self.store.create(title='<script>alert("x")</script>', severity="high", actual='<img src=x onerror=alert(1)>')
        code, headers, body = self.request(path=f"/reports/{report['id']}")
        self.assertEqual(code, 200)
        self.assertNotIn('<script>alert(', body)
        self.assertNotIn('<img src=x', body)
        self.assertIn('&lt;script&gt;', body)
        self.assertIn("frame-ancestors 'none'", headers["Content-Security-Policy"])
        self.assertEqual(headers["X-Content-Type-Options"], "nosniff")
        self.assertEqual(headers["Cache-Control"], "no-store")

    def test_missing_wrong_and_non_ascii_csrf_rejected_without_write(self):
        before = self.store.counts()["total"]
        for token in ("", "wrong", "伪造"):
            data = self.form_data()
            data["_csrf"] = token
            with self.subTest(token=token):
                self.assertEqual(self.request("POST", "/reports", data)[0], 403)
        self.assertEqual(self.store.counts()["total"], before)

    def test_foreign_origin_and_untrusted_host_are_rejected(self):
        before = self.store.counts()["total"]
        self.assertEqual(self.request("POST", "/reports", self.form_data(), headers={"Origin": "https://evil.example"})[0], 403)
        self.assertEqual(self.request(headers={"Host": "evil.example"})[0], 400)
        self.assertEqual(self.store.counts()["total"], before)

    def test_form_body_limits_media_type_and_duplicate_fields(self):
        self.assertEqual(self.request("POST", "/reports", raw=b"{}", headers={"Content-Type": "application/json"})[0], 415)
        self.assertEqual(self.request("POST", "/reports", raw=b"x"*(MAX_BODY+1), headers={"Content-Type": "application/x-www-form-urlencoded"})[0], 413)
        self.assertEqual(self.request("POST", "/reports", raw=b"title=a&title=b", headers={"Content-Type": "application/x-www-form-urlencoded"})[0], 400)

    def test_rejected_post_bodies_deliver_feedback_without_aborting_connections(self):
        before = self.store.counts()["total"]
        for attempt in range(30):
            with self.subTest(attempt=attempt):
                self.assertEqual(self.request("POST", "/reports", raw=b"{}", headers={"Content-Type": "application/json"})[0], 415)
                self.assertEqual(self.request("POST", "/reports", self.form_data(), headers={"Origin": "https://foreign.example"})[0], 403)
        self.assertEqual(self.store.counts()["total"], before)

    def test_status_conflict_and_invalid_transition_do_not_overwrite(self):
        report = self.store.create(title="Concurrent", severity="low")
        path = f"/reports/{report['id']}/status"
        values = dict(_csrf=self.server.csrf_token, status="In progress", expected_status="Open")
        self.assertEqual(self.request("POST", path, values)[0], 303)
        self.assertEqual(self.request("POST", path, values)[0], 409)
        values.update(status="Open", expected_status="In progress")
        self.assertEqual(self.request("POST", path, values)[0], 422)
        self.assertEqual(self.store.get(report["id"])["status"], "In progress")

    def test_unknown_route_and_static_traversal_return_404(self):
        for path in ("/reports/00000000-0000-0000-0000-000000000000", "/static/../service.py", "/missing"):
            with self.subTest(path=path):
                self.assertEqual(self.request(path=path)[0], 404)

    def test_same_origin_post_succeeds(self):
        headers = {"Origin": f"http://127.0.0.1:{self.port}"}
        self.assertEqual(self.request("POST", "/reports", self.form_data(), headers=headers)[0], 303)

    def test_server_refuses_public_bind(self):
        with self.assertRaisesRegex(ValueError, "loopback"):
            ReportServer(("0.0.0.0", 0), self.store)

    def test_filters_have_clear_empty_state_and_reject_invalid_queries(self):
        code, _, body = self.request(path="/?severity=critical&status=Resolved")
        self.assertEqual(code, 200)
        self.assertIn("No reports match these filters", body)
        self.assertIn("Clear filters", body)
        for path in ("/?severity=urgent", "/?status=Closed", "/?severity=low&severity=high"):
            with self.subTest(path=path):
                self.assertEqual(self.request(path=path)[0], 400)

    def test_incomplete_report_is_saved_with_precise_server_guidance_without_js(self):
        code, headers, _ = self.request("POST", "/reports", self.form_data())
        self.assertEqual(code, 303)
        _, _, body = self.request(path=headers["Location"])
        self.assertIn('id="completeness-score">29%', body)
        self.assertIn('data-field="steps" >', body)
        self.assertIn("Information presence, not correctness", body)

    def test_paginated_http_navigation_preserves_filters_and_reaches_all_records(self):
        for index in range(30):
            self.store.create(title=f"HTTP page {index:02d}", severity="high")
        expected = self.store.list_reports(severity="high", status="Open")
        observed = []
        for number in range(1, (len(expected)+24)//25+1):
            code, _, body = self.request(path=f"/?severity=high&status=Open&page={number}")
            self.assertEqual(code, 200)
            ids = re.findall(r'data-report-id="([^"]+)"', body)
            self.assertLessEqual(len(ids), 25)
            observed.extend(ids)
            if number == 1:
                self.assertIn("severity=high&amp;status=Open&amp;page=2", body)
        self.assertEqual(observed, [report["id"] for report in expected])

    def test_invalid_page_values_are_errors_and_out_of_range_is_clamped(self):
        for value in ("0", "-1", "word", "1.5"):
            with self.subTest(value=value):
                self.assertEqual(self.request(path="/?page="+value)[0], 400)
        self.assertEqual(self.request(path="/?page=99999")[0], 200)

    def test_status_success_has_explicit_persisted_feedback(self):
        report = self.store.create(title="Status feedback", severity="low")
        code, headers, _ = self.request("POST", f"/reports/{report['id']}/status",
                                      dict(_csrf=self.server.csrf_token, status="In progress", expected_status="Open"))
        self.assertEqual(code, 303)
        _, _, body = self.request(path=headers["Location"])
        self.assertIn("Status updated to <strong>In progress</strong>", body)

    def test_null_input_returns_validation_feedback_and_keeps_server_healthy(self):
        before = self.store.counts()["total"]
        data = self.form_data(steps="Keep these steps")
        data["title"] = "\x00hidden title"
        code, _, body = self.request("POST", "/reports", data)
        self.assertEqual(code, 422)
        self.assertIn('id="title-error"', body)
        self.assertIn("Keep these steps", body)
        self.assertEqual(self.store.counts()["total"], before)
        self.assertEqual(self.request(path="/health")[0], 200)

    def test_detail_navigation_context_survives_status_redirect_and_conflict(self):
        report = self.store.create(title="Context detail", severity="high")
        context = "severity=high&status=Open&page=2"
        path = f"/reports/{report['id']}"
        code, _, body = self.request(path=path+"?"+context)
        self.assertEqual(code, 200)
        self.assertIn('href="/?severity=high&amp;status=Open&amp;page=2"', body)
        data = dict(_csrf=self.server.csrf_token, status="In progress", expected_status="Open")
        code, headers, _ = self.request("POST", path+"/status?"+context, data)
        self.assertEqual(code, 303)
        self.assertEqual(headers["Location"], path+"?updated=1&"+context)
        code, _, body = self.request("POST", path+"/status?"+context, data)
        self.assertEqual(code, 409)
        self.assertIn(f'href="{path}?severity=high&amp;status=Open&amp;page=2"', body)

    def test_invalid_navigation_context_is_rejected_before_status_mutation(self):
        report = self.store.create(title="Context validation", severity="low")
        path = f"/reports/{report['id']}"
        data = dict(_csrf=self.server.csrf_token, status="In progress", expected_status="Open")
        for query in ("severity=urgent", "status=Closed", "page=0", "page=2&page=3"):
            with self.subTest(query=query):
                self.assertEqual(self.request(path=path+"?"+query)[0], 400)
                self.assertEqual(self.request("POST", path+"/status?"+query, data)[0], 400)
                self.assertEqual(self.store.get(report["id"])["status"], "Open")
        code, headers, _ = self.request("POST", path+"/status?return_to=https%3A%2F%2Fevil.example", data)
        self.assertEqual(code, 303)
        self.assertEqual(headers["Location"], path+"?updated=1")
