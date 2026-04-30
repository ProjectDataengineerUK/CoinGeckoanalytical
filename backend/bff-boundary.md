# BFF Boundary

## Purpose

Define the backend-for-frontend layer that mediates all public UI requests.

## Responsibilities

- normalize frontend requests
- enforce tenant-aware authorization checks
- route requests to `Genie` or the copilot path
- attach audit metadata
- record usage telemetry

## Request Handling Rules

1. accept only validated frontend contracts
2. reject requests missing tenant or session context
3. classify the request as analytics or copilot
4. enrich with workspace or policy context
5. call the correct downstream engine

## Downstream Targets

- `Genie` for structured analytical NLQ
- `Mosaic AI Agent Framework` for market reasoning and grounded narrative answers
- internal admin workflows only when explicitly allowed

## Security Rules

- no direct browser-to-Databricks credential path
- no cross-tenant context leakage
- no unscoped access to raw evidence or logs

## Output Rules

- return the unified response envelope
- include freshness and confidence metadata when available
- include refusal or degradation warnings when policy requires it
