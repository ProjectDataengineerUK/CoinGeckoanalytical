# Build Slice 1 Databricks Notebooks - 2026-05-01

## Problem

The Databricks bundle used tested `spark_python_task` jobs, but the workspace did not expose the familiar notebook structure many Databricks teams expect.

## Decision

Keep production logic in versioned Python and SQL files for CI/CD, but add thin Databricks notebooks as workspace entrypoints and review surfaces.

## Delivered

- `databricks/notebooks/01_ingest_coingecko_market.py`
- `databricks/notebooks/02_validate_market_layers.py`
- `databricks/notebooks/03_ops_readiness_review.py`
- `databricks/notebooks/README.md`
- `databricks/test_notebook_assets.py`

Updated:

- `databricks/README.md`
- `databricks/bundle-manifest.md`
- `databricks/validate_bundle.py`
- `databricks/test_validate_bundle.py`

## Notebook Roles

- `01_ingest_coingecko_market.py`: runs the versioned ingestion module and displays Bronze landing counts.
- `02_validate_market_layers.py`: shows Bronze, Silver, Gold, and Genie metric-view row counts.
- `03_ops_readiness_review.py`: displays ops readiness, route readiness, bundle status, Sentinela status, and alert backlog.

## Guardrail

Notebooks must stay thin. They should call or query versioned assets rather than becoming the only place where production logic lives.

## Verification

Run locally:

- `python3 -m unittest databricks.test_notebook_assets`
- `python3 -m unittest databricks.test_validate_bundle`
- `python3 databricks/validate_bundle.py`
