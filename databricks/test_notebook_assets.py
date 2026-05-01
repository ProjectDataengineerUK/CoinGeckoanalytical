from __future__ import annotations

from pathlib import Path
import unittest


class NotebookAssetTests(unittest.TestCase):
    def test_expected_databricks_notebooks_exist(self) -> None:
        notebooks_dir = Path(__file__).resolve().parent / "notebooks"
        expected = {
            "01_ingest_coingecko_market.py",
            "02_validate_market_layers.py",
            "03_ops_readiness_review.py",
        }

        self.assertEqual(expected, {path.name for path in notebooks_dir.glob("*.py")})

    def test_notebooks_use_databricks_source_format(self) -> None:
        notebooks_dir = Path(__file__).resolve().parent / "notebooks"
        for notebook_path in notebooks_dir.glob("*.py"):
            with self.subTest(notebook=notebook_path.name):
                content = notebook_path.read_text(encoding="utf-8")
                self.assertTrue(content.startswith("# Databricks notebook source"))
                self.assertIn("# COMMAND ----------", content)

    def test_ingestion_notebook_delegates_to_versioned_job_module(self) -> None:
        notebook_path = Path(__file__).resolve().parent / "notebooks" / "01_ingest_coingecko_market.py"
        content = notebook_path.read_text(encoding="utf-8")

        self.assertIn("from market_source_ingestion_job import main", content)
        self.assertIn("result = main(", content)


if __name__ == "__main__":
    unittest.main()
