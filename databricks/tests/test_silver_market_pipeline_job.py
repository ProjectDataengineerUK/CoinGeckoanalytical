from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
import unittest


MODULE_PATH = Path(__file__).resolve().parent.parent / "jobs/silver_market_pipeline_job.py"
SPEC = importlib.util.spec_from_file_location("silver_market_pipeline_job", MODULE_PATH)
silver_market_pipeline_job = importlib.util.module_from_spec(SPEC)
assert SPEC is not None and SPEC.loader is not None
sys.modules[SPEC.name] = silver_market_pipeline_job
SPEC.loader.exec_module(silver_market_pipeline_job)


class NormalizeSilverChangesRowTests(unittest.TestCase):
    def _valid_row(self) -> dict:
        return {
            "asset_id": "bitcoin",
            "symbol": "btc",
            "name": "Bitcoin",
            "observed_at": "2026-04-30T12:00:00Z",
            "price_change_pct_1h": 0.5,
            "price_change_pct_24h": -1.2,
            "price_change_pct_7d": 3.4,
            "volume_24h_usd": 35000000000.0,
            "market_cap_usd": 1850000000000.0,
        }

    def test_maps_standard_fields_correctly(self) -> None:
        row = silver_market_pipeline_job.normalize_silver_changes_row(self._valid_row())

        self.assertEqual(row["asset_id"], "bitcoin")
        self.assertEqual(row["symbol"], "BTC")
        self.assertEqual(row["name"], "Bitcoin")
        self.assertEqual(row["window_id"], "2026-04-30")
        self.assertAlmostEqual(row["price_change_pct_1h"], 0.5)
        self.assertAlmostEqual(row["price_change_pct_24h"], -1.2)
        self.assertAlmostEqual(row["price_change_pct_7d"], 3.4)
        self.assertAlmostEqual(row["volume_24h_usd"], 35000000000.0)
        self.assertAlmostEqual(row["market_cap_usd"], 1850000000000.0)

    def test_symbol_is_uppercased(self) -> None:
        row_in = self._valid_row()
        row_in["symbol"] = "eth"
        row = silver_market_pipeline_job.normalize_silver_changes_row(row_in)
        self.assertEqual(row["symbol"], "ETH")

    def test_window_id_derived_from_observed_at_date_portion(self) -> None:
        row_in = self._valid_row()
        row_in["observed_at"] = "2026-01-15T23:59:59Z"
        row = silver_market_pipeline_job.normalize_silver_changes_row(row_in)
        self.assertEqual(row["window_id"], "2026-01-15")

    def test_price_change_none_becomes_null(self) -> None:
        row_in = self._valid_row()
        row_in["price_change_pct_1h"] = None
        row_in["price_change_pct_24h"] = None
        row_in["price_change_pct_7d"] = None
        row = silver_market_pipeline_job.normalize_silver_changes_row(row_in)
        self.assertIsNone(row["price_change_pct_1h"])
        self.assertIsNone(row["price_change_pct_24h"])
        self.assertIsNone(row["price_change_pct_7d"])

    def test_missing_asset_id_raises_value_error(self) -> None:
        row_in = self._valid_row()
        del row_in["asset_id"]
        with self.assertRaises(ValueError):
            silver_market_pipeline_job.normalize_silver_changes_row(row_in)

    def test_missing_symbol_raises_value_error(self) -> None:
        row_in = self._valid_row()
        del row_in["symbol"]
        with self.assertRaises(ValueError):
            silver_market_pipeline_job.normalize_silver_changes_row(row_in)

    def test_missing_observed_at_raises_value_error(self) -> None:
        row_in = self._valid_row()
        del row_in["observed_at"]
        with self.assertRaises(ValueError):
            silver_market_pipeline_job.normalize_silver_changes_row(row_in)

    def test_missing_volume_24h_raises_value_error(self) -> None:
        row_in = self._valid_row()
        del row_in["volume_24h_usd"]
        with self.assertRaises(ValueError):
            silver_market_pipeline_job.normalize_silver_changes_row(row_in)

    def test_missing_market_cap_raises_value_error(self) -> None:
        row_in = self._valid_row()
        del row_in["market_cap_usd"]
        with self.assertRaises(ValueError):
            silver_market_pipeline_job.normalize_silver_changes_row(row_in)

    def test_name_defaults_to_unmapped_when_absent(self) -> None:
        row_in = self._valid_row()
        del row_in["name"]
        row = silver_market_pipeline_job.normalize_silver_changes_row(row_in)
        self.assertEqual(row["name"], "unmapped")


