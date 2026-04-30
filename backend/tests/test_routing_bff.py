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
    def test_routes_dashboard_query_to_dashboard_market_overview(self) -> None:
        response = routing_bff.route_frontend_request(
            {
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

    def test_routes_analytics_request_to_genie_surface(self) -> None:
        response = routing_bff.route_frontend_request(
            {
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

    def test_routes_narrative_request_to_copilot_surface(self) -> None:
        response = routing_bff.route_frontend_request(
            {
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


if __name__ == "__main__":
    unittest.main()
