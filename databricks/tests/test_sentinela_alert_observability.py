from __future__ import annotations

from pathlib import Path
import unittest


class SentinelaAlertObservabilityTests(unittest.TestCase):
    def test_sql_surface_exists(self) -> None:
        sql_path = Path(__file__).resolve().parent.parent / "sql/observability/sentinela_alert_observability.sql"
        text = sql_path.read_text(encoding="utf-8")

        self.assertIn("ops_sentinela_alerts", text)
        self.assertIn("ops_sentinela_alert_readiness", text)
        self.assertIn("sentinela_alert_status", text)


if __name__ == "__main__":
    unittest.main()
