from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock

_MOD_PATH = Path(__file__).resolve().parent.parent / "copilot_orchestrator.py"
spec = importlib.util.spec_from_file_location("copilot_orchestrator", _MOD_PATH)
orchestrator = importlib.util.module_from_spec(spec)  # type: ignore[arg-type]
sys.modules[spec.name] = orchestrator
spec.loader.exec_module(orchestrator)  # type: ignore[union-attr]


def _make_mosaic(answer_text: str = "market insight", status: str = "completed") -> MagicMock:
    answer = MagicMock()
    answer.answer_text = answer_text
    answer.execution_status = status
    answer.token_count_hint = 120
    client = MagicMock()
    client.ask_mosaic.return_value = answer
    return client


def _make_config() -> MagicMock:
    return MagicMock()


class AgentResultTests(unittest.TestCase):
    def test_fields_are_accessible(self):
        result = orchestrator.AgentResult(
            agent_name="market_agent",
            answer_text="BTC is up",
            sources=("unity_catalog.market_gold.gold_market_rankings",),
            token_count=80,
            latency_ms=200,
            execution_status="completed",
        )
        self.assertEqual(result.agent_name, "market_agent")
        self.assertEqual(result.execution_status, "completed")
        self.assertEqual(len(result.sources), 1)

    def test_frozen_prevents_mutation(self):
        result = orchestrator.AgentResult(
            agent_name="x", answer_text="", sources=(), token_count=0, latency_ms=0, execution_status="failed",
        )
        with self.assertRaises((AttributeError, TypeError)):
            result.agent_name = "y"  # type: ignore[misc]


class OrchestratorResultTests(unittest.TestCase):
    def test_fields_are_accessible(self):
        result = orchestrator.OrchestratorResult(
            answer_text="synthesis",
            agent_results=(),
            total_tokens=300,
            total_latency_ms=800,
            sources=("s1", "s2"),
            execution_status="completed",
        )
        self.assertEqual(result.answer_text, "synthesis")
        self.assertEqual(result.total_tokens, 300)


class SourceForTests(unittest.TestCase):
    def test_known_agents_map_to_tables(self):
        self.assertIn("gold_market_rankings", orchestrator._source_for("market_agent"))
        self.assertIn("gold_macro_regime", orchestrator._source_for("macro_agent"))
        self.assertIn("gold_defi_protocols", orchestrator._source_for("defi_agent"))
        self.assertIn("gold_enriched_rankings", orchestrator._source_for("enriched_agent"))

    def test_unknown_agent_returns_name(self):
        self.assertEqual(orchestrator._source_for("custom_agent"), "custom_agent")


class FetchContextTests(unittest.TestCase):
    def test_returns_rows_from_dbsql(self):
        mock_client = MagicMock()
        mock_client.run_query.return_value = [{"asset_id": "bitcoin", "price_usd": 50000.0}]
        rows = orchestrator._fetch_context(mock_client, "SELECT 1 FROM {catalog}.t", "cgadev")
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["asset_id"], "bitcoin")

    def test_returns_empty_on_exception(self):
        mock_client = MagicMock()
        mock_client.run_query.side_effect = RuntimeError("connection refused")
        rows = orchestrator._fetch_context(mock_client, "SELECT 1 FROM {catalog}.t", "cgadev")
        self.assertEqual(rows, [])

    def test_returns_empty_when_run_query_returns_non_list(self):
        mock_client = MagicMock()
        mock_client.run_query.return_value = None
        rows = orchestrator._fetch_context(mock_client, "SELECT 1 FROM {catalog}.t", "cgadev")
        self.assertEqual(rows, [])


class RunMarketAgentTests(unittest.TestCase):
    def test_completed_result_has_correct_fields(self):
        mosaic = _make_mosaic("BTC leads the market.")
        result = orchestrator.run_market_agent(mosaic, _make_config(), "What is BTC doing?", [])
        self.assertEqual(result.execution_status, "completed")
        self.assertEqual(result.agent_name, "market_agent")
        self.assertEqual(result.answer_text, "BTC leads the market.")
        self.assertGreater(result.latency_ms, -1)

    def test_failed_mosaic_returns_failed_status(self):
        mosaic = _make_mosaic(status="error")
        result = orchestrator.run_market_agent(mosaic, _make_config(), "question", [])
        self.assertEqual(result.execution_status, "no_data")

    def test_exception_returns_failed_status(self):
        mosaic = MagicMock()
        mosaic.ask_mosaic.side_effect = RuntimeError("timeout")
        result = orchestrator.run_market_agent(mosaic, _make_config(), "question", [])
        self.assertEqual(result.execution_status, "failed")


