import unittest

from model_router.providers.mock_provider import MockProvider
from model_router.types import HandoffPacket, TaskRequest
from model_router.workflow import WorkflowEngine


class WorkflowTests(unittest.TestCase):
    def test_execute_requires_approval(self) -> None:
        engine = WorkflowEngine(
            premium_provider=MockProvider("premium"),
            cheap_provider=MockProvider("cheap"),
        )
        state = engine.start(TaskRequest(task_id="1", user_input="Plan this refactor"))
        with self.assertRaises(PermissionError):
            engine.execute(state)

    def test_full_workflow(self) -> None:
        engine = WorkflowEngine(
            premium_provider=MockProvider("premium"),
            cheap_provider=MockProvider("cheap"),
        )
        request = TaskRequest(task_id="2", user_input="Rename fields in one module")
        state = engine.start(request)
        handoff = HandoffPacket(
            goal="Rename fields in one module",
            files_in_scope=["module.py"],
            out_of_scope=["other.py"],
            constraints=["Keep patch minimal"],
            acceptance_checks=["Names are updated consistently"],
            escalate_if=["Ambiguity appears"],
        )
        state = engine.approve_plan(state, handoff)
        state = engine.execute(state)
        state = engine.review(state)
        self.assertIsNotNone(state.plan_output)
        self.assertIsNotNone(state.execute_output)
        self.assertIsNotNone(state.review_output)
