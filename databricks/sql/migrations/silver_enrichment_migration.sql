-- Phase 2 Silver enrichment tables

CREATE TABLE IF NOT EXISTS cgadev.market_silver.silver_asset_enriched (
  asset_id              STRING        NOT NULL,
  symbol                STRING,
  name                  STRING,
  market_cap_rank       BIGINT,
  price_usd             DECIMAL(38,8),
  market_cap_usd        DECIMAL(38,8),
  volume_24h_usd        DECIMAL(38,8),
  snapshot_ingested_at  TIMESTAMP,
  protocol_slug         STRING,
  defi_category         STRING,
  tvl_usd               DECIMAL(38,8),
  fees_24h_usd          DECIMAL(38,8),
  revenue_24h_usd       DECIMAL(38,8),
  mcap_tvl_ratio        DECIMAL(38,8),
  repo_full_name        STRING,
  stars                 BIGINT,
  forks                 BIGINT,
  open_issues           BIGINT,
  contributors_count    BIGINT,
  commits_30d           BIGINT,
  commits_90d           BIGINT,
  repo_age_days         BIGINT,
  dev_activity_score    INT,
  enriched_at           TIMESTAMP     NOT NULL
)
USING DELTA
TBLPROPERTIES (
  'delta.minReaderVersion' = '1',
  'delta.minWriterVersion' = '2'
);

CREATE TABLE IF NOT EXISTS cgadev.market_silver.silver_macro_context (
  series_id      STRING        NOT NULL,
  series_name    STRING        NOT NULL,
  latest_date    STRING        NOT NULL,
  current_value  DECIMAL(38,8) NOT NULL,
  value_30d_ago  DECIMAL(38,8),
  change_30d_pct DECIMAL(38,8),
  enriched_at    TIMESTAMP     NOT NULL
)
USING DELTA
TBLPROPERTIES (
  'delta.minReaderVersion' = '1',
  'delta.minWriterVersion' = '2'
)
