from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
import tempfile
import unittest


MODULE_PATH = Path(__file__).resolve().parent / "validate_market_overview_chain.py"
SPEC = importlib.util.spec_from_file_location("validate_market_overview_chain", MODULE_PATH)
validate_market_overview_chain = importlib.util.module_from_spec(SPEC)
assert SPEC is not None and SPEC.loader is not None
sys.modules[SPEC.name] = validate_market_overview_chain
SPEC.loader.exec_module(validate_market_overview_chain)


class ValidateMarketOverviewChainTests(unittest.TestCase):
    def test_current_chain_passes(self) -> None:
        errors = validate_market_overview_chain.validate_market_overview_chain(
            Path(__file__).resolve().parent
        )

        self.assertEqual(errors, [])

    def test_missing_gold_dependency_is_reported(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            source_root = Path(__file__).resolve().parent
            for name in (
                "bronze_silver_market_foundation.sql",
                "gold_market_views.sql",
                "genie_metric_views.sql",
                "unity-catalog-lineage-map.md",
                "market_source_ingestion_job.py",
            ):
                (root / name).write_text((source_root / name).read_text(encoding="utf-8"), encoding="utf-8")

            gold_path = root / "gold_market_views.sql"
            gold_path.write_text(
                gold_path.read_text(encoding="utf-8").replace(
                    "FROM silver_market_changes", "FROM missing_silver_market_changes", 1
                ),
                encoding="utf-8",
            )

            errors = validate_market_overview_chain.validate_market_overview_chain(root)

            self.assertTrue(
                any("missing dependency FROM silver_market_changes for gold_top_movers" in error for error in errors)
            )


if __name__ == "__main__":
    unittest.main()
