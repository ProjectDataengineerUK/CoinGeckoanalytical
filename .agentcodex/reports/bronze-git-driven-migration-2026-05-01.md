# Bronze Git-Driven Migration

## Summary

The Bronze schema remediation was wired into the repository as a versioned Databricks job and Terraform-managed job resource.

## What Changed

- added `databricks/bronze_market_table_migration_job.py`
- added `databricks/test_bronze_market_table_migration_job.py`
- added `databricks/bronze_market_table_migration_job.md`
- added `bronze_market_table_migration_job` to `databricks/databricks.yml`
- added `bronze_market_table_migration_job` to `databricks/terraform/jobs.tf`
- updated `databricks/validate_bundle.py` to require the migration job in the bundle manifest
- updated bundle and deployment docs to treat migration as on-demand remediation for legacy workspaces

## Safety Posture

- the migration SQL remains destructive in the sense that it recreates the Bronze table
- the job is therefore intentionally not scheduled as a recurring task
- deploys can provision the job from Git, but execution stays explicit and operator-driven

## Validation

- `python3 databricks/validate_bundle.py` passed
- `python3 -m unittest discover -s databricks -p 'test_*.py'` passed

## Operational Note

Use the migration job only when a workspace still has a legacy Bronze schema and must be remediated before ingest.
