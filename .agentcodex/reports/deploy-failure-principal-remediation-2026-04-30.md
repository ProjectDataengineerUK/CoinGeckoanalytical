# Deploy Failure Principal Remediation - 2026-04-30

## Failure Summary

The GitHub Actions deploy reached the Databricks workspace and successfully completed the first live execution steps:

- bundle files uploaded to the dev workspace
- resources deployed
- `market_source_ingestion_job` succeeded and wrote `3` rows to `bronze_market_snapshots`
- `ops_usage_ingestion_job` succeeded
- `ops_bundle_run_ingestion_job` succeeded
- `ops_sentinela_alert_ingestion_job` succeeded

The deploy failed at:

- `ops_readiness_refresh_job`
- task: `refresh_readiness_views`
- Databricks error class: `PRINCIPAL_DOES_NOT_EXIST.PRINCIPAL_DOES_NOT_EXIST`
- missing principal: `data_platform`

## Root Cause

The refresh path executed a Unity Catalog ownership statement that attempted to change schema owner to `data_platform`.

That principal is part of the design and Terraform ownership posture, but it is not guaranteed to exist in the runtime workspace before the Terraform principal-binding path has completed.

Runtime readiness refresh should create or refresh schemas/views only. Ownership and grants belong to Terraform or an explicitly reviewed workspace governance step.

## Applied Fix

Updated `databricks/ops_readiness_refresh_job.py` so runtime refresh skips principal-management statements:

- `ALTER ... OWNER`
- `GRANT ...`
- `REVOKE ...`

This makes the job resilient if a governance SQL file is accidentally included in the runtime refresh path.

Updated `databricks/test_ops_readiness_refresh_job.py` with a regression test that proves the refresh still executes safe schema/view statements while skipping ownership and grant statements.

Documentation updated:

- `databricks/ops_readiness_refresh_job.md`
- `databricks/ops_jobs_manifest.md`
- `databricks/bundle-manifest.md`

## Verification

Passed locally:

- `python3 -m unittest databricks.test_ops_readiness_refresh_job`
- `python3 databricks/validate_bundle.py`
- `python3 databricks/validate_market_overview_chain.py`
- `python3 -m unittest discover -s databricks -p 'test_*.py'`
- `python3 -m unittest discover -s repo_tests -p 'test_*.py'`
- `python3 -m unittest discover -s backend/tests -p 'test_*.py'`

## Next Action

Commit and push this remediation, then rerun the deploy workflow.

Expected result:

- `ops_readiness_refresh_job` should no longer fail because `data_platform` is missing.
- live SQL validation should proceed after deploy if `DATABRICKS_SQL_WAREHOUSE_ID` is configured.

## Follow-Up

Terraform or a workspace admin action still needs to bind the real workspace groups/principals for the final governance posture.

The runtime deploy path should not be responsible for creating or changing those principals.
