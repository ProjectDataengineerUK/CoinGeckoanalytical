from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
import unittest


MODULE_PATH = Path(__file__).resolve().parent.parent / "jobs/bundle_run_ingestion_job.py"
SPEC = importlib.util.spec_from_file_location("bundle_run_ingestion_job", MODULE_PATH)
bundle_run_ingestion_job = importlib.util.module_from_spec(SPEC)
assert SPEC is not None and SPEC.loader is not None
sys.modules[SPEC.name] = bundle_run_ingestion_job
SPEC.loader.exec_module(bundle_run_ingestion_job)


class BundleRunIngestionJobTests(unittest.TestCase):
    def test_parse_payload_accepts_single_object(self) -> None:
        rows = bundle_run_ingestion_job.parse_payload(
            '{"job_name":"ops_usage_ingestion_job","status":"SUCCESS"}'
        )

        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["job_name"], "ops_usage_ingestion_job")

    def test_validate_bundle_run_row_coerces_duration(self) -> None:
        row = bundle_run_ingestion_job.validate_bundle_run_row(
            {
                "job_name": "ops_usage_ingestion_job",
                "status": "FAILED",
                "run_id": "run-1",
                "result_state": "FAILED",
                "update_time": "2026-04-30T00:05:00Z",
                "duration_ms": "500",
            }
        )

        self.assertEqual(row["duration_ms"], 500)
        self.assertEqual(row["status"], "FAILED")

    def test_validate_bundle_run_row_rejects_invalid_status(self) -> None:
        with self.assertRaises(ValueError):
            bundle_run_ingestion_job.validate_bundle_run_row(
                {
                    "job_name": "ops_usage_ingestion_job",
                    "status": "BROKEN",
                }
            )


if __name__ == "__main__":
    unittest.main()
