# Backend

Backend-for-frontend and governed serving placeholder.

This layer should route requests to structured analytics via `Genie` and to the coded copilot via `Mosaic AI Agent Framework`.

## Build Slice 3 Scope

- validate request envelopes from the frontend
- route structured analytics requests to `Genie`
- route narrative or grounded research requests to the copilot
- attach tenant, locale, policy, and audit context
- never expose raw workspace credentials to the public frontend
- build Databricks-ready telemetry rows for the ops landing table
- write telemetry handoff files for the Databricks ingestion job

## Concrete Assets

- `dashboard_market_overview.py`
- `routing_bff.py`
- `copilot_mvp.py`
- `sentinela.py`
- `telemetry_handoff.py`
- `market_source_handoff.py`
- `notification_handoff.py`
- `tests/test_dashboard_market_overview.py`
- `tests/test_routing_bff.py`
- `tests/test_copilot_mvp.py`
- `tests/test_sentinela.py`
- `tests/test_telemetry_handoff.py`
- `tests/test_market_source_handoff.py`
- `tests/test_notification_handoff.py`
