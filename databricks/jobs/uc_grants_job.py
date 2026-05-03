from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


SQL_FILE = Path(__file__).resolve().parents[2] / "databricks/sql/migrations/unity_catalog_foundation.sql"


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
    path = sql_path or SQL_FILE
    sql_text = Path(path).read_text(encoding="utf-8")
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

    return GrantsResult(statements_run=statements_run, statements_failed=statements_failed)


if __name__ == "__main__":
    try:
        _spark = spark  # type: ignore[name-defined]
    except NameError as exc:  # pragma: no cover
        raise RuntimeError("This job is meant to run inside Databricks with a Spark session.") from exc

    result = main(_spark)
    print(json.dumps({"statements_run": result.statements_run, "statements_failed": result.statements_failed}))
