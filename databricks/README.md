# Databricks

Databricks-side assets for the CoinGecko analytical slice.

Use this area for governed data assets, analytical serving contracts, deployment notes, and environment-aware configuration.

GitHub Actions deploys use `DATABRICKS_HOST` and `DATABRICKS_TOKEN`. If `DATABRICKS_SQL_WAREHOUSE_ID` is also configured as a secret, the workflow additionally runs live SQL validation and uploads the `databricks-live-sql-validation` artifact.

## Build Slice 3 Scope

- Gold market views for dashboard and Genie
- Bronze and Silver market foundation for the first governed slice
- Unity Catalog foundation for governed namespaces and boundaries
- Terraform baseline for environment and governance IaC
- governed metric views for AI/BI NLQ
- freshness and quality baseline checks
- telemetry observability and release-readiness views
- Unity Catalog governance for data and models
- Databricks Apps only for admin and internal operations
- thin Databricks notebooks for workspace execution, validation, and operations review

## Concrete Assets

- `gold_market_views.sql`
- `bronze_silver_market_foundation.sql`
- `unity_catalog_foundation.sql`
- `terraform/providers.tf`
- `terraform/variables.tf`
- `terraform/main.tf`
- `genie_metric_views.sql`
- `freshness_quality_baseline.sql`
- `telemetry-observability.sql`
- `ops_readiness_dashboard.sql`
- `market_source_ingestion_job.py`
- `ops_usage_ingestion_job.py`
- `bundle_run_ingestion_job.py`
- `sentinela_alert_ingestion_job.py`
- `ops_readiness_refresh_job.py`
- `databricks.yml`
- `validate_bundle.py`
- `preflight_databricks_deploy.py`
- `bundle_run_observability.sql`
- `gold-market-views.md`
- `bronze-silver-market-foundation.md`
- `unity-catalog-foundation.md`
- `unity-catalog-lineage-map.md`
- `terraform-phase1-baseline.md`
- `genie-metric-views.md`
- `freshness-and-quality-baseline.md`
- `telemetry-observability.md`
- `ops_readiness_dashboard.md`
- `market_source_ingestion_job.md`
- `ops_usage_ingestion_job.md`
- `bundle_run_ingestion_job.md`
- `sentinela_alert_ingestion_job.md`
- `ops_readiness_refresh_job.md`
- `bundle-manifest.md`
- `deployment_runbook.md`
- `notification_policy.md`
- `test_validate_bundle.py`
- `test_preflight_databricks_deploy.py`
- `bundle_run_observability.md`
- `test_market_source_ingestion_job.py`
- `test_bundle_run_ingestion_job.py`
- `test_bundle_run_observability.py`
- `test_sentinela_alert_ingestion_job.py`
- `model-version-governance.md`
- `notebooks/01_ingest_coingecko_market.py`
- `notebooks/02_validate_market_layers.py`
- `notebooks/03_ops_readiness_review.py`
- `notebooks/README.md`

## Notebook Layer

The notebooks are intentionally thin. Production logic remains in versioned Python and SQL files, while notebooks provide the familiar Databricks workspace experience:

- run the CoinGecko market ingestion path
- inspect Bronze/Silver/Gold/Genie row counts
- review operational readiness and Sentinela views

## Operational Contracts

- `../contracts/bundle_run_event.schema.json`
- `../contracts/sentinela_alert_event.schema.json`

## Observability Scope

- bundle run events are used as release blockers when jobs fail or are cancelled
