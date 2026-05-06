from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path
from typing import Any

_CLIENT_PATH = Path(__file__).resolve().parent.parent / "mosaic_copilot_client.py"


def _load(name: str, path: Path) -> Any:
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


client = _load("mosaic_copilot_client", _CLIENT_PATH)


class TestLoadConfigFromEnv(unittest.TestCase):
    def test_returns_config_for_valid_databricks_host(self) -> None:
        env = {"DATABRICKS_HOST": "https://adb-123.azuredatabricks.net"}
        config = client.load_config_from_env(env)
        self.assertIsNotNone(config)
        self.assertEqual(config.host, "https://adb-123.azuredatabricks.net")

    def test_returns_none_for_untrusted_host(self) -> None:
        env = {"DATABRICKS_HOST": "https://evil.example.com"}
        self.assertIsNone(client.load_config_from_env(env))


class TestResponseParsing(unittest.TestCase):
    def test_extracts_text_from_responses_output_blocks(self) -> None:
        payload = {
            "output": [
                {
                    "type": "reasoning",
                    "summary": [
                        {"type": "summary_text", "text": "reasoning text"},
                    ],
                },
                {
                    "type": "text",
                    "text": "Oi! Como posso ajudar você hoje?",
                },
            ]
        }

        self.assertEqual(
            client._extract_answer_text(payload),
            "reasoning text\n\nOi! Como posso ajudar você hoje?",
        )

    def test_extracts_text_from_stringified_block_list(self) -> None:
        payload = {
            "choices": [
                {
                    "message": {
                        "content": (
                            "[{'type': 'reasoning', 'summary': [{'type': 'summary_text', "
                            "'text': 'resumo interno'}]}, {'type': 'text', 'text': 'Resposta final'}]"
                        )
                    }
                }
            ]
        }

        self.assertEqual(
            client._extract_answer_text(payload),
            "resumo interno\n\nResposta final",
        )


if __name__ == "__main__":
    unittest.main()
