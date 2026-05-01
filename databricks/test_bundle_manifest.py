from __future__ import annotations

from pathlib import Path
import unittest

import yaml


class BundleManifestTests(unittest.TestCase):
    def test_bundle_defines_expected_jobs(self) -> None:
        bundle_path = Path(__file__).resolve().parent / "databricks.yml"
        bundle = yaml.safe_load(bundle_path.read_text(encoding="utf-8"))

        jobs = bundle["resources"]["jobs"]
        self.assertEqual(
            set(jobs.keys()),
            {
                "bronze_market_table_migration_job",
                "market_source_ingestion_job",
                "ops_usage_ingestion_job",
                "ops_bundle_run_ingestion_job",
                "ops_sentinela_alert_ingestion_job",
                "ops_readiness_refresh_job",
            },
        )
        self.assertNotIn("schedule", jobs["bronze_market_table_migration_job"])
        self.assertEqual(jobs["market_source_ingestion_job"]["schedule"]["pause_status"], "UNPAUSED")
        self.assertEqual(jobs["ops_usage_ingestion_job"]["schedule"]["timezone_id"], "America/Sao_Paulo")
        self.assertEqual(jobs["ops_readiness_refresh_job"]["schedule"]["pause_status"], "UNPAUSED")
        self.assertNotIn("schedule", jobs["ops_bundle_run_ingestion_job"])
        self.assertNotIn("schedule", jobs["ops_sentinela_alert_ingestion_job"])

if __name__ == "__main__":
    unittest.main()
