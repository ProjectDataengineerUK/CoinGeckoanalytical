from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock


MODULE_PATH = Path(__file__).resolve().parent.parent / "jobs/rls_migration_job.py"
SPEC = importlib.util.spec_from_file_location("rls_migration_job", MODULE_PATH)
rls_migration_job = importlib.util.module_from_spec(SPEC)
assert SPEC is not None and SPEC.loader is not None
sys.modules[SPEC.name] = rls_migration_job
SPEC.loader.exec_module(rls_migration_job)


class RlsMigrationJobTests(unittest.TestCase):
    def test_parse_sql_statements(self) -> None:
        sql = (
            "CREATE OR REPLACE FUNCTION cgadev.audit_control.ops_usage_row_filter(event_user_id STRING)\n"
            "RETURNS BOOLEAN\n"
            "RETURN is_member('platform_ops') OR current_user() = event_user_id;\n"
            "ALTER TABLE cgadev.ops_observability.ops_usage_events\n"
            "SET ROW FILTER cgadev.audit_control.ops_usage_row_filter ON (user_id);\n"
        )
        statements = rls_migration_job.parse_sql_statements(sql)
        self.assertEqual(len(statements), 2)
        self.assertIn("CREATE OR REPLACE FUNCTION", statements[0])
        self.assertIn("ALTER TABLE", statements[1])

    def test_skips_blank_and_comment_lines(self) -> None:
        sql = (
            "-- RLS migration header\n"
            "\n"
            "ALTER TABLE cgadev.ops_observability.ops_usage_events\n"
            "SET ROW FILTER cgadev.audit_control.ops_usage_row_filter ON (user_id);\n"
            "-- trailing comment only\n"
        )
        statements = rls_migration_job.parse_sql_statements(sql)
        # The header comment block and the trailing comment-only block must be dropped.
        self.assertEqual(len(statements), 1)
        self.assertIn("ALTER TABLE", statements[0])

    def test_rls_result_dataclass(self) -> None:
        result = rls_migration_job.RlsResult(statements_run=4, statements_failed=0)
        self.assertEqual(result.statements_run, 4)
        self.assertEqual(result.statements_failed, 0)
        # Must be frozen — assigning to a field should raise
        with self.assertRaises(Exception):
            result.statements_run = 99  # type: ignore[misc]

    def test_main_executes_all_statements(self) -> None:
        sql = (
            "CREATE OR REPLACE FUNCTION cgadev.audit_control.ops_usage_row_filter(event_user_id STRING)\n"
            "RETURNS BOOLEAN\n"
            "RETURN is_member('platform_ops') OR current_user() = event_user_id;\n"
            "ALTER TABLE cgadev.ops_observability.ops_usage_events\n"
            "SET ROW FILTER cgadev.audit_control.ops_usage_row_filter ON (user_id);\n"
        )
        with tempfile.TemporaryDirectory() as tmp:
            sql_path = Path(tmp) / "rls_column_masking.sql"
            sql_path.write_text(sql, encoding="utf-8")

            mock_spark = MagicMock()
            result = rls_migration_job.main(mock_spark, sql_path=sql_path)

        self.assertEqual(result.statements_run, 2)
        self.assertEqual(result.statements_failed, 0)
        self.assertEqual(mock_spark.sql.call_count, 2)

    def test_main_tolerates_spark_sql_failures(self) -> None:
        sql = (
            "CREATE OR REPLACE FUNCTION cgadev.audit_control.ops_usage_row_filter(event_user_id STRING)\n"
            "RETURNS BOOLEAN\n"
            "RETURN is_member('platform_ops') OR current_user() = event_user_id;\n"
            "ALTER TABLE cgadev.ops_observability.ops_usage_events\n"
            "SET ROW FILTER cgadev.audit_control.ops_usage_row_filter ON (user_id);\n"
        )
        with tempfile.TemporaryDirectory() as tmp:
            sql_path = Path(tmp) / "rls_column_masking.sql"
            sql_path.write_text(sql, encoding="utf-8")

            mock_spark = MagicMock()
            mock_spark.sql.side_effect = Exception("function already exists")
            result = rls_migration_job.main(mock_spark, sql_path=sql_path)

        self.assertEqual(result.statements_run, 2)
        self.assertEqual(result.statements_failed, 2)


if __name__ == "__main__":
    unittest.main()
