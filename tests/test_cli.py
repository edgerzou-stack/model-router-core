import tempfile
import unittest
from pathlib import Path

from model_router.cli import main
from model_router.state_store import StateStore


class CliTests(unittest.TestCase):
    def test_start_command_creates_state_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            cwd = Path(tmp)
            old = Path.cwd()
            try:
                import os
                os.chdir(cwd)
                exit_code = main(["start", "--task", "Plan this refactor", "--id", "task-1"])
                self.assertEqual(exit_code, 0)
                path = cwd / ".runs" / "task-1.json"
                self.assertTrue(path.exists())
                state = StateStore(cwd / ".runs").load(path)
                self.assertEqual(state.request.task_id, "task-1")
            finally:
                os.chdir(old)
