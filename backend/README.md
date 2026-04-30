# Backend

Backend-for-frontend and governed serving placeholder.

This layer should route requests to structured analytics via `Genie` and to the coded copilot via `Mosaic AI Agent Framework`.

## Build Slice 3 Scope

- validate request envelopes from the frontend
- route structured analytics requests to `Genie`
- route narrative or grounded research requests to the copilot
- attach tenant, locale, policy, and audit context
- never expose raw workspace credentials to the public frontend
