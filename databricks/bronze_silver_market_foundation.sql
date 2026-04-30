-- Databricks Bronze/Silver Market Foundation
-- Purpose: materialize the first executable Bronze and Silver contract
-- baseline required by WS1 / Slice 1 and consumed by the Gold market views.

CREATE OR REPLACE TABLE bronze_market_snapshots (
  source_system STRING,
  source_record_id STRING,
  asset_id STRING,
  symbol STRING,
  name STRING,
  category STRING,
  observed_at TIMESTAMP,
  ingested_at TIMESTAMP,
  market_cap_usd DECIMAL(38, 8),
  price_usd DECIMAL(38, 8),
  volume_24h_usd DECIMAL(38, 8),
  circulating_supply DECIMAL(38, 8),
  market_cap_rank INT,
  payload_version STRING
);

CREATE OR REPLACE VIEW silver_market_snapshots AS
WITH latest_bronze AS (
  SELECT
    source_system,
    source_record_id,
    asset_id,
    UPPER(symbol) AS symbol,
    name,
    category,
    CAST(observed_at AS TIMESTAMP) AS observed_at,
    CAST(ingested_at AS TIMESTAMP) AS ingested_at,
    market_cap_usd,
    price_usd,
    volume_24h_usd,
    circulating_supply,
    market_cap_rank,
    payload_version,
    ROW_NUMBER() OVER (
      PARTITION BY asset_id, CAST(observed_at AS TIMESTAMP)
      ORDER BY CAST(ingested_at AS TIMESTAMP) DESC, source_record_id DESC
    ) AS source_row_number
  FROM bronze_market_snapshots
  WHERE asset_id IS NOT NULL
    AND observed_at IS NOT NULL
)
SELECT
  source_system,
  source_record_id,
  asset_id,
  symbol,
  COALESCE(name, 'unmapped') AS name,
  COALESCE(category, 'unclassified') AS category,
  observed_at,
  ingested_at,
  market_cap_usd,
  price_usd,
  volume_24h_usd,
  circulating_supply,
  market_cap_rank,
  payload_version
FROM latest_bronze
WHERE source_row_number = 1;

CREATE OR REPLACE VIEW silver_market_changes AS
WITH current_snapshots AS (
  SELECT
    asset_id,
    symbol,
    name,
    observed_at,
    market_cap_usd,
    price_usd,
    volume_24h_usd,
    LAG(price_usd, 1) OVER (
      PARTITION BY asset_id
      ORDER BY observed_at
    ) AS prev_price_1h_proxy,
    LAG(price_usd, 24) OVER (
      PARTITION BY asset_id
      ORDER BY observed_at
    ) AS prev_price_24h_proxy,
    LAG(price_usd, 24 * 7) OVER (
      PARTITION BY asset_id
      ORDER BY observed_at
    ) AS prev_price_7d_proxy
  FROM silver_market_snapshots
)
SELECT
  asset_id,
  symbol,
  name,
  observed_at,
  'rolling_standard' AS window_id,
  CASE
    WHEN prev_price_1h_proxy IS NULL OR prev_price_1h_proxy = 0 THEN NULL
    ELSE ((price_usd - prev_price_1h_proxy) / prev_price_1h_proxy) * 100
  END AS price_change_pct_1h,
  CASE
    WHEN prev_price_24h_proxy IS NULL OR prev_price_24h_proxy = 0 THEN NULL
    ELSE ((price_usd - prev_price_24h_proxy) / prev_price_24h_proxy) * 100
  END AS price_change_pct_24h,
  CASE
    WHEN prev_price_7d_proxy IS NULL OR prev_price_7d_proxy = 0 THEN NULL
    ELSE ((price_usd - prev_price_7d_proxy) / prev_price_7d_proxy) * 100
  END AS price_change_pct_7d,
  volume_24h_usd,
  market_cap_usd
FROM current_snapshots;

CREATE OR REPLACE VIEW silver_market_dominance AS
WITH dominance_base AS (
  SELECT
    observed_at,
    asset_id,
    symbol,
    market_cap_usd,
    SUM(market_cap_usd) OVER (PARTITION BY observed_at) AS total_market_cap_usd
  FROM silver_market_snapshots
  WHERE observed_at IS NOT NULL
    AND market_cap_usd IS NOT NULL
    AND market_cap_usd >= 0
)
SELECT
  observed_at,
  CASE
    WHEN symbol = 'BTC' THEN 'btc'
    WHEN symbol = 'ETH' THEN 'eth'
    WHEN symbol IN ('USDT', 'USDC', 'DAI', 'FDUSD', 'TUSD') THEN 'stablecoins'
    ELSE 'long_tail'
  END AS dominance_group,
  SUM(market_cap_usd) AS market_cap_usd,
  CASE
    WHEN MAX(total_market_cap_usd) = 0 THEN NULL
    ELSE (SUM(market_cap_usd) / MAX(total_market_cap_usd)) * 100
  END AS dominance_pct
FROM dominance_base
GROUP BY
  observed_at,
  CASE
    WHEN symbol = 'BTC' THEN 'btc'
    WHEN symbol = 'ETH' THEN 'eth'
    WHEN symbol IN ('USDT', 'USDC', 'DAI', 'FDUSD', 'TUSD') THEN 'stablecoins'
    ELSE 'long_tail'
  END;

CREATE OR REPLACE VIEW silver_cross_asset_comparison AS
SELECT
  asset_id,
  symbol,
  observed_at,
  price_usd,
  market_cap_usd,
  volume_24h_usd,
  CASE
    WHEN market_cap_rank <= 10 THEN 'large_cap'
    WHEN market_cap_rank <= 50 THEN 'mid_cap'
    ELSE 'broad_market'
  END AS correlation_bucket,
  CASE
    WHEN LAG(price_usd, 24) OVER (PARTITION BY asset_id ORDER BY observed_at) IS NULL
      OR LAG(price_usd, 24) OVER (PARTITION BY asset_id ORDER BY observed_at) = 0
    THEN NULL
    ELSE (
      (price_usd - LAG(price_usd, 24) OVER (PARTITION BY asset_id ORDER BY observed_at))
      / LAG(price_usd, 24) OVER (PARTITION BY asset_id ORDER BY observed_at)
    ) * 100
  END AS price_change_pct_24h,
  CASE
    WHEN LAG(price_usd, 24 * 7) OVER (PARTITION BY asset_id ORDER BY observed_at) IS NULL
      OR LAG(price_usd, 24 * 7) OVER (PARTITION BY asset_id ORDER BY observed_at) = 0
    THEN NULL
    ELSE (
      (price_usd - LAG(price_usd, 24 * 7) OVER (PARTITION BY asset_id ORDER BY observed_at))
      / LAG(price_usd, 24 * 7) OVER (PARTITION BY asset_id ORDER BY observed_at)
    ) * 100
  END AS price_change_pct_7d
FROM silver_market_snapshots
WHERE asset_id IS NOT NULL
  AND observed_at IS NOT NULL;
