# Market Source Ingestion Job

## Purpose

Append normalized market-source rows into the governed Bronze landing table `bronze_market_snapshots`.

## Implementation Asset

- executable job: `market_source_ingestion_job.py`

## Inputs

- `payload_json`: inline JSON object or array of source rows
- `payload_path`: path to a JSON file containing source rows
- `target_table`: target Delta table, defaulting to `bronze_market_snapshots`
- runtime CLI flags also support `--payload-json`, `--payload-path`, and `--target-table`
- when no payload is supplied, the job fetches CoinGecko `/coins/markets` directly

## Backend Handoff

- `backend/market_source_handoff.py` writes a Databricks-ready JSON array in CoinGecko-compatible shape
- `databricks/fixtures/market_source_sample.json` is the repo-local fixture for smoke validation
- handoff files are still supported for smoke tests, replays, and controlled validation

## Supported Source Shape

- canonical Bronze-shaped rows
- CoinGecko-style market rows with:
  - `id`
  - `symbol`
  - `name`
  - `market_cap`
  - `current_price`
  - `total_volume`
  - `circulating_supply`
  - `market_cap_rank`
  - `last_updated`

## Behavior

- parses one row or many rows
- fetches CoinGecko market data directly when no payload is supplied
- supports CoinGecko pagination through environment configuration
- uses retry/backoff for transient provider failures
- normalizes CoinGecko-style input into the Bronze contract
- builds a Spark DataFrame for the Bronze contract
- applies Spark `selectExpr` casts for strings, timestamps, decimals, and integers
- deduplicates each batch by `source_system` and `source_record_id`
- enforces the required Bronze market fields
- coerces numeric fields into stable types
- appends the normalized rows to the target Delta table

## Spark Contract

The job writes through a Spark DataFrame, not a raw Python payload append:

- `observed_at` and `ingested_at` are cast to `TIMESTAMP`
- market numeric fields are cast to `DECIMAL(38, 8)`
- `market_cap_rank` is cast to `INT`
- `symbol` is uppercased in Spark
- duplicate source records are removed within the batch before write

## Provider Configuration

- `COINGECKO_API_BASE_URL`: default `https://api.coingecko.com/api/v3`
- `COINGECKO_API_KEY`: optional API key
- `COINGECKO_API_KEY_HEADER`: default `x-cg-demo-api-key`
- `COINGECKO_VS_CURRENCY`: default `usd`
- `COINGECKO_MARKET_ORDER`: default `market_cap_desc`
- `COINGECKO_PER_PAGE`: default `250`
- `COINGECKO_PAGES`: default `1`
- `COINGECKO_PRICE_CHANGE_PERCENTAGE`: default `1h,24h,7d,30d`
- `COINGECKO_REQUEST_TIMEOUT_SECONDS`: default `30`
- `COINGECKO_MAX_RETRIES`: default `3`
- `COINGECKO_RETRY_BACKOFF_SECONDS`: default `1.0`

## Runtime Shape

- designed for Databricks Jobs / serverless execution
- uses batch append only
- fetches from CoinGecko during scheduled runs unless a payload override is supplied
- uses Spark DataFrame transformations before Delta write

## Next Step

- schedule it ahead of Gold-serving refresh and downstream route validation
- capture live row counts from a scheduled provider-backed run
