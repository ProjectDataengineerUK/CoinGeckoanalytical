# Frontend

Public SaaS frontend for CoinGeckoAnalytical.

This surface stays outside Databricks and talks only to the backend-for-frontend layer.

## Current Slice

- `index.html`: public shell with dashboard/chat entry points
- `app.css`: product styling and responsive layout
- `app.js`: local mock + BFF-ready request/response rendering
- `frontend-shell.md`: behavior and responsibilities
- `auth-and-tenant-boundary.md`: tenant and session rules

## Runtime Contract

- browser collects tenant, session, locale, and plan context
- browser never handles Databricks credentials directly
- BFF returns a single response envelope for dashboard or copilot rendering

## Local Mode

Open `index.html` directly or serve the folder with any static server.

If `window.__CGA_API_BASE__` is set, the shell will POST to `${API_BASE}/routing`.

## Notes

- dashboard queries use the structured analytics path
- chat questions route to Genie or copilot based on the BFF decision
- the shell includes a safe fallback mock so layout and state can be reviewed without backend wiring
