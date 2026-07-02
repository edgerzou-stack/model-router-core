from __future__ import annotations

from .config import AppConfig
from .providers.deepseek_provider import DeepSeekProvider
from .providers.mock_provider import MockProvider
from .providers.openai_provider import OpenAIProvider


def resolve_provider(app_config: AppConfig, role: str):
    role_config = app_config.roles[role]
    provider_name = role_config.provider.lower()
    if provider_name == "mock":
        return MockProvider(role)
    if provider_name == "openai":
        return OpenAIProvider(role_config.api_key_env)
    if provider_name == "deepseek":
        return DeepSeekProvider(role_config.api_key_env)
    raise ValueError(f"Unknown provider: {provider_name}")
