from __future__ import annotations

from pathlib import Path
import unittest

import yaml


class BundleManifestTests(unittest.TestCase):
    def test_bundle_defines_expected_jobs(self) -> None:
        bundle_path = Path(__file__).resolve().parents[2] / "databricks.yml"
        bundle = yaml.safe_load(bundle_path.read_text(encoding="utf-8"))

        jobs = bundle["resources"]["jobs"]
        self.assertEqual(
            set(jobs.keys()),
            {
                "bronze_market_table_migration_job",
                "silver_market_table_migration_job",
                "silver_market_pipeline_job",
                "market_source_ingestion_job",
                "ops_usage_ingestion_job",
                "ops_bundle_run_ingestion_job",
                "ops_sentinela_alert_ingestion_job",
                "ops_readiness_refresh_job",
                "bronze_enrichment_migration_job",
                "silver_enrichment_migration_job",
                "defillama_ingestion_job",
                "github_activity_ingestion_job",
                "fred_macro_ingestion_job",
                "silver_enrichment_pipeline_job",
                "feature_engineering_job",
                "train_market_model_job",
                "score_market_assets_job",
                "sentinela_evaluation_job",
            },
        )
        self.assertNotIn("schedule", jobs["bronze_market_table_migration_job"])
        self.assertEqual(jobs["market_source_ingestion_job"]["schedule"]["pause_status"], "UNPAUSED")
        self.assertEqual(jobs["ops_usage_ingestion_job"]["schedule"]["timezone_id"], "America/Sao_Paulo")
        self.assertEqual(jobs["ops_readiness_refresh_job"]["schedule"]["pause_status"], "UNPAUSED")
        self.assertNotIn("schedule", jobs["ops_bundle_run_ingestion_job"])
        self.assertNotIn("schedule", jobs["ops_sentinela_alert_ingestion_job"])

    def test_bundle_has_no_external_model_endpoints(self) -> None:
        bundle_path = Path(__file__).resolve().parents[2] / "databricks.yml"
        bundle = yaml.safe_load(bundle_path.read_text(encoding="utf-8"))

        endpoints = bundle.get("resources", {}).get("model_serving_endpoints", {})
        self.assertEqual(endpoints, {}, "No external model endpoints should be defined; use Unity AI Gateway FMAPI endpoints instead")

if __name__ == "__main__":
    unittest.main()