class NormalizeSilverDominanceRowTests(unittest.TestCase):
    def _valid_row(self) -> dict:
        return {
            "observed_at": "2026-04-30T12:00:00Z",
            "dominance_group": "btc",
            "market_cap_usd": 1850000000000.0,
            "dominance_pct": 52.3,
        }

    def test_maps_standard_fields_correctly(self) -> None:
        row = silver_market_pipeline_job.normalize_silver_dominance_row(self._valid_row())

        self.assertEqual(row["observed_at"], "2026-04-30T12:00:00Z")
        self.assertEqual(row["dominance_group"], "btc")
        self.assertAlmostEqual(row["market_cap_usd"], 1850000000000.0)
        self.assertAlmostEqual(row["dominance_pct"], 52.3)

    def test_dominance_pct_none_becomes_null(self) -> None:
        row_in = self._valid_row()
        row_in["dominance_pct"] = None
        row = silver_market_pipeline_job.normalize_silver_dominance_row(row_in)
        self.assertIsNone(row["dominance_pct"])

    def test_market_cap_zero_is_accepted(self) -> None:
        row_in = self._valid_row()
        row_in["market_cap_usd"] = 0.0
        row = silver_market_pipeline_job.normalize_silver_dominance_row(row_in)
        self.assertAlmostEqual(row["market_cap_usd"], 0.0)

    def test_missing_observed_at_raises_value_error(self) -> None:
        row_in = self._valid_row()
        del row_in["observed_at"]
        with self.assertRaises(ValueError):
            silver_market_pipeline_job.normalize_silver_dominance_row(row_in)

    def test_missing_dominance_group_raises_value_error(self) -> None:
        row_in = self._valid_row()
        del row_in["dominance_group"]
        with self.assertRaises(ValueError):
            silver_market_pipeline_job.normalize_silver_dominance_row(row_in)

    def test_missing_market_cap_raises_value_error(self) -> None:
        row_in = self._valid_row()
        del row_in["market_cap_usd"]
        with self.assertRaises(ValueError):
            silver_market_pipeline_job.normalize_silver_dominance_row(row_in)

    def test_market_cap_explicitly_none_raises_value_error(self) -> None:
        row_in = self._valid_row()
        row_in["market_cap_usd"] = None
        with self.assertRaises(ValueError):
            silver_market_pipeline_job.normalize_silver_dominance_row(row_in)


