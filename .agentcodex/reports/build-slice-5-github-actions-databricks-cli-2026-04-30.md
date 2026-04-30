# Build Slice 5 GitHub Actions Databricks CLI

- date: `2026-04-30`
- project: `CoinGeckoAnalytical`
- slice: `github actions live databricks prerequisites`
- result_type: `implemented`

## Delivered

- updated `databricks/market_source_ingestion_job.py` to accept runtime CLI flags
- updated `databricks/test_market_source_ingestion_job.py`
- updated `.github/workflows/ci.yml`
- updated `repo_tests/test_ci_workflow.py`

## What This Closes

- GitHub Actions no longer depends on a preinstalled `databricks` binary in the runner image
- the live deploy job can pass the repo fixture payload directly into `market_source_ingestion_job`
- the first live smoke for Bronze landing is now executable from CI without inventing an ad hoc payload step

## Verification

- local tests should cover CLI argument parsing and workflow expectations
- the workflow now installs the Databricks CLI and runs market ingestion with explicit payload and target table

## Remaining Work

- add live SQL verification for Silver, Gold, and Genie if a workspace-side SQL execution path is chosen
- capture the first successful live run into a dedicated workspace validation report
