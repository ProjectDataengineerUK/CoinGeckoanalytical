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
    / "copilot_service.py"
)
SPEC = importlib.util.spec_from_file_location("cga_copilot_service", MODULE_PATH)
copilot_service = importlib.util.module_from_spec(SPEC)
assert SPEC is not None and SPEC.loader is not None
sys.modules[SPEC.name] = copilot_service
SPEC.loader.exec_module(copilot_service)


class _FakeBackend:
    class CopilotRequest:
        def __init__(self, **kwargs):
            self.payload = kwargs

    @staticmethod
    def build_copilot_response(_request):
        return {
            "body": "",
            "routing": {"model_tier": "standard", "latency_ms": 42},
            "warnings": ["empty_body"],
            "citations": [],
        }


class CopilotServiceTests(unittest.TestCase):
    def test_returns_unavailable_message_when_backend_cannot_load(self) -> None:
        original = copilot_service._load
        try:
            copilot_service._load = lambda: None
            result = copilot_service.ask("Analise BTC")
        finally:
            copilot_service._load = original

        self.assertEqual(result.model_tier, "unavailable")
        self.assertIn("Copilot indisponível", result.body)

    def test_replaces_empty_body_with_explicit_fallback_message(self) -> None:
        original = copilot_service._load
        try:
            copilot_service._load = lambda: _FakeBackend()
            result = copilot_service.ask("Analise BTC", selected_assets=["bitcoin"])
        finally:
            copilot_service._load = original

        self.assertEqual(result.model_tier, "standard")
        self.assertIn("Copilot sem resposta útil", result.body)
        self.assertIn("empty_body", result.warnings)


if __name__ == "__main__":
    unittest.main()
