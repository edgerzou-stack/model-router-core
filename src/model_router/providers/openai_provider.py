from __future__ import annotations

import os

import requests

from ..exceptions import ProviderRequestError
from .base import BaseProvider


class OpenAIProvider(BaseProvider):
    def __init__(self, api_key_env: str, base_url: str | None = None, api_style: str | None = None) -> None:
        self.api_key_env = api_key_env
        self.base_url = (base_url or "https://api.openai.com/v1").rstrip("/")
        self.api_style = api_style or "responses"

    def generate(self, prompt: str, model: str) -> str:
        api_key = os.getenv(self.api_key_env)
        if not api_key:
            raise ValueError(f"Missing environment variable: {self.api_key_env}")
        try:
            if self.api_style == "chat_completions":
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
            payload = {"model": model, "input": prompt}
            import os as _os
            if _os.getenv("MODEL_ROUTER_DEBUG_PAYLOAD") == "1":
                print("DEBUG_OPENAI_PAYLOAD:", payload)
            response = requests.post(
                f"{self.base_url}/responses",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json=payload,
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
            if texts:
                return "\n".join(texts).strip()
            if isinstance(data.get("output_text"), str):
                return data["output_text"].strip()
            return str(data)
        except requests.RequestException as exc:
            status_code = getattr(getattr(exc, "response", None), "status_code", None)
            excerpt = None
            if getattr(exc, "response", None) is not None:
                excerpt = exc.response.text[:500]
            raise ProviderRequestError("openai", model, f"OpenAI-compatible request failed: {exc}", status_code=status_code, response_excerpt=excerpt) from exc
