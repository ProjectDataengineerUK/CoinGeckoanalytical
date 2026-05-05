from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


# SQL embedded inline — __file__ is not available on Databricks Serverless Spark tasks.
# Scope: cgadev catalog only — the CI service principal can execute these without
# metastore-admin rights.  Staging/prod catalog creation and group-based grants live in
# databricks/sql/migrations/unity_catalog_grants_full.sql and must be applied manually
# by a metastore admin once those catalogs and workspace groups are provisioned.
_UC_FOUNDATION_SQL = """
CREATE CATALOG IF NOT EXISTS cgadev;

CREATE SCHEMA IF NOT EXISTS cgadev.market_bronze;
CREATE SCHEMA IF NOT EXISTS cgadev.market_silver;
CREATE SCHEMA IF NOT EXISTS cgadev.market_gold;
CREATE SCHEMA IF NOT EXISTS cgadev.ai_serving;
CREATE SCHEMA IF NOT EXISTS cgadev.ops_observability;
CREATE SCHEMA IF NOT EXISTS cgadev.audit_control;
CREATE SCHEMA IF NOT EXISTS cgadev.reference_data;
"""


@dataclass(frozen=True)
class GrantsResult:
    statements_run: int
    statements_failed: int


def _has_executable_sql(statement: str) -> bool:
    for line in statement.splitlines():
        stripped = line.strip()
        if stripped and not stripped.startswith("--"):
            return True
    return False


def parse_sql_statements(sql_text: str) -> list[str]:
    """Split a SQL string on semicolons; skip blank and comment-only blocks."""
    parts = [s.strip() for s in sql_text.split(";")]
    return [s for s in parts if _has_executable_sql(s)]


def main(spark: Any, sql_path: Path | None = None) -> GrantsResult:
    if sql_path is not None:
        sql_text = Path(sql_path).read_text(encoding="utf-8")
    else:
        sql_text = _UC_FOUNDATION_SQL
    statements = parse_sql_statements(sql_text)

    statements_run = 0
    statements_failed = 0

    for stmt in statements:
        statements_run += 1
        try:
            spark.sql(stmt)
        except Exception as e:  # noqa: BLE001
            print(f"WARN: {stmt[:60]}: {e}")
            statements_failed += 1

    if statements_failed > 0:
        raise RuntimeError(
            f"UC grants: {statements_failed}/{statements_run} statements failed — "
            "governance grants are incomplete. Check WARN lines above for details."
        )
    return GrantsResult(statements_run=statements_run, statements_failed=statements_failed)


if __name__ == "__main__":
    try:
        _spark = spark  # type: ignore[name-defined]
    except NameError as exc:  # pragma: no cover
        raise RuntimeError("This job is meant to run inside Databricks with a Spark session.") from exc

    result = main(_spark)
    print(json.dumps({"statements_run": result.statements_run, "statements_failed": result.statements_failed}))
