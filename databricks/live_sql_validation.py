from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any


VALIDATION_QUERIES = {
    "bronze_rows": "SELECT COUNT(*) AS bronze_rows FROM cgadev.market_bronze.bronze_market_snapshots",
    "silver_snapshot_rows": "SELECT COUNT(*) AS silver_snapshot_rows FROM cgadev.market_silver.silver_market_snapshots",
    "silver_changes_rows": "SELECT COUNT(*) AS silver_changes_rows FROM cgadev.market_silver.silver_market_changes",
    "silver_dominance_rows": "SELECT COUNT(*) AS silver_dominance_rows FROM cgadev.market_silver.silver_market_dominance",
    "silver_comparison_rows": "SELECT COUNT(*) AS silver_comparison_rows FROM cgadev.market_silver.silver_cross_asset_comparison",
    "gold_rankings_rows": "SELECT COUNT(*) AS gold_rankings_rows FROM cgadev.market_gold.gold_market_rankings",
    "gold_movers_rows": "SELECT COUNT(*) AS gold_movers_rows FROM cgadev.market_gold.gold_top_movers",
    "gold_dominance_rows": "SELECT COUNT(*) AS gold_dominance_rows FROM cgadev.market_gold.gold_market_dominance",
    "gold_comparison_rows": "SELECT COUNT(*) AS gold_comparison_rows FROM cgadev.market_gold.gold_cross_asset_comparison",
    "mv_rankings_rows": "SELECT COUNT(*) AS mv_rankings_rows FROM cgadev.ai_serving.mv_market_rankings",
    "mv_movers_rows": "SELECT COUNT(*) AS mv_movers_rows FROM cgadev.ai_serving.mv_top_movers",
    "mv_dominance_rows": "SELECT COUNT(*) AS mv_dominance_rows FROM cgadev.ai_serving.mv_market_dominance",
    "mv_compare_rows": "SELECT COUNT(*) AS mv_compare_rows FROM cgadev.ai_serving.mv_cross_asset_compare",
}


def build_statement_request(statement: str, warehouse_id: str) -> dict[str, Any]:
    return {
        "statement": statement,
        "warehouse_id": warehouse_id,
        "wait_timeout": "50s",
        "disposition": "INLINE",
        "format": "JSON_ARRAY",
    }


def execute_statement(
    host: str,
    token: str,
    warehouse_id: str,
    statement: str,
) -> dict[str, Any]:
    payload = build_statement_request(statement, warehouse_id)
    request = urllib.request.Request(
        f"{host.rstrip('/')}/api/2.0/sql/statements/",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(request) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:  # pragma: no cover - networked path
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Statement execution failed: {exc.code} {body}") from exc


def summarize_statement_response(response: dict[str, Any]) -> dict[str, Any]:
    status = response.get("status", {})
    result = response.get("result", {})
    data_array = result.get("data_array") or []
    first_row = data_array[0] if data_array else []
    first_value = first_row[0] if first_row else None
    return {
        "statement_id": response.get("statement_id"),
        "state": status.get("state"),
        "row_count_value": first_value,
        "manifest": result.get("manifest"),
    }


def run_live_validation(
    host: str,
    token: str,
    warehouse_id: str,
) -> dict[str, Any]:
    summary: dict[str, Any] = {}
    for key, statement in VALIDATION_QUERIES.items():
        response = execute_statement(host, token, warehouse_id, statement)
        summary[key] = summarize_statement_response(response)
    return summary


def write_results(path: str | Path, results: dict[str, Any]) -> Path:
    target_path = Path(path)
    target_path.parent.mkdir(parents=True, exist_ok=True)
    target_path.write_text(json.dumps(results, indent=2, sort_keys=True), encoding="utf-8")
    return target_path


def main() -> int:
    host = os.environ.get("DATABRICKS_HOST")
    token = os.environ.get("DATABRICKS_TOKEN")
    warehouse_id = os.environ.get("DATABRICKS_SQL_WAREHOUSE_ID")
    output_path = os.environ.get("LIVE_SQL_VALIDATION_OUTPUT", "databricks/live_sql_validation_results.json")

    missing = [
        name
        for name, value in (
            ("DATABRICKS_HOST", host),
            ("DATABRICKS_TOKEN", token),
            ("DATABRICKS_SQL_WAREHOUSE_ID", warehouse_id),
        )
        if not value
    ]
    if missing:
        print(f"Skipping live SQL validation; missing: {', '.join(missing)}")
        return 0

    results = run_live_validation(host, token, warehouse_id)
    written = write_results(output_path, results)
    print(f"Live SQL validation results written to {written}")
    print(json.dumps(results, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
