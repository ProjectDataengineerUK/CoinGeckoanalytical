from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
import unittest


MODULE_PATH = Path(__file__).resolve().parent.parent / "jobs/sentinela_evaluation_job.py"
SPEC = importlib.util.spec_from_file_location("sentinela_evaluation_job", MODULE_PATH)
_mod = importlib.util.module_from_spec(SPEC)  # type: ignore[arg-type]
assert SPEC is not None and SPEC.loader is not None
sys.modules[SPEC.name] = _mod
SPEC.loader.exec_module(_mod)  # type: ignore[union-attr]


class SentinelaEvaluationJobTests(unittest.TestCase):
    def _usage_row(self, status: str = "success", latency_ms: int = 200, cost: float = 0.001) -> dict:
        return {"response_status": status, "latency_ms": latency_ms, "cost_estimate": cost}

    def test_evaluate_usage_empty(self) -> None:
        self.assertEqual(_mod.evaluate_usage_events([]), [])

    def test_evaluate_usage_no_alerts_when_healthy(self) -> None:
        rows = [self._usage_row() for _ in range(10)]
        alerts = _mod.evaluate_usage_events(rows)
        self.assertEqual(alerts, [])

    def test_evaluate_usage_error_spike(self) -> None:
        rows = [self._usage_row(status="error")] * 5 + [self._usage_row()] * 5
        alerts = _mod.evaluate_usage_events(rows, threshold_error_rate_pct=10.0)
        kinds = [a["kind"] for a in alerts]
        self.assertIn("error_spike", kinds)

    def test_evaluate_usage_latency_breach(self) -> None:
        rows = [self._usage_row(latency_ms=9000) for _ in range(10)]
        alerts = _mod.evaluate_usage_events(rows, threshold_p95_latency_ms=5000)
        kinds = [a["kind"] for a in alerts]
        self.assertIn("latency_breach", kinds)

    def test_evaluate_usage_cost_anomaly(self) -> None:
        rows = [self._usage_row(cost=0.5) for _ in range(4)]
        alerts = _mod.evaluate_usage_events(rows, threshold_hourly_cost_usd=1.0)
        kinds = [a["kind"] for a in alerts]
        self.assertIn("cost_anomaly", kinds)

    def test_evaluate_bundle_runs_empty(self) -> None:
        self.assertEqual(_mod.evaluate_bundle_runs([]), [])

    def test_evaluate_bundle_runs_failed(self) -> None:
        rows = [{"job_name": "market_source_ingestion_job", "status": "FAILED", "run_id": "42"}]
        alerts = _mod.evaluate_bundle_runs(rows)
        self.assertEqual(len(alerts), 1)
        self.assertEqual(alerts[0]["kind"], "bundle_failure")
        self.assertEqual(alerts[0]["job_name"], "market_source_ingestion_job")

    def test_evaluate_bundle_runs_cancelled(self) -> None:
        rows = [{"job_name": "silver_market_pipeline_job", "status": "CANCELLED", "run_id": "7"}]
        alerts = _mod.evaluate_bundle_runs(rows)
        self.assertEqual(alerts[0]["kind"], "bundle_cancelled")

    def test_evaluate_bundle_runs_success_no_alert(self) -> None:
        rows = [{"job_name": "some_job", "status": "SUCCESS", "run_id": "1"}]
        alerts = _mod.evaluate_bundle_runs(rows)
        self.assertEqual(alerts, [])

    def test_alert_has_required_fields(self) -> None:
        rows = [self._usage_row(status="error") for _ in range(10)]
        alerts = _mod.evaluate_usage_events(rows, threshold_error_rate_pct=5.0)
        for alert in alerts:
            self.assertIn("kind", alert)
            self.assertIn("message", alert)
            self.assertIn("source", alert)
            self.assertIn("created_at", alert)

    def test_evaluation_result_dataclass(self) -> None:
        result = _mod.EvaluationResult(
            alerts_written=3,
            usage_rows_read=100,
            bundle_rows_read=5,
            target_table="cgadev.ops_observability.ops_sentinela_alerts",
        )
        self.assertEqual(result.alerts_written, 3)
        self.assertEqual(result.usage_rows_read, 100)


if __name__ == "__main__":
    unittest.main()
