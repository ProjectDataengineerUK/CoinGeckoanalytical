# Build Slice 1 CoinGecko Fetch - 2026-05-01

## Problem

The Databricks ingestion pipeline was deployed and working, but the market source job only consumed explicit fixture or handoff payloads. Scheduled runs without a payload did not fetch provider data.

## Source Reference

CoinGecko's documented market-data endpoint is `/coins/markets`, which returns price, market cap, volume, and market-related data and supports `per_page` and `page` pagination parameters.

Reference:

- `https://docs.coingecko.com/reference/coins-markets`

## Delivered

- updated `databricks/market_source_ingestion_job.py`
- updated `databricks/test_market_source_ingestion_job.py`
- updated `databricks/market_source_ingestion_job.md`
- updated `databricks/bundle-manifest.md`
- updated `databricks/ops_jobs_manifest.md`

## Behavior

The job now supports two modes:

1. explicit payload mode through `payload_json` or `payload_path`
2. provider-backed mode through CoinGecko `/coins/markets` when no payload is supplied

Provider-backed mode supports:

- configurable base URL
- API key header
- `vs_currency`
- market ordering
- `per_page`
- page count
- sparkline flag
- price-change percentage windows
- request timeout
- retry/backoff for transient provider errors

## Why The CI Smoke Still Uses A Fixture

The deploy smoke keeps passing a fixture payload so GitHub Actions remains deterministic and does not depend on third-party API availability.

The scheduled Databricks job can now run without a payload and fetch real CoinGecko market data.

## Verification

Run locally:

- `python3 -m unittest databricks.test_market_source_ingestion_job`
- `python3 -m unittest discover -s databricks -p 'test_*.py'`
- `python3 databricks/validate_bundle.py`
- `python3 databricks/validate_market_overview_chain.py`

## Next Step

Deploy the updated bundle and let a scheduled `market_source_ingestion_job` run without a payload. Then capture Bronze row counts and observed timestamps in the live workspace validation report.
