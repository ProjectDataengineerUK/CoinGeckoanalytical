from __future__ import annotations

import inspect
from pathlib import Path
from typing import Any


DEFAULT_SQL_FILE = "bronze_market_table_migration.sql"


def _has_executable_sql(statement: str) -> bool:
    for line in statement.splitlines():
        stripped = line.strip()
        if stripped and not stripped.startswith("--"):
            return True
    return False


def load_sql_statements(path: str | Path) -> list[str]:
    sql_text = Path(path).read_text(encoding="utf-8")
    statements = [s.strip() for s in sql_text.split(";")]
    return [s for s in statements if _has_executable_sql(s)]


def resolve_base_dir(base_dir: str | Path | None = None) -> Path:
    if base_dir is not None:
        return Path(base_dir)

    module_file = globals().get("__file__")
    if module_file:
        return Path(module_file).resolve().parent

    source_file = inspect.getsourcefile(resolve_base_dir)
    if source_file:
        return Path(source_file).resolve().parent

    return Path.cwd()


def run_migration(spark: Any, sql_file: str = DEFAULT_SQL_FILE, base_dir: str | Path | None = None) -> dict[str, Any]:
    root = resolve_base_dir(base_dir)
    sql_path = root / sql_file
    executed_statements: list[str] = []

    for statement in load_sql_statements(sql_path):
        spark.sql(statement)
        executed_statements.append(statement)

    return {
        "file": sql_file,
        "statements_executed": len(executed_statements),
    }


def main(spark: Any) -> dict[str, Any]:
    return run_migration(spark)


if __name__ == "__main__":
    try:
        spark_session = spark  # type: ignore[name-defined]
    except NameError as exc:  # pragma: no cover - Databricks runtime entrypoint only
        raise RuntimeError("This job is meant to run inside Databricks with a Spark session.") from exc

    result = main(spark_session)
    print(result)
