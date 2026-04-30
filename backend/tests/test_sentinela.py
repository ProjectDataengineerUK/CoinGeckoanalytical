from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
import unittest


MODULE_PATH = Path(__file__).resolve().parent.parent / "sentinela.py"
SPEC = importlib.util.spec_from_file_location("sentinela", MODULE_PATH)
sentinela = importlib.util.module_from_spec(SPEC)
assert SPEC is not None and SPEC.loader is not None
sys.modules[SPEC.name] = sentinela
SPEC.loader.exec_module(sentinela)


class SentinelaTests(unittest.TestCase):
    def test_analyze_usage_events_reports_clean_summary(self) -> None:
        result = sentinela.analyze_usage_events(
            [
                {
                    "event_time": "2026-04-30T00:00:00Z",
                    "request_id": "req-1",
                    "tenant_id": "tenant-1",
                    "user_id": "user-1",
                    "route_selected": "genie",
                    "model_or_engine": "genie",
                    "prompt_tokens": 10,
                    "completion_tokens": 20,
                    "total_tokens": 30,
                    "latency_ms": 140,
                    "cost_estimate": 0.01,
                    "freshness_watermark": "2026-04-30T00:00:00Z",
                    "response_status": "success",
                }
            ]
        )

        self.assertEqual(result["summary"]["errors"], 0)
        self.assertEqual(result["summary"]["alerts"], 0)

    def test_analyze_usage_events_flags_anomalies(self) -> None:
        result = sentinela.analyze_usage_events(
            [
                {
                    "event_time": "2026-04-30T00:00:00Z",
                    "request_id": "req-2",
                    "tenant_id": "tenant-1",
                    "user_id": "user-1",
                    "route_selected": "copilot",
                    "model_or_engine": "mosaic-ai-agent-framework",
                    "prompt_tokens": 3000,
                    "completion_tokens": 1500,
                    "total_tokens": 4500,
                    "latency_ms": 1200,
                    "cost_estimate": 0.08,
                    "freshness_watermark": None,
                    "response_status": "error",
                }
            ]
        )

        kinds = {alert["kind"] for alert in result["alerts"]}
        self.assertIn("error_spike", kinds)
        self.assertIn("latency_breach", kinds)
        self.assertIn("cost_anomaly", kinds)
        self.assertIn("freshness_gap", kinds)
        self.assertIn("token_spike", kinds)
        self.assertEqual(result["summary"]["errors"], 1)

    def test_analyze_usage_events_aggregates_routing_mix(self) -> None:
        result = sentinela.analyze_usage_events(
            [
                {
                    "event_time": "2026-04-30T00:00:00Z",
                    "request_id": "req-3",
                    "tenant_id": "tenant-1",
                    "user_id": "user-1",
                    "route_selected": "genie",
                    "model_or_engine": "genie",
                    "prompt_tokens": 18,
                    "completion_tokens": 22,
                    "total_tokens": 40,
                    "latency_ms": 180,
                    "cost_estimate": 0.01,
                    "freshness_watermark": "2026-04-30T00:00:00Z",
                    "response_status": "success",
                },
                {
                    "event_time": "2026-04-30T00:00:00Z",
                    "request_id": "req-4",
                    "tenant_id": "tenant-1",
                    "user_id": "user-1",
                    "route_selected": "copilot",
                    "model_or_engine": "mosaic-ai-agent-framework",
                    "prompt_tokens": 60,
                    "completion_tokens": 80,
                    "total_tokens": 140,
                    "latency_ms": 220,
                    "cost_estimate": 0.02,
                    "freshness_watermark": "pending",
                    "response_status": "partial",
                },
            ]
        )

        self.assertEqual(result["summary"]["events"], 2)
        self.assertEqual(result["summary"]["partials"], 1)
        self.assertEqual(result["summary"]["errors"], 0)
        self.assertEqual(result["summary"]["alerts"], 1)


if __name__ == "__main__":
    unittest.main()
