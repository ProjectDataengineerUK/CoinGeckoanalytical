# Daily Flow

## Purpose

Define the repo-local daily operating ritual for building CoinGeckoAnalytical with AgentCodex.

## Start Of Day

1. Read `.agentcodex/history/CONTEXT-HISTORY.md`.
2. Read the active design artifact.
3. Confirm the current priority slice.
4. Record any scope or architecture shift in `.agentcodex/history/CONTEXT-HISTORY.md`.

## Planning Sequence

1. Check the active phase: `brainstorm`, `define`, `design`, `build`, or `ship`.
2. Select the relevant specialists from `.agentcodex/reports/specialist-routing-matrix-2026-04-29.md`.
3. Confirm whether the task changes architecture, contracts, governance, or observability.
4. Prefer durable artifacts over chat-only conclusions.

## Build-Day Flow

1. Pick one implementation slice.
2. Define expected inputs, outputs, and verification.
3. Update or create the relevant report in `.agentcodex/reports/`.
4. Keep telemetry, cost, and freshness implications visible in the work item.

## End Of Day

1. Update `.agentcodex/history/CONTEXT-HISTORY.md`.
2. Write or update a concise report under `.agentcodex/reports/`.
3. Capture blockers, open risks, and next action.
4. Do not end the day with architecture drift only in chat.

## Required Daily Questions

- what changed in the architecture or scope?
- what was implemented versus only designed?
- what new risk appeared in security, cost, or operations?
- what is the next smallest high-value slice?
