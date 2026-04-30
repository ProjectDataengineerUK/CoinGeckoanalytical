# Build Slice 1 Market Source Ingestion

- date: `2026-04-30`
- project: `CoinGeckoAnalytical`
- slice: `WS1 market source ingestion baseline`
- result_type: `implemented`

## Delivered

- created `databricks/market_source_ingestion_job.py`
- created `databricks/test_market_source_ingestion_job.py`
- created `databricks/market_source_ingestion_job.md`
- updated `databricks/databricks.yml`
- updated `databricks/validate_bundle.py`
- updated `databricks/terraform/jobs.tf`
- updated `.github/workflows/ci.yml`

## What This Closes

- the active design flow now has an executable ingestion job at the start of the `market overview intelligence` chain
- the Bronze landing table is no longer only a SQL contract; it now has a bundle-managed ingestion entrypoint
- CI and bundle validation now enforce the presence of the first market-source ingestion job

## Verification

- local unit tests should cover payload parsing, CoinGecko-shape normalization, and bundle manifest validation
- the bundle manifest now includes `market_source_ingestion_job`
- Terraform now includes the matching Databricks job resource

## Remaining Work

- connect the market payload handoff to a real source extraction path
- execute the Bronze -> Silver -> Gold chain in a live Databricks workspace
- bind backend dashboard retrieval to served Gold assets instead of demo payloads
