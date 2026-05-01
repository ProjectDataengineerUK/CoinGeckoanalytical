# Configuration Sweep - 2026-04-30

## Scope

- project: `CoinGeckoAnalytical`
- branch: `main`
- latest local commit: `9294778 Document automatic commit and push flow`
- purpose: verify the local readiness surface after Databricks, Terraform, and GitHub Actions configuration work.

## Git State

The working tree has intentional local changes from the Terraform apply hardening pass:

- `.github/workflows/terraform.yml`
- `repo_tests/test_terraform_workflow.py`
- `.agentcodex/reports/build-slice-1-terraform-github-actions-plan-2026-04-30.md`
- `.agentcodex/reports/status-handoff-2026-04-30.md`

No unrelated dirty files were detected in this sweep.

## Local Validation Results

Passed:

- `python3 -m unittest discover -s repo_tests -p 'test_*.py'`
- `python3 -m unittest discover -s backend/tests -p 'test_*.py'`
- `python3 -m unittest discover -s databricks -p 'test_*.py'`
- `python3 databricks/validate_bundle.py`
- `python3 databricks/validate_market_overview_chain.py`
- `python3 -m compileall backend databricks repo_tests`

Notes:

- the first sandboxed `compileall` attempt failed with `Read-only file system` while writing `__pycache__`; rerunning with escalated filesystem permission completed successfully.
- `databricks.test_live_sql_validation` intentionally skips live SQL execution when `DATABRICKS_SQL_WAREHOUSE_ID` is not present in the local environment.

## Local Tooling Availability

Unavailable in this local shell:

- `terraform`
- `databricks`
- `gh`

Local Databricks preflight result:

- `cli_available`: `False`
- `host_configured`: `False`
- `token_configured`: `False`
- `ready`: `False`
- missing: `databricks-cli`, `DATABRICKS_HOST`, `DATABRICKS_TOKEN`

This does not prove GitHub Actions secrets are missing. It only means the current local shell cannot execute Databricks or Terraform live checks directly.

## Workflow Contract Findings

`ci.yml`:

- runs Python compile validation
- runs backend tests
- validates Databricks bundle metadata
- validates the market overview SQL chain
- runs Databricks helper tests
- runs repo workflow contract tests
- installs Databricks CLI in the deploy job
- deploys only on `push` to `main`
- runs live SQL validation after deploy
- uploads `databricks-live-sql-validation` only when `DATABRICKS_SQL_WAREHOUSE_ID` is present

`terraform.yml`:

- runs Terraform plan on `push`, `pull_request`, and `workflow_dispatch`
- uses GitHub secrets for Databricks host/token, principals, service identities, bundle root, and cluster inputs
- uploads `terraform-dev-plan`
- runs controlled apply only via `workflow_dispatch` with `confirm_apply=true`
- now initializes Terraform in the clean apply runner before applying the downloaded plan artifact

## Remote Verification Limit

The GitHub CLI is not installed in this environment, so this sweep could not verify the actual remote secret inventory or workflow run history from the shell.

The remote repository is:

- `https://github.com/ProjectDataengineerUK/CoinGeckoanalytical.git`

## Remaining Evidence To Capture

The next evidence artifacts should come from GitHub Actions and Databricks, not more local scaffolding:

1. `terraform-dev-plan` artifact from the `terraform` workflow.
2. Reviewed `tfplan.txt` persisted into `.agentcodex/reports/`.
3. Controlled `dev` apply after plan review.
4. Databricks bundle deploy on `main`.
5. `databricks-live-sql-validation` artifact with real row counts.
6. Dated live validation report under `.agentcodex/reports/`.

## Practical Conclusion

The repo-local configuration surface is coherent and test-backed. The only remaining blockers are environment-side proof points: GitHub Actions secret availability, Terraform plan/apply execution, Databricks bundle deployment, and live SQL validation evidence.
