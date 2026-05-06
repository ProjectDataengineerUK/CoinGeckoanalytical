from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path


MODULE_PATH = (
    Path(__file__).resolve().parents[1]
    / "apps"
    / "cga-analytics"
    / "services"
    / "genie_service.py"
)
SPEC = importlib.util.spec_from_file_location("cga_genie_service", MODULE_PATH)
genie_service = importlib.util.module_from_spec(SPEC)
assert SPEC is not None and SPEC.loader is not None
sys.modules[SPEC.name] = genie_service
SPEC.loader.exec_module(genie_service)


class _FakeAnswer:
    def __init__(self, answer_text: str, generated_query: str | None, execution_status: str, latency_ms: int):
        self.answer_text = answer_text
        self.generated_query = generated_query
        self.execution_status = execution_status
        self.latency_ms = latency_ms


class _FakeBackend:
    @staticmethod
    def ask_genie(_config, _question):
        return _FakeAnswer("", "SELECT 1", "no_answer", 210)


class GenieServiceTests(unittest.TestCase):
    def test_returns_unavailable_message_when_backend_cannot_load(self) -> None:
        original = genie_service._load
        try:
            genie_service._load = lambda: False
            result = genie_service.ask("Top 5 assets")
        finally:
            genie_service._load = original

        self.assertEqual(result.execution_status, "unavailable")
        self.assertIn("Genie indisponível", result.answer_text)

    def test_replaces_no_answer_with_operator_message(self) -> None:
        original_load = genie_service._load
        original_mod = genie_service._genie_mod
        original_config = genie_service._genie_config
        try:
            genie_service._load = lambda: True
            genie_service._genie_mod = _FakeBackend()
            genie_service._genie_config = object()
            result = genie_service.ask("Top 5 assets")
        finally:
            genie_service._load = original_load
            genie_service._genie_mod = original_mod
            genie_service._genie_config = original_config

        self.assertEqual(result.execution_status, "no_answer")
        self.assertIn("Genie não retornou texto final", result.answer_text)
        self.assertEqual(result.generated_query, "SELECT 1")


if __name__ == "__main__":
    unittest.main()
