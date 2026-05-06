# Approval Gate Status

## Current Status

- current live baseline: `online`
- `ci.yml` deploy gate for the current baseline: `executed`
- `deploy_apps` gate for the current baseline: `executed`
- `uc_grants` / `rls_migration` gate for the current baseline: `executed`
- `confirm_train` gate: `available for future retraining runs`
- `terraform.yml` apply gate: `manual and approval-gated for future infrastructure mutations`

## Interpretation

- the current runtime is already online
- no additional approval is required to describe or document the current baseline
- any future Databricks, governance, or Terraform mutation still requires explicit approval in chat before execution
- `workflow_dispatch` remains the execution mechanism for controlled changes

## Current Controlled Mutation Paths

1. `ci.yml` with `confirm_deploy=true`
   - bundle deploy
   - data pipeline execution
   - optional live SQL validation artifact generation
2. `ci.yml` with `confirm_apps_deploy=true`
   - app refresh/redeploy for `cga-analytics` and `cga-admin`
3. `ci.yml` with `confirm_uc_grants=true`
   - `uc_grants_job`
   - `rls_migration_job`
4. `ci.yml` with `confirm_train=true`
   - `train_market_model_job`
5. `terraform.yml` with `confirm_apply=true`
   - approved infrastructure mutation after plan review

## Operational Rule

Treat the current online state as the approved baseline.

For any new change after this point:

- validate locally first
- record evidence in `.agentcodex/reports/`
- require explicit operator approval before live mutation
