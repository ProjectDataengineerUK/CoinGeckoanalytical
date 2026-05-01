# Databricks Notebooks

Thin workspace notebooks for Databricks users.

The production logic stays in versioned Python and SQL files so CI can test it. These notebooks provide familiar Databricks UI entrypoints for execution, validation, and operations review.

The production Databricks Asset Bundle deploy path excludes this folder from job file sync. That keeps scheduled job deployment deterministic while preserving notebooks as source-controlled workspace entrypoints. Import or attach these notebooks explicitly when using them for exploration or operations review.

## Notebooks

- `01_ingest_coingecko_market.py`: runs the CoinGecko market ingestion path and displays Bronze landing counts.
- `02_validate_market_layers.py`: validates Bronze, Silver, Gold, and Genie metric views.
- `03_ops_readiness_review.py`: reviews operational readiness and Sentinela status views.

## Design Rule

Do not duplicate production logic in notebooks. Import or query the versioned assets under `databricks/`.
