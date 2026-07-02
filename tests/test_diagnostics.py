import os
import tempfile
import unittest
from pathlib import Path

from model_router.diagnostics import ReadinessState, diagnose


class DiagnosticsTests(unittest.TestCase):
    def test_uninitialized_when_missing_config(self) -> None:
        report = diagnose("/tmp/definitely_missing_model_router_config.yaml")
        self.assertEqual(report.state, ReadinessState.UNINITIALIZED)

    def test_misconfigured_when_env_missing(self) -> None:
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
  escalate_on: []
""".strip(),
                encoding="utf-8",
            )
            os.environ.pop("OPENAI_API_KEY", None)
            os.environ.pop("DEEPSEEK_API_KEY", None)
            report = diagnose(path)
            self.assertEqual(report.state, ReadinessState.MISCONFIGURED)
