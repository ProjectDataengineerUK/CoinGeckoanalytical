from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
import unittest


MODULE_PATH = Path(__file__).resolve().parent / "ops_usage_ingestion_job.py"
SPEC = importlib.util.spec_from_file_location("ops_usage_ingestion_job", MODULE_PATH)
ops_usage_ingestion_job = importlib.util.module_from_spec(SPEC)
assert SPEC is not None and SPEC.loader is not None
sys.modules[SPEC.name] = ops_usage_ingestion_job
SPEC.loader.exec_module(ops_usage_ingestion_job)


class OpsUsageIngestionJobTests(unittest.TestCase):
    def test_parse_payload_accepts_single_object(self) -> None:
        rows = ops_usage_ingestion_job.parse_payload(
            '{"event_time":"2026-04-30T00:00:00Z","request_id":"req-1","tenant_id":"tenant-1","route_selected":"copilot","model_or_engine":"engine","latency_ms":100,"response_status":"success"}'
        )

        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["request_id"], "req-1")

    def test_validate_usage_row_coerces_numeric_fields(self) -> None:
        row = ops_usage_ingestion_job.validate_usage_row(
            {
                "event_time": "2026-04-30T00:00:00Z",
                "request_id": "req-2",
                "tenant_id": "tenant-1",
                "route_selected": "dashboard_api",
                "model_or_engine": "dashboard-shell",
                "prompt_tokens": "3",
                "completion_tokens": "5",
                "total_tokens": "8",
                "latency_ms": "200",
                "cost_estimate": "0.01",
                "freshness_watermark": "2026-04-30T00:00:00Z",
                "response_status": "success",
            }
        )

        self.assertEqual(row["latency_ms"], 200)
        self.assertEqual(row["prompt_tokens"], 3)
        self.assertEqual(row["total_tokens"], 8)
        self.assertEqual(row["cost_estimate"], 0.01)

    def test_validate_usage_row_rejects_invalid_route(self) -> None:
        with self.assertRaises(ValueError):
            ops_usage_ingestion_job.validate_usage_row(
                {
                    "event_time": "2026-04-30T00:00:00Z",
                    "request_id": "req-3",
                    "tenant_id": "tenant-1",
                    "route_selected": "unsupported",
                    "model_or_engine": "engine",
                    "latency_ms": 100,
                    "response_status": "success",
                }
            )


if __name__ == "__main__":
    unittest.main()
