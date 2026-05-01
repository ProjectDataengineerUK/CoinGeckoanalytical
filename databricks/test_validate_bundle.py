from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
import unittest


MODULE_PATH = Path(__file__).resolve().parent / "validate_bundle.py"
SPEC = importlib.util.spec_from_file_location("validate_bundle", MODULE_PATH)
validate_bundle = importlib.util.module_from_spec(SPEC)
assert SPEC is not None and SPEC.loader is not None
sys.modules[SPEC.name] = validate_bundle
SPEC.loader.exec_module(validate_bundle)


class ValidateBundleTests(unittest.TestCase):
    def test_load_bundle_reads_databricks_yml(self) -> None:
        bundle = validate_bundle.load_bundle(Path(__file__).resolve().parent / "databricks.yml")

        self.assertEqual(bundle["bundle"]["name"], "coingeckoanalytical-databricks")

    def test_validate_bundle_accepts_current_manifest(self) -> None:
        bundle = validate_bundle.load_bundle(Path(__file__).resolve().parent / "databricks.yml")
        errors = validate_bundle.validate_bundle(bundle, root_dir=Path(__file__).resolve().parent)

        self.assertEqual(errors, [])

    def test_validate_bundle_requires_notebook_assets(self) -> None:
        bundle = validate_bundle.load_bundle(Path(__file__).resolve().parent / "databricks.yml")
        errors = validate_bundle.validate_bundle(bundle, root_dir=Path(__file__).resolve().parent / "missing-root")

        self.assertTrue(any("missing Databricks notebook asset" in error for error in errors))

    def test_validate_bundle_requires_notebooks_excluded_from_job_file_sync(self) -> None:
        bundle = validate_bundle.load_bundle(Path(__file__).resolve().parent / "databricks.yml")
        bundle["sync"]["exclude"] = []

        errors = validate_bundle.validate_bundle(bundle, root_dir=Path(__file__).resolve().parent)

        self.assertIn("Databricks notebooks must be excluded from job bundle file sync", errors)

    def test_validate_bundle_flags_bad_job_schedule(self) -> None:
        bundle = validate_bundle.load_bundle(Path(__file__).resolve().parent / "databricks.yml")
        bundle["resources"]["jobs"]["ops_usage_ingestion_job"]["schedule"]["pause_status"] = "PAUSED"
        errors = validate_bundle.validate_bundle(bundle, root_dir=Path(__file__).resolve().parent)

        self.assertTrue(any("ops_usage_ingestion_job must be unpaused" in error for error in errors))

    def test_validate_bundle_accepts_event_driven_bundle_run_job(self) -> None:
        bundle = validate_bundle.load_bundle(Path(__file__).resolve().parent / "databricks.yml")
        job = bundle["resources"]["jobs"]["ops_bundle_run_ingestion_job"]

        self.assertNotIn("schedule", job)
        errors = validate_bundle.validate_bundle(bundle, root_dir=Path(__file__).resolve().parent)
        self.assertEqual(errors, [])

    def test_validate_bundle_accepts_event_driven_sentinela_alert_job(self) -> None:
        bundle = validate_bundle.load_bundle(Path(__file__).resolve().parent / "databricks.yml")
        job = bundle["resources"]["jobs"]["ops_sentinela_alert_ingestion_job"]

        self.assertNotIn("schedule", job)
        errors = validate_bundle.validate_bundle(bundle, root_dir=Path(__file__).resolve().parent)
        self.assertEqual(errors, [])


if __name__ == "__main__":
    unittest.main()
