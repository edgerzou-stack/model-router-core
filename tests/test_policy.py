import unittest

from model_router.policy import RoutingPolicy
from model_router.types import TaskClass, TaskRequest


class PolicyTests(unittest.TestCase):
    def test_strategic_keyword_routes_to_complex_or_higher(self) -> None:
        policy = RoutingPolicy()
        request = TaskRequest(task_id="1", user_input="Please plan the architecture for this change")
        self.assertEqual(policy.classify(request), TaskClass.P1_COMPLEX_EXECUTION)

    def test_high_risk_flag_routes_to_strategic(self) -> None:
        policy = RoutingPolicy()
        request = TaskRequest(task_id="2", user_input="Update auth flow", risk_flags=["high_risk"])
        self.assertEqual(policy.classify(request), TaskClass.P0_STRATEGIC)

    def test_routine_keyword_routes_to_routine(self) -> None:
        policy = RoutingPolicy()
        request = TaskRequest(task_id="3", user_input="Rename these fields using the approved mapping")
        self.assertEqual(policy.classify(request), TaskClass.P2_ROUTINE_EXECUTION)
