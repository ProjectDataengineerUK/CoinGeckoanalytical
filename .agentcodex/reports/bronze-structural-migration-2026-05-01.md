# Bronze Structural Migration

- date: `2026-05-01`
- project: `CoinGeckoAnalytical`
- purpose: `make the Bronze schema correction structural, not only defensive`

## Changes

- added `databricks/bronze_market_table_migration.sql`
- updated `databricks/market_source_ingestion_job.md`
- updated `databricks/deployment_runbook.md`

## Outcome

- the canonical Bronze schema now has an explicit recreation path
- the deploy runbook now requires the schema migration before the first live ingest on a legacy workspace
- the ingest job still remains safe against legacy tables during transition

## Notes

- the migration is dev-catalog oriented in the current baseline
- apply the same recreation pattern to staging and prod catalogs during promotion
