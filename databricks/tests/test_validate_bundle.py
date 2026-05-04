from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
import unittest


MODULE_PATH = Path(__file__).resolve().parent.parent / "tools/validate_bundle.py"
SPEC = importlib.util.spec_from_file_location("validate_bundle", MODULE_PATH)
validate_bundle = importlib.util.module_from_spec(SPEC)
assert SPEC is not None and SPEC.loader is not None
sys.modules[SPEC.name] = validate_bundle
SPEC.loader.exec_module(validate_bundle)


class ValidateBundleTests(unittest.TestCase):
    def test_load_bundle_reads_databricks_yml(self) -> None:
        bundle = validate_bundle.load_bundle(Path(__file__).resolve().parents[2] / "databricks.yml")

        self.assertEqual(bundle["bundle"]["name"], "coingeckoanalytical-databricks")

    def test_validate_bundle_accepts_current_manifest(self) -> None:
        bundle = validate_bundle.load_bundle(Path(__file__).resolve().parents[2] / "databricks.yml")
        errors = validate_bundle.validate_bundle(bundle, root_dir=Path(__file__).resolve().parents[2])

        self.assertEqual(errors, [])

    def test_validate_bundle_requires_notebook_assets(self) -> None:
        bundle = validate_bundle.load_bundle(Path(__file__).resolve().parents[2] / "databricks.yml")
        errors = validate_bundle.validate_bundle(bundle, root_dir=Path(__file__).resolve().parents[2] / "missing-root")

        self.assertTrue(any("missing Databricks notebook asset" in error for error in errors))

    def test_validate_bundle_requires_notebooks_excluded_from_job_file_sync(self) -> None:
        bundle = validate_bundle.load_bundle(Path(__file__).resolve().parents[2] / "databricks.yml")
        bundle["sync"]["exclude"] = []

        errors = validate_bundle.validate_bundle(bundle, root_dir=Path(__file__).resolve().parents[2])

        self.assertIn("Databricks notebooks must be excluded from job bundle file sync", errors)

    def test_validate_bundle_flags_bad_job_schedule(self) -> None:
        bundle = validate_bundle.load_bundle(Path(__file__).resolve().parents[2] / "databricks.yml")
        bundle["resources"]["jobs"]["ops_usage_ingestion_job"]["schedule"]["pause_status"] = "PAUSED"
        errors = validate_bundle.validate_bundle(bundle, root_dir=Path(__file__).resolve().parents[2])

        self.assertTrue(any("ops_usage_ingestion_job must be unpaused" in error for error in errors))

    def test_validate_bundle_accepts_event_driven_bundle_run_job(self) -> None:
        bundle = validate_bundle.load_bundle(Path(__file__).resolve().parents[2] / "databricks.yml")
        job = bundle["resources"]["jobs"]["ops_bundle_run_ingestion_job"]

        self.assertNotIn("schedule", job)
        errors = validate_bundle.validate_bundle(bundle, root_dir=Path(__file__).resolve().parents[2])
        self.assertEqual(errors, [])

    def test_validate_bundle_accepts_event_driven_sentinela_alert_job(self) -> None:
        bundle = validate_bundle.load_bundle(Path(__file__).resolve().parents[2] / "databricks.yml")
        job = bundle["resources"]["jobs"]["ops_sentinela_alert_ingestion_job"]

        self.assertNotIn("schedule", job)
        errors = validate_bundle.validate_bundle(bundle, root_dir=Path(__file__).resolve().parents[2])
        self.assertEqual(errors, [])

    def test_validate_bundle_rejects_invalid_app_env_item(self) -> None:
        bundle = validate_bundle.load_bundle(Path(__file__).resolve().parents[2] / "databricks.yml")
        bundle_path = Path(__file__).resolve().parents[2]
        app_yaml = bundle_path / "apps/cga-analytics/app.yaml"
        original = app_yaml.read_text(encoding="utf-8")
        try:
            app_yaml.write_text(
                "command: [\"python3\", \"app.py\"]\n\nenv:\n  - name: BROKEN_ONLY_NAME\n",
                encoding="utf-8",
            )
            errors = validate_bundle.validate_bundle(bundle, root_dir=bundle_path)
        finally:
            app_yaml.write_text(original, encoding="utf-8")

        self.assertTrue(any("must define exactly one of value or valueFrom" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
