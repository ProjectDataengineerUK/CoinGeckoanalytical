from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


# SQL embedded inline — __file__ is not available on Databricks Serverless Spark tasks
_UC_FOUNDATION_SQL = """
CREATE CATALOG IF NOT EXISTS cgadev;
CREATE CATALOG IF NOT EXISTS cgastaging;
CREATE CATALOG IF NOT EXISTS cgaprod;

CREATE SCHEMA IF NOT EXISTS cgadev.market_bronze;
CREATE SCHEMA IF NOT EXISTS cgadev.market_silver;
CREATE SCHEMA IF NOT EXISTS cgadev.market_gold;
CREATE SCHEMA IF NOT EXISTS cgadev.ai_serving;
CREATE SCHEMA IF NOT EXISTS cgadev.ops_observability;
CREATE SCHEMA IF NOT EXISTS cgadev.audit_control;
CREATE SCHEMA IF NOT EXISTS cgadev.reference_data;

CREATE SCHEMA IF NOT EXISTS cgastaging.market_bronze;
CREATE SCHEMA IF NOT EXISTS cgastaging.market_silver;
CREATE SCHEMA IF NOT EXISTS cgastaging.market_gold;
CREATE SCHEMA IF NOT EXISTS cgastaging.ai_serving;
CREATE SCHEMA IF NOT EXISTS cgastaging.ops_observability;
CREATE SCHEMA IF NOT EXISTS cgastaging.audit_control;
CREATE SCHEMA IF NOT EXISTS cgastaging.reference_data;

CREATE SCHEMA IF NOT EXISTS cgaprod.market_bronze;
CREATE SCHEMA IF NOT EXISTS cgaprod.market_silver;
CREATE SCHEMA IF NOT EXISTS cgaprod.market_gold;
CREATE SCHEMA IF NOT EXISTS cgaprod.ai_serving;
CREATE SCHEMA IF NOT EXISTS cgaprod.ops_observability;
CREATE SCHEMA IF NOT EXISTS cgaprod.audit_control;
CREATE SCHEMA IF NOT EXISTS cgaprod.reference_data;

ALTER SCHEMA cgadev.market_bronze OWNER TO `data_platform`;
ALTER SCHEMA cgadev.market_silver OWNER TO `data_platform`;
ALTER SCHEMA cgadev.market_gold OWNER TO `data_platform`;
ALTER SCHEMA cgadev.reference_data OWNER TO `data_platform`;
ALTER SCHEMA cgadev.ai_serving OWNER TO `product_analytics`;
ALTER SCHEMA cgadev.ops_observability OWNER TO `platform_ops`;
ALTER SCHEMA cgadev.audit_control OWNER TO `governance_admin`;

GRANT USE CATALOG ON CATALOG cgadev TO `product_backend`, `platform_ops`, `governance_admin`;
GRANT USE SCHEMA ON SCHEMA cgadev.market_gold TO `product_backend`, `platform_ops`, `governance_admin`;
GRANT SELECT ON FUTURE TABLES IN SCHEMA cgadev.market_gold TO `product_backend`;
GRANT SELECT ON FUTURE VIEWS IN SCHEMA cgadev.market_gold TO `product_backend`;
GRANT USE SCHEMA ON SCHEMA cgadev.ai_serving TO `product_backend`, `product_analytics`;
GRANT SELECT ON FUTURE VIEWS IN SCHEMA cgadev.ai_serving TO `product_backend`, `product_analytics`;
GRANT USE SCHEMA ON SCHEMA cgadev.ops_observability TO `platform_ops`, `governance_admin`;
GRANT SELECT ON FUTURE TABLES IN SCHEMA cgadev.ops_observability TO `platform_ops`, `governance_admin`;
GRANT SELECT ON FUTURE VIEWS IN SCHEMA cgadev.ops_observability TO `platform_ops`, `governance_admin`;
GRANT USE SCHEMA ON SCHEMA cgadev.audit_control TO `governance_admin`;
GRANT SELECT ON FUTURE TABLES IN SCHEMA cgadev.audit_control TO `governance_admin`;
GRANT SELECT ON FUTURE VIEWS IN SCHEMA cgadev.audit_control TO `governance_admin`;
GRANT USE SCHEMA ON SCHEMA cgadev.market_bronze TO `svc_market_ingestion`;
GRANT CREATE TABLE, MODIFY ON SCHEMA cgadev.market_bronze TO `svc_market_ingestion`;
GRANT USE SCHEMA ON SCHEMA cgadev.market_silver TO `svc_market_pipeline`;
GRANT CREATE TABLE, CREATE VIEW, MODIFY ON SCHEMA cgadev.market_silver TO `svc_market_pipeline`;
GRANT USE SCHEMA ON SCHEMA cgadev.market_gold TO `svc_market_pipeline`;
GRANT CREATE TABLE, CREATE VIEW, MODIFY ON SCHEMA cgadev.market_gold TO `svc_market_pipeline`;
GRANT USE SCHEMA ON SCHEMA cgadev.ops_observability TO `svc_ops_pipeline`;
GRANT CREATE TABLE, CREATE VIEW, MODIFY ON SCHEMA cgadev.ops_observability TO `svc_ops_pipeline`;
GRANT USE SCHEMA ON SCHEMA cgadev.audit_control TO `svc_audit_pipeline`;
GRANT CREATE TABLE, CREATE VIEW, MODIFY ON SCHEMA cgadev.audit_control TO `svc_audit_pipeline`
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

    return GrantsResult(statements_run=statements_run, statements_failed=statements_failed)


if __name__ == "__main__":
    try:
        _spark = spark  # type: ignore[name-defined]
    except NameError as exc:  # pragma: no cover
        raise RuntimeError("This job is meant to run inside Databricks with a Spark session.") from exc

    result = main(_spark)
    print(json.dumps({"statements_run": result.statements_run, "statements_failed": result.statements_failed}))