class NormalizeSilverComparisonRowTests(unittest.TestCase):
    def _valid_row(self) -> dict:
        return {
            "asset_id": "bitcoin",
            "symbol": "btc",
            "observed_at": "2026-04-30T12:00:00Z",
            "price_usd": 95000.0,
            "market_cap_usd": 1850000000000.0,
            "volume_24h_usd": 35000000000.0,
            "market_cap_rank": 1,
            "price_change_pct_24h": -1.5,
            "price_change_pct_7d": 4.2,
        }

    def test_maps_standard_fields_correctly(self) -> None:
        row = silver_market_pipeline_job.normalize_silver_comparison_row(self._valid_row())

        self.assertEqual(row["asset_id"], "bitcoin")
        self.assertEqual(row["symbol"], "BTC")
        self.assertEqual(row["observed_at"], "2026-04-30T12:00:00Z")
        self.assertAlmostEqual(row["price_usd"], 95000.0)
        self.assertAlmostEqual(row["market_cap_usd"], 1850000000000.0)
        self.assertAlmostEqual(row["volume_24h_usd"], 35000000000.0)
        self.assertAlmostEqual(row["price_change_pct_24h"], -1.5)
        self.assertAlmostEqual(row["price_change_pct_7d"], 4.2)

    def test_symbol_is_uppercased(self) -> None:
        row_in = self._valid_row()
        row_in["symbol"] = "sol"
        row = silver_market_pipeline_job.normalize_silver_comparison_row(row_in)
        self.assertEqual(row["symbol"], "SOL")

    def test_correlation_bucket_large_cap_for_rank_1_to_10(self) -> None:
        for rank in (1, 5, 10):
            row_in = self._valid_row()
            row_in["market_cap_rank"] = rank
            row = silver_market_pipeline_job.normalize_silver_comparison_row(row_in)
            self.assertEqual(row["correlation_bucket"], "large_cap", f"rank={rank}")

    def test_correlation_bucket_mid_cap_for_rank_11_to_50(self) -> None:
        for rank in (11, 25, 50):
            row_in = self._valid_row()
            row_in["market_cap_rank"] = rank
            row = silver_market_pipeline_job.normalize_silver_comparison_row(row_in)
            self.assertEqual(row["correlation_bucket"], "mid_cap", f"rank={rank}")

    def test_correlation_bucket_broad_market_for_rank_above_50(self) -> None:
        for rank in (51, 100, 5000):
            row_in = self._valid_row()
            row_in["market_cap_rank"] = rank
            row = silver_market_pipeline_job.normalize_silver_comparison_row(row_in)
            self.assertEqual(row["correlation_bucket"], "broad_market", f"rank={rank}")

    def test_correlation_bucket_defaults_to_broad_market_when_rank_absent(self) -> None:
        row_in = self._valid_row()
        del row_in["market_cap_rank"]
        row = silver_market_pipeline_job.normalize_silver_comparison_row(row_in)
        self.assertEqual(row["correlation_bucket"], "broad_market")

    def test_price_change_none_becomes_null(self) -> None:
        row_in = self._valid_row()
        row_in["price_change_pct_24h"] = None
        row_in["price_change_pct_7d"] = None
        row = silver_market_pipeline_job.normalize_silver_comparison_row(row_in)
        self.assertIsNone(row["price_change_pct_24h"])
        self.assertIsNone(row["price_change_pct_7d"])

    def test_market_cap_zero_is_accepted(self) -> None:
        row_in = self._valid_row()
        row_in["market_cap_usd"] = 0.0
        row = silver_market_pipeline_job.normalize_silver_comparison_row(row_in)
        self.assertAlmostEqual(row["market_cap_usd"], 0.0)

    def test_missing_asset_id_raises_value_error(self) -> None:
        row_in = self._valid_row()
        del row_in["asset_id"]
        with self.assertRaises(ValueError):
            silver_market_pipeline_job.normalize_silver_comparison_row(row_in)

    def test_missing_symbol_raises_value_error(self) -> None:
        row_in = self._valid_row()
        del row_in["symbol"]
        with self.assertRaises(ValueError):
            silver_market_pipeline_job.normalize_silver_comparison_row(row_in)

    def test_missing_observed_at_raises_value_error(self) -> None:
        row_in = self._valid_row()
        del row_in["observed_at"]
        with self.assertRaises(ValueError):
            silver_market_pipeline_job.normalize_silver_comparison_row(row_in)

    def test_missing_price_usd_raises_value_error(self) -> None:
        row_in = self._valid_row()
        del row_in["price_usd"]
        with self.assertRaises(ValueError):
            silver_market_pipeline_job.normalize_silver_comparison_row(row_in)

    def test_missing_volume_24h_raises_value_error(self) -> None:
        row_in = self._valid_row()
        del row_in["volume_24h_usd"]
        with self.assertRaises(ValueError):
            silver_market_pipeline_job.normalize_silver_comparison_row(row_in)


