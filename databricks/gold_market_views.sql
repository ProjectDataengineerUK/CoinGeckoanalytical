-- Databricks Gold Market Views Baseline
-- Purpose: executable starter for the Gold layer used by dashboards and Genie.

CREATE OR REPLACE VIEW gold_market_rankings AS
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
  market_cap_rank
FROM bronze_market_snapshots
WHERE asset_id IS NOT NULL;

CREATE OR REPLACE VIEW gold_top_movers AS
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
  market_cap_usd
FROM silver_market_changes
WHERE asset_id IS NOT NULL;

CREATE OR REPLACE VIEW gold_market_dominance AS
SELECT
  observed_at,
  dominance_group,
  market_cap_usd,
  dominance_pct
FROM silver_market_dominance
WHERE dominance_group IS NOT NULL;

CREATE OR REPLACE VIEW gold_cross_asset_comparison AS
SELECT
  asset_id,
  symbol,
  observed_at,
  price_usd,
  market_cap_usd,
  volume_24h_usd,
  price_change_pct_24h,
  price_change_pct_7d,
  correlation_bucket
FROM silver_cross_asset_comparison
WHERE asset_id IS NOT NULL;
