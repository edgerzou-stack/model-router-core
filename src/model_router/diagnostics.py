from __future__ import annotations

import os
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

from .config import AppConfig, ConfigError, load_config


class ReadinessState(str, Enum):
    UNINITIALIZED = "uninitialized"
    MISCONFIGURED = "misconfigured"
    READY = "ready"


@dataclass
class DiagnosticReport:
    state: ReadinessState
    config_path: Path
    messages: list[str] = field(default_factory=list)
    missing_env_vars: list[str] = field(default_factory=list)
    config_loaded: bool = False
    config: AppConfig | None = None


def diagnose(config_path: str | Path = "config/runtime.yaml") -> DiagnosticReport:
    path = Path(config_path)
    if not path.exists():
        return DiagnosticReport(
            state=ReadinessState.UNINITIALIZED,
            config_path=path,
            messages=[f"Missing config file: {path}"],
        )
    try:
        config = load_config(path)
    except ConfigError as exc:
        return DiagnosticReport(
            state=ReadinessState.MISCONFIGURED,
            config_path=path,
            messages=[str(exc)],
        )
    missing_env_vars = []
    for role in config.roles.values():
        if not os.getenv(role.api_key_env):
            missing_env_vars.append(role.api_key_env)
    if missing_env_vars:
        return DiagnosticReport(
            state=ReadinessState.MISCONFIGURED,
            config_path=path,
            messages=["Config is valid but required environment variables are missing."],
            missing_env_vars=sorted(set(missing_env_vars)),
            config_loaded=True,
            config=config,
        )
    return DiagnosticReport(
        state=ReadinessState.READY,
        config_path=path,
        messages=["Runtime is ready."],
        config_loaded=True,
        config=config,
    )
