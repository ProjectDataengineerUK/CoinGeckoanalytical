# Databricks Notebooks

Thin workspace notebooks for Databricks users.

The production logic stays in versioned Python and SQL files so CI can test it. These notebooks provide familiar Databricks UI entrypoints for execution, validation, and operations review.

## Notebooks

- `01_ingest_coingecko_market.py`: runs the CoinGecko market ingestion path and displays Bronze landing counts.
- `02_validate_market_layers.py`: validates Bronze, Silver, Gold, and Genie metric views.
- `03_ops_readiness_review.py`: reviews operational readiness and Sentinela status views.

## Design Rule

Do not duplicate production logic in notebooks. Import or query the versioned assets under `databricks/`.
