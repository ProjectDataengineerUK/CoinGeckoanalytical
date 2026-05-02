# Approval Gate Status

## Current Status

- `ci.yml` deploy gate: `approved` → `dispatched` (2026-05-01)
- `terraform.yml` apply gate: `approved`
- `bronze-migration.yml` migration gate: `executed`

## Approval Log

| Date       | Action                          | Approved by | State      | Notes |
|------------|---------------------------------|-------------|------------|-------|
| 2026-05-02 | `ci.yml` confirm_deploy=true    | operator    | dispatched | Fix ai_serving views + CoinGecko API key injection. Commits: 63c512a, 1281aa3 + genie/ops fixes |
| 2026-05-02 | `ci.yml` confirm_deploy=true    | operator    | executed   | Full deploy post folder reorg + validator fixes. Run 25252497484 ✓ |
| 2026-05-01 | `bronze-migration.yml`          | operator    | executed   | Bronze schema remediation run 25216983089 |

## Interpretation

- the workflows exist and are ready
- the operator must approve each action explicitly in chat before execution
- no Databricks or Terraform mutation should run without an explicit approval step

## Deploy Sequence (ci.yml confirm_deploy=true)

When dispatched, the workflow runs in this order:
1. `lint` — compile all Python
2. `contract` — unit tests + bundle validation + chain validation
3. `deploy` (manual gate):
   - `databricks bundle deploy -t dev`
   - `bronze_market_table_migration_job` (schema DDL)
   - `market_source_ingestion_job` (ingest sample payload)
   - `silver_market_table_migration_job` (provision Silver Delta tables)
   - `silver_market_pipeline_job` (materialise Silver)
   - `ops_usage_ingestion_job`
   - `ops_bundle_run_ingestion_job`
   - `ops_sentinela_alert_ingestion_job`
   - `ops_readiness_refresh_job`
   - live SQL validation artifact upload
