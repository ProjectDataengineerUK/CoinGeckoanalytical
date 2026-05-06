# Disaster Recovery Runbook

## Purpose

Define the minimum recovery posture for the live Databricks baseline across `dev`, `staging`, and `prod`.

## Recovery Scope

- Bronze, Silver, Gold, and ops Delta tables
- Unity Catalog views, grants, and model aliases
- Databricks Apps deploy state
- AI serving dependencies required by `cga-analytics` and `cga-admin`

## Minimum Recovery Controls

1. Keep all production logic in versioned Python, SQL, YAML, and workflow files in git.
2. Treat Databricks Asset Bundles as the canonical redeploy mechanism for apps and jobs.
3. Keep Unity Catalog DDL, grants, and masking rules in version-controlled SQL and Terraform-backed artifacts.
4. Preserve the latest successful `databricks-live-sql-validation` artifact for each environment.
5. Preserve model alias state and champion/candidate promotion history before changing aliases.

## Recovery Order

1. Stop or pause affected jobs in the target environment.
2. Confirm whether data corruption, deploy corruption, or serving corruption is the primary failure mode.
3. Re-deploy the last known-good bundle revision for the target environment.
4. Re-apply `uc_grants_job` and `rls_migration_job` if governance surfaces were impacted.
5. Re-run `live-validation.yml` for the affected target.
6. Re-check Apps health for `cga-analytics` and `cga-admin`.
7. Re-open traffic only after live SQL validation and app health are green.

## Data Recovery Guidance

- Use Delta table history and time travel when row-level or table-level rollback is needed.
- Prefer controlled overwrite/rebuild from upstream Bronze sources over ad hoc table edits.
- If Bronze ingestion is the fault domain, re-run migrations first, then re-ingest, then rebuild Silver and Gold.

## Evidence To Record

- failing commit or workflow run
- affected target (`dev`, `staging`, or `prod`)
- recovery commands used
- restored artifact versions
- post-recovery live SQL validation results

## Acceptance Rule

Do not claim recovery complete until:

- live SQL validation passes
- governance jobs complete when relevant
- app surfaces start successfully
- evidence is written under `.agentcodex/reports/`
