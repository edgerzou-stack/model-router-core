from __future__ import annotations

from .base import BaseProvider


class MockProvider(BaseProvider):
    def __init__(self, name: str) -> None:
        self.name = name

    def generate(self, prompt: str, model: str) -> str:
        head = prompt.splitlines()[0] if prompt else ""
        return f"[{self.name}:{model}] {head}"
