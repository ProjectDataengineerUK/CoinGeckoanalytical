from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
import tempfile
import unittest


COPILOT_MODULE_PATH = Path(__file__).resolve().parent.parent / "copilot_mvp.py"
COPILOT_SPEC = importlib.util.spec_from_file_location("copilot_mvp", COPILOT_MODULE_PATH)
copilot_mvp = importlib.util.module_from_spec(COPILOT_SPEC)
assert COPILOT_SPEC is not None and COPILOT_SPEC.loader is not None
sys.modules[COPILOT_SPEC.name] = copilot_mvp
COPILOT_SPEC.loader.exec_module(copilot_mvp)

HANDOFF_MODULE_PATH = Path(__file__).resolve().parent.parent / "telemetry_handoff.py"
HANDOFF_SPEC = importlib.util.spec_from_file_location("telemetry_handoff", HANDOFF_MODULE_PATH)
telemetry_handoff = importlib.util.module_from_spec(HANDOFF_SPEC)
assert HANDOFF_SPEC is not None and HANDOFF_SPEC.loader is not None
sys.modules[HANDOFF_SPEC.name] = telemetry_handoff
HANDOFF_SPEC.loader.exec_module(telemetry_handoff)


class TelemetryHandoffTests(unittest.TestCase):
    def test_write_usage_handoff_file_creates_json_array(self) -> None:
        request = copilot_mvp.CopilotRequest(
            request_id="req-1",
            tenant_id="tenant-1",
            user_id="user-1",
            conversation_id="conv-1",
            message_text="Explain what is happening in the market right now.",
            conversation_summary=None,
            retrieval_scope="gold_market_views",
            selected_assets=["btc"],
            time_range=None,
            policy_context={"locale": "pt-BR"},
            locale="pt-BR",
        )
        response = copilot_mvp.build_copilot_response(request)

        with tempfile.TemporaryDirectory() as temp_dir:
            target_path = Path(temp_dir) / "handoff.json"
            written_path = telemetry_handoff.write_usage_handoff_file(
                target_path,
                request,
                response,
                latency_ms=180,
                prompt_tokens=15,
                completion_tokens=20,
                total_tokens=35,
                cost_estimate=0.01,
            )

            payload = written_path.read_text(encoding="utf-8")

        self.assertEqual(written_path, target_path)
        self.assertIn('"request_id": "req-1"', payload)
        self.assertIn('"route_selected": "copilot"', payload)
        self.assertIn('"total_tokens": 35', payload)

    def test_build_usage_handoff_row_matches_databricks_shape(self) -> None:
        request = copilot_mvp.CopilotRequest(
            request_id="req-2",
            tenant_id="tenant-1",
            user_id=None,
            conversation_id="conv-1",
            message_text="What is the trend in market cap?",
            conversation_summary=None,
            retrieval_scope="gold_market_views",
            selected_assets=["eth"],
            time_range=None,
            policy_context={"locale": "pt-BR"},
            locale="pt-BR",
        )
        response = copilot_mvp.build_copilot_response(request)
        row = telemetry_handoff.build_usage_handoff_row(
            request,
            response,
            prompt_tokens=11,
            completion_tokens=22,
            total_tokens=33,
            cost_estimate=0.009,
        )

        self.assertEqual(row["request_id"], "req-2")
        self.assertEqual(row["route_selected"], "genie")
        self.assertEqual(row["prompt_tokens"], 11)
        self.assertEqual(row["cost_estimate"], 0.009)


if __name__ == "__main__":
    unittest.main()
