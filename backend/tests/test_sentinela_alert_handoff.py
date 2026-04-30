from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
import tempfile
import unittest


MODULE_PATH = Path(__file__).resolve().parent.parent / "sentinela_alert_handoff.py"
SPEC = importlib.util.spec_from_file_location("sentinela_alert_handoff", MODULE_PATH)
sentinela_alert_handoff = importlib.util.module_from_spec(SPEC)
assert SPEC is not None and SPEC.loader is not None
sys.modules[SPEC.name] = sentinela_alert_handoff
SPEC.loader.exec_module(sentinela_alert_handoff)


class SentinelaAlertHandoffTests(unittest.TestCase):
    def test_write_alert_handoff_file_creates_json_array(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "alerts.json"
            written = sentinela_alert_handoff.write_alert_handoff_file(
                path,
                [
                    {
                        "kind": "bundle_failure",
                        "message": "Databricks bundle job ops_usage_ingestion_job failed.",
                        "job_name": "ops_usage_ingestion_job",
                        "run_id": "run-1",
                        "escalation": "page_oncall",
                    }
                ],
            )
            payload = written.read_text(encoding="utf-8")

        self.assertEqual(written, path)
        self.assertIn('"kind": "bundle_failure"', payload)
        self.assertIn('"source": "sentinela"', payload)

    def test_normalize_alert_adds_source_and_created_at(self) -> None:
        row = sentinela_alert_handoff.normalize_alert(
            {
                "kind": "latency_breach",
                "message": "Latency exceeded the operational threshold.",
            }
        )

        self.assertEqual(row["source"], "sentinela")
        self.assertIn("created_at", row)


if __name__ == "__main__":
    unittest.main()
