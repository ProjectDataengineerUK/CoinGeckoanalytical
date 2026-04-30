from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
import unittest


MODULE_PATH = Path(__file__).resolve().parent / "market_source_ingestion_job.py"
SPEC = importlib.util.spec_from_file_location("market_source_ingestion_job", MODULE_PATH)
market_source_ingestion_job = importlib.util.module_from_spec(SPEC)
assert SPEC is not None and SPEC.loader is not None
sys.modules[SPEC.name] = market_source_ingestion_job
SPEC.loader.exec_module(market_source_ingestion_job)


class MarketSourceIngestionJobTests(unittest.TestCase):
    def test_parse_payload_accepts_single_object(self) -> None:
        rows = market_source_ingestion_job.parse_payload(
            '{"id":"bitcoin","symbol":"btc","name":"Bitcoin","market_cap":1850000000000,"current_price":95000,"total_volume":35000000000,"circulating_supply":19500000,"market_cap_rank":1,"last_updated":"2026-04-30T00:00:00Z"}'
        )

        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["id"], "bitcoin")

    def test_normalize_market_row_maps_coingecko_shape(self) -> None:
        row = market_source_ingestion_job.normalize_market_row(
            {
                "id": "ethereum",
                "symbol": "eth",
                "name": "Ethereum",
                "market_cap": "420000000000",
                "current_price": "3200",
                "total_volume": "18000000000",
                "circulating_supply": "120000000",
                "market_cap_rank": "2",
                "last_updated": "2026-04-30T00:00:00Z",
            }
        )

        self.assertEqual(row["source_system"], "coingecko_api")
        self.assertEqual(row["asset_id"], "ethereum")
        self.assertEqual(row["symbol"], "ETH")
        self.assertEqual(row["market_cap_rank"], 2)
        self.assertEqual(row["price_usd"], 3200.0)

    def test_validate_market_row_rejects_invalid_source(self) -> None:
        with self.assertRaises(ValueError):
            market_source_ingestion_job.validate_market_row(
                {
                    "source_system": "unsupported",
                    "source_record_id": "bitcoin:2026-04-30T00:00:00Z",
                    "asset_id": "bitcoin",
                    "symbol": "BTC",
                    "name": "Bitcoin",
                    "category": "store_of_value",
                    "observed_at": "2026-04-30T00:00:00Z",
                    "ingested_at": "2026-04-30T00:01:00Z",
                    "market_cap_usd": 1850000000000,
                    "price_usd": 95000,
                    "volume_24h_usd": 35000000000,
                    "circulating_supply": 19500000,
                    "market_cap_rank": 1,
                    "payload_version": "coingecko_markets_v1",
                }
            )

    def test_parse_runtime_args_supports_cli_flags(self) -> None:
        parsed = market_source_ingestion_job.parse_runtime_args(
            [
                "--payload-json",
                '[{"id":"bitcoin","symbol":"btc","name":"Bitcoin","market_cap":1,"current_price":1,"total_volume":1,"circulating_supply":1,"market_cap_rank":1,"last_updated":"2026-04-30T00:00:00Z"}]',
                "--target-table",
                "cgadev.market_bronze.bronze_market_snapshots",
            ]
        )

        self.assertEqual(parsed["target_table"], "cgadev.market_bronze.bronze_market_snapshots")
        self.assertIn('"id":"bitcoin"', parsed["payload_json"])


if __name__ == "__main__":
    unittest.main()
