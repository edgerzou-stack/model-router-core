import io
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

from model_router.cli import main


class CliOutputTests(unittest.TestCase):
    def test_init_outputs_playbook_style_block(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            old = Path.cwd()
            try:
                import os
                os.chdir(tmp)
                Path('config').mkdir(exist_ok=True)
                Path('config/runtime.example.yaml').write_text('runtime:\n  approval_after_plan: true\n  strategy: rule_based\nroles:\n  premium:\n    provider: mock\n    model: mock-premium\n    api_key_env: OPENAI_API_KEY\n  cheap:\n    provider: mock\n    model: mock-cheap\n    api_key_env: DEEPSEEK_API_KEY\nrouting:\n  escalate_on: []\n', encoding='utf-8')
                buf = io.StringIO()
                with redirect_stdout(buf):
                    code = main(['init'])
                self.assertEqual(code, 0)
                out = buf.getvalue()
                self.assertIn('### Initialization', out)
                self.assertIn('✅ Completed', out)
                self.assertIn('➡️ Next', out)
            finally:
                os.chdir(old)
