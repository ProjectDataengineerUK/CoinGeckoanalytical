from __future__ import annotations

import os
import shutil
from dataclasses import dataclass, asdict
from typing import Any


@dataclass(frozen=True)
class PreflightResult:
    cli_available: bool
    host_configured: bool
    token_configured: bool
    ready: bool
    missing: list[str]


def run_preflight(env: dict[str, str] | None = None) -> PreflightResult:
    active_env = env if env is not None else os.environ
    cli_available = shutil.which("databricks") is not None
    host_configured = bool(active_env.get("DATABRICKS_HOST"))
    token_configured = bool(active_env.get("DATABRICKS_TOKEN"))
    missing: list[str] = []

    if not cli_available:
        missing.append("databricks-cli")
    if not host_configured:
        missing.append("DATABRICKS_HOST")
    if not token_configured:
        missing.append("DATABRICKS_TOKEN")

    return PreflightResult(
        cli_available=cli_available,
        host_configured=host_configured,
        token_configured=token_configured,
        ready=not missing,
        missing=missing,
    )


def format_preflight(result: PreflightResult) -> str:
    payload = asdict(result)
    lines = ["Databricks deploy preflight"]
    for key in ("cli_available", "host_configured", "token_configured", "ready"):
        lines.append(f"- {key}: {payload[key]}")
    if result.missing:
        lines.append("- missing:")
        for item in result.missing:
            lines.append(f"  - {item}")
    return "\n".join(lines)


def main() -> dict[str, Any]:
    result = run_preflight()
    print(format_preflight(result))
    return asdict(result)


if __name__ == "__main__":  # pragma: no cover - CLI entrypoint
    main()
