from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def build_market_source_handoff_row(
    asset_id: str,
    symbol: str,
    name: str,
    market_cap: float,
    current_price: float,
    total_volume: float,
    circulating_supply: float,
    market_cap_rank: int,
    last_updated: str,
    category: str | None = None,
    source_system: str = "coingecko_api",
    payload_version: str = "coingecko_markets_v1",
) -> dict[str, Any]:
    return {
        "id": asset_id,
        "symbol": symbol,
        "name": name,
        "category": category,
        "market_cap": market_cap,
        "current_price": current_price,
        "total_volume": total_volume,
        "circulating_supply": circulating_supply,
        "market_cap_rank": market_cap_rank,
        "last_updated": last_updated,
        "source_system": source_system,
        "payload_version": payload_version,
    }


def write_market_source_handoff_file(
    path: str | Path,
    rows: list[dict[str, Any]],
) -> Path:
    target_path = Path(path)
    target_path.parent.mkdir(parents=True, exist_ok=True)
    target_path.write_text(json.dumps(rows, indent=2, sort_keys=True), encoding="utf-8")
    return target_path
