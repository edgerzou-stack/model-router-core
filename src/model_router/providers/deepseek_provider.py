from __future__ import annotations

import os

import requests

from .base import BaseProvider


class DeepSeekProvider(BaseProvider):
    def __init__(self, api_key_env: str) -> None:
        self.api_key_env = api_key_env

    def generate(self, prompt: str, model: str) -> str:
        api_key = os.getenv(self.api_key_env)
        if not api_key:
            raise ValueError(f"Missing environment variable: {self.api_key_env}")
        response = requests.post(
            "https://api.deepseek.com/chat/completions",
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