class SilverPipelineConfigTests(unittest.TestCase):
    def test_full_table_names_compose_catalog_schema_table(self) -> None:
        config = silver_market_pipeline_job.SilverPipelineConfig(
            target_catalog="cgadev",
            target_env="cgadev",
            silver_schema="market_silver",
            bronze_schema="market_bronze",
            bronze_table="bronze_market_snapshots",
        )

        self.assertEqual(
            config.bronze_full_table,
            "cgadev.market_bronze.bronze_market_snapshots",
        )
        self.assertEqual(
            config.changes_full_table,
            "cgadev.market_silver.silver_market_changes",
        )
        self.assertEqual(
            config.dominance_full_table,
            "cgadev.market_silver.silver_market_dominance",
        )
        self.assertEqual(
            config.comparison_full_table,
            "cgadev.market_silver.silver_cross_asset_comparison",
        )

    def test_load_pipeline_config_from_env_uses_provided_values(self) -> None:
        config = silver_market_pipeline_job.load_pipeline_config_from_env(
            {
                "SILVER_TARGET_CATALOG": "cgaprod",
                "SILVER_TARGET_ENV": "cgaprod",
                "SILVER_SCHEMA": "market_silver",
                "BRONZE_SCHEMA": "market_bronze",
                "BRONZE_TABLE": "bronze_market_snapshots",
            }
        )

        self.assertEqual(config.target_catalog, "cgaprod")
        self.assertEqual(config.silver_schema, "market_silver")
        self.assertEqual(config.bronze_schema, "market_bronze")
        self.assertEqual(config.bronze_table, "bronze_market_snapshots")

    def test_load_pipeline_config_from_env_uses_defaults_when_absent(self) -> None:
        config = silver_market_pipeline_job.load_pipeline_config_from_env({})

        self.assertEqual(config.target_catalog, "cgadev")
        self.assertEqual(config.silver_schema, "market_silver")
        self.assertEqual(config.bronze_schema, "market_bronze")
        self.assertEqual(config.bronze_table, "bronze_market_snapshots")


class ParsePayloadTests(unittest.TestCase):
    def test_accepts_single_json_object(self) -> None:
        rows = silver_market_pipeline_job.parse_payload(
            '{"asset_id": "bitcoin", "symbol": "btc"}'
        )

        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["asset_id"], "bitcoin")

    def test_accepts_json_array(self) -> None:
        rows = silver_market_pipeline_job.parse_payload(
            '[{"asset_id": "bitcoin"}, {"asset_id": "ethereum"}]'
        )

        self.assertEqual(len(rows), 2)

    def test_empty_inputs_return_empty_list(self) -> None:
        rows = silver_market_pipeline_job.parse_payload(None, payload_path=None)
        self.assertEqual(rows, [])

    def test_invalid_json_structure_raises(self) -> None:
        with self.assertRaises(Exception):
            silver_market_pipeline_job.parse_payload('"just a string"')


class ParseRuntimeArgsTests(unittest.TestCase):
    def test_parses_payload_json_flag(self) -> None:
        parsed = silver_market_pipeline_job.parse_runtime_args(
            ["--payload-json", '[{"asset_id":"bitcoin"}]']
        )
        self.assertEqual(parsed["payload_json"], '[{"asset_id":"bitcoin"}]')

    def test_parses_target_catalog_flag(self) -> None:
        parsed = silver_market_pipeline_job.parse_runtime_args(
            ["--target-catalog", "cgaprod"]
        )
        self.assertEqual(parsed["target_catalog"], "cgaprod")

    def test_parses_target_env_flag(self) -> None:
        parsed = silver_market_pipeline_job.parse_runtime_args(
            ["--target-env", "cgaprod"]
        )
        self.assertEqual(parsed["target_env"], "cgaprod")

    def test_unrecognized_flags_are_ignored(self) -> None:
        parsed = silver_market_pipeline_job.parse_runtime_args(
            ["--unknown-flag", "value", "--target-catalog", "cgadev"]
        )
        self.assertEqual(parsed["target_catalog"], "cgadev")
        self.assertIsNone(parsed["payload_json"])

    def test_all_defaults_are_none_when_no_args_given(self) -> None:
        parsed = silver_market_pipeline_job.parse_runtime_args([])
        self.assertIsNone(parsed["payload_json"])
        self.assertIsNone(parsed["payload_path"])
        self.assertIsNone(parsed["target_catalog"])
        self.assertIsNone(parsed["target_env"])


