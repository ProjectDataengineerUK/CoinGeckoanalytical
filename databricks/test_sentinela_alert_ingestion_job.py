from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
import unittest


MODULE_PATH = Path(__file__).resolve().parent / "sentinela_alert_ingestion_job.py"
SPEC = importlib.util.spec_from_file_location("sentinela_alert_ingestion_job", MODULE_PATH)
sentinela_alert_ingestion_job = importlib.util.module_from_spec(SPEC)
assert SPEC is not None and SPEC.loader is not None
sys.modules[SPEC.name] = sentinela_alert_ingestion_job
SPEC.loader.exec_module(sentinela_alert_ingestion_job)


class SentinelaAlertIngestionJobTests(unittest.TestCase):
    def test_parse_payload_accepts_single_object(self) -> None:
        rows = sentinela_alert_ingestion_job.parse_payload(
            '{"kind":"bundle_failure","message":"failed"}'
        )

        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["kind"], "bundle_failure")

    def test_validate_alert_row_accepts_known_kind(self) -> None:
        row = sentinela_alert_ingestion_job.validate_alert_row(
            {
                "kind": "latency_breach",
                "message": "Latency exceeded the operational threshold.",
                "job_name": "ops_readiness_refresh_job",
                "escalation": "investigate_performance",
            }
        )

        self.assertEqual(row["kind"], "latency_breach")
        self.assertEqual(row["source"], "sentinela")

    def test_validate_alert_row_rejects_unknown_kind(self) -> None:
        with self.assertRaises(ValueError):
            sentinela_alert_ingestion_job.validate_alert_row(
                {
                    "kind": "unknown",
                    "message": "bad",
                }
            )


if __name__ == "__main__":
    unittest.main()
