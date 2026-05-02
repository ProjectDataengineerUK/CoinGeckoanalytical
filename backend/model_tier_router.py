from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class ModelTier(str, Enum):
    LIGHT = "light"
    STANDARD = "standard"
    COMPLEX = "complex"


@dataclass(frozen=True)
class TierClassification:
    tier: ModelTier
    reason: str
    signals: tuple[str, ...]
    estimated_prompt_tokens: int


# Databricks Foundation Model API endpoint names (external model proxies)
DEFAULT_ENDPOINT_BY_TIER: dict[ModelTier, str] = {
    ModelTier.LIGHT: "databricks-claude-haiku-3-5",
    ModelTier.STANDARD: "databricks-claude-sonnet-4",
    ModelTier.COMPLEX: "databricks-claude-opus-4",
}

# Blended input+output cost estimate per 1K tokens (USD, approximate 2026 pricing)
COST_PER_1K_TOKENS: dict[ModelTier, float] = {
    ModelTier.LIGHT: 0.0008,
    ModelTier.STANDARD: 0.0040,
    ModelTier.COMPLEX: 0.0250,
}

_LIGHT_SIGNALS = (
    "what is the price",
    "current price",
    "price of",
    "how much is",
    "what's the price",
    "whats the price",
    "preço do",
    "cotação do",
    "market cap of",
    "is it up",
    "is it down",
    "subiu",
    "caiu",
)

_COMPLEX_SIGNALS = (
    "analyze the relationship",
    "portfolio analysis",
    "correlation between",
    "historical analysis",
    "macro regime",
    "risk assessment",
    "multi-asset",
    "across all assets",
    "comprehensive analysis",
    "deep dive",
    "defi and macro",
    "tvl and price",
    "compare macro",
    "explain why the market",
    "why is bitcoin",
    "why did the market",
    "analise de portfolio",
    "analise completa",
    "relacao entre",
)

_LIGHT_MAX_WORDS = 12
_LIGHT_MAX_TURNS = 1
_COMPLEX_MIN_WORDS = 60
_COMPLEX_MIN_TURNS = 5
_COMPLEX_MIN_ASSETS = 4


def _word_count(text: str) -> int:
    return len(text.split())


def classify_model_tier(
    message_text: str,
    asset_count: int = 0,
    conversation_turns: int = 0,
) -> TierClassification:
    lowered = message_text.lower().strip()
    words = _word_count(lowered)

    complex_hits = tuple(s for s in _COMPLEX_SIGNALS if s in lowered)
    light_hits = tuple(s for s in _LIGHT_SIGNALS if s in lowered)

    if (
        complex_hits
        or words >= _COMPLEX_MIN_WORDS
        or asset_count >= _COMPLEX_MIN_ASSETS
        or conversation_turns >= _COMPLEX_MIN_TURNS
    ):
        reason = (
            "complex_signal" if complex_hits
            else "long_query" if words >= _COMPLEX_MIN_WORDS
            else "high_asset_count" if asset_count >= _COMPLEX_MIN_ASSETS
            else "deep_conversation"
        )
        return TierClassification(
            tier=ModelTier.COMPLEX,
            reason=reason,
            signals=complex_hits,
            estimated_prompt_tokens=max(words * 2, 200),
        )

    if (
        light_hits
        and words <= _LIGHT_MAX_WORDS
        and conversation_turns <= _LIGHT_MAX_TURNS
        and asset_count <= 1
    ):
        return TierClassification(
            tier=ModelTier.LIGHT,
            reason="simple_factual_lookup",
            signals=light_hits,
            estimated_prompt_tokens=max(words * 2, 30),
        )

    return TierClassification(
        tier=ModelTier.STANDARD,
        reason="standard_market_analysis",
        signals=(),
        estimated_prompt_tokens=max(words * 2, 80),
    )


def estimate_cost_usd(tier: ModelTier, total_tokens: int) -> float:
    rate = COST_PER_1K_TOKENS.get(tier, COST_PER_1K_TOKENS[ModelTier.STANDARD])
    return round(total_tokens / 1000.0 * rate, 6)