class BuildSilverChangesDataframeTests(unittest.TestCase):
    def _make_fake_spark(self, sql_result_rows: list[dict]) -> object:
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
            def __init__(self, rows: list[dict]) -> None:
                self._rows = rows
                self.write = FakeWriter()
                self.select_expressions: tuple = ()
                self.dedup_keys: list[str] = []

            def selectExpr(self, *expressions: str) -> "FakeDataFrame":
                self.select_expressions = expressions
                return self

            def dropDuplicates(self, keys: list[str]) -> "FakeDataFrame":
                self.dedup_keys = keys
                return self

            def cache(self) -> "FakeDataFrame":
                return self

            def unpersist(self) -> None:
                pass

            def count(self) -> int:
                return len(self._rows)

        class FakeSpark:
            def __init__(self, rows: list[dict]) -> None:
                self.dataframe = FakeDataFrame(rows)
                self.sql_calls: list[str] = []

            def sql(self, query: str) -> "FakeDataFrame":
                self.sql_calls.append(query)
                return self.dataframe

            def table(self, name: str) -> "FakeDataFrame":
                return self.dataframe

            def createDataFrame(self, rows: list[dict]) -> "FakeDataFrame":
                return self.dataframe

        return FakeSpark(sql_result_rows)

    def test_build_silver_changes_issues_sql_and_applies_select_and_dedup(self) -> None:
        fake_spark = self._make_fake_spark([{"asset_id": "bitcoin"}])
        config = silver_market_pipeline_job.SilverPipelineConfig(
            target_catalog="cgadev",
            target_env="cgadev",
            silver_schema="market_silver",
            bronze_schema="market_bronze",
            bronze_table="bronze_market_snapshots",
        )

        dataframe = silver_market_pipeline_job.build_silver_changes_dataframe(fake_spark, config)

        self.assertTrue(len(fake_spark.sql_calls) >= 1)
        self.assertIn("cgadev.market_bronze.bronze_market_snapshots", fake_spark.sql_calls[0])
        self.assertIn(["asset_id", "window_id", "observed_at"], [dataframe.dedup_keys])

    def test_build_silver_dominance_issues_sql_referencing_bronze_table(self) -> None:
        fake_spark = self._make_fake_spark([{"observed_at": "2026-04-30T12:00:00Z"}])
        config = silver_market_pipeline_job.SilverPipelineConfig(
            target_catalog="cgadev",
            target_env="cgadev",
            silver_schema="market_silver",
            bronze_schema="market_bronze",
            bronze_table="bronze_market_snapshots",
        )

        dataframe = silver_market_pipeline_job.build_silver_dominance_dataframe(fake_spark, config)

        self.assertTrue(len(fake_spark.sql_calls) >= 1)
        self.assertIn("cgadev.market_bronze.bronze_market_snapshots", fake_spark.sql_calls[0])
        self.assertEqual(dataframe.dedup_keys, ["dominance_group", "observed_at"])

    def test_build_silver_comparison_issues_sql_referencing_bronze_table(self) -> None:
        fake_spark = self._make_fake_spark([{"asset_id": "bitcoin"}])
        config = silver_market_pipeline_job.SilverPipelineConfig(
            target_catalog="cgadev",
            target_env="cgadev",
            silver_schema="market_silver",
            bronze_schema="market_bronze",
            bronze_table="bronze_market_snapshots",
        )

        dataframe = silver_market_pipeline_job.build_silver_comparison_dataframe(fake_spark, config)

        self.assertTrue(len(fake_spark.sql_calls) >= 1)
        self.assertIn("cgadev.market_bronze.bronze_market_snapshots", fake_spark.sql_calls[0])
        self.assertEqual(
            dataframe.dedup_keys, ["asset_id", "observed_at", "correlation_bucket"]
        )


