from __future__ import annotations

import os

import requests

from .base import BaseProvider


class OpenAIProvider(BaseProvider):
    def __init__(self, api_key_env: str) -> None:
        self.api_key_env = api_key_env

    def generate(self, prompt: str, model: str) -> str:
        api_key = os.getenv(self.api_key_env)
        if not api_key:
            raise ValueError(f"Missing environment variable: {self.api_key_env}")
        response = requests.post(
            "https://api.openai.com/v1/responses",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": model,
                "input": prompt,
            },
            timeout=60,
        )
        response.raise_for_status()
        data = response.json()
        output = data.get("output", [])
        texts: list[str] = []
        for item in output:
            for content in item.get("content", []):
                if content.get("type") == "output_text":
                    texts.append(content.get("text", ""))
        return "\n".join(texts).strip()