class RunSynthAgentTests(unittest.TestCase):
    def _make_completed(self, name: str, text: str) -> orchestrator.AgentResult:
        return orchestrator.AgentResult(
            agent_name=name, answer_text=text, sources=(), token_count=50, latency_ms=100, execution_status="completed",
        )

    def _make_failed(self, name: str) -> orchestrator.AgentResult:
        return orchestrator.AgentResult(
            agent_name=name, answer_text="", sources=(), token_count=0, latency_ms=50, execution_status="failed",
        )

    def test_synth_combines_all_agent_sources(self):
        mosaic = _make_mosaic("Synthesis complete.")
        market_r = orchestrator.AgentResult(
            agent_name="market_agent", answer_text="BTC up", sources=("src_market",), token_count=50, latency_ms=100, execution_status="completed",
        )
        macro_r = orchestrator.AgentResult(
            agent_name="macro_agent", answer_text="rates stable", sources=("src_macro",), token_count=50, latency_ms=100, execution_status="completed",
        )
        defi_r = orchestrator.AgentResult(
            agent_name="defi_agent", answer_text="TVL growing", sources=("src_defi",), token_count=50, latency_ms=100, execution_status="completed",
        )
        result = orchestrator.run_synth_agent(mosaic, _make_config(), "question", market_r, macro_r, defi_r)
        self.assertEqual(result.execution_status, "completed")
        self.assertIn("src_market", result.sources)
        self.assertIn("src_macro", result.sources)
        self.assertIn("src_defi", result.sources)
        self.assertIn("copilot_orchestrator.synthesis", result.sources)

    def test_synth_fails_gracefully_on_exception(self):
        mosaic = MagicMock()
        mosaic.ask_mosaic.side_effect = RuntimeError("timeout")
        result = orchestrator.run_synth_agent(
            mosaic, _make_config(), "q",
            self._make_failed("market_agent"),
            self._make_failed("macro_agent"),
            self._make_failed("defi_agent"),
        )
        self.assertEqual(result.execution_status, "failed")


class OrchestrateTests(unittest.TestCase):
    def test_no_dbsql_runs_with_empty_context(self):
        mosaic = _make_mosaic("multi-agent answer")
        result = orchestrator.orchestrate("What is the market doing?", mosaic, _make_config())
        self.assertIn(result.execution_status, {"completed", "failed"})
        self.assertEqual(len(result.agent_results), 4)  # market, macro, defi, synth

    def test_returns_failed_when_all_domain_agents_fail(self):
        mosaic = MagicMock()
        mosaic.ask_mosaic.side_effect = RuntimeError("all down")
        result = orchestrator.orchestrate("question", mosaic, _make_config())
        self.assertEqual(result.execution_status, "failed")
        self.assertEqual(result.answer_text, "")
        self.assertEqual(len(result.agent_results), 3)  # only domain agents, no synth

    def test_sources_are_deduplicated(self):
        mosaic = _make_mosaic("answer")
        result = orchestrator.orchestrate("question", mosaic, _make_config())
        if result.execution_status == "completed":
            self.assertEqual(len(result.sources), len(set(result.sources)))

    def test_total_tokens_sums_all_agents(self):
        mosaic = _make_mosaic("answer")
        result = orchestrator.orchestrate("question", mosaic, _make_config())
        if result.execution_status == "completed":
            expected = sum(r.token_count for r in result.agent_results)
            self.assertEqual(result.total_tokens, expected)

    def test_dbsql_context_is_passed_to_agents(self):
        mock_dbsql = MagicMock()
        mock_dbsql.run_query.return_value = [{"asset_id": "bitcoin", "price_usd": 50000.0}]
        mosaic = _make_mosaic("answer with context")
        orchestrator.orchestrate("question", mosaic, _make_config(), dbsql_client=mock_dbsql)
        self.assertGreater(mock_dbsql.run_query.call_count, 0)


if __name__ == "__main__":
    unittest.main()
