-- Bronze Market Table Migration
-- Purpose: recreate the Bronze landing table with the canonical decimal schema.
-- Run this before the first live ingest if the workspace already has a legacy
-- Bronze table with DoubleType numeric columns.

CREATE OR REPLACE TABLE cgadev.market_bronze.bronze_market_snapshots (
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

-- Apply the same recreation pattern to staging and prod catalog targets during
-- promotion when those workspaces already contain a legacy Bronze table.
