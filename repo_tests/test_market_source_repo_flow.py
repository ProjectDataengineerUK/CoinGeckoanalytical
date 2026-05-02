from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path
import tempfile
import unittest


BACKEND_MODULE_PATH = Path(__file__).resolve().parent.parent / "backend" / "market_source_handoff.py"
BACKEND_SPEC = importlib.util.spec_from_file_location("market_source_handoff", BACKEND_MODULE_PATH)
market_source_handoff = importlib.util.module_from_spec(BACKEND_SPEC)
assert BACKEND_SPEC is not None and BACKEND_SPEC.loader is not None
sys.modules[BACKEND_SPEC.name] = market_source_handoff
BACKEND_SPEC.loader.exec_module(market_source_handoff)

INGESTION_MODULE_PATH = Path(__file__).resolve().parent.parent / "databricks" / "jobs" / "market_source_ingestion_job.py"
INGESTION_SPEC = importlib.util.spec_from_file_location("market_source_ingestion_job", INGESTION_MODULE_PATH)
market_source_ingestion_job = importlib.util.module_from_spec(INGESTION_SPEC)
assert INGESTION_SPEC is not None and INGESTION_SPEC.loader is not None
sys.modules[INGESTION_SPEC.name] = market_source_ingestion_job
INGESTION_SPEC.loader.exec_module(market_source_ingestion_job)


class MarketSourceRepoFlowTests(unittest.TestCase):
    def test_backend_handoff_matches_databricks_ingestion_shape(self) -> None:
        rows = [
            market_source_handoff.build_market_source_handoff_row(
                asset_id="bitcoin",
                symbol="btc",
                name="Bitcoin",
                market_cap=1850000000000,
                current_price=95000,
                total_volume=35000000000,
                circulating_supply=19500000,
                market_cap_rank=1,
                last_updated="2026-04-30T00:00:00Z",
                category="store_of_value",
            ),
            market_source_handoff.build_market_source_handoff_row(
                asset_id="ethereum",
                symbol="eth",
                name="Ethereum",
                market_cap=420000000000,
                current_price=3200,
                total_volume=18000000000,
                circulating_supply=120000000,
                market_cap_rank=2,
                last_updated="2026-04-30T00:00:00Z",
                category="smart_contract_platform",
            ),
        ]

        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "market-source.json"
            market_source_handoff.write_market_source_handoff_file(path, rows)
            parsed_rows = market_source_ingestion_job.parse_payload(payload_path=str(path), payload_json=None)
            normalized_rows = market_source_ingestion_job.normalize_market_rows(parsed_rows)

        self.assertEqual(len(normalized_rows), 2)
        self.assertEqual(normalized_rows[0]["asset_id"], "bitcoin")
        self.assertEqual(normalized_rows[0]["symbol"], "BTC")
        self.assertEqual(normalized_rows[0]["payload_version"], "coingecko_markets_v1")
        self.assertEqual(normalized_rows[1]["asset_id"], "ethereum")
        self.assertEqual(normalized_rows[1]["market_cap_rank"], 2)

    def test_fixture_matches_ingestion_shape(self) -> None:
        fixture_path = Path(__file__).resolve().parent.parent / "databricks" / "fixtures" / "market_source_sample.json"
        fixture_rows = json.loads(fixture_path.read_text(encoding="utf-8"))
        normalized_rows = market_source_ingestion_job.normalize_market_rows(fixture_rows)

        self.assertEqual(len(normalized_rows), 3)
        self.assertEqual(normalized_rows[0]["target_table"] if "target_table" in normalized_rows[0] else "bronze_market_snapshots", "bronze_market_snapshots")
        self.assertEqual(normalized_rows[0]["asset_id"], "bitcoin")
        self.assertEqual(normalized_rows[2]["symbol"], "SOL")


if __name__ == "__main__":
    unittest.main()
