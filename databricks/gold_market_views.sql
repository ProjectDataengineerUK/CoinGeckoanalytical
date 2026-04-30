-- Databricks Gold Market Views Baseline
-- Purpose: concrete starter for the Gold layer used by dashboards, AI/BI Genie,
-- and governed analytical serving.

CREATE OR REPLACE VIEW gold_market_rankings AS
WITH ranked_source AS (
  SELECT
    asset_id,
    symbol,
    COALESCE(name, 'unmapped') AS name,
    COALESCE(category, 'unclassified') AS category,
    CAST(observed_at AS TIMESTAMP) AS observed_at,
    market_cap_usd,
    price_usd,
    volume_24h_usd,
    circulating_supply,
    market_cap_rank,
    ROW_NUMBER() OVER (
      PARTITION BY asset_id, CAST(observed_at AS TIMESTAMP)
      ORDER BY market_cap_rank ASC, volume_24h_usd DESC, symbol ASC
    ) AS source_row_number
  FROM bronze_market_snapshots
  WHERE asset_id IS NOT NULL
    AND observed_at IS NOT NULL
    AND market_cap_rank IS NOT NULL
)
SELECT
  asset_id,
  symbol,
  name,
  category,
  observed_at,
  market_cap_usd,
  price_usd,
  volume_24h_usd,
  circulating_supply,
  market_cap_rank,
  'tier_a' AS freshness_tier,
  15 AS freshness_target_minutes,
  'bronze_market_snapshots' AS lineage_source,
  CASE
    WHEN market_cap_usd >= 0
      AND price_usd >= 0
      AND volume_24h_usd >= 0
      AND circulating_supply >= 0
    THEN 'pass'
    ELSE 'review'
  END AS quality_status
FROM ranked_source
WHERE source_row_number = 1;

CREATE OR REPLACE VIEW gold_top_movers AS
WITH ranked_source AS (
  SELECT
    asset_id,
    symbol,
    COALESCE(name, 'unmapped') AS name,
    CAST(observed_at AS TIMESTAMP) AS observed_at,
    window_id,
    price_change_pct_1h,
    price_change_pct_24h,
    price_change_pct_7d,
    volume_24h_usd,
    market_cap_usd,
    CASE
      WHEN price_change_pct_24h > 0 THEN 'positive'
      WHEN price_change_pct_24h < 0 THEN 'negative'
      ELSE 'flat'
    END AS move_direction_24h,
    CASE
      WHEN ABS(price_change_pct_24h) >= 20 THEN 'high'
      WHEN ABS(price_change_pct_24h) >= 5 THEN 'medium'
      ELSE 'low'
    END AS move_band_24h,
    ROW_NUMBER() OVER (
      PARTITION BY asset_id, window_id, CAST(observed_at AS TIMESTAMP)
      ORDER BY ABS(price_change_pct_24h) DESC, volume_24h_usd DESC, symbol ASC
    ) AS source_row_number
  FROM silver_market_changes
  WHERE asset_id IS NOT NULL
    AND window_id IS NOT NULL
    AND observed_at IS NOT NULL
)
SELECT
  asset_id,
  symbol,
  name,
  observed_at,
  window_id,
  price_change_pct_1h,
  price_change_pct_24h,
  price_change_pct_7d,
  volume_24h_usd,
  market_cap_usd,
  move_direction_24h,
  move_band_24h,
  'tier_a' AS freshness_tier,
  30 AS freshness_target_minutes,
  'silver_market_changes' AS lineage_source,
  CASE
    WHEN ABS(price_change_pct_1h) <= 500
      AND ABS(price_change_pct_24h) <= 500
      AND ABS(price_change_pct_7d) <= 500
    THEN 'pass'
    ELSE 'review'
  END AS quality_status
FROM ranked_source
WHERE source_row_number = 1;

CREATE OR REPLACE VIEW gold_market_dominance AS
WITH ranked_source AS (
  SELECT
    CAST(observed_at AS TIMESTAMP) AS observed_at,
    dominance_group,
    market_cap_usd,
    dominance_pct,
    CASE
      WHEN dominance_pct >= 50 THEN 'macro'
      WHEN dominance_pct >= 20 THEN 'major'
      ELSE 'long_tail'
    END AS dominance_band,
    ROW_NUMBER() OVER (
      PARTITION BY CAST(observed_at AS TIMESTAMP), dominance_group
      ORDER BY dominance_pct DESC, market_cap_usd DESC
    ) AS source_row_number
  FROM silver_market_dominance
  WHERE observed_at IS NOT NULL
    AND dominance_group IS NOT NULL
)
SELECT
  observed_at,
  dominance_group,
  market_cap_usd,
  dominance_pct,
  dominance_band,
  'tier_a' AS freshness_tier,
  15 AS freshness_target_minutes,
  'silver_market_dominance' AS lineage_source,
  CASE
    WHEN dominance_pct BETWEEN 0 AND 100 THEN 'pass'
    ELSE 'review'
  END AS quality_status
FROM ranked_source
WHERE source_row_number = 1;

CREATE OR REPLACE VIEW gold_cross_asset_comparison AS
WITH ranked_source AS (
  SELECT
    asset_id,
    symbol,
    CAST(observed_at AS TIMESTAMP) AS observed_at,
    price_usd,
    market_cap_usd,
    volume_24h_usd,
    price_change_pct_24h,
    price_change_pct_7d,
    COALESCE(correlation_bucket, 'general') AS correlation_bucket,
    ROW_NUMBER() OVER (
      PARTITION BY asset_id, CAST(observed_at AS TIMESTAMP), COALESCE(correlation_bucket, 'general')
      ORDER BY volume_24h_usd DESC, price_usd DESC, symbol ASC
    ) AS source_row_number
  FROM silver_cross_asset_comparison
  WHERE asset_id IS NOT NULL
    AND observed_at IS NOT NULL
)
SELECT
  asset_id,
  symbol,
  observed_at,
  price_usd,
  market_cap_usd,
  volume_24h_usd,
  price_change_pct_24h,
  price_change_pct_7d,
  correlation_bucket,
  CASE
    WHEN price_change_pct_24h > 0 THEN 'positive'
    WHEN price_change_pct_24h < 0 THEN 'negative'
    ELSE 'flat'
  END AS price_change_direction_24h,
  'tier_b' AS freshness_tier,
  60 AS freshness_target_minutes,
  'silver_cross_asset_comparison' AS lineage_source,
  CASE
    WHEN price_usd >= 0
      AND market_cap_usd >= 0
      AND volume_24h_usd >= 0
    THEN 'pass'
    ELSE 'review'
  END AS quality_status
FROM ranked_source
WHERE source_row_number = 1;
