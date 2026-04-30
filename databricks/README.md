# Databricks

Databricks-side assets for the CoinGecko analytical slice.

Use this area for governed data assets, analytical serving contracts, deployment notes, and environment-aware configuration.

## Build Slice 3 Scope

- Gold market views for dashboard and Genie
- governed metric views for AI/BI NLQ
- freshness and quality baseline checks
- telemetry observability and release-readiness views
- Unity Catalog governance for data and models
- Databricks Apps only for admin and internal operations

## Concrete Assets

- `gold_market_views.sql`
- `genie_metric_views.sql`
- `freshness_quality_baseline.sql`
- `telemetry-observability.sql`
- `ops_readiness_dashboard.sql`
- `ops_usage_ingestion_job.py`
- `bundle_run_ingestion_job.py`
- `ops_readiness_refresh_job.py`
- `databricks.yml`
- `validate_bundle.py`
- `bundle_run_observability.sql`
- `gold-market-views.md`
- `genie-metric-views.md`
- `freshness-and-quality-baseline.md`
- `telemetry-observability.md`
- `ops_readiness_dashboard.md`
- `ops_usage_ingestion_job.md`
- `bundle_run_ingestion_job.md`
- `ops_readiness_refresh_job.md`
- `bundle-manifest.md`
- `test_validate_bundle.py`
- `bundle_run_observability.md`
- `test_bundle_run_ingestion_job.py`
- `test_bundle_run_observability.py`
- `model-version-governance.md`

## Operational Contracts

- `../contracts/bundle_run_event.schema.json`

## Observability Scope

- bundle run events are used as release blockers when jobs fail or are cancelled
