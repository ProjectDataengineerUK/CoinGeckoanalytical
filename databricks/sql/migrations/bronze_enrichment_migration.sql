-- Phase 2 Bronze enrichment tables

CREATE TABLE IF NOT EXISTS cgadev.market_bronze.bronze_defillama_protocols (
  source_system      STRING        NOT NULL,
  source_record_id   STRING        NOT NULL,
  protocol_slug      STRING        NOT NULL,
  protocol_name      STRING        NOT NULL,
  chain              STRING,
  category           STRING,
  tvl_usd            DECIMAL(38,8) NOT NULL,
  fees_24h_usd       DECIMAL(38,8),
  revenue_24h_usd    DECIMAL(38,8),
  mcap_tvl_ratio     DECIMAL(38,8),
  observed_at        TIMESTAMP     NOT NULL,
  ingested_at        TIMESTAMP     NOT NULL,
  payload_version    STRING        NOT NULL
)
USING DELTA
TBLPROPERTIES (
  'delta.minReaderVersion' = '1',
  'delta.minWriterVersion' = '2'
);

CREATE TABLE IF NOT EXISTS cgadev.market_bronze.bronze_github_activity (
  source_system      STRING  NOT NULL,
  source_record_id   STRING  NOT NULL,
  asset_id           STRING  NOT NULL,
  repo_full_name     STRING  NOT NULL,
  stars              BIGINT,
  forks              BIGINT,
  open_issues        BIGINT,
  contributors_count BIGINT,
  commits_30d        BIGINT,
  commits_90d        BIGINT,
  repo_age_days      BIGINT,
  last_push_at       STRING,
  observed_at        TIMESTAMP NOT NULL,
  ingested_at        TIMESTAMP NOT NULL,
  payload_version    STRING    NOT NULL
)
USING DELTA
TBLPROPERTIES (
  'delta.minReaderVersion' = '1',
  'delta.minWriterVersion' = '2'
);

CREATE TABLE IF NOT EXISTS cgadev.market_bronze.bronze_fred_macro (
  source_system      STRING        NOT NULL,
  source_record_id   STRING        NOT NULL,
  series_id          STRING        NOT NULL,
  series_name        STRING        NOT NULL,
  observation_date   STRING        NOT NULL,
  value              DECIMAL(38,8) NOT NULL,
  observed_at        TIMESTAMP     NOT NULL,
  ingested_at        TIMESTAMP     NOT NULL,
  payload_version    STRING        NOT NULL
)
USING DELTA
TBLPROPERTIES (
  'delta.minReaderVersion' = '1',
  'delta.minWriterVersion' = '2'
)
