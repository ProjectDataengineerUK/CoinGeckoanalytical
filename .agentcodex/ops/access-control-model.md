# Access Control Model

## Purpose

Define the minimum access-control posture required for the first real CoinGeckoAnalytical build slice.

## Access Domains

- `public product access`: authenticated tenant end users using the external frontend
- `operator access`: platform and operations users reviewing telemetry, alerts, and readiness
- `admin access`: elevated governance and release control
- `service access`: backend and Databricks service principals executing governed flows

## Baseline Role Model

### End User

- can access dashboard, governed analytical responses, and copilot responses within tenant policy
- cannot access raw telemetry tables, alert queues, audit views, or admin surfaces

### Analyst

- inherits end-user access
- may receive broader governed analytical scope inside the same tenant plan
- cannot bypass backend route and policy enforcement

### Institutional Reviewer

- inherits analyst access
- can access additional provenance, freshness, and review metadata allowed by plan and tenant policy
- cannot access platform-global operational data

### Operator

- can access telemetry observability, alert views, readiness checks, and operational notebooks
- can review degraded-state behavior and route health
- cannot access secrets directly through repo-local tooling

### Admin

- can approve governed release posture, review compliance-sensitive events, and manage control surfaces
- access is separate from routine operator access

## Enforcement Rules

- the frontend never talks directly to workspace-bound AI or analytical services
- the backend attaches `tenant_id`, `user_id`, `policy_context`, and route metadata before execution
- all AI and analytical requests are logged with request-scoped identifiers
- operational and audit storage is tenant-aware where applicable and role-restricted by default

## Resource Classification

- `shared governed market intelligence`: dashboard Gold views and governed metric views
- `tenant-scoped operational data`: usage telemetry, alert events, audit traces, and future tenant configuration
- `restricted control surfaces`: readiness dashboards, internal Databricks Apps, release gates, and admin review assets

## Immediate Control Requirements

- tenant isolation test coverage for routed requests
- separate access posture for end-user, operator, and admin surfaces
- governed read-only access for public analytical serving assets
- restricted write access for ingestion, telemetry landing, and alert landing jobs
