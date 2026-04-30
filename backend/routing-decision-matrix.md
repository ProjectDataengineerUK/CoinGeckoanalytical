# Routing Decision Matrix

## Purpose

Define the first routing rules between frontend, Genie, and copilot.

| User Intent | Route | Reason |
|-------------|-------|--------|
| ranking, movers, comparisons | Genie | structured analytics fit |
| general market question with provenance | copilot | reasoning and citations needed |
| dashboard browse | BFF + Gold APIs | low-latency public UX |
| internal operational tool | Databricks Apps | workspace-adjacent utility only |

## Escalation Rules

- if a structured question exceeds the analytical scope, redirect to the copilot
- if the copilot request is simple and clearly metric-based, prefer Genie
- if the request is not tenant-safe, refuse explicitly

## Audit Requirements

- record selected route
- record request id
- record tenant id
- record model or engine
- record latency and token usage when applicable
