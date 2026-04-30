# Build Slice 1 Terraform GitHub Actions Plan

- date: `2026-04-30`
- project: `CoinGeckoAnalytical`
- slice: `WS1 terraform dev plan in github actions`
- result_type: `implemented`

## Delivered

- updated `.github/workflows/ci.yml`
- created `.github/workflows/terraform.yml`
- updated `repo_tests/test_ci_workflow.py`
- created `repo_tests/test_terraform_workflow.py`

## What This Closes

- the native Terraform sequence now has a compatible execution path outside the current local environment
- GitHub Actions can run `terraform init`, `terraform validate`, and `terraform plan` for `dev` in the dedicated `terraform` workflow
- the `ci` workflow no longer mixes Terraform planning into the release/deploy path
- the dedicated workflow can upload a `terraform-dev-plan` artifact when the required Terraform secrets are configured
- manual `workflow_dispatch` support exists for an explicit `terraform apply` step after plan review

## Required Secrets

- `DATABRICKS_HOST`
- `DATABRICKS_TOKEN`
- `TF_VAR_DATA_PLATFORM_GROUP`
- `TF_VAR_PRODUCT_BACKEND_GROUP`
- `TF_VAR_PRODUCT_ANALYTICS_GROUP`
- `TF_VAR_PLATFORM_OPS_GROUP`
- `TF_VAR_GOVERNANCE_ADMIN_GROUP`
- `TF_VAR_SVC_MARKET_INGESTION`
- `TF_VAR_SVC_MARKET_PIPELINE`
- `TF_VAR_SVC_OPS_PIPELINE`
- `TF_VAR_SVC_AUDIT_PIPELINE`
- `TF_VAR_BUNDLE_ROOT`
- `TF_VAR_OPS_CLUSTER_ID`
- optional overrides:
  - `TF_VAR_OPS_SPARK_VERSION`
  - `TF_VAR_OPS_NODE_TYPE_ID`

## Verification

- `python3 -m unittest repo_tests.test_ci_workflow`
- `python3 -m unittest repo_tests.test_terraform_workflow`
- `python3 -m unittest discover -s repo_tests -p 'test_*.py'`

## Remaining Work

- configure the Terraform secrets in GitHub Actions
- run the workflow and capture the first `terraform-dev-plan` artifact
- after the plan artifact is reviewed, decide whether to trigger the controlled `dev` apply from `workflow_dispatch`
