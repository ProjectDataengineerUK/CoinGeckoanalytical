from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
import unittest


MODULE_PATH = Path(__file__).resolve().parent.parent / "jobs/market_source_ingestion_job.py"
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

    def test_build_coingecko_markets_url_uses_expected_endpoint_and_pagination(self) -> None:
        config = market_source_ingestion_job.CoinGeckoFetchConfig(
            base_url="https://api.coingecko.com/api/v3",
            per_page=100,
            pages=2,
            price_change_percentage="24h",
        )

        url = market_source_ingestion_job.build_coingecko_markets_url(config, page=2)

        self.assertTrue(url.startswith("https://api.coingecko.com/api/v3/coins/markets?"))
        self.assertIn("vs_currency=usd", url)
        self.assertIn("order=market_cap_desc", url)
        self.assertIn("per_page=100", url)
        self.assertIn("page=2", url)
        self.assertIn("sparkline=false", url)
        self.assertIn("price_change_percentage=24h", url)

    def test_load_coingecko_fetch_config_from_env(self) -> None:
        config = market_source_ingestion_job.load_coingecko_fetch_config_from_env(
            {
                "COINGECKO_API_BASE_URL": "https://example.test/api/v3",
                "COINGECKO_VS_CURRENCY": "brl",
                "COINGECKO_MARKET_ORDER": "volume_desc",
                "COINGECKO_PER_PAGE": "50",
                "COINGECKO_PAGES": "3",
                "COINGECKO_SPARKLINE": "true",
                "COINGECKO_PRICE_CHANGE_PERCENTAGE": "1h,24h",
                "COINGECKO_REQUEST_TIMEOUT_SECONDS": "9",
                "COINGECKO_MAX_RETRIES": "2",
                "COINGECKO_RETRY_BACKOFF_SECONDS": "0.5",
                "COINGECKO_API_KEY": "demo-key",
                "COINGECKO_API_KEY_HEADER": "x-cg-demo-api-key",
            }
        )

        self.assertEqual(config.base_url, "https://example.test/api/v3")
        self.assertEqual(config.vs_currency, "brl")
        self.assertEqual(config.order, "volume_desc")
        self.assertEqual(config.per_page, 50)
        self.assertEqual(config.pages, 3)
        self.assertTrue(config.sparkline)
        self.assertEqual(config.api_key, "demo-key")

    def test_fetch_coingecko_market_rows_paginates_until_short_page(self) -> None:
        calls: list[str] = []
        original_request_json = market_source_ingestion_job.request_json

        def fake_request_json(url: str, config: market_source_ingestion_job.CoinGeckoFetchConfig) -> list[dict[str, object]]:
            calls.append(url)
            if "page=1" in url:
                return [
                    {
                        "id": "bitcoin",
                        "symbol": "btc",
                        "name": "Bitcoin",
                        "market_cap": 1,
                        "current_price": 1,
                        "total_volume": 1,
                        "circulating_supply": 1,
                        "market_cap_rank": 1,
                        "last_updated": "2026-04-30T00:00:00Z",
                    },
                    {
                        "id": "ethereum",
                        "symbol": "eth",
                        "name": "Ethereum",
                        "market_cap": 1,
                        "current_price": 1,
                        "total_volume": 1,
                        "circulating_supply": 1,
                        "market_cap_rank": 2,
                        "last_updated": "2026-04-30T00:00:00Z",
                    },
                ]
            return [
                {
                    "id": "solana",
                    "symbol": "sol",
                    "name": "Solana",
                    "market_cap": 1,
                    "current_price": 1,
                    "total_volume": 1,
                    "circulating_supply": 1,
                    "market_cap_rank": 5,
                    "last_updated": "2026-04-30T00:00:00Z",
                }
            ]

        try:
            market_source_ingestion_job.request_json = fake_request_json
            rows = market_source_ingestion_job.fetch_coingecko_market_rows(
                market_source_ingestion_job.CoinGeckoFetchConfig(per_page=2, pages=3)
            )
        finally:
            market_source_ingestion_job.request_json = original_request_json

        self.assertEqual(len(rows), 3)
        self.assertEqual(len(calls), 2)
        self.assertIn("page=1", calls[0])
        self.assertIn("page=2", calls[1])

    def test_main_fetches_coingecko_when_no_payload_is_provided(self) -> None:
        class FakeWriter:
            def __init__(self) -> None:
                self.mode_value: str | None = None
                self.format_value: str | None = None
                self.target_table: str | None = None

            def mode(self, value: str) -> "FakeWriter":
                self.mode_value = value
                return self

            def format(self, value: str) -> "FakeWriter":
                self.format_value = value
                return self

            def saveAsTable(self, target_table: str) -> None:
                self.target_table = target_table

        class FakeDataFrame:
            def __init__(self) -> None:
                self.write = FakeWriter()
                self.select_expressions: tuple[str, ...] = ()
                self.dedup_keys: list[str] = []

            def selectExpr(self, *expressions: str) -> "FakeDataFrame":
                self.select_expressions = expressions
                return self

            def dropDuplicates(self, keys: list[str]) -> "FakeDataFrame":
                self.dedup_keys = keys
                return self

        class FakeSpark:
            def __init__(self) -> None:
                self.rows: list[dict[str, object]] | None = None
                self.dataframe = FakeDataFrame()

            def createDataFrame(self, rows: list[dict[str, object]]) -> FakeDataFrame:
                self.rows = rows
                return self.dataframe

        original_fetch = market_source_ingestion_job.fetch_coingecko_market_rows

        def fake_fetch(config: market_source_ingestion_job.CoinGeckoFetchConfig | None = None) -> list[dict[str, object]]:
            return [
                {
                    "id": "bitcoin",
                    "symbol": "btc",
                    "name": "Bitcoin",
                    "market_cap": 1,
                    "current_price": 1,
                    "total_volume": 1,
                    "circulating_supply": 1,
                    "market_cap_rank": 1,
                    "last_updated": "2026-04-30T00:00:00Z",
                }
            ]

        try:
            market_source_ingestion_job.fetch_coingecko_market_rows = fake_fetch
            fake_spark = FakeSpark()
            result = market_source_ingestion_job.main(fake_spark, target_table="cgadev.market_bronze.bronze_market_snapshots")
        finally:
            market_source_ingestion_job.fetch_coingecko_market_rows = original_fetch

        self.assertEqual(result.rows_written, 1)
        self.assertIsNotNone(fake_spark.rows)
        assert fake_spark.rows is not None
        self.assertEqual(fake_spark.rows[0]["asset_id"], "bitcoin")
        self.assertIn("CAST(observed_at AS TIMESTAMP) AS observed_at", fake_spark.dataframe.select_expressions)
        self.assertIn("CAST(market_cap_usd AS DECIMAL(38, 8)) AS market_cap_usd", fake_spark.dataframe.select_expressions)
        self.assertEqual(fake_spark.dataframe.dedup_keys, ["source_system", "source_record_id"])
        self.assertEqual(fake_spark.dataframe.write.mode_value, "append")
        self.assertEqual(fake_spark.dataframe.write.format_value, "delta")
        self.assertEqual(fake_spark.dataframe.write.target_table, "cgadev.market_bronze.bronze_market_snapshots")

    def test_build_bronze_market_dataframe_applies_spark_contract_transformations(self) -> None:
        class FakeDataFrame:
            def __init__(self) -> None:
                self.select_expressions: tuple[str, ...] = ()
                self.dedup_keys: list[str] = []

            def selectExpr(self, *expressions: str) -> "FakeDataFrame":
                self.select_expressions = expressions
                return self

            def dropDuplicates(self, keys: list[str]) -> "FakeDataFrame":
                self.dedup_keys = keys
                return self

        class FakeSpark:
            def __init__(self) -> None:
                self.rows: list[dict[str, object]] | None = None
                self.dataframe = FakeDataFrame()

            def createDataFrame(self, rows: list[dict[str, object]]) -> FakeDataFrame:
                self.rows = rows
                return self.dataframe

        normalized_rows = market_source_ingestion_job.normalize_market_rows(
            [
                {
                    "id": "bitcoin",
                    "symbol": "btc",
                    "name": "Bitcoin",
                    "market_cap": 1,
                    "current_price": 1,
                    "total_volume": 1,
                    "circulating_supply": 1,
                    "market_cap_rank": 1,
                    "last_updated": "2026-04-30T00:00:00Z",
                }
            ]
        )
        fake_spark = FakeSpark()

        dataframe = market_source_ingestion_job.build_bronze_market_dataframe(fake_spark, normalized_rows)

        self.assertIs(dataframe, fake_spark.dataframe)
        self.assertEqual(fake_spark.rows, normalized_rows)
        self.assertEqual(len(fake_spark.dataframe.select_expressions), len(market_source_ingestion_job.BRONZE_SELECT_EXPRESSIONS))
        self.assertIn("UPPER(CAST(symbol AS STRING)) AS symbol", fake_spark.dataframe.select_expressions)
        self.assertIn("CAST(price_usd AS DECIMAL(38, 8)) AS price_usd", fake_spark.dataframe.select_expressions)
        self.assertEqual(fake_spark.dataframe.dedup_keys, ["source_system", "source_record_id"])

    def test_align_bronze_dataframe_to_target_schema_casts_legacy_double_columns(self) -> None:
        class FakeField:
            def __init__(self, name: str, data_type: object) -> None:
                self.name = name
                self.dataType = data_type

        class FakeSchema:
            def __iter__(self):
                return iter(
                    [
                        FakeField("market_cap_usd", type("DoubleType", (), {})()),
                        FakeField("price_usd", type("DoubleType", (), {})()),
                        FakeField("circulating_supply", type("DoubleType", (), {})()),
                    ]
                )

        class FakeTable:
            def __init__(self) -> None:
                self.schema = FakeSchema()

        class FakeCatalog:
            def tableExists(self, target_table: str) -> bool:
                return target_table == "cgadev.market_bronze.bronze_market_snapshots"

        class FakeDataFrame:
            def __init__(self) -> None:
                self.columns = [
                    "market_cap_usd",
                    "price_usd",
                    "circulating_supply",
                ]
                self.select_expressions: tuple[str, ...] = ()

            def selectExpr(self, *expressions: str) -> "FakeDataFrame":
                self.select_expressions = expressions
                return self

        class FakeSpark:
            def __init__(self) -> None:
                self.catalog = FakeCatalog()
                self.dataframe = FakeDataFrame()
                self.table_calls: list[str] = []

            def table(self, target_table: str) -> FakeTable:
                self.table_calls.append(target_table)
                return FakeTable()

        fake_spark = FakeSpark()
        aligned = market_source_ingestion_job.align_bronze_dataframe_to_target_schema(
            fake_spark,
            fake_spark.dataframe,
            "cgadev.market_bronze.bronze_market_snapshots",
        )

        self.assertIs(aligned, fake_spark.dataframe)
        self.assertIn("CAST(market_cap_usd AS DOUBLE) AS market_cap_usd", fake_spark.dataframe.select_expressions)
        self.assertIn("CAST(price_usd AS DOUBLE) AS price_usd", fake_spark.dataframe.select_expressions)
        self.assertIn("CAST(circulating_supply AS DOUBLE) AS circulating_supply", fake_spark.dataframe.select_expressions)
        self.assertEqual(fake_spark.table_calls, ["cgadev.market_bronze.bronze_market_snapshots"])


if __name__ == "__main__":
    unittest.main()
