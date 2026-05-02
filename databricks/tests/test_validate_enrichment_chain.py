from __future__ import annotations

import importlib.util
import shutil
import tempfile
import unittest
from pathlib import Path

_TOOL_PATH = Path(__file__).resolve().parent.parent / "tools" / "validate_enrichment_chain.py"
spec = importlib.util.spec_from_file_location("validate_enrichment_chain", _TOOL_PATH)
validate_enrichment_chain = importlib.util.module_from_spec(spec)  # type: ignore[arg-type]
spec.loader.exec_module(validate_enrichment_chain)  # type: ignore[union-attr]

_SOURCE_ROOT = Path(__file__).resolve().parent.parent


def _copy_tree(src_root: Path, dst_root: Path, relative_paths: list[str]) -> None:
    for rel in relative_paths:
        src = src_root / rel
        dst = dst_root / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)


class ValidateEnrichmentChainTests(unittest.TestCase):
    def test_current_chain_passes(self):
        errors = validate_enrichment_chain.validate_enrichment_chain()
        self.assertEqual(errors, [], msg=f"Unexpected errors: {errors}")

    def test_missing_bronze_object_is_reported(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            source_map = [
                "sql/migrations/bronze_enrichment_migration.sql",
                "sql/migrations/silver_enrichment_migration.sql",
                "sql/layers/gold_market_views.sql",
                "sql/layers/genie_metric_views.sql",
                "jobs/defillama_ingestion_job.py",
                "config/github_asset_repo_map.json",
            ]
            _copy_tree(_SOURCE_ROOT, tmp, source_map)

            broken = tmp / "sql/migrations/bronze_enrichment_migration.sql"
            content = broken.read_text(encoding="utf-8")
            broken.write_text(
                content.replace(
                    "CREATE TABLE IF NOT EXISTS cgadev.market_bronze.bronze_fred_macro",
                    "-- removed",
                ),
                encoding="utf-8",
            )
            errors = validate_enrichment_chain.validate_enrichment_chain(tmpdir)
        self.assertTrue(any("bronze_fred_macro" in e for e in errors))

    def test_missing_repo_map_is_reported(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            source_map = [
                "sql/migrations/bronze_enrichment_migration.sql",
                "sql/migrations/silver_enrichment_migration.sql",
                "sql/layers/gold_market_views.sql",
                "sql/layers/genie_metric_views.sql",
                "jobs/defillama_ingestion_job.py",
            ]
            _copy_tree(_SOURCE_ROOT, tmp, source_map)
            errors = validate_enrichment_chain.validate_enrichment_chain(tmpdir)
        self.assertTrue(any("github_asset_repo_map" in e for e in errors))


if __name__ == "__main__":
    unittest.main()
