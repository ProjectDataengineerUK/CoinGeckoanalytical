from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
import tempfile
import unittest


MODULE_PATH = Path(__file__).resolve().parent.parent / "notification_handoff.py"
SPEC = importlib.util.spec_from_file_location("notification_handoff", MODULE_PATH)
notification_handoff = importlib.util.module_from_spec(SPEC)
assert SPEC is not None and SPEC.loader is not None
sys.modules[SPEC.name] = notification_handoff
SPEC.loader.exec_module(notification_handoff)


class NotificationHandoffTests(unittest.TestCase):
    def test_write_notification_handoff_file_creates_json_array(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "notifications.json"
            written = notification_handoff.write_notification_handoff_file(
                path,
                [
                    {
                        "kind": "bundle_failure",
                        "message": "Databricks bundle job ops_usage_ingestion_job failed.",
                        "escalation": "page_oncall",
                    }
                ],
            )
            payload = written.read_text(encoding="utf-8")

        self.assertEqual(written, path)
        self.assertIn('"kind": "bundle_failure"', payload)
        self.assertIn('"source": "coingeckoanalytical"', payload)

    def test_normalize_notification_adds_metadata(self) -> None:
        row = notification_handoff.normalize_notification(
            {
                "kind": "latency_breach",
                "message": "Latency exceeded the operational threshold.",
            }
        )

        self.assertEqual(row["source"], "coingeckoanalytical")
        self.assertIn("created_at", row)


if __name__ == "__main__":
    unittest.main()
