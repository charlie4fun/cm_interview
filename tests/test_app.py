import json
import logging
import threading
import time
import unittest
from http.client import HTTPConnection

from app.server import AppServer, ApplicationState, JsonFormatter, logger


class JsonFormatterTest(unittest.TestCase):
    def test_timestamp_is_utc(self) -> None:
        formatter = JsonFormatter()
        record = logging.LogRecord("test", logging.INFO, "", 0, "message", (), None)
        record.created = 0

        event = json.loads(formatter.format(record))

        self.assertIs(formatter.converter, time.gmtime)
        self.assertEqual(event["timestamp"], "1970-01-01T00:00:00Z")


class ApplicationTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.logger_disabled = logger.disabled
        logger.disabled = True
        cls.state = ApplicationState()
        cls.server = AppServer(("127.0.0.1", 0), cls.state)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.port = cls.server.server_address[1]

    @classmethod
    def tearDownClass(cls) -> None:
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join()
        logger.disabled = cls.logger_disabled

    def get(self, path: str) -> tuple[int, str, bytes]:
        connection = HTTPConnection("127.0.0.1", self.port)
        connection.request("GET", path)
        response = connection.getresponse()
        result = (response.status, response.getheader("Content-Type"), response.read())
        connection.close()
        return result

    def test_root_exposes_build_information(self) -> None:
        status, content_type, body = self.get("/")
        self.assertEqual(status, 200)
        self.assertEqual(content_type, "application/json")
        self.assertEqual(set(json.loads(body)), {"name", "version", "commit"})

    def test_health_and_readiness(self) -> None:
        self.assertEqual(self.get("/healthz")[0], 200)
        self.assertEqual(self.get("/readyz")[0], 200)
        self.state.ready = False
        try:
            self.assertEqual(self.get("/readyz")[0], 503)
        finally:
            self.state.ready = True

    def test_metrics_are_prometheus_text(self) -> None:
        status, content_type, body = self.get("/metrics")
        self.assertEqual(status, 200)
        self.assertEqual(content_type, "text/plain; version=0.0.4")
        self.assertIn(b"app_info", body)
        self.assertIn(b"http_requests_total", body)

    def test_unknown_path_returns_404(self) -> None:
        status, _, body = self.get("/missing")
        self.assertEqual(status, 404)
        self.assertEqual(json.loads(body), {"error": "not_found"})


if __name__ == "__main__":
    unittest.main()
