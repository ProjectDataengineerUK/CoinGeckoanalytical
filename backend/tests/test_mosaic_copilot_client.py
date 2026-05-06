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
        self.assertEqual(config.temperature, 0.15)
        self.assertEqual(config.top_p, 0.20)
        self.assertEqual(config.max_output_tokens, 700)

    def test_returns_none_for_untrusted_host(self) -> None:
        env = {"DATABRICKS_HOST": "https://evil.example.com"}
        self.assertIsNone(client.load_config_from_env(env))

    def test_reads_generation_controls_from_env(self) -> None:
        env = {
            "DATABRICKS_HOST": "https://adb-123.azuredatabricks.net",
            "DATABRICKS_MOSAIC_TEMPERATURE": "0.05",
            "DATABRICKS_MOSAIC_TOP_P": "0.10",
            "DATABRICKS_MOSAIC_MAX_OUTPUT_TOKENS": "320",
        }
        config = client.load_config_from_env(env)
        self.assertIsNotNone(config)
        self.assertEqual(config.temperature, 0.05)
        self.assertEqual(config.top_p, 0.10)
        self.assertEqual(config.max_output_tokens, 320)


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
            "Oi! Como posso ajudar você hoje?",
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
            "Resposta final",
        )

    def test_strips_meta_wrapper_and_keeps_user_facing_answer(self) -> None:
        payload = {
            "choices": [
                {
                    "message": {
                        "content": (
                            "The user writes in Portuguese: \"posso compra btc\". "
                            "Likely they ask guidance.\n"
                            "Claro! Comprar Bitcoin (BTC) e relativamente simples hoje em dia."
                        )
                    }
                }
            ]
        }

        self.assertEqual(
            client._extract_answer_text(payload),
            "Claro! Comprar Bitcoin (BTC) e relativamente simples hoje em dia.",
        )


if __name__ == "__main__":
    unittest.main()
