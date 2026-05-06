from __future__ import annotations

import importlib.util
import logging
import sys
import threading
from dataclasses import dataclass
from pathlib import Path
from typing import Any

_log = logging.getLogger(__name__)

_REPO_ROOT = Path(__file__).resolve().parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

_genie_mod: Any = None
_genie_config: Any = None
_load_lock = threading.Lock()


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
    with _load_lock:
        if _genie_mod is not None:
            return _genie_config is not None
        try:
            spec = importlib.util.spec_from_file_location(
                "genie_client",
                _REPO_ROOT / "backend" / "genie_client.py",
            )
            mod = importlib.util.module_from_spec(spec)  # type: ignore[arg-type]
            sys.modules["genie_client"] = mod
            spec.loader.exec_module(mod)  # type: ignore[union-attr]
            _genie_mod = mod
            _genie_config = mod.load_config_from_env()
        except Exception:
            _log.error("Failed to load app-local genie backend", exc_info=True)
    return _genie_config is not None


def ask(question: str) -> GenieResult:
    clean_question = question.strip()
    _log.info("Genie request received: chars=%d", len(clean_question))
    if not _load():
        return GenieResult(
            answer_text="Genie indisponível — variáveis de ambiente não configuradas.",
            generated_query=None,
            execution_status="unavailable",
            latency_ms=0,
        )
    try:
        answer = _genie_mod.ask_genie(_genie_config, clean_question)
        answer_text = (answer.answer_text or "").strip()
        execution_status = answer.execution_status
        if execution_status == "completed" and not answer_text:
            execution_status = "no_answer"
        if execution_status == "no_answer":
            answer_text = (
                "Genie não retornou texto final para esta consulta. "
                "Tente reformular a pergunta ou verifique os logs do app."
            )
        elif execution_status == "failed":
            answer_text = (
                "Genie não conseguiu concluir a consulta. "
                "Verifique permissões do Space/Warehouse ou os logs do servidor."
            )
        elif execution_status == "query_result_expired":
            answer_text = "O resultado do Genie expirou antes de ser recuperado. Tente novamente."
        _log.info(
            "Genie response ready: status=%s latency_ms=%s has_sql=%s",
            execution_status,
            answer.latency_ms,
            bool(answer.generated_query),
        )
        return GenieResult(
            answer_text=answer_text,
            generated_query=answer.generated_query,
            execution_status=execution_status,
            latency_ms=answer.latency_ms,
        )
    except Exception as exc:
        import urllib.error as _ue
        _log.error("Genie request failed", exc_info=True)
        if isinstance(exc, _ue.HTTPError) and exc.code == 403:
            return GenieResult(
                answer_text=(
                    "Genie: permissão negada (403). O service principal do app precisa de "
                    "CAN_RUN no Genie Space e CAN_USE no SQL Warehouse. "
                    "Veja os logs do servidor para o detalhe exato retornado pelo Databricks."
                ),
                generated_query=None,
                execution_status="permission_denied",
                latency_ms=0,
            )
        if isinstance(exc, _ue.HTTPError) and exc.code == 404:
            return GenieResult(
                answer_text=(
                    "Genie: recurso não encontrado (404). "
                    "Verifique se o DATABRICKS_GENIE_SPACE_ID está correto no ambiente da app."
                ),
                generated_query=None,
                execution_status="not_found",
                latency_ms=0,
            )
        return GenieResult(
            answer_text="Serviço temporariamente indisponível. Tente novamente.",
            generated_query=None,
            execution_status="failed",
            latency_ms=0,
        )
