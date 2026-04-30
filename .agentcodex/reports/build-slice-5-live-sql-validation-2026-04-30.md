# Build Slice 5 Live SQL Validation

- date: `2026-04-30`
- project: `CoinGeckoAnalytical`
- slice: `github actions live sql validation`
- result_type: `implemented`

## Delivered

- created `databricks/live_sql_validation.py`
- created `databricks/test_live_sql_validation.py`
- updated `.github/workflows/ci.yml`
- updated `repo_tests/test_ci_workflow.py`
- updated `databricks/deployment_runbook.md`
- updated `databricks/README.md`
- updated `.agentcodex/reports/dev-live-validation-checklist-2026-04-30.md`
- updated `.agentcodex/reports/status-handoff-2026-04-30.md`

## What This Closes

- GitHub Actions can now perform workspace-side SQL row-count validation after the deploy and ingestion steps
- the validation is optional and guarded by `DATABRICKS_SQL_WAREHOUSE_ID`
- live SQL results are written to a JSON artifact for later review
- the operator-facing docs now state clearly that deploy continues with `DATABRICKS_HOST` and `DATABRICKS_TOKEN`, while the full live SQL Actions path additionally needs the warehouse secret

## Verification

- local unit tests should cover request payload shape, response summarization, output writing, and missing-env skip behavior
- workflow contract tests should confirm the new validation and artifact steps are present

## Remaining Work

- add a durable repo-local report from the first successful live validation run
- decide whether failed live SQL row counts should hard-fail the deploy job or remain advisory in the first iteration
- execute the next `push` to `main` in an environment where the GitHub secret is present, then confirm the `databricks-live-sql-validation` artifact is produced
