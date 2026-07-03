from __future__ import annotations

import os

import requests

from ..exceptions import ProviderRequestError
from .base import BaseProvider


class DeepSeekProvider(BaseProvider):
    def __init__(self, api_key_env: str, base_url: str | None = None) -> None:
        self.api_key_env = api_key_env
        self.base_url = (base_url or "https://api.deepseek.com").rstrip("/")

    def generate(self, prompt: str, model: str) -> str:
        api_key = os.getenv(self.api_key_env)
        if not api_key:
            raise ValueError(f"Missing environment variable: {self.api_key_env}")
        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": model,
                    "messages": [{"role": "user", "content": prompt}],
                },
                timeout=60,
            )
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"].strip()
        except requests.RequestException as exc:
            status_code = getattr(getattr(exc, "response", None), "status_code", None)
            excerpt = None
            if getattr(exc, "response", None) is not None:
                excerpt = exc.response.text[:500]
            raise ProviderRequestError("deepseek", model, f"DeepSeek request failed: {exc}", status_code=status_code, response_excerpt=excerpt) from exc
