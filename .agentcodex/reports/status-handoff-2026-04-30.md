# Status Handoff

- date: `2026-04-30`
- project: `CoinGeckoAnalytical`
- workflow_phase: `build`
- status: `build-active`

## Where We Are

- `brainstorm`, `define`, and `design` were refreshed and are now aligned to the chosen full-product V1 direction
- the earlier build drift was preserved as context, but the workflow has been reset correctly before new build planning
- the repository contains useful build assets in `backend/`, `databricks/`, and `contracts/`
- CI validation exists in `.github/workflows/ci.yml`
- local verification passed on `2026-04-30`
- deploy automation supports optional live SQL validation when `DATABRICKS_SQL_WAREHOUSE_ID` is present in GitHub Actions secrets
- the native next infrastructure step is `terraform plan` for `dev`, but this local environment currently lacks the Terraform CLI and real `dev` credentials
- a real Terraform execution attempt was started, `init` succeeded, and the current blocker is now the Databricks provider schema handshake in this environment before `plan`
- the repository now routes Terraform through a dedicated `terraform` workflow so the native infrastructure sequence stays separated from the release/deploy path
- the default publication flow now includes commit and push after validation when the user is ready to publish the change set

## Verified Locally

- `python3 -m unittest discover -s backend/tests -p 'test_*.py'`
- `python3 databricks/validate_bundle.py`
- `python3 -m unittest discover -s repo_tests -p 'test_*.py'`
- `python3 -m unittest databricks.test_live_sql_validation`
- `terraform version` could not run locally because the CLI is not installed in this environment
- local Terraform bootstrap to `/tmp` succeeded and `terraform init` completed under `databricks/terraform`
- `terraform validate` is currently blocked by Databricks provider schema loading in this environment
- `python3 -m unittest repo_tests.test_ci_workflow`
- `python3 -m unittest repo_tests.test_terraform_workflow`
- the workflow model now separates `terraform.yml` from `ci.yml`

## Current Practical Position

- the product definition is now durable in `brainstorm`, `define`, and `design`
- the contract layer exists and remains useful for later build work
- backend telemetry and handoff writers exist, but the copilot path is still a prototype
- Databricks bundle helpers and ops assets exist, but they are build-local infrastructure rather than ship evidence
- the deploy workflow can now persist `databricks/live_sql_validation_results.json` as a CI artifact when the warehouse secret is configured
- the Terraform path is sequenced ahead of live environment claims, but workspace execution evidence is still blocked by missing local CLI plus missing real `dev` inputs
- the Terraform path is now also blocked by provider runtime behavior in this environment, so the next valid infrastructure move is to re-run `validate/plan` where the Databricks provider handshake succeeds
- the current repo answer to that environment limit is a dedicated GitHub Actions `terraform` workflow with plan/artifact output and a controlled manual apply path, while `ci.yml` keeps release/deploy concerns separate
- the controlled Terraform apply path now initializes Terraform in the clean apply runner before applying the downloaded reviewed plan artifact
- a configuration sweep was recorded at `.agentcodex/reports/configuration-sweep-2026-04-30.md`; local tests, bundle validation, market chain validation, and compile validation passed, while remote secret/workflow verification remains blocked locally because `gh` is not installed
- the native next-step analysis was recorded at `.agentcodex/reports/native-next-step-2026-04-30.md`; since local `HEAD` and `origin/main` are aligned before the current validated changes, the next native action is to commit and push the local change set to trigger GitHub Actions evidence
- the first live deploy failed only at `ops_readiness_refresh_job` because a runtime refresh path attempted to apply ownership to missing Unity Catalog principal `data_platform`; remediation is recorded at `.agentcodex/reports/deploy-failure-principal-remediation-2026-04-30.md`
- after publishing `9e0e299`, the user reported that the deploy passed; the next evidence step is recorded at `.agentcodex/reports/post-deploy-success-next-step-2026-04-30.md`
- GitHub Actions API confirmed `ci` run `25198087949` completed `lint`, `contract`, and `deploy` successfully; the run uploaded `databricks-live-sql-validation`, and live evidence is recorded at `.agentcodex/reports/live-workspace-validation-2026-04-30.md`
- the market ingestion gap was closed in `.agentcodex/reports/build-slice-1-coingecko-fetch-2026-05-01.md`; `market_source_ingestion_job` now fetches CoinGecko `/coins/markets` directly when no explicit payload is supplied, while CI smoke can still pass a deterministic fixture payload
- a thin Databricks notebook layer was added in `.agentcodex/reports/build-slice-1-databricks-notebooks-2026-05-01.md`; production logic remains in tested Python/SQL assets while notebooks provide workspace-native entrypoints and review surfaces
- GitHub Actions API confirmed `ci` run `25215006212` failed only in the `deploy` job after adding notebooks; remediation is recorded at `.agentcodex/reports/deploy-failure-notebook-sync-remediation-2026-05-01.md`, and the bundle now excludes `notebooks/**` from production job file sync while still validating source-controlled notebook assets
- commit and push are now the normal publication path after validation, unless the user explicitly asks to hold back publication
- the frontend remains a placeholder and no real user-facing V1 slice is closed yet

## Next Steps

1. configure the Terraform GitHub secrets required by the `terraform` workflow
2. trigger the plan job and capture the first `terraform-dev-plan` artifact
3. review the `plan` output and persist the resulting evidence into `.agentcodex/reports/`
4. if the plan is approved, trigger `workflow_dispatch` with `confirm_apply=true` for the controlled `dev` apply
5. after the workspace baseline exists, resume live deploy validation and artifact-producing SQL checks

## Resume Pointers

- `.agentcodex/history/CONTEXT-HISTORY.md`
- `.agentcodex/features/BRAINSTORM_coingeckoanalytical.md`
- `.agentcodex/features/DEFINE_coingeckoanalytical.md`
- `.agentcodex/features/DESIGN_coingeckoanalytical.md`
- `.agentcodex/features/BUILD_coingeckoanalytical.md`
