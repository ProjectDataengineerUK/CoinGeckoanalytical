from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
import tempfile
import unittest


MODULE_PATH = Path(__file__).resolve().parent.parent / "bundle_run_handoff.py"
SPEC = importlib.util.spec_from_file_location("bundle_run_handoff", MODULE_PATH)
bundle_run_handoff = importlib.util.module_from_spec(SPEC)
assert SPEC is not None and SPEC.loader is not None
sys.modules[SPEC.name] = bundle_run_handoff
SPEC.loader.exec_module(bundle_run_handoff)


class BundleRunHandoffTests(unittest.TestCase):
    def test_write_bundle_run_handoff_file_creates_json_array(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "bundle-run.json"
            written_path = bundle_run_handoff.write_bundle_run_handoff_file(
                path,
                job_name="ops_usage_ingestion_job",
                status="FAILED",
                run_id="run-1",
                result_state="FAILED",
                update_time="2026-04-30T00:05:00Z",
                duration_ms=500,
            )
            payload = written_path.read_text(encoding="utf-8")

        self.assertEqual(written_path, path)
        self.assertIn('"job_name": "ops_usage_ingestion_job"', payload)
        self.assertIn('"status": "FAILED"', payload)
        self.assertIn('"duration_ms": 500', payload)

    def test_build_bundle_run_handoff_row_minimal(self) -> None:
        row = bundle_run_handoff.build_bundle_run_handoff_row(
            job_name="ops_readiness_refresh_job",
            status="SUCCESS",
        )

        self.assertEqual(row["job_name"], "ops_readiness_refresh_job")
        self.assertEqual(row["status"], "SUCCESS")
        self.assertIsNone(row["run_id"])


if __name__ == "__main__":
    unittest.main()
