from __future__ import annotations

import importlib.util
import json
import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

_JOB_PATH = Path(__file__).resolve().parent.parent / "jobs" / "fred_macro_ingestion_job.py"
spec = importlib.util.spec_from_file_location("fred_macro_ingestion_job", _JOB_PATH)
fred_macro_ingestion_job = importlib.util.module_from_spec(spec)  # type: ignore[arg-type]
sys.modules[spec.name] = fred_macro_ingestion_job
spec.loader.exec_module(fred_macro_ingestion_job)  # type: ignore[union-attr]


class FredMacroIngestionJobTests(unittest.TestCase):
    def test_normalize_observation_maps_fields(self):
        obs = {"date": "2026-04-01", "value": "4.45"}
        row = fred_macro_ingestion_job.normalize_observation("DGS10", "10yr_treasury_yield", obs)
        self.assertIsNotNone(row)
        self.assertEqual(row["source_system"], "fred")
        self.assertEqual(row["source_record_id"], "DGS10:2026-04-01")
        self.assertEqual(row["series_id"], "DGS10")
        self.assertEqual(row["series_name"], "10yr_treasury_yield")
        self.assertAlmostEqual(row["value"], 4.45)
        self.assertEqual(row["payload_version"], "fred_observations_v1")

    def test_normalize_observation_skips_missing_value(self):
        obs = {"date": "2026-04-01", "value": "."}
        result = fred_macro_ingestion_job.normalize_observation("DGS10", "10yr_treasury_yield", obs)
        self.assertIsNone(result)

    def test_normalize_observation_skips_empty_date(self):
        obs = {"date": "", "value": "4.0"}
        result = fred_macro_ingestion_job.normalize_observation("DGS10", "10yr_treasury_yield", obs)
        self.assertIsNone(result)

    def test_main_returns_zero_rows_when_no_api_key(self):
        class FakeSpark:
            pass
        result = fred_macro_ingestion_job.main(FakeSpark(), api_key=None)
        self.assertEqual(result.rows_written, 0)

    def test_main_returns_zero_rows_when_skip_live(self):
        class FakeSpark:
            pass
        result = fred_macro_ingestion_job.main(FakeSpark(), api_key="fake_key", skip_live=True)
        self.assertEqual(result.rows_written, 0)

    def test_fetch_series_calls_fred_api(self):
        sample_obs = [{"date": "2026-04-01", "value": "4.45"}]
        response_body = json.dumps({"observations": sample_obs})
        with patch("urllib.request.urlopen") as mock_urlopen:
            mock_response = MagicMock()
            mock_response.read.return_value = response_body.encode()
            mock_response.__enter__ = lambda s: s
            mock_response.__exit__ = MagicMock(return_value=False)
            mock_urlopen.return_value = mock_response
            result = fred_macro_ingestion_job.fetch_series("DGS10", "test_key")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["value"], "4.45")

    def test_build_fred_url_includes_series_and_key(self):
        url = fred_macro_ingestion_job.build_fred_url("DGS10", "mykey")
        self.assertIn("series_id=DGS10", url)
        self.assertIn("api_key=mykey", url)
        self.assertIn("file_type=json", url)

    def test_default_target_table_is_fully_qualified(self):
        self.assertEqual(
            fred_macro_ingestion_job.DEFAULT_TARGET_TABLE,
            "cgadev.market_bronze.bronze_fred_macro",
        )

    def test_parse_runtime_args_recognises_skip_live(self):
        args = fred_macro_ingestion_job.parse_runtime_args(["--skip-live"])
        self.assertTrue(args["skip_live"])


if __name__ == "__main__":
    unittest.main()
