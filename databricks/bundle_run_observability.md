# Bundle Run Observability Baseline

## Purpose

Land Databricks bundle and job run results and expose a governed readiness layer for Sentinela and the ops dashboard.

## Implementation Asset

- executable baseline: `bundle_run_observability.sql`

## Surface

- `ops_bundle_runs`: landing table for normalized bundle/job runs
- `ops_bundle_runs_normalized`: normalized and classified run view
- `ops_bundle_run_health`: job-level readiness summary
- `ops_bundle_run_latest`: latest run per job
- `ops_bundle_run_readiness`: combined readiness and serving view

## Operational Rules

- failed or cancelled runs hold release readiness
- successful runs keep the bundle path ready
- duration bands help separate quick failures from long-running operations

## Next Step

- ingest real Databricks job run results into `ops_bundle_runs`
- render the bundle readiness view on the ops dashboard
- connect the readiness outcome to Sentinela alerts and release checks
