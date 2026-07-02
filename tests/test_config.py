import tempfile
import unittest
from pathlib import Path

from model_router.config import ConfigError, load_config


class ConfigTests(unittest.TestCase):
    def test_load_valid_config(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "runtime.yaml"
            path.write_text(
                """
runtime:
  approval_after_plan: true
  strategy: rule_based
roles:
  premium:
    provider: openai
    model: gpt-5.5
    api_key_env: OPENAI_API_KEY
  cheap:
    provider: deepseek
    model: deepseek-chat
    api_key_env: DEEPSEEK_API_KEY
routing:
  escalate_on:
    - ambiguous
""".strip(),
                encoding="utf-8",
            )
            config = load_config(path)
            self.assertEqual(config.roles["premium"].provider, "openai")

    def test_missing_roles_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "runtime.yaml"
            path.write_text("runtime: {}\nrouting: {}\n", encoding="utf-8")
            with self.assertRaises(ConfigError):
                load_config(path)
