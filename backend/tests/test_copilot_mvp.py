from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
import unittest


MODULE_PATH = Path(__file__).resolve().parent.parent / "copilot_mvp.py"
SPEC = importlib.util.spec_from_file_location("copilot_mvp", MODULE_PATH)
copilot_mvp = importlib.util.module_from_spec(SPEC)
assert SPEC is not None and SPEC.loader is not None
sys.modules[SPEC.name] = copilot_mvp
SPEC.loader.exec_module(copilot_mvp)


class CopilotMvpTests(unittest.TestCase):
    def test_routes_structured_queries_to_genie(self) -> None:
        self.assertEqual(copilot_mvp.route_request("Which asset has the highest market cap?"), "genie")

    def test_routes_narrative_queries_to_copilot(self) -> None:
        self.assertEqual(copilot_mvp.route_request("Explain what is happening in the market right now."), "copilot")

    def test_builds_copilot_response_with_telemetry_fields(self) -> None:
        request = copilot_mvp.CopilotRequest(
            request_id="req-1",
            tenant_id="tenant-1",
            user_id="user-1",
            conversation_id="conv-1",
            message_text="Explain what is happening in the market right now.",
            conversation_summary=None,
            retrieval_scope="gold_market_views",
            selected_assets=["btc", "eth"],
            time_range={"from": "2026-04-01", "to": "2026-04-30"},
            policy_context={"locale": "pt-BR"},
            locale="pt-BR",
        )
        response = copilot_mvp.build_copilot_response(request)
        telemetry = copilot_mvp.build_usage_event(request, response)

        self.assertEqual(response["surface_type"], "copilot_answer")
        self.assertIn("provenance", response["body"].lower())
        self.assertEqual(telemetry["route_selected"], "copilot")
        self.assertEqual(telemetry["tenant_id"], "tenant-1")
        self.assertEqual(telemetry["request_id"], "req-1")


if __name__ == "__main__":
    unittest.main()
