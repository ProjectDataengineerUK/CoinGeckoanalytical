# Frontend Shell

## Purpose

Define the public SaaS frontend shell for CoinGeckoAnalytical.

## Responsibilities

- render the authenticated public experience
- collect tenant and session context
- route user intent to dashboard or chat flows
- call the backend-for-frontend layer, not Databricks services directly

## UI Entry Points

### Dashboard

- market overview
- rankings
- movers
- dominance
- comparison views

### Chat

- structured analytics questions
- guided market copilot questions
- provenance-aware answer rendering

## Tenant Context

Required frontend context:

- `tenant_id`
- `user_id`
- `session_id`
- `locale`
- `plan_tier`

## Auth Boundary

- the frontend must rely on external identity/session handling
- the frontend must never embed raw Databricks credentials
- the frontend must forward only signed or session-bound identity to the BFF

## Rendering Rules

- analytics answers should emphasize freshness and structured evidence
- copilot answers should emphasize citations and confidence metadata
- warnings should be visible for stale, partial, or policy-limited responses

## Initial Routes

- `/`
- `/dashboard`
- `/chat`
- `/admin` reserved for internal surfaces only
