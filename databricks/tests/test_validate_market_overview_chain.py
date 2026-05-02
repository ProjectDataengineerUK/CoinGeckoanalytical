from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
import tempfile
import unittest


MODULE_PATH = Path(__file__).resolve().parent.parent / "tools/validate_market_overview_chain.py"
SPEC = importlib.util.spec_from_file_location("validate_market_overview_chain", MODULE_PATH)
validate_market_overview_chain = importlib.util.module_from_spec(SPEC)
assert SPEC is not None and SPEC.loader is not None
sys.modules[SPEC.name] = validate_market_overview_chain
SPEC.loader.exec_module(validate_market_overview_chain)


class ValidateMarketOverviewChainTests(unittest.TestCase):
    def test_current_chain_passes(self) -> None:
        errors = validate_market_overview_chain.validate_market_overview_chain(
            Path(__file__).resolve().parent.parent
        )

        self.assertEqual(errors, [])

    def test_missing_gold_dependency_is_reported(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            source_root = Path(__file__).resolve().parent.parent

            source_map = {
                "sql/migrations/bronze_market_table_migration.sql": "sql/migrations/bronze_market_table_migration.sql",
                "sql/layers/bronze_silver_market_foundation.sql": "sql/layers/bronze_silver_market_foundation.sql",
                "sql/migrations/silver_market_migration.sql": "sql/migrations/silver_market_migration.sql",
                "jobs/silver_market_pipeline_job.py": "jobs/silver_market_pipeline_job.py",
                "sql/layers/gold_market_views.sql": "sql/layers/gold_market_views.sql",
                "sql/layers/genie_metric_views.sql": "sql/layers/genie_metric_views.sql",
                "unity-catalog-lineage-map.md": "unity-catalog-lineage-map.md",
                "jobs/market_source_ingestion_job.py": "jobs/market_source_ingestion_job.py",
            }
            for dest_relpath, src_relpath in source_map.items():
                dest = root / dest_relpath
                dest.parent.mkdir(parents=True, exist_ok=True)
                dest.write_text((source_root / src_relpath).read_text(encoding="utf-8"), encoding="utf-8")

            gold_path = root / "sql/layers/gold_market_views.sql"
            gold_path.write_text(
                gold_path.read_text(encoding="utf-8").replace(
                    "FROM cgadev.market_silver.silver_market_changes",
                    "FROM missing_silver_market_changes",
                    1,
                ),
                encoding="utf-8",
            )

            errors = validate_market_overview_chain.validate_market_overview_chain(root)

            self.assertTrue(
                any(
                    "missing dependency FROM cgadev.market_silver.silver_market_changes for gold_top_movers"
                    in error
                    for error in errors
                )
            )


if __name__ == "__main__":
    unittest.main()
