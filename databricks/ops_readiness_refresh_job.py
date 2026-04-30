from __future__ import annotations

import inspect
from pathlib import Path
from typing import Any


DEFAULT_SQL_FILES = (
    "bronze_silver_market_foundation.sql",
    "gold_market_views.sql",
    "freshness_quality_baseline.sql",
    "telemetry-observability.sql",
    "bundle_run_observability.sql",
    "sentinela_alert_observability.sql",
    "ops_readiness_dashboard.sql",
)


def load_sql_statements(path: str | Path) -> list[str]:
    sql_text = Path(path).read_text(encoding="utf-8")
    statements = [statement.strip() for statement in sql_text.split(";")]
    return [statement for statement in statements if statement]


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


def refresh_views(spark: Any, sql_files: tuple[str, ...] = DEFAULT_SQL_FILES, base_dir: str | Path | None = None) -> dict[str, Any]:
    root = resolve_base_dir(base_dir)
    executed_statements: list[str] = []
    executed_files: list[str] = []

    for sql_file in sql_files:
        sql_path = root / sql_file
        for statement in load_sql_statements(sql_path):
            spark.sql(statement)
            executed_statements.append(statement)
        executed_files.append(sql_file)

    return {
        "files": executed_files,
        "statements_executed": len(executed_statements),
    }


def main(spark: Any) -> dict[str, Any]:
    return refresh_views(spark)


if __name__ == "__main__":
    try:
        spark_session = spark  # type: ignore[name-defined]
    except NameError as exc:  # pragma: no cover - Databricks runtime entrypoint only
        raise RuntimeError("This job is meant to run inside Databricks with a Spark session.") from exc

    result = main(spark_session)
    print(result)
