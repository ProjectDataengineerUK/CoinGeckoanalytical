from __future__ import annotations

from pathlib import Path
import unittest

import yaml


class BundleManifestTests(unittest.TestCase):
    def test_bundle_defines_expected_jobs(self) -> None:
        bundle_path = Path(__file__).resolve().parent.parent / "databricks.yml"
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
            },
        )
        self.assertNotIn("schedule", jobs["bronze_market_table_migration_job"])
        self.assertEqual(jobs["market_source_ingestion_job"]["schedule"]["pause_status"], "UNPAUSED")
        self.assertEqual(jobs["ops_usage_ingestion_job"]["schedule"]["timezone_id"], "America/Sao_Paulo")
        self.assertEqual(jobs["ops_readiness_refresh_job"]["schedule"]["pause_status"], "UNPAUSED")
        self.assertNotIn("schedule", jobs["ops_bundle_run_ingestion_job"])
        self.assertNotIn("schedule", jobs["ops_sentinela_alert_ingestion_job"])

    def test_bundle_defines_model_serving_endpoints(self) -> None:
        bundle_path = Path(__file__).resolve().parent.parent / "databricks.yml"
        bundle = yaml.safe_load(bundle_path.read_text(encoding="utf-8"))

        endpoints = bundle["resources"]["model_serving_endpoints"]
        self.assertEqual(
            set(endpoints.keys()),
            {"coingecko_copilot_light", "coingecko_copilot_standard", "coingecko_copilot_complex"},
        )
        for ep_key, ep in endpoints.items():
            served = ep["config"]["served_entities"]
            self.assertTrue(len(served) >= 1, f"{ep_key} has no served_entities")
            ext = served[0]["external_model"]
            self.assertEqual(ext["provider"], "anthropic")
            self.assertEqual(ext["task"], "llm/v1/chat")
            self.assertTrue(
                ext["anthropic_config"]["anthropic_api_key"].startswith("{{secrets/"),
                f"{ep_key} api key must be a secret reference",
            )
        tier_model_map = {
            "coingecko_copilot_light": "haiku",
            "coingecko_copilot_standard": "sonnet",
            "coingecko_copilot_complex": "opus",
        }
        for ep_key, fragment in tier_model_map.items():
            model_name = endpoints[ep_key]["config"]["served_entities"][0]["external_model"]["name"]
            self.assertIn(fragment, model_name, f"{ep_key} should use a {fragment} model")

if __name__ == "__main__":
    unittest.main()
