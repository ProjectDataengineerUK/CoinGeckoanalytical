from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock


MODULE_PATH = Path(__file__).resolve().parent.parent / "jobs/uc_grants_job.py"
SPEC = importlib.util.spec_from_file_location("uc_grants_job", MODULE_PATH)
uc_grants_job = importlib.util.module_from_spec(SPEC)
assert SPEC is not None and SPEC.loader is not None
sys.modules[SPEC.name] = uc_grants_job
SPEC.loader.exec_module(uc_grants_job)


class UcGrantsJobTests(unittest.TestCase):
    def test_parse_sql_statements(self) -> None:
        sql = (
            "CREATE CATALOG IF NOT EXISTS cgadev;\n"
            "CREATE SCHEMA IF NOT EXISTS cgadev.market_bronze;\n"
            "GRANT USAGE ON CATALOG cgadev TO `platform_ops`;\n"
        )
        statements = uc_grants_job.parse_sql_statements(sql)
        self.assertEqual(len(statements), 3)
        self.assertIn("CREATE CATALOG IF NOT EXISTS cgadev", statements[0])
        self.assertIn("CREATE SCHEMA IF NOT EXISTS cgadev.market_bronze", statements[1])
        self.assertIn("GRANT USAGE ON CATALOG cgadev TO `platform_ops`", statements[2])

    def test_skips_blank_and_comment_lines(self) -> None:
        sql = (
            "-- This is a header comment\n"
            "-- Another comment line\n"
            "\n"
            "CREATE CATALOG IF NOT EXISTS cgadev;\n"
            "-- trailing comment only\n"
        )
        statements = uc_grants_job.parse_sql_statements(sql)
        # Only the CREATE CATALOG statement should survive; the trailing
        # comment-only block after the last semicolon must be dropped.
        self.assertEqual(len(statements), 1)
        self.assertIn("CREATE CATALOG", statements[0])

    def test_grants_result_dataclass(self) -> None:
        result = uc_grants_job.GrantsResult(statements_run=5, statements_failed=1)
        self.assertEqual(result.statements_run, 5)
        self.assertEqual(result.statements_failed, 1)
        # Must be frozen — assigning to a field should raise
        with self.assertRaises(Exception):
            result.statements_run = 99  # type: ignore[misc]

    def test_main_executes_all_statements(self) -> None:
        sql = (
            "CREATE CATALOG IF NOT EXISTS cgadev;\n"
            "CREATE SCHEMA IF NOT EXISTS cgadev.market_bronze;\n"
            "GRANT USAGE ON CATALOG cgadev TO `platform_ops`;\n"
        )
        with tempfile.TemporaryDirectory() as tmp:
            sql_path = Path(tmp) / "unity_catalog_foundation.sql"
            sql_path.write_text(sql, encoding="utf-8")

            mock_spark = MagicMock()
            result = uc_grants_job.main(mock_spark, sql_path=sql_path)

        self.assertEqual(result.statements_run, 3)
        self.assertEqual(result.statements_failed, 0)
        self.assertEqual(mock_spark.sql.call_count, 3)

    def test_main_tolerates_spark_sql_failures(self) -> None:
        sql = (
            "CREATE CATALOG IF NOT EXISTS cgadev;\n"
            "GRANT USAGE ON CATALOG cgadev TO `platform_ops`;\n"
        )
        with tempfile.TemporaryDirectory() as tmp:
            sql_path = Path(tmp) / "unity_catalog_foundation.sql"
            sql_path.write_text(sql, encoding="utf-8")

            mock_spark = MagicMock()
            mock_spark.sql.side_effect = Exception("permission denied")
            result = uc_grants_job.main(mock_spark, sql_path=sql_path)

        self.assertEqual(result.statements_run, 2)
        self.assertEqual(result.statements_failed, 2)


if __name__ == "__main__":
    unittest.main()
