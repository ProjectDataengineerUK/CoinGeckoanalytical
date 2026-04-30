# Build Slice 5 CI Split Report

- date: `2026-04-30`
- project: `CoinGeckoAnalytical`
- slice: `ci lint-contract-deploy split`

## Delivered

- split the GitHub Actions workflow into `lint`, `contract`, and `deploy` jobs
- made deploy conditional on push-to-main plus Databricks credentials and CLI availability
- updated the workflow contract test to assert the new job structure

## Verification

- the workflow YAML parses locally
- the workflow contract test passes locally
- backend tests still pass
- deploy gating is explicit and non-blocking when the Databricks CLI or credentials are missing

## Remaining Work

- run the workflow in GitHub Actions to confirm job gating
- install or provision the Databricks CLI in a deploy-capable environment
- optionally add linting beyond `compileall` later
