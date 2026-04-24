from __future__ import annotations

import json
import socket
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Callable

from app.models.schemas import ClientInfo
from app.services.dispatch_ai import DispatchPlanner


def _get_free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return int(s.getsockname()[1])


class MockLLMServer:
    def __init__(self, response_factory: Callable[[], dict], with_health: bool = True) -> None:
        self.response_factory = response_factory
        self.with_health = with_health
        self.calls = 0
        self._server: ThreadingHTTPServer | None = None
        self._thread: threading.Thread | None = None
        self.base_url: str | None = None

    def start(self) -> None:
        port = _get_free_port()

        outer = self

        class Handler(BaseHTTPRequestHandler):
            def _send_json(self, status: int, payload: dict) -> None:
                body = json.dumps(payload).encode("utf-8")
                self.send_response(status)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)

            def do_GET(self) -> None:  # noqa: N802
                if self.path == "/v1/health" and outer.with_health:
                    self._send_json(200, {"ok": True})
                    return
                self._send_json(404, {"error": "not found"})

            def do_POST(self) -> None:  # noqa: N802
                if self.path != "/v1/chat/completions":
                    self._send_json(404, {"error": "not found"})
                    return
                outer.calls += 1
                _ = self.rfile.read(int(self.headers.get("Content-Length", "0")))
                self._send_json(200, outer.response_factory())

            def log_message(self, format: str, *args) -> None:  # noqa: A003
                return

        self._server = ThreadingHTTPServer(("127.0.0.1", port), Handler)
        self.base_url = f"http://127.0.0.1:{port}/v1"
        self._thread = threading.Thread(target=self._server.serve_forever, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        if self._server is not None:
            self._server.shutdown()
            self._server.server_close()
        if self._thread is not None:
            self._thread.join(timeout=2)


class LinkMechanismTestCase(unittest.TestCase):
    def _clients(self) -> list[ClientInfo]:
        return [
            ClientInfo(
                userId="patient-1",
                displayName="Patient",
                organization="community",
                healthCondition="risk",
                professionIdentity="",
                profileBio="",
                deviceType="ANDROID",
                online=True,
                lastSeenTs=1,
                isPatient=True,
            ),
            ClientInfo(
                userId="doctor-1",
                displayName="Doctor",
                organization="hospital",
                healthCondition="good",
                professionIdentity="doctor",
                profileBio="cpr aed",
                deviceType="ANDROID",
                online=True,
                lastSeenTs=2,
            ),
            ClientInfo(
                userId="runner-1",
                displayName="Runner",
                organization="campus",
                healthCondition="good",
                professionIdentity="student",
                profileBio="runs fast",
                deviceType="ANDROID",
                online=True,
                lastSeenTs=3,
            ),
            ClientInfo(
                userId="guide-1",
                displayName="Guide",
                organization="property",
                healthCondition="good",
                professionIdentity="security",
                profileBio="knows route",
                deviceType="ANDROID",
                online=True,
                lastSeenTs=4,
            ),
        ]

    def test_local_model_preferred_when_available(self) -> None:
        local = MockLLMServer(
            response_factory=lambda: {
                "choices": [
                    {
                        "message": {
                            "content": json.dumps(
                                {
                                    "PRIME": "doctor-1",
                                    "RUNNER": "runner-1",
                                    "GUIDE": "guide-1",
                                }
                            )
                        }
                    }
                ]
            }
        )
        api = MockLLMServer(
            response_factory=lambda: {
                "choices": [{"message": {"content": '{"PRIME":null,"RUNNER":null,"GUIDE":null}'}}]
            }
        )
        local.start()
        api.start()

        try:
            planner = DispatchPlanner(
                api_key="key",
                model="remote-model",
                base_url=api.base_url or "",
                timeout_sec=2,
                local_base_url=local.base_url,
                local_model="local-model",
                local_timeout_sec=2,
                prefer_local=True,
            )
            assignments, source = planner.assign_roles("patient-1", self._clients())

            self.assertEqual(source, "local_model")
            self.assertEqual(assignments["PRIME"], "doctor-1")
            self.assertEqual(local.calls, 1)
            self.assertEqual(api.calls, 0)
        finally:
            local.stop()
            api.stop()

    def test_fallback_to_api_when_local_unavailable(self) -> None:
        api = MockLLMServer(
            response_factory=lambda: {
                "choices": [
                    {
                        "message": {
                            "content": json.dumps(
                                {
                                    "PRIME": "doctor-1",
                                    "RUNNER": "runner-1",
                                    "GUIDE": "guide-1",
                                }
                            )
                        }
                    }
                ]
            }
        )
        api.start()

        dead_port = _get_free_port()
        dead_local_url = f"http://127.0.0.1:{dead_port}/v1"

        try:
            planner = DispatchPlanner(
                api_key="key",
                model="remote-model",
                base_url=api.base_url or "",
                timeout_sec=2,
                local_base_url=dead_local_url,
                local_model="local-model",
                local_timeout_sec=1,
                prefer_local=True,
            )
            assignments, source = planner.assign_roles("patient-1", self._clients())

            self.assertEqual(source, "siliconflow")
            self.assertEqual(assignments["GUIDE"], "guide-1")
            self.assertEqual(api.calls, 1)
        finally:
            api.stop()

    def test_fallback_to_rules_when_no_llm_available(self) -> None:
        planner = DispatchPlanner(
            api_key=None,
            model="remote-model",
            base_url="http://127.0.0.1:1/v1",
            timeout_sec=1,
            local_base_url="http://127.0.0.1:2/v1",
            local_model="local-model",
            local_timeout_sec=1,
            prefer_local=True,
        )
        assignments, source = planner.assign_roles("patient-1", self._clients())

        self.assertEqual(source, "fallback")
        self.assertTrue(any(value is not None for value in assignments.values()))

    def test_prefer_remote_when_switch_disabled(self) -> None:
        local = MockLLMServer(
            response_factory=lambda: {
                "choices": [
                    {
                        "message": {
                            "content": json.dumps(
                                {
                                    "PRIME": "doctor-1",
                                    "RUNNER": "runner-1",
                                    "GUIDE": "guide-1",
                                }
                            )
                        }
                    }
                ]
            }
        )
        api = MockLLMServer(
            response_factory=lambda: {
                "choices": [
                    {
                        "message": {
                            "content": json.dumps(
                                {
                                    "PRIME": "doctor-1",
                                    "RUNNER": "runner-1",
                                    "GUIDE": "guide-1",
                                }
                            )
                        }
                    }
                ]
            }
        )
        local.start()
        api.start()

        try:
            planner = DispatchPlanner(
                api_key="key",
                model="remote-model",
                base_url=api.base_url or "",
                timeout_sec=2,
                local_base_url=local.base_url,
                local_model="local-model",
                local_timeout_sec=2,
                prefer_local=False,
            )
            _, source = planner.assign_roles("patient-1", self._clients())

            self.assertEqual(source, "siliconflow")
            self.assertEqual(api.calls, 1)
            self.assertEqual(local.calls, 0)
        finally:
            local.stop()
            api.stop()


if __name__ == "__main__":
    unittest.main()
