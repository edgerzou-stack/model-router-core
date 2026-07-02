import tempfile
import unittest
from pathlib import Path

from model_router.config import load_config
from model_router.registry import resolve_provider


class RegistryTests(unittest.TestCase):
    def test_resolve_mock_provider(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "runtime.yaml"
            path.write_text(
                """
runtime:
  approval_after_plan: true
  strategy: rule_based
roles:
  premium:
    provider: mock
    model: mock-premium
    api_key_env: OPENAI_API_KEY
  cheap:
    provider: mock
    model: mock-cheap
    api_key_env: DEEPSEEK_API_KEY
routing:
  escalate_on: []
""".strip(),
                encoding="utf-8",
            )
            cfg = load_config(path)
            provider = resolve_provider(cfg, "premium")
            self.assertEqual(provider.__class__.__name__, "MockProvider")
