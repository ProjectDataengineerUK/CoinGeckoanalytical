from __future__ import annotations

import importlib.util
import json
import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

_JOB_PATH = Path(__file__).resolve().parent.parent / "jobs" / "defillama_ingestion_job.py"
spec = importlib.util.spec_from_file_location("defillama_ingestion_job", _JOB_PATH)
defillama_ingestion_job = importlib.util.module_from_spec(spec)  # type: ignore[arg-type]
sys.modules[spec.name] = defillama_ingestion_job
spec.loader.exec_module(defillama_ingestion_job)  # type: ignore[union-attr]


class DefiLlamaIngestionJobTests(unittest.TestCase):
    def _sample_raw(self) -> dict:
        return {
            "slug": "uniswap",
            "name": "Uniswap",
            "chain": "Ethereum",
            "category": "Dexes",
            "tvl": 3_500_000_000.0,
            "fees": 1_200_000.0,
            "revenue": 400_000.0,
            "mcap": 7_000_000_000.0,
        }

    def test_normalize_protocol_row_maps_fields(self):
        row = defillama_ingestion_job.normalize_protocol_row(self._sample_raw())
        self.assertIsNotNone(row)
        self.assertEqual(row["source_system"], "defillama")
        self.assertEqual(row["source_record_id"], "uniswap")
        self.assertEqual(row["protocol_slug"], "uniswap")
        self.assertEqual(row["protocol_name"], "Uniswap")
        self.assertEqual(row["tvl_usd"], 3_500_000_000.0)
        self.assertAlmostEqual(row["mcap_tvl_ratio"], 2.0, places=2)
        self.assertEqual(row["payload_version"], "defillama_protocols_v1")

    def test_normalize_protocol_row_returns_none_when_tvl_missing(self):
        raw = self._sample_raw()
        del raw["tvl"]
        self.assertIsNone(defillama_ingestion_job.normalize_protocol_row(raw))

    def test_normalize_protocol_row_returns_none_when_slug_missing(self):
        raw = {"name": "", "tvl": 1000}
        self.assertIsNone(defillama_ingestion_job.normalize_protocol_row(raw))

    def test_normalize_protocol_rows_filters_invalid(self):
        rows = [self._sample_raw(), {"name": "", "tvl": None}]
        result = defillama_ingestion_job.normalize_protocol_rows(rows)
        self.assertEqual(len(result), 1)

    def test_write_protocol_rows_uses_saveAsTable(self):
        class FakeWrite:
            def mode(self, _): return self
            def format(self, _): return self
            def saveAsTable(self, t): self.table = t

        class FakeDF:
            write = FakeWrite()
            def count(self): return 1
            def dropDuplicates(self, _): return self

        class FakeSpark:
            def createDataFrame(self, _): return FakeDF()

        rows = [defillama_ingestion_job.normalize_protocol_row(self._sample_raw())]
        result = defillama_ingestion_job.write_protocol_rows(FakeSpark(), rows)
        self.assertEqual(result.target_table, defillama_ingestion_job.DEFAULT_TARGET_TABLE)

    def test_fetch_protocols_calls_defillama_api(self):
        sample = [self._sample_raw()]
        with patch("urllib.request.urlopen") as mock_urlopen:
            mock_response = MagicMock()
            mock_response.read.return_value = json.dumps(sample).encode()
            mock_response.__enter__ = lambda s: s
            mock_response.__exit__ = MagicMock(return_value=False)
            mock_urlopen.return_value = mock_response
            result = defillama_ingestion_job.fetch_protocols()
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["slug"], "uniswap")

    def test_default_target_table_is_fully_qualified(self):
        self.assertEqual(
            defillama_ingestion_job.DEFAULT_TARGET_TABLE,
            "cgadev.market_bronze.bronze_defillama_protocols",
        )


if __name__ == "__main__":
    unittest.main()
