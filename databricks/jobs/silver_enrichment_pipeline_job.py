from __future__ import annotations

import json
from typing import Any

DEFAULT_BRONZE_CATALOG = "cgadev"

SILVER_ASSET_ENRICHED_SQL = """
WITH latest_snapshots AS (
  SELECT *,
    ROW_NUMBER() OVER (PARTITION BY asset_id ORDER BY ingested_at DESC) AS rn
  FROM cgadev.market_bronze.bronze_market_snapshots
),
latest_defi AS (
  SELECT *,
    ROW_NUMBER() OVER (PARTITION BY source_record_id ORDER BY ingested_at DESC) AS rn
  FROM cgadev.market_bronze.bronze_defillama_protocols
),
latest_github AS (
  SELECT *,
    ROW_NUMBER() OVER (PARTITION BY asset_id ORDER BY ingested_at DESC) AS rn
  FROM cgadev.market_bronze.bronze_github_activity
)
SELECT
  s.asset_id,
  s.symbol,
  s.name,
  s.market_cap_rank,
  s.price_usd,
  s.market_cap_usd,
  s.volume_24h_usd,
  s.ingested_at         AS snapshot_ingested_at,
  d.protocol_slug,
  d.category            AS defi_category,
  d.tvl_usd,
  d.fees_24h_usd,
  d.revenue_24h_usd,
  d.mcap_tvl_ratio,
  g.repo_full_name,
  g.stars,
  g.forks,
  g.open_issues,
  g.contributors_count,
  g.commits_30d,
  g.commits_90d,
  g.repo_age_days,
  CAST(
    LEAST(100, COALESCE(g.commits_30d, 0) * 2
              + COALESCE(g.stars, 0) / 1000.0
              + COALESCE(g.contributors_count, 0) * 5)
  AS INT) AS dev_activity_score,
  CURRENT_TIMESTAMP()   AS enriched_at
FROM (SELECT * FROM latest_snapshots WHERE rn = 1) s
LEFT JOIN (SELECT * FROM latest_defi WHERE rn = 1) d
  ON LOWER(s.asset_id) = LOWER(d.source_record_id)
LEFT JOIN (SELECT * FROM latest_github WHERE rn = 1) g
  ON LOWER(s.asset_id) = LOWER(g.asset_id)
"""

SILVER_MACRO_CONTEXT_SQL = """
WITH latest_obs AS (
  SELECT *,
    ROW_NUMBER() OVER (PARTITION BY series_id ORDER BY observation_date DESC) AS rn_latest
  FROM cgadev.market_bronze.bronze_fred_macro
),
lag_obs AS (
  SELECT *,
    ROW_NUMBER() OVER (PARTITION BY series_id ORDER BY observation_date DESC) AS rn_lag
  FROM cgadev.market_bronze.bronze_fred_macro
  WHERE observation_date <= DATE_SUB(CURRENT_DATE(), 30)
)
SELECT
  l.series_id,
  l.series_name,
  l.observation_date AS latest_date,
  l.value            AS current_value,
  p.value            AS value_30d_ago,
  CASE
    WHEN p.value IS NOT NULL AND p.value != 0
    THEN ROUND((l.value - p.value) / ABS(p.value) * 100, 4)
    ELSE NULL
  END AS change_30d_pct,
  CURRENT_TIMESTAMP() AS enriched_at
FROM (SELECT * FROM latest_obs WHERE rn_latest = 1) l
LEFT JOIN (SELECT * FROM lag_obs WHERE rn_lag = 1) p
  ON l.series_id = p.series_id
"""


def run_silver_enrichment(spark: Any) -> dict[str, Any]:
    asset_enriched_table = "cgadev.market_silver.silver_asset_enriched"
    macro_context_table = "cgadev.market_silver.silver_macro_context"

    asset_df = spark.sql(SILVER_ASSET_ENRICHED_SQL)
    asset_df.write.mode("overwrite").format("delta").option("overwriteSchema", "true").saveAsTable(asset_enriched_table)
    asset_rows = asset_df.count()

    try:
        macro_df = spark.sql(SILVER_MACRO_CONTEXT_SQL)
        macro_df.write.mode("overwrite").format("delta").option("overwriteSchema", "true").saveAsTable(macro_context_table)
        macro_rows = macro_df.count()
    except Exception as exc:
        print(f"WARN: silver_macro_context skipped (bronze_fred_macro may be empty): {exc}")
        macro_rows = 0

    return {
        "asset_enriched_rows": asset_rows,
        "macro_context_rows": macro_rows,
        "asset_enriched_table": asset_enriched_table,
        "macro_context_table": macro_context_table,
    }


def main(spark: Any) -> dict[str, Any]:
    return run_silver_enrichment(spark)


if __name__ == "__main__":
    try:
        spark_session = spark  # type: ignore[name-defined]
    except NameError as exc:
        raise RuntimeError("This job is meant to run inside Databricks with a Spark session.") from exc

    result = main(spark_session)
    print(json.dumps(result))
