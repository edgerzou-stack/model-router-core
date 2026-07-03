from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


class ConfigError(ValueError):
    pass


@dataclass
class RoleConfig:
    provider: str
    model: str
    api_key_env: str
    base_url: str | None = None
    api_style: str | None = None


@dataclass
class RuntimeConfig:
    approval_after_plan: bool
    strategy: str


@dataclass
class RoutingConfig:
    escalate_on: list[str]


@dataclass
class AppConfig:
    runtime: RuntimeConfig
    roles: dict[str, RoleConfig]
    routing: RoutingConfig
    path: Path


def load_config(path: str | Path = "config/runtime.yaml") -> AppConfig:
    config_path = Path(path)
    if not config_path.exists():
        raise ConfigError(f"Config file not found: {config_path}")
    data = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
    return parse_config(data, config_path)


def parse_config(data: dict[str, Any], path: Path) -> AppConfig:
    runtime = data.get("runtime")
    roles = data.get("roles")
    routing = data.get("routing")
    if not isinstance(runtime, dict):
        raise ConfigError("Missing or invalid 'runtime' section")
    if not isinstance(roles, dict):
        raise ConfigError("Missing or invalid 'roles' section")
    if not isinstance(routing, dict):
        raise ConfigError("Missing or invalid 'routing' section")
    parsed_roles: dict[str, RoleConfig] = {}
    for role_name in ("premium", "cheap"):
        role = roles.get(role_name)
        if not isinstance(role, dict):
            raise ConfigError(f"Missing or invalid role: {role_name}")
        for field_name in ("provider", "model", "api_key_env"):
            if not role.get(field_name):
                raise ConfigError(f"Missing '{field_name}' for role '{role_name}'")
        parsed_roles[role_name] = RoleConfig(
            provider=str(role["provider"]),
            model=str(role["model"]),
            api_key_env=str(role["api_key_env"]),
            base_url=str(role["base_url"]) if role.get("base_url") else None,
            api_style=str(role["api_style"]) if role.get("api_style") else None,
        )
    approval_after_plan = runtime.get("approval_after_plan")
    strategy = runtime.get("strategy")
    if not isinstance(approval_after_plan, bool):
        raise ConfigError("'runtime.approval_after_plan' must be boolean")
    if not strategy:
        raise ConfigError("Missing 'runtime.strategy'")
    escalate_on = routing.get("escalate_on", [])
    if not isinstance(escalate_on, list):
        raise ConfigError("'routing.escalate_on' must be a list")
    return AppConfig(
        runtime=RuntimeConfig(approval_after_plan=approval_after_plan, strategy=str(strategy)),
        roles=parsed_roles,
        routing=RoutingConfig(escalate_on=[str(item) for item in escalate_on]),
        path=path,
    )
