from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).resolve().parent.parent / "jobs/silver_market_migration_job.py"
SPEC = importlib.util.spec_from_file_location("silver_market_migration_job", MODULE_PATH)
silver_market_migration_job = importlib.util.module_from_spec(SPEC)
assert SPEC is not None and SPEC.loader is not None
sys.modules[SPEC.name] = silver_market_migration_job
SPEC.loader.exec_module(silver_market_migration_job)


class FakeDF:
    def __init__(self, rows: list) -> None:
        self._rows = rows

    def collect(self) -> list:
        return self._rows


class TestLoadSqlStatements(unittest.TestCase):
    def test_splits_multiple_statements(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "m.sql"
            path.write_text(
                "CREATE SCHEMA IF NOT EXISTS cgadev.market_silver;\n"
                "CREATE TABLE IF NOT EXISTS cgadev.market_silver.t (id STRING) USING DELTA;\n",
                encoding="utf-8",
            )
            stmts = silver_market_migration_job.load_sql_statements(path)
        self.assertEqual(len(stmts), 2)

    def test_skips_comment_only_trailing_block(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "m.sql"
            path.write_text(
                "CREATE TABLE t (id STRING) USING DELTA;\n-- trailing comment\n",
                encoding="utf-8",
            )
            stmts = silver_market_migration_job.load_sql_statements(path)
        self.assertEqual(len(stmts), 1)

    def test_skips_header_comment_block(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "m.sql"
            path.write_text(
                "-- header\nCREATE TABLE t (id STRING) USING DELTA;\n",
                encoding="utf-8",
            )
            stmts = silver_market_migration_job.load_sql_statements(path)
        self.assertEqual(len(stmts), 1)


class TestIsView(unittest.TestCase):
    def test_returns_true_for_view_ddl(self) -> None:
        class FakeSpark:
            def sql(self, stmt: str) -> FakeDF:
                return FakeDF([["CREATE VIEW cgadev.market_silver.t AS SELECT 1"]])

        self.assertTrue(
            silver_market_migration_job._is_view(FakeSpark(), "cgadev.market_silver.t")
        )

    def test_returns_false_for_table_ddl(self) -> None:
        class FakeSpark:
            def sql(self, stmt: str) -> FakeDF:
                return FakeDF([["CREATE TABLE cgadev.market_silver.t (id STRING) USING DELTA"]])

        self.assertFalse(
            silver_market_migration_job._is_view(FakeSpark(), "cgadev.market_silver.t")
        )

    def test_returns_false_on_exception(self) -> None:
        class FakeSpark:
            def sql(self, stmt: str) -> FakeDF:
                raise RuntimeError("table not found")

        self.assertFalse(
            silver_market_migration_job._is_view(FakeSpark(), "cgadev.market_silver.t")
        )

    def test_returns_false_for_empty_result(self) -> None:
        class FakeSpark:
            def sql(self, stmt: str) -> FakeDF:
                return FakeDF([])

        self.assertFalse(
            silver_market_migration_job._is_view(FakeSpark(), "cgadev.market_silver.t")
        )


class TestDropSilverViews(unittest.TestCase):
    def _make_spark(self, view_names: set[str]) -> tuple[object, list[str]]:
        dropped: list[str] = []

        class FakeSpark:
            def sql(self, stmt: str) -> FakeDF:
                if "SHOW CREATE TABLE" in stmt:
                    name = stmt.split()[-1]
                    ddl = "CREATE VIEW ..." if name in view_names else "CREATE TABLE ..."
                    return FakeDF([[ddl]])
                if stmt.startswith("DROP VIEW"):
                    dropped.append(stmt.split()[-1])
                return FakeDF([])

        return FakeSpark(), dropped

    def test_drops_all_views_and_skips_tables(self) -> None:
        view_names = {
            "cgadev.market_silver.silver_market_changes",
            "cgadev.market_silver.silver_cross_asset_comparison",
        }
        spark, dropped = self._make_spark(view_names)
        result = silver_market_migration_job.drop_silver_views(spark)
        self.assertIn("cgadev.market_silver.silver_market_changes", result)
        self.assertIn("cgadev.market_silver.silver_cross_asset_comparison", result)
        self.assertNotIn("cgadev.market_silver.silver_market_dominance", result)

    def test_returns_empty_list_when_no_views(self) -> None:
        spark, _ = self._make_spark(set())
        result = silver_market_migration_job.drop_silver_views(spark)
        self.assertEqual(result, [])

    def test_custom_table_names(self) -> None:
        view_names = {"cgadev.market_silver.custom_view"}
        spark, dropped = self._make_spark(view_names)
        result = silver_market_migration_job.drop_silver_views(
            spark, ("cgadev.market_silver.custom_view",)
        )
        self.assertEqual(result, ["cgadev.market_silver.custom_view"])


class TestRunMigration(unittest.TestCase):
    def test_executes_sql_statements_and_returns_count(self) -> None:
        executed: list[str] = []

        class FakeSpark:
            def sql(self, stmt: str) -> FakeDF:
                executed.append(stmt)
                return FakeDF([["CREATE TABLE ..."]])

        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "m.sql"
            path.write_text(
                "CREATE SCHEMA IF NOT EXISTS cgadev.market_silver;\n"
                "CREATE TABLE IF NOT EXISTS cgadev.market_silver.t (id STRING) USING DELTA;\n",
                encoding="utf-8",
            )
            result = silver_market_migration_job.run_migration(
                FakeSpark(),
                sql_file="m.sql",
                base_dir=tmp,
                table_names=(),
            )

        self.assertEqual(result["statements_executed"], 2)
        self.assertEqual(result["file"], "m.sql")
        self.assertEqual(result["views_dropped"], [])

    def test_drops_views_before_running_sql(self) -> None:
        calls: list[str] = []

        class FakeSpark:
            def sql(self, stmt: str) -> FakeDF:
                calls.append(stmt)
                if "SHOW CREATE TABLE" in stmt:
                    return FakeDF([["CREATE VIEW ..."]])
                return FakeDF([])

        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "m.sql"
            path.write_text(
                "CREATE TABLE IF NOT EXISTS cgadev.market_silver.t (id STRING) USING DELTA;\n",
                encoding="utf-8",
            )
            result = silver_market_migration_job.run_migration(
                FakeSpark(),
                sql_file="m.sql",
                base_dir=tmp,
                table_names=("cgadev.market_silver.t",),
            )

        drop_calls = [c for c in calls if c.startswith("DROP VIEW")]
        self.assertEqual(len(drop_calls), 1)
        self.assertEqual(result["statements_executed"], 1)
        self.assertEqual(len(result["views_dropped"]), 1)


if __name__ == "__main__":
    unittest.main()
