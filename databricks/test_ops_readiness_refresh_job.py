from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
import tempfile
import unittest
from unittest import mock


MODULE_PATH = Path(__file__).resolve().parent / "ops_readiness_refresh_job.py"
SPEC = importlib.util.spec_from_file_location("ops_readiness_refresh_job", MODULE_PATH)
ops_readiness_refresh_job = importlib.util.module_from_spec(SPEC)
assert SPEC is not None and SPEC.loader is not None
sys.modules[SPEC.name] = ops_readiness_refresh_job
SPEC.loader.exec_module(ops_readiness_refresh_job)


class OpsReadinessRefreshJobTests(unittest.TestCase):
    def test_load_sql_statements_splits_multiple_statements(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            sql_path = Path(temp_dir) / "refresh.sql"
            sql_path.write_text(
                "CREATE OR REPLACE VIEW a AS SELECT 1;\nCREATE OR REPLACE VIEW b AS SELECT 2;\n",
                encoding="utf-8",
            )

            statements = ops_readiness_refresh_job.load_sql_statements(sql_path)

        self.assertEqual(len(statements), 2)
        self.assertTrue(statements[0].startswith("CREATE OR REPLACE VIEW a"))
        self.assertTrue(statements[1].startswith("CREATE OR REPLACE VIEW b"))

    def test_refresh_views_reports_executed_files(self) -> None:
        class FakeSpark:
            def __init__(self) -> None:
                self.statements: list[str] = []

            def sql(self, statement: str) -> None:
                self.statements.append(statement)

        fake_spark = FakeSpark()
        result = ops_readiness_refresh_job.refresh_views(
            fake_spark,
            sql_files=("ops_readiness_dashboard.sql",),
            base_dir=Path(__file__).resolve().parent,
        )

        self.assertEqual(result["files"], ["ops_readiness_dashboard.sql"])
        self.assertGreater(result["statements_executed"], 0)
        self.assertGreater(len(fake_spark.statements), 0)

    def test_default_sql_file_order_includes_unity_catalog_first(self) -> None:
        self.assertEqual(
            ops_readiness_refresh_job.DEFAULT_SQL_FILES[0],
            "unity_catalog_runtime_foundation.sql",
        )

    def test_refresh_views_works_without_module___file__(self) -> None:
        class FakeSpark:
            def __init__(self) -> None:
                self.statements: list[str] = []

            def sql(self, statement: str) -> None:
                self.statements.append(statement)

        fake_spark = FakeSpark()
        original_file = ops_readiness_refresh_job.__dict__.pop("__file__", None)
        try:
            with mock.patch.object(
                ops_readiness_refresh_job.inspect,
                "getsourcefile",
                return_value=str(Path(__file__).resolve().parent / "ops_readiness_refresh_job.py"),
            ):
                result = ops_readiness_refresh_job.refresh_views(
                    fake_spark,
                    sql_files=("ops_readiness_dashboard.sql",),
                )
        finally:
            if original_file is not None:
                ops_readiness_refresh_job.__dict__["__file__"] = original_file

        self.assertEqual(result["files"], ["ops_readiness_dashboard.sql"])
        self.assertGreater(result["statements_executed"], 0)
        self.assertGreater(len(fake_spark.statements), 0)


if __name__ == "__main__":
    unittest.main()
