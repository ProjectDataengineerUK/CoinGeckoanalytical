from __future__ import annotations

from pathlib import Path
import unittest


class BundleRunObservabilityTests(unittest.TestCase):
    def test_sql_surface_exists(self) -> None:
        sql_path = Path(__file__).resolve().parent / "bundle_run_observability.sql"
        text = sql_path.read_text(encoding="utf-8")

        self.assertIn("ops_bundle_runs", text)
        self.assertIn("ops_bundle_run_readiness", text)
        self.assertIn("bundle_readiness_status", text)


if __name__ == "__main__":
    unittest.main()
