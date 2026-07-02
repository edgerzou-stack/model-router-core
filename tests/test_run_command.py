import os
import tempfile
import unittest
from pathlib import Path

from model_router.cli import main


class RunCommandTests(unittest.TestCase):
    def test_run_refuses_without_config(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            old = Path.cwd()
            try:
                os.chdir(tmp)
                code = main(["run", "--task", "Plan this change"])
                self.assertEqual(code, 2)
            finally:
                os.chdir(old)
