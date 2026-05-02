from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
import tempfile
import unittest


MODULE_PATH = Path(__file__).resolve().parent.parent / "jobs/bronze_market_table_migration_job.py"
SPEC = importlib.util.spec_from_file_location("bronze_market_table_migration_job", MODULE_PATH)
bronze_market_table_migration_job = importlib.util.module_from_spec(SPEC)
assert SPEC is not None and SPEC.loader is not None
sys.modules[SPEC.name] = bronze_market_table_migration_job
SPEC.loader.exec_module(bronze_market_table_migration_job)


class BronzeMarketTableMigrationJobTests(unittest.TestCase):
    def test_load_sql_statements_splits_single_statement(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            sql_path = Path(temp_dir) / "migration.sql"
            sql_path.write_text(
                "-- comment\nCREATE OR REPLACE TABLE a AS SELECT 1;\n",
                encoding="utf-8",
            )

            statements = bronze_market_table_migration_job.load_sql_statements(sql_path)

        self.assertEqual(statements, ["-- comment\nCREATE OR REPLACE TABLE a AS SELECT 1"])

    def test_load_sql_statements_skips_comment_only_blocks(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            sql_path = Path(temp_dir) / "migration.sql"
            sql_path.write_text(
                "CREATE OR REPLACE TABLE a AS SELECT 1;\n-- trailing comment only\n",
                encoding="utf-8",
            )
            statements = bronze_market_table_migration_job.load_sql_statements(sql_path)
        self.assertEqual(len(statements), 1)
        self.assertIn("SELECT 1", statements[0])

    def test_load_sql_statements_skips_header_comment_block(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            sql_path = Path(temp_dir) / "migration.sql"
            sql_path.write_text(
                "-- header\n-- line 2\n\nCREATE TABLE x (id STRING);\n",
                encoding="utf-8",
            )
            statements = bronze_market_table_migration_job.load_sql_statements(sql_path)
        self.assertEqual(len(statements), 1)

    def test_run_migration_executes_sql_statements(self) -> None:
        class FakeSpark:
            def __init__(self) -> None:
                self.statements: list[str] = []

            def sql(self, statement: str) -> None:
                self.statements.append(statement)

        with tempfile.TemporaryDirectory() as temp_dir:
            sql_path = Path(temp_dir) / "migration.sql"
            sql_path.write_text(
                "CREATE OR REPLACE TABLE cgadev.market_bronze.bronze_market_snapshots (id STRING);\n",
                encoding="utf-8",
            )

            fake_spark = FakeSpark()
            result = bronze_market_table_migration_job.run_migration(
                fake_spark,
                sql_file="migration.sql",
                base_dir=temp_dir,
            )

        self.assertEqual(result["file"], "migration.sql")
        self.assertEqual(result["statements_executed"], 1)
        self.assertEqual(
            fake_spark.statements,
            ["CREATE OR REPLACE TABLE cgadev.market_bronze.bronze_market_snapshots (id STRING)"],
        )


if __name__ == "__main__":
    unittest.main()
