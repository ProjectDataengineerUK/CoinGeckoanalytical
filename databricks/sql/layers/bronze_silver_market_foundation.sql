-- Databricks Bronze/Silver Market Foundation
-- Purpose: provision the Silver snapshot view that reads from Bronze.
-- Bronze table DDL is managed by bronze_market_table_migration_job.
-- Silver changes/dominance/comparison tables are managed by
-- silver_market_migration_job and populated by silver_market_pipeline_job.

CREATE OR REPLACE VIEW cgadev.market_silver.silver_market_snapshots AS
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
  FROM cgadev.market_bronze.bronze_market_snapshots
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
