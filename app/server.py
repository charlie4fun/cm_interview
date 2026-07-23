"""A small, dependency-free HTTP service for the deployment exercise."""

from __future__ import annotations

import json
import logging
import os
import signal
import threading
import time
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any


APP_NAME = os.getenv("APP_NAME", "interview-app")
APP_VERSION = os.getenv("APP_VERSION", "dev")
COMMIT_SHA = os.getenv("COMMIT_SHA", "unknown")


class JsonFormatter(logging.Formatter):
    """Render application logs as one JSON object per line."""

    converter = time.gmtime

    def format(self, record: logging.LogRecord) -> str:
        event: dict[str, Any] = {
            "timestamp": self.formatTime(record, "%Y-%m-%dT%H:%M:%SZ"),
            "level": record.levelname.lower(),
            "message": record.getMessage(),
        }
        for field in ("method", "path", "status", "duration_ms", "client"):
            if hasattr(record, field):
                event[field] = getattr(record, field)
        return json.dumps(event, separators=(",", ":"))


logger = logging.getLogger("interview_app")
handler = logging.StreamHandler()
handler.setFormatter(JsonFormatter())
logger.addHandler(handler)
logger.setLevel(os.getenv("LOG_LEVEL", "INFO").upper())
logger.propagate = False


class ApplicationState:
    def __init__(self) -> None:
        self.ready = True
        self.started_at = time.monotonic()
        self._requests: dict[tuple[str, int], int] = {}
        self._lock = threading.Lock()

    def record_request(self, path: str, status: int) -> None:
        with self._lock:
            key = (path, status)
            self._requests[key] = self._requests.get(key, 0) + 1

    def metrics(self) -> str:
        with self._lock:
            requests = sorted(self._requests.items())

        lines = [
            "# HELP app_info Application build information.",
            "# TYPE app_info gauge",
            f'app_info{{version="{_escape(APP_VERSION)}",commit="{_escape(COMMIT_SHA)}"}} 1',
            "# HELP app_uptime_seconds Time since the process started.",
            "# TYPE app_uptime_seconds gauge",
            f"app_uptime_seconds {time.monotonic() - self.started_at:.3f}",
            "# HELP http_requests_total Total HTTP requests handled.",
            "# TYPE http_requests_total counter",
        ]
        lines.extend(
            f'http_requests_total{{path="{_escape(path)}",status="{status}"}} {count}'
            for (path, status), count in requests
        )
        return "\n".join(lines) + "\n"


def _escape(value: str) -> str:
    return value.replace("\\", "\\\\").replace("\n", "\\n").replace('"', '\\"')


class AppServer(ThreadingHTTPServer):
    daemon_threads = True

    def __init__(self, address: tuple[str, int], state: ApplicationState):
        super().__init__(address, RequestHandler)
        self.state = state


class RequestHandler(BaseHTTPRequestHandler):
    server: AppServer

    def do_GET(self) -> None:  # noqa: N802 - required by BaseHTTPRequestHandler
        started = time.monotonic()
        path = self.path.split("?", 1)[0]

        if path == "/":
            status = self._json(
                HTTPStatus.OK,
                {"name": APP_NAME, "version": APP_VERSION, "commit": COMMIT_SHA},
            )
        elif path == "/healthz":
            status = self._json(HTTPStatus.OK, {"status": "ok"})
        elif path == "/readyz":
            if self.server.state.ready:
                status = self._json(HTTPStatus.OK, {"status": "ready"})
            else:
                status = self._json(
                    HTTPStatus.SERVICE_UNAVAILABLE, {"status": "not_ready"}
                )
        elif path == "/metrics":
            status = self._text(HTTPStatus.OK, self.server.state.metrics())
        else:
            status = self._json(HTTPStatus.NOT_FOUND, {"error": "not_found"})

        self.server.state.record_request(path, status)
        logger.info(
            "request completed",
            extra={
                "method": self.command,
                "path": path,
                "status": status,
                "duration_ms": round((time.monotonic() - started) * 1000, 3),
                "client": self.client_address[0],
            },
        )

    def _json(self, status: HTTPStatus, value: dict[str, str]) -> int:
        body = (json.dumps(value, separators=(",", ":")) + "\n").encode()
        return self._respond(status, body, "application/json")

    def _text(self, status: HTTPStatus, value: str) -> int:
        return self._respond(status, value.encode(), "text/plain; version=0.0.4")

    def _respond(self, status: HTTPStatus, body: bytes, content_type: str) -> int:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)
        return int(status)

    def log_message(self, format: str, *args: object) -> None:
        # Access logs are emitted as structured records in do_GET.
        return


def run() -> None:
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8080"))
    state = ApplicationState()
    server = AppServer((host, port), state)

    def stop(signum: int, _frame: object) -> None:
        logger.info("shutdown requested", extra={"status": signum})
        state.ready = False
        # shutdown() must be called from a different thread than serve_forever().
        threading.Thread(target=server.shutdown, daemon=True).start()

    signal.signal(signal.SIGTERM, stop)
    signal.signal(signal.SIGINT, stop)

    logger.info(f"server started on {host}:{port}")
    try:
        server.serve_forever()
    finally:
        server.server_close()
        logger.info("server stopped")


if __name__ == "__main__":
    run()
