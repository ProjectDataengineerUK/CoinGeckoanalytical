-- Databricks Freshness and Quality Baseline
-- Purpose: executable serving checks for Gold assets before they are treated
-- as trusted current intelligence.

CREATE OR REPLACE VIEW cgadev.market_gold.gold_freshness_status AS
SELECT
  'gold_market_rankings' AS asset_name,
  'tier_a' AS freshness_tier,
  15 AS freshness_target_minutes,
  MAX(observed_at) AS latest_observed_at,
  CURRENT_TIMESTAMP() AS checked_at,
  timestampdiff(MINUTE, MAX(observed_at), CURRENT_TIMESTAMP()) AS freshness_age_minutes,
  CASE
    WHEN MAX(observed_at) IS NULL THEN 'missing'
    WHEN timestampdiff(MINUTE, MAX(observed_at), CURRENT_TIMESTAMP()) <= 15 THEN 'within_target'
    ELSE 'stale'
  END AS freshness_status
FROM cgadev.market_gold.gold_market_rankings

UNION ALL

SELECT
  'gold_top_movers' AS asset_name,
  'tier_a' AS freshness_tier,
  30 AS freshness_target_minutes,
  MAX(observed_at) AS latest_observed_at,
  CURRENT_TIMESTAMP() AS checked_at,
  timestampdiff(MINUTE, MAX(observed_at), CURRENT_TIMESTAMP()) AS freshness_age_minutes,
  CASE
    WHEN MAX(observed_at) IS NULL THEN 'missing'
    WHEN timestampdiff(MINUTE, MAX(observed_at), CURRENT_TIMESTAMP()) <= 30 THEN 'within_target'
    ELSE 'stale'
  END AS freshness_status
FROM cgadev.market_gold.gold_top_movers

UNION ALL

SELECT
  'gold_market_dominance' AS asset_name,
  'tier_a' AS freshness_tier,
  15 AS freshness_target_minutes,
  MAX(observed_at) AS latest_observed_at,
  CURRENT_TIMESTAMP() AS checked_at,
  timestampdiff(MINUTE, MAX(observed_at), CURRENT_TIMESTAMP()) AS freshness_age_minutes,
  CASE
    WHEN MAX(observed_at) IS NULL THEN 'missing'
    WHEN timestampdiff(MINUTE, MAX(observed_at), CURRENT_TIMESTAMP()) <= 15 THEN 'within_target'
    ELSE 'stale'
  END AS freshness_status
FROM cgadev.market_gold.gold_market_dominance

UNION ALL

SELECT
  'gold_cross_asset_comparison' AS asset_name,
  'tier_b' AS freshness_tier,
  60 AS freshness_target_minutes,
  MAX(observed_at) AS latest_observed_at,
  CURRENT_TIMESTAMP() AS checked_at,
  timestampdiff(MINUTE, MAX(observed_at), CURRENT_TIMESTAMP()) AS freshness_age_minutes,
  CASE
    WHEN MAX(observed_at) IS NULL THEN 'missing'
    WHEN timestampdiff(MINUTE, MAX(observed_at), CURRENT_TIMESTAMP()) <= 60 THEN 'within_target'
    ELSE 'stale'
  END AS freshness_status
FROM cgadev.market_gold.gold_cross_asset_comparison;

CREATE OR REPLACE VIEW cgadev.market_gold.gold_quality_status AS
SELECT
  'gold_market_rankings' AS asset_name,
  COUNT(*) AS row_count,
  SUM(CASE WHEN asset_id IS NULL OR observed_at IS NULL OR market_cap_rank IS NULL THEN 1 ELSE 0 END) AS critical_null_rows,
  COUNT(*) - COUNT(DISTINCT CONCAT_WS('|', COALESCE(asset_id, '__NULL__'), COALESCE(CAST(observed_at AS STRING), '__NULL__'))) AS duplicate_key_rows,
  SUM(CASE WHEN market_cap_usd < 0 OR price_usd < 0 OR volume_24h_usd < 0 OR circulating_supply < 0 THEN 1 ELSE 0 END) AS numeric_outlier_rows,
  CASE
    WHEN SUM(CASE WHEN asset_id IS NULL OR observed_at IS NULL OR market_cap_rank IS NULL THEN 1 ELSE 0 END) = 0
      AND COUNT(*) = COUNT(DISTINCT CONCAT_WS('|', COALESCE(asset_id, '__NULL__'), COALESCE(CAST(observed_at AS STRING), '__NULL__')))
      AND SUM(CASE WHEN market_cap_usd < 0 OR price_usd < 0 OR volume_24h_usd < 0 OR circulating_supply < 0 THEN 1 ELSE 0 END) = 0
    THEN 'pass'
    ELSE 'review'
  END AS quality_status
FROM cgadev.market_gold.gold_market_rankings

UNION ALL

