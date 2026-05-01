# Bronze Manual Dispatch Workflow

## Summary

The Bronze schema remediation now has a dedicated manual GitHub Actions workflow.

## Workflow

- file: `.github/workflows/bronze-migration.yml`
- trigger: `workflow_dispatch`
- confirmation input: `confirm_migration=true`

## Behavior

- validates the Databricks bundle
- deploys the bundle to `dev`
- runs `bronze_market_table_migration_job` on demand

## Safety Posture

- no automatic Bronze remediation on push
- the operator must approve and trigger the workflow manually
- the migration remains explicit because it recreates the Bronze table

## Validation

- `python3 -m unittest repo_tests.test_bronze_migration_workflow repo_tests.test_ci_workflow repo_tests.test_terraform_workflow repo_tests.test_frontend_shell` passed
- `python3 -m unittest discover -s repo_tests -p 'test_*.py'` passed
- `python3 databricks/validate_bundle.py` passed
