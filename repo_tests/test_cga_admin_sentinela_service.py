from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


MODULE_PATH = (
    Path(__file__).resolve().parents[1]
    / "apps"
    / "cga-admin"
    / "services"
    / "sentinela_service.py"
)
SPEC = importlib.util.spec_from_file_location("cga_admin_sentinela_service", MODULE_PATH)
sentinela_service = importlib.util.module_from_spec(SPEC)
assert SPEC is not None and SPEC.loader is not None
sys.modules[SPEC.name] = sentinela_service
SPEC.loader.exec_module(sentinela_service)


class _FakeSentinela:
    @staticmethod
    def evaluate_release_readiness(events, policy=None, bundle_runs=None):
        return {
            "ready": True,
            "checks": [
                {"name": "telemetry_present", "passed": True},
                {"name": "bundle_runs_failure_free", "passed": True},
                {"name": "alert_free", "passed": False},
            ],
            "blockers": [],
            "bundle_runs_seen": bundle_runs,
            "policy_seen": policy,
        }


class _StatusSentinela:
    @staticmethod
    def evaluate_release_readiness(events, policy=None, bundle_runs=None):
        return {
            "ready": False,
            "checks": [
                {"name": "telemetry_present", "status": "fail"},
                {"name": "bundle_runs_failure_free", "status": "pass"},
                {"name": "alert_free", "status": "pass"},
            ],
            "blockers": [{"kind": "missing_telemetry"}],
            "bundle_runs_seen": bundle_runs,
            "policy_seen": policy,
        }


class SentinelaServiceTests(unittest.TestCase):
    def test_evaluate_readiness_passes_bundle_runs_by_keyword_and_computes_score(self) -> None:
        original = sentinela_service._load
        try:
            sentinela_service._load = lambda: _FakeSentinela()
            result = sentinela_service.evaluate_readiness(
                usage_events=[{"route_selected": "copilot"}],
                bundle_events=[{"job_name": "market_source_ingestion_job"}],
            )
        finally:
            sentinela_service._load = original

        self.assertEqual(result["bundle_runs_seen"], [{"job_name": "market_source_ingestion_job"}])
        self.assertIsNone(result["policy_seen"])
        self.assertEqual(result["score"], 67)

    def test_evaluate_readiness_uses_status_checks_and_downgrades_missing_telemetry(self) -> None:
        original = sentinela_service._load
        try:
            sentinela_service._load = lambda: _StatusSentinela()
            result = sentinela_service.evaluate_readiness(
                usage_events=[],
                bundle_events=[{"job_name": "market_source_ingestion_job", "status": "SUCCESS"}],
            )
        finally:
            sentinela_service._load = original

        self.assertTrue(result["ready"])
        self.assertEqual(result["score"], 67)
        self.assertEqual(result["blockers"], [])
        self.assertEqual(result["operational_state"], "monitoring_limited")
        self.assertEqual(result["warnings"], [{"kind": "missing_telemetry"}])


if __name__ == "__main__":
    unittest.main()
