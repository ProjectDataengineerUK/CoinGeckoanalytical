from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
import tempfile
import unittest


MODULE_PATH = Path(__file__).resolve().parent.parent / "market_source_handoff.py"
SPEC = importlib.util.spec_from_file_location("market_source_handoff", MODULE_PATH)
market_source_handoff = importlib.util.module_from_spec(SPEC)
assert SPEC is not None and SPEC.loader is not None
sys.modules[SPEC.name] = market_source_handoff
SPEC.loader.exec_module(market_source_handoff)


class MarketSourceHandoffTests(unittest.TestCase):
    def test_write_market_source_handoff_file_creates_json_array(self) -> None:
        rows = [
            market_source_handoff.build_market_source_handoff_row(
                asset_id="bitcoin",
                symbol="btc",
                name="Bitcoin",
                market_cap=1850000000000,
                current_price=95000,
                total_volume=35000000000,
                circulating_supply=19500000,
                market_cap_rank=1,
                last_updated="2026-04-30T00:00:00Z",
                category="store_of_value",
            )
        ]

        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "market-source.json"
            written_path = market_source_handoff.write_market_source_handoff_file(path, rows)
            payload = written_path.read_text(encoding="utf-8")

        self.assertEqual(written_path, path)
        self.assertIn('"id": "bitcoin"', payload)
        self.assertIn('"symbol": "btc"', payload)
        self.assertIn('"market_cap_rank": 1', payload)

    def test_build_market_source_handoff_row_defaults(self) -> None:
        row = market_source_handoff.build_market_source_handoff_row(
            asset_id="ethereum",
            symbol="eth",
            name="Ethereum",
            market_cap=420000000000,
            current_price=3200,
            total_volume=18000000000,
            circulating_supply=120000000,
            market_cap_rank=2,
            last_updated="2026-04-30T00:00:00Z",
        )

        self.assertEqual(row["source_system"], "coingecko_api")
        self.assertEqual(row["payload_version"], "coingecko_markets_v1")
        self.assertIsNone(row["category"])


if __name__ == "__main__":
    unittest.main()
