from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

APP_ROOT = (
    Path(__file__).resolve().parents[1]
    / "apps"
    / "cga-admin"
)
if str(APP_ROOT) not in sys.path:
    sys.path.insert(0, str(APP_ROOT))

MODULE_PATH = (
    Path(__file__).resolve().parents[1]
    / "apps"
    / "cga-admin"
    / "pages"
    / "architecture_ops.py"
)
SPEC = importlib.util.spec_from_file_location("pages.architecture_ops", MODULE_PATH)
architecture_ops = importlib.util.module_from_spec(SPEC)
assert SPEC is not None and SPEC.loader is not None
sys.modules[SPEC.name] = architecture_ops
SPEC.loader.exec_module(architecture_ops)


class ArchitectureOpsTests(unittest.TestCase):
    def test_derives_critical_for_route_with_errors(self) -> None:
        resources = architecture_ops._derive_resource_health(
            {"stale_freshness_count": 0},
            [
                {"route_selected": "genie", "readiness_status": "hold", "avg_latency_ms": 200, "error_count": 2, "total_cost_estimate": 0.01},
                {"route_selected": "copilot", "readiness_status": "ready", "avg_latency_ms": 500, "error_count": 0, "total_cost_estimate": 0.02},
                {"route_selected": "dashboard_api", "readiness_status": "ready", "avg_latency_ms": 100, "error_count": 0, "total_cost_estimate": 0.001},
                {"route_selected": "internal_app", "readiness_status": "ready", "avg_latency_ms": 100, "error_count": 0, "total_cost_estimate": 0.001},
            ],
            [{"job_name": "market_source_ingestion_job", "bundle_readiness_status": "ready", "failed_count": 0, "running_count": 0}],
            [{"sentinela_alert_status": "ready", "runtime_alerts": 0, "bundle_alerts": 0}],
            [],
        )

        genie_row = next(row for row in resources if row["resource"] == "Genie")
        self.assertEqual(genie_row["status"], "critical")

    def test_builds_optimization_items_for_high_cost_and_failed_jobs(self) -> None:
        items = architecture_ops._derive_optimization_opportunities(
            [
                {
                    "route_selected": "copilot",
                    "total_cost_estimate": 0.045,
                    "policy_max_cost_estimate": 0.05,
                    "total_tokens": 3500,
                    "stale_freshness_count": 0,
                },
                {
                    "route_selected": "genie",
                    "total_cost_estimate": 0.001,
                    "policy_max_cost_estimate": 0.02,
                    "stale_freshness_count": 1,
                },
            ],
            [{"job_name": "defillama_ingestion_job", "failed_count": 1}],
            [{"route_selected": "copilot", "total_cost_estimate": 0.032}],
            [{"runtime_alerts": 2}],
        )

        titles = {item["title"] for item in items}
        self.assertIn("Ajustar tier routing do Copilot", titles)
        self.assertIn("Reduzir reruns de jobs com falha", titles)


if __name__ == "__main__":
    unittest.main()
