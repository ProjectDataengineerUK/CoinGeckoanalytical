# Build Slice 2 BFF Routing Report

- date: `2026-04-30`
- project: `CoinGeckoAnalytical`
- slice: `WS2 frontend-to-backend routing foundation`
- result_type: `implemented`

## Delivered

- created `backend/routing_bff.py`
- created `backend/tests/test_routing_bff.py`
- updated `backend/README.md`

## What This Closes

- the project now has a single backend entry foundation for `frontend -> dashboard / Genie / copilot`
- the `frontend_to_routing` contract now has executable validation behavior in the backend layer
- `dashboard.market-overview` can now be reached through the same BFF surface that also routes analytical and narrative requests

## Verification

- `python3 -m unittest discover -s backend/tests -p 'test_*.py'`
- backend tests now pass with `28` tests total

## Remaining Work

- connect BFF routing to real Gold queries instead of demo datasets
- implement the real external frontend shell that calls the BFF path
- add a live request server or API boundary around the routing layer
- replace the copilot MVP branch with the real grounded copilot route

## Important Limitation

This is a routing foundation inside the repository, not a deployed public API.

The frontend is still placeholder-only and no live HTTP surface exists yet.
