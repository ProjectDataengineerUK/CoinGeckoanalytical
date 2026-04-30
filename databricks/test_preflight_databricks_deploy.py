from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
import unittest
from unittest.mock import patch


MODULE_PATH = Path(__file__).resolve().parent / "preflight_databricks_deploy.py"
SPEC = importlib.util.spec_from_file_location("preflight_databricks_deploy", MODULE_PATH)
preflight_databricks_deploy = importlib.util.module_from_spec(SPEC)
assert SPEC is not None and SPEC.loader is not None
sys.modules[SPEC.name] = preflight_databricks_deploy
SPEC.loader.exec_module(preflight_databricks_deploy)


class PreflightDatabricksDeployTests(unittest.TestCase):
    def test_run_preflight_reports_missing_prereqs(self) -> None:
        with patch("shutil.which", return_value=None):
            result = preflight_databricks_deploy.run_preflight({})

        self.assertFalse(result.ready)
        self.assertIn("databricks-cli", result.missing)
        self.assertIn("DATABRICKS_HOST", result.missing)
        self.assertIn("DATABRICKS_TOKEN", result.missing)

    def test_run_preflight_accepts_full_env(self) -> None:
        with patch("shutil.which", return_value="/usr/local/bin/databricks"):
            result = preflight_databricks_deploy.run_preflight(
                {
                    "DATABRICKS_HOST": "https://example.cloud.databricks.com",
                    "DATABRICKS_TOKEN": "token",
                }
            )

        self.assertTrue(result.ready)
        self.assertEqual(result.missing, [])

    def test_format_preflight_includes_missing_section(self) -> None:
        result = preflight_databricks_deploy.PreflightResult(
            cli_available=False,
            host_configured=False,
            token_configured=True,
            ready=False,
            missing=["databricks-cli", "DATABRICKS_HOST"],
        )

        output = preflight_databricks_deploy.format_preflight(result)

        self.assertIn("Databricks deploy preflight", output)
        self.assertIn("- missing:", output)
        self.assertIn("databricks-cli", output)


if __name__ == "__main__":
    unittest.main()
