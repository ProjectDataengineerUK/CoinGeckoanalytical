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
    def test_routes_structured_queries_to_genie_with_decision(self) -> None:
        decision = copilot_mvp.classify_route("Which asset has the highest market cap?")

        self.assertEqual(decision.surface, "genie")
        self.assertEqual(copilot_mvp.route_request("Which asset has the highest market cap?"), "genie")
        self.assertIn("market cap", decision.signals)
        self.assertEqual(decision.reason, "structured_analytics_request")

    def test_routes_narrative_queries_to_copilot_with_serialization(self) -> None:
        decision = copilot_mvp.classify_route("Explain what is happening in the market right now.")

        self.assertEqual(decision.surface, "copilot")
        self.assertEqual(decision.reason, "narrative_market_request")

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
        serialized_response = copilot_mvp.serialize_response_envelope(response)
        serialized_telemetry = copilot_mvp.serialize_telemetry_envelope(telemetry)

        self.assertEqual(response["surface_type"], "copilot_answer")
        self.assertIn("provenance", response["body"].lower())
        self.assertEqual(telemetry["route_selected"], "copilot")
        self.assertEqual(telemetry["tenant_id"], "tenant-1")
        self.assertEqual(telemetry["request_id"], "req-1")
        self.assertEqual(serialized_response["schema_version"], "copilot.response.v1")
        self.assertEqual(serialized_response["routing"]["surface"], "copilot")
        self.assertEqual(serialized_telemetry["schema_version"], "copilot.telemetry.v1")
        self.assertEqual(serialized_telemetry["response_surface_type"], "copilot_answer")

    def test_builds_genie_response_for_structured_request(self) -> None:
        request = copilot_mvp.CopilotRequest(
            request_id="req-2",
            tenant_id="tenant-1",
            user_id="user-1",
            conversation_id="conv-1",
            message_text="Compare the top assets by market cap over the last 7 days.",
            conversation_summary=None,
            retrieval_scope="gold_market_views",
            selected_assets=["btc", "eth"],
            time_range={"from": "2026-04-23", "to": "2026-04-30"},
            policy_context={"locale": "pt-BR"},
            locale="pt-BR",
        )
        response = copilot_mvp.build_copilot_response(request)
        telemetry = copilot_mvp.build_usage_event(request, response)

        self.assertEqual(response["surface_type"], "analytics_answer")
        self.assertEqual(response["routing"]["surface"], "genie")
        self.assertIn("estruturada", response["body"].lower())
        self.assertEqual(telemetry["route_selected"], "genie")

    def test_builds_databricks_usage_row_for_landing_table(self) -> None:
        request = copilot_mvp.CopilotRequest(
            request_id="req-3",
            tenant_id="tenant-1",
            user_id=None,
            conversation_id="conv-1",
            message_text="What is the trend in market cap?",
            conversation_summary=None,
            retrieval_scope="gold_market_views",
            selected_assets=["btc"],
            time_range=None,
            policy_context={"locale": "pt-BR"},
            locale="pt-BR",
        )
        response = copilot_mvp.build_copilot_response(request)
        row = copilot_mvp.build_databricks_usage_row(
            request,
            response,
            latency_ms=155,
            prompt_tokens=21,
            completion_tokens=34,
            total_tokens=55,
            cost_estimate=0.012,
        )

        self.assertEqual(
            set(row.keys()),
            {
                "event_time",
                "request_id",
                "tenant_id",
                "user_id",
                "route_selected",
                "model_or_engine",
                "prompt_tokens",
                "completion_tokens",
                "total_tokens",
                "latency_ms",
                "cost_estimate",
                "freshness_watermark",
                "response_status",
            },
        )
        self.assertEqual(row["request_id"], "req-3")
        self.assertEqual(row["route_selected"], "genie")
        self.assertEqual(row["prompt_tokens"], 21)
        self.assertEqual(row["response_status"], "success")


if __name__ == "__main__":
    unittest.main()
