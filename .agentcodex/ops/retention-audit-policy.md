# Retention And Audit Policy

## Purpose

Define the minimum retention and audit posture required for Phase 1 compliance and auditability claims.

## Records In Scope

- routed request metadata
- usage telemetry
- Sentinela alert events
- bundle and job run events
- governed answer provenance metadata

## Retention Baseline

- request and telemetry records: retain according to environment policy and operator review needs
- alert and readiness records: retain long enough for trend analysis and release review
- audit-sensitive traces: retain under the stricter governance-admin boundary

## Audit Rules

- every routed request must preserve `request_id`
- tenant-aware records must preserve `tenant_id`
- AI-assisted responses must preserve provenance and freshness metadata where applicable
- operational review should be able to trace from route outcome back to source dataset family and event metadata

## Environment Separation

- dev retention can be shorter and more disposable
- staging should be long enough to support release review
- prod retention must support audit and investigation requirements

## Phase 1 Limitation

This policy defines the baseline posture only.

Jurisdiction-specific legal retention schedules and enterprise overlays still need real implementation decisions later.
