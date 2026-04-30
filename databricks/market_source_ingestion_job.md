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

## Backend Handoff

- `backend/market_source_handoff.py` writes a Databricks-ready JSON array in CoinGecko-compatible shape
- `databricks/fixtures/market_source_sample.json` is the repo-local fixture for smoke validation
- the handoff file is intended to be passed as `payload_path`

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
- normalizes CoinGecko-style input into the Bronze contract
- enforces the required Bronze market fields
- coerces numeric fields into stable types
- appends the normalized rows to the target Delta table

## Runtime Shape

- designed for Databricks Jobs / serverless execution
- uses batch append only
- does not fetch from the provider directly; V1 uses a governed file or payload handoff

## Next Step

- connect the job to the first real market-source extraction handoff
- schedule it ahead of Gold-serving refresh and downstream route validation