class MainFunctionTests(unittest.TestCase):
    def _make_fake_spark(self) -> object:
        class FakeWriter:
            def __init__(self) -> None:
                self.saves: list[str] = []

            def mode(self, value: str) -> "FakeWriter":
                return self

            def format(self, value: str) -> "FakeWriter":
                return self

            def saveAsTable(self, target_table: str) -> None:
                self.saves.append(target_table)

        class FakeDataFrame:
            def __init__(self) -> None:
                self.write = FakeWriter()

            def selectExpr(self, *expressions: str) -> "FakeDataFrame":
                return self

            def dropDuplicates(self, keys: list[str]) -> "FakeDataFrame":
                return self

            def cache(self) -> "FakeDataFrame":
                return self

            def unpersist(self) -> None:
                pass

            def count(self) -> int:
                return 5

            def createOrReplaceTempView(self, name: str) -> None:
                pass

        class FakeSpark:
            def __init__(self) -> None:
                self.dataframe = FakeDataFrame()
                self.sql_calls: list[str] = []

            def sql(self, query: str) -> "FakeDataFrame":
                self.sql_calls.append(query)
                return self.dataframe

            def table(self, name: str) -> "FakeDataFrame":
                return self.dataframe

            def createDataFrame(self, rows: list[dict]) -> "FakeDataFrame":
                return self.dataframe

        return FakeSpark()

    def test_main_returns_silver_pipeline_result_with_counts(self) -> None:
        fake_spark = self._make_fake_spark()
        config = silver_market_pipeline_job.SilverPipelineConfig(
            target_catalog="cgadev",
            target_env="cgadev",
            silver_schema="market_silver",
            bronze_schema="market_bronze",
            bronze_table="bronze_market_snapshots",
        )

        result = silver_market_pipeline_job.main(fake_spark, config=config)

        self.assertIsInstance(
            result, silver_market_pipeline_job.SilverPipelineResult
        )
        self.assertEqual(result.changes_rows_written, 5)
        self.assertEqual(result.dominance_rows_written, 5)
        self.assertEqual(result.comparison_rows_written, 5)
        self.assertEqual(
            result.changes_target_table,
            "cgadev.market_silver.silver_market_changes",
        )
        self.assertEqual(
            result.dominance_target_table,
            "cgadev.market_silver.silver_market_dominance",
        )
        self.assertEqual(
            result.comparison_target_table,
            "cgadev.market_silver.silver_cross_asset_comparison",
        )

    def test_main_writes_to_all_three_silver_tables(self) -> None:
        fake_spark = self._make_fake_spark()
        config = silver_market_pipeline_job.SilverPipelineConfig(
            target_catalog="cgadev",
            target_env="cgadev",
            silver_schema="market_silver",
            bronze_schema="market_bronze",
            bronze_table="bronze_market_snapshots",
        )

        silver_market_pipeline_job.main(fake_spark, config=config)

        all_saves = fake_spark.dataframe.write.saves
        self.assertIn("cgadev.market_silver.silver_market_changes", all_saves)
        self.assertIn("cgadev.market_silver.silver_market_dominance", all_saves)
        self.assertIn("cgadev.market_silver.silver_cross_asset_comparison", all_saves)

    def test_main_issues_sql_referencing_bronze_table(self) -> None:
        fake_spark = self._make_fake_spark()
        config = silver_market_pipeline_job.SilverPipelineConfig(
            target_catalog="cgadev",
            target_env="cgadev",
            silver_schema="market_silver",
            bronze_schema="market_bronze",
            bronze_table="bronze_market_snapshots",
        )

        silver_market_pipeline_job.main(fake_spark, config=config)

        bronze_refs = [
            q for q in fake_spark.sql_calls
            if "cgadev.market_bronze.bronze_market_snapshots" in q
        ]
        self.assertEqual(len(bronze_refs), 3)


if __name__ == "__main__":
    unittest.main()
