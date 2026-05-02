from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

_PATH = Path(__file__).resolve().parent.parent / "model_tier_router.py"
spec = importlib.util.spec_from_file_location("model_tier_router", _PATH)
model_tier_router = importlib.util.module_from_spec(spec)  # type: ignore[arg-type]
sys.modules[spec.name] = model_tier_router
spec.loader.exec_module(model_tier_router)  # type: ignore[union-attr]


class ModelTierRouterTests(unittest.TestCase):
    def test_simple_price_lookup_is_light(self):
        result = model_tier_router.classify_model_tier(
            "What is the price of bitcoin?", asset_count=1
        )
        self.assertEqual(result.tier, model_tier_router.ModelTier.LIGHT)
        self.assertEqual(result.reason, "simple_factual_lookup")

    def test_short_query_without_light_signal_is_standard(self):
        result = model_tier_router.classify_model_tier(
            "What is happening in crypto today?", asset_count=1
        )
        self.assertEqual(result.tier, model_tier_router.ModelTier.STANDARD)

    def test_long_query_is_complex(self):
        long_query = " ".join(["analyze"] * 65)
        result = model_tier_router.classify_model_tier(long_query)
        self.assertEqual(result.tier, model_tier_router.ModelTier.COMPLEX)
        self.assertEqual(result.reason, "long_query")

    def test_high_asset_count_is_complex(self):
        result = model_tier_router.classify_model_tier(
            "Compare BTC, ETH, SOL, ADA, and DOT", asset_count=5
        )
        self.assertEqual(result.tier, model_tier_router.ModelTier.COMPLEX)
        self.assertEqual(result.reason, "high_asset_count")

    def test_deep_conversation_is_complex(self):
        result = model_tier_router.classify_model_tier(
            "Tell me more about the trend", conversation_turns=6
        )
        self.assertEqual(result.tier, model_tier_router.ModelTier.COMPLEX)
        self.assertEqual(result.reason, "deep_conversation")

    def test_complex_signal_triggers_complex_tier(self):
        result = model_tier_router.classify_model_tier(
            "Analyze the relationship between DeFi TVL and macro rates"
        )
        self.assertEqual(result.tier, model_tier_router.ModelTier.COMPLEX)
        self.assertEqual(result.reason, "complex_signal")
        self.assertIn("analyze the relationship", result.signals)

    def test_narrative_market_query_is_standard(self):
        result = model_tier_router.classify_model_tier(
            "Explain what is happening in the Ethereum ecosystem right now"
        )
        self.assertEqual(result.tier, model_tier_router.ModelTier.STANDARD)

    def test_light_with_multiple_assets_is_standard(self):
        result = model_tier_router.classify_model_tier(
            "What is the price of bitcoin?", asset_count=3
        )
        self.assertEqual(result.tier, model_tier_router.ModelTier.STANDARD)

    def test_light_with_conversation_history_is_standard(self):
        result = model_tier_router.classify_model_tier(
            "What is the price of bitcoin?", asset_count=1, conversation_turns=3
        )
        self.assertEqual(result.tier, model_tier_router.ModelTier.STANDARD)

    def test_estimate_cost_light_tier(self):
        cost = model_tier_router.estimate_cost_usd(
            model_tier_router.ModelTier.LIGHT, 1000
        )
        self.assertAlmostEqual(cost, 0.0008, places=4)

    def test_estimate_cost_standard_tier(self):
        cost = model_tier_router.estimate_cost_usd(
            model_tier_router.ModelTier.STANDARD, 1000
        )
        self.assertAlmostEqual(cost, 0.004, places=4)

    def test_estimate_cost_complex_tier(self):
        cost = model_tier_router.estimate_cost_usd(
            model_tier_router.ModelTier.COMPLEX, 1000
        )
        self.assertAlmostEqual(cost, 0.025, places=4)

    def test_complex_costs_more_than_light(self):
        light = model_tier_router.estimate_cost_usd(model_tier_router.ModelTier.LIGHT, 5000)
        standard = model_tier_router.estimate_cost_usd(model_tier_router.ModelTier.STANDARD, 5000)
        complex_ = model_tier_router.estimate_cost_usd(model_tier_router.ModelTier.COMPLEX, 5000)
        self.assertLess(light, standard)
        self.assertLess(standard, complex_)

    def test_default_endpoints_by_tier(self):
        endpoints = model_tier_router.DEFAULT_ENDPOINT_BY_TIER
        self.assertIn("gemma", endpoints[model_tier_router.ModelTier.LIGHT])
        self.assertIn("120b", endpoints[model_tier_router.ModelTier.STANDARD])
        self.assertIn("qwen", endpoints[model_tier_router.ModelTier.COMPLEX])

    def test_portfolio_analysis_signal_is_complex(self):
        result = model_tier_router.classify_model_tier("Give me a portfolio analysis for my holdings")
        self.assertEqual(result.tier, model_tier_router.ModelTier.COMPLEX)

    def test_price_of_signal_in_portuguese(self):
        result = model_tier_router.classify_model_tier(
            "qual é o preço do bitcoin?", asset_count=1
        )
        self.assertEqual(result.tier, model_tier_router.ModelTier.LIGHT)


if __name__ == "__main__":
    unittest.main()
