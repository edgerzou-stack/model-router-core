import unittest

from model_router.policy import RoutingPolicy
from model_router.router import Router
from model_router.types import TaskPhase, TaskRequest


class RouterTests(unittest.TestCase):
    def test_plan_uses_premium_provider(self) -> None:
        router = Router(RoutingPolicy())
        request = TaskRequest(task_id="1", user_input="Plan this refactor")
        decision = router.route(request, TaskPhase.PLAN)
        self.assertEqual(decision.selected_provider, "mock-premium")
        self.assertTrue(decision.requires_human_approval)

    def test_execute_uses_cheap_provider(self) -> None:
        router = Router(RoutingPolicy())
        request = TaskRequest(task_id="2", user_input="Rename these fields")
        decision = router.route(request, TaskPhase.EXECUTE)
        self.assertEqual(decision.selected_provider, "mock-cheap")
        self.assertFalse(decision.requires_human_approval)
