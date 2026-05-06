from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
import unittest


MODULE_PATH = Path(__file__).resolve().parent.parent / "routing_bff.py"
SPEC = importlib.util.spec_from_file_location("routing_bff", MODULE_PATH)
routing_bff = importlib.util.module_from_spec(SPEC)
assert SPEC is not None and SPEC.loader is not None
sys.modules[SPEC.name] = routing_bff
SPEC.loader.exec_module(routing_bff)


class RoutingBffTests(unittest.TestCase):
    def setUp(self) -> None:
        routing_bff.reset_runtime_controls()

    def test_routes_dashboard_query_to_dashboard_market_overview(self) -> None:
        response = routing_bff.route_frontend_request(
            {
                "api_version": "v1",
                "tenant_id": "tenant-1",
                "user_id": "user-1",
                "session_id": "sess-1",
                "request_id": "req-20",
                "locale": "pt-BR",
                "channel": "web_dashboard",
                "request_type_hint": "dashboard_query",
                "message_text": "Visao geral do mercado",
                "selected_assets": ["btc", "eth"],
            }
        )

        self.assertEqual(response["surface_type"], "dashboard_payload")
        self.assertEqual(response["routing"]["route_id"], "dashboard.market-overview")
        self.assertEqual(response["routing"]["channel"], "web_dashboard")
        self.assertEqual(response["api_version"], "v1")

    def test_routes_analytics_request_to_genie_surface(self) -> None:
        response = routing_bff.route_frontend_request(
            {
                "api_version": "v1",
                "tenant_id": "tenant-1",
                "user_id": "user-1",
                "session_id": "sess-2",
                "request_id": "req-21",
                "locale": "pt-BR",
                "channel": "web_chat",
                "request_type_hint": "analytics_nlq",
                "message_text": "Compare the top assets by market cap.",
            }
        )

        self.assertEqual(response["surface_type"], "analytics_answer")
        self.assertEqual(response["routing"]["surface"], "genie")
        self.assertEqual(response["routing"]["request_type_hint"], "analytics_nlq")
        self.assertEqual(response["routing"]["api_version"], "v1")

    def test_routes_narrative_request_to_copilot_surface(self) -> None:
        response = routing_bff.route_frontend_request(
            {
                "api_version": "v1",
                "tenant_id": "tenant-1",
                "user_id": "user-1",
                "session_id": "sess-3",
                "request_id": "req-22",
                "locale": "pt-BR",
                "channel": "web_chat",
                "request_type_hint": "auto",
                "message_text": "Explain what is happening in the market right now.",
            }
        )

        self.assertEqual(response["surface_type"], "copilot_answer")
        self.assertEqual(response["routing"]["surface"], "copilot")
        self.assertEqual(response["routing"]["api_version"], "v1")

    def test_validates_required_fields(self) -> None:
        with self.assertRaisesRegex(ValueError, "Missing required request fields"):
            routing_bff.route_frontend_request(
                {
                    "tenant_id": "tenant-1",
                    "session_id": "sess-4",
                    "request_id": "req-23",
                    "locale": "pt-BR",
                    "channel": "web_chat",
                    "request_type_hint": "auto",
                }
            )

    def test_rejects_unsupported_api_version(self) -> None:
        with self.assertRaisesRegex(ValueError, "Unsupported api_version"):
            routing_bff.route_frontend_request(
                {
                    "api_version": "v2",
                    "tenant_id": "tenant-1",
                    "user_id": "user-1",
                    "session_id": "sess-4",
                    "request_id": "req-24",
                    "locale": "pt-BR",
                    "channel": "web_chat",
                    "request_type_hint": "copilot",
                    "message_text": "Explain the market.",
                }
            )

    def test_rejects_invalid_tenant_identifier(self) -> None:
        with self.assertRaisesRegex(ValueError, "Invalid tenant_id"):
            routing_bff.route_frontend_request(
                {
                    "api_version": "v1",
                    "tenant_id": "../tenant",
                    "user_id": "user-1",
                    "session_id": "sess-4",
                    "request_id": "req-25",
                    "locale": "pt-BR",
                    "channel": "web_chat",
                    "request_type_hint": "copilot",
                    "message_text": "Explain the market.",
                }
            )

    def test_rate_limits_repeated_ai_requests(self) -> None:
        original_limiter = routing_bff._AI_RATE_LIMITER
        routing_bff._AI_RATE_LIMITER = routing_bff._SlidingWindowRateLimiter(limit=2, window_seconds=60)
        try:
            payload = {
                "api_version": "v1",
                "tenant_id": "tenant-1",
                "user_id": "user-1",
                "session_id": "sess-5",
                "request_id": "req-26",
                "locale": "pt-BR",
                "channel": "web_chat",
                "request_type_hint": "copilot",
                "message_text": "Explain the market.",
            }
            first = routing_bff.route_frontend_request(payload)
            second_payload = dict(payload)
            second_payload["request_id"] = "req-27"
            second = routing_bff.route_frontend_request(second_payload)
            third_payload = dict(payload)
            third_payload["request_id"] = "req-28"
            third = routing_bff.route_frontend_request(third_payload)
        finally:
            routing_bff._AI_RATE_LIMITER = original_limiter

        self.assertEqual(first["surface_type"], "copilot_answer")
        self.assertEqual(second["surface_type"], "copilot_answer")
        self.assertEqual(third["surface_type"], "policy_error")
        self.assertIn("rate_limited", third["warnings"])


if __name__ == "__main__":
    unittest.main()