SELECT
  'gold_top_movers' AS asset_name,
  COUNT(*) AS row_count,
  SUM(CASE WHEN asset_id IS NULL OR observed_at IS NULL OR window_id IS NULL THEN 1 ELSE 0 END) AS critical_null_rows,
  COUNT(*) - COUNT(DISTINCT CONCAT_WS('|', COALESCE(asset_id, '__NULL__'), COALESCE(window_id, '__NULL__'), COALESCE(CAST(observed_at AS STRING), '__NULL__'))) AS duplicate_key_rows,
  SUM(CASE WHEN ABS(price_change_pct_1h) > 500 OR ABS(price_change_pct_24h) > 500 OR ABS(price_change_pct_7d) > 500 THEN 1 ELSE 0 END) AS numeric_outlier_rows,
  CASE
    WHEN SUM(CASE WHEN asset_id IS NULL OR observed_at IS NULL OR window_id IS NULL THEN 1 ELSE 0 END) = 0
      AND COUNT(*) = COUNT(DISTINCT CONCAT_WS('|', COALESCE(asset_id, '__NULL__'), COALESCE(window_id, '__NULL__'), COALESCE(CAST(observed_at AS STRING), '__NULL__')))
      AND SUM(CASE WHEN ABS(price_change_pct_1h) > 500 OR ABS(price_change_pct_24h) > 500 OR ABS(price_change_pct_7d) > 500 THEN 1 ELSE 0 END) = 0
    THEN 'pass'
    ELSE 'review'
  END AS quality_status
FROM cgadev.market_gold.gold_top_movers

UNION ALL

SELECT
  'gold_market_dominance' AS asset_name,
  COUNT(*) AS row_count,
  SUM(CASE WHEN observed_at IS NULL OR dominance_group IS NULL THEN 1 ELSE 0 END) AS critical_null_rows,
  COUNT(*) - COUNT(DISTINCT CONCAT_WS('|', COALESCE(CAST(observed_at AS STRING), '__NULL__'), COALESCE(dominance_group, '__NULL__'))) AS duplicate_key_rows,
  SUM(CASE WHEN dominance_pct < 0 OR dominance_pct > 100 THEN 1 ELSE 0 END) AS numeric_outlier_rows,
  CASE
    WHEN SUM(CASE WHEN observed_at IS NULL OR dominance_group IS NULL THEN 1 ELSE 0 END) = 0
      AND COUNT(*) = COUNT(DISTINCT CONCAT_WS('|', COALESCE(CAST(observed_at AS STRING), '__NULL__'), COALESCE(dominance_group, '__NULL__')))
      AND SUM(CASE WHEN dominance_pct < 0 OR dominance_pct > 100 THEN 1 ELSE 0 END) = 0
    THEN 'pass'
    ELSE 'review'
  END AS quality_status
FROM cgadev.market_gold.gold_market_dominance

UNION ALL

SELECT
  'gold_cross_asset_comparison' AS asset_name,
  COUNT(*) AS row_count,
  SUM(CASE WHEN asset_id IS NULL OR observed_at IS NULL THEN 1 ELSE 0 END) AS critical_null_rows,
  COUNT(*) - COUNT(DISTINCT CONCAT_WS('|', COALESCE(asset_id, '__NULL__'), COALESCE(CAST(observed_at AS STRING), '__NULL__'), COALESCE(correlation_bucket, '__NULL__'))) AS duplicate_key_rows,
  SUM(CASE WHEN price_usd < 0 OR market_cap_usd < 0 OR volume_24h_usd < 0 THEN 1 ELSE 0 END) AS numeric_outlier_rows,
  CASE
    WHEN SUM(CASE WHEN asset_id IS NULL OR observed_at IS NULL THEN 1 ELSE 0 END) = 0
      AND COUNT(*) = COUNT(DISTINCT CONCAT_WS('|', COALESCE(asset_id, '__NULL__'), COALESCE(CAST(observed_at AS STRING), '__NULL__'), COALESCE(correlation_bucket, '__NULL__')))
      AND SUM(CASE WHEN price_usd < 0 OR market_cap_usd < 0 OR volume_24h_usd < 0 THEN 1 ELSE 0 END) = 0
    THEN 'pass'
    ELSE 'review'
  END AS quality_status
FROM cgadev.market_gold.gold_cross_asset_comparison;

CREATE OR REPLACE VIEW cgadev.market_gold.gold_serving_readiness AS
SELECT
  q.asset_name,
  f.freshness_tier,
  f.freshness_target_minutes,
  f.latest_observed_at,
  f.checked_at,
  f.freshness_age_minutes,
  f.freshness_status,
  q.row_count,
  q.critical_null_rows,
  q.duplicate_key_rows,
  q.numeric_outlier_rows,
  q.quality_status,
  CASE
    WHEN f.freshness_status = 'within_target' AND q.quality_status = 'pass' THEN 'serve'
    ELSE 'hold'
  END AS serving_status
FROM cgadev.market_gold.gold_quality_status q
JOIN cgadev.market_gold.gold_freshness_status f
  ON q.asset_name = f.asset_name;
