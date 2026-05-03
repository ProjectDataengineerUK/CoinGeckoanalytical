from __future__ import annotations

import importlib.util
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

_REPO_ROOT = Path(__file__).resolve().parents[3]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

_genie_mod: Any = None
_genie_config: Any = None


@dataclass(frozen=True)
class GenieResult:
    answer_text: str
    generated_query: str | None
    execution_status: str
    latency_ms: int


def _load() -> bool:
    global _genie_mod, _genie_config
    if _genie_mod is not None:
        return _genie_config is not None
    try:
        spec = importlib.util.spec_from_file_location(
            "genie_client",
            _REPO_ROOT / "backend" / "genie_client.py",
        )
        mod = importlib.util.module_from_spec(spec)  # type: ignore[arg-type]
        spec.loader.exec_module(mod)  # type: ignore[union-attr]
        _genie_mod = mod
        _genie_config = mod.load_config_from_env()
    except Exception:
        pass
    return _genie_config is not None


def ask(question: str) -> GenieResult:
    if not _load():
        return GenieResult(
            answer_text="Genie indisponível — variáveis de ambiente não configuradas.",
            generated_query=None,
            execution_status="unavailable",
            latency_ms=0,
        )
    try:
        answer = _genie_mod.ask_genie(_genie_config, question)
        return GenieResult(
            answer_text=answer.answer_text,
            generated_query=answer.generated_query,
            execution_status=answer.execution_status,
            latency_ms=answer.latency_ms,
        )
    except Exception as exc:
        return GenieResult(
            answer_text=f"Erro ao consultar Genie: {exc}",
            generated_query=None,
            execution_status="failed",
            latency_ms=0,
        )
