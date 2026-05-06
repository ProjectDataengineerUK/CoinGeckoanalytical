# Copilot MVP

This slice provides the first grounded market-answer workflow.

## Responsibilities

- route structured requests to Genie
- keep narrative requests in the copilot path
- preserve provenance and freshness metadata
- emit usage telemetry compatible with the project schema
- build Databricks landing rows for the telemetry observability table

## Current Limitations

- runtime still depends on live Databricks credentials and serving endpoints being present in the target workspace
- rate limiting and abuse protection are still pending hardening work
- PR-time integration tests against a live SQL warehouse are still absent; live validation remains deploy/runtime evidence
