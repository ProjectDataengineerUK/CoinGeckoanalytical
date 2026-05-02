from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path

_JOB_PATH = Path(__file__).resolve().parent.parent / "jobs" / "silver_enrichment_migration_job.py"
spec = importlib.util.spec_from_file_location("silver_enrichment_migration_job", _JOB_PATH)
silver_enrichment_migration_job = importlib.util.module_from_spec(spec)  # type: ignore[arg-type]
spec.loader.exec_module(silver_enrichment_migration_job)  # type: ignore[union-attr]


class SilverEnrichmentMigrationJobTests(unittest.TestCase):
    def test_run_migration_executes_all_statements(self):
        executed = []

        class FakeSpark:
            def sql(self, statement: str) -> None:
                executed.append(statement)

        base_dir = Path(__file__).resolve().parent.parent / "jobs"
        result = silver_enrichment_migration_job.run_migration(FakeSpark(), base_dir=base_dir)
        self.assertGreater(result["statements_executed"], 0)
        self.assertEqual(result["statements_executed"], len(executed))

    def test_load_sql_statements_parses_two_tables(self):
        stmts = silver_enrichment_migration_job.load_sql_statements(
            Path(__file__).resolve().parent.parent / "sql/migrations/silver_enrichment_migration.sql"
        )
        self.assertEqual(len(stmts), 2)


if __name__ == "__main__":
    unittest.main()
