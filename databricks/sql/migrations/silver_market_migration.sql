-- Silver Market Migration
-- Purpose: provision Silver Delta tables in cgadev.market_silver.
-- The Python migration job drops any legacy views with conflicting names
-- before these statements run. Uses CREATE TABLE IF NOT EXISTS to preserve
-- existing data on subsequent runs.

CREATE SCHEMA IF NOT EXISTS cgadev.market_silver;

CREATE TABLE IF NOT EXISTS cgadev.market_silver.silver_market_changes (
  asset_id STRING,
  symbol STRING,
  name STRING,
  observed_at TIMESTAMP,
  window_id STRING,
  price_change_pct_1h DECIMAL(38, 8),
  price_change_pct_24h DECIMAL(38, 8),
  price_change_pct_7d DECIMAL(38, 8),
  volume_24h_usd DECIMAL(38, 8),
  market_cap_usd DECIMAL(38, 8)
) USING DELTA;

CREATE TABLE IF NOT EXISTS cgadev.market_silver.silver_market_dominance (
  observed_at TIMESTAMP,
  dominance_group STRING,
  market_cap_usd DECIMAL(38, 8),
  dominance_pct DECIMAL(38, 8)
) USING DELTA;

CREATE TABLE IF NOT EXISTS cgadev.market_silver.silver_cross_asset_comparison (
  asset_id STRING,
  symbol STRING,
  observed_at TIMESTAMP,
  price_usd DECIMAL(38, 8),
  market_cap_usd DECIMAL(38, 8),
  volume_24h_usd DECIMAL(38, 8),
  price_change_pct_24h DECIMAL(38, 8),
  price_change_pct_7d DECIMAL(38, 8),
  correlation_bucket STRING
) USING DELTA;
