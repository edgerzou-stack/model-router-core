from __future__ import annotations

from .policy import RoutingPolicy
from .prompts import build_execute_prompt, build_plan_prompt, build_review_prompt
from .providers.base import BaseProvider
from .router import Router
from .types import HandoffPacket, TaskPhase, TaskRequest, WorkflowState


class WorkflowEngine:
    def __init__(
        self,
        router: Router | None = None,
        premium_provider: BaseProvider | None = None,
        cheap_provider: BaseProvider | None = None,
    ) -> None:
        self.router = router or Router(RoutingPolicy())
        self.premium_provider = premium_provider
        self.cheap_provider = cheap_provider

    def start(self, request: TaskRequest) -> WorkflowState:
        state = WorkflowState(request=request)
        decision = self.router.route(request, TaskPhase.PLAN)
        prompt = build_plan_prompt(request, self.router.policy)
        if self.premium_provider is None:
            raise ValueError("premium_provider is required")
        state.plan_output = self.premium_provider.generate(prompt, decision.selected_model)
        return state

    def approve_plan(self, state: WorkflowState, handoff_packet: HandoffPacket) -> WorkflowState:
        state.approved = True
        state.handoff_packet = handoff_packet
        state.current_phase = TaskPhase.EXECUTE
        return state

    def execute(self, state: WorkflowState) -> WorkflowState:
        if not state.approved or state.handoff_packet is None:
            raise PermissionError("Plan must be approved before execution")
        if self.cheap_provider is None:
            raise ValueError("cheap_provider is required")
        prompt = build_execute_prompt(state.request, state.handoff_packet)
        decision = self.router.route(state.request, TaskPhase.EXECUTE)
        state.execute_output = self.cheap_provider.generate(prompt, decision.selected_model)
        state.current_phase = TaskPhase.REVIEW
        return state

    def review(self, state: WorkflowState) -> WorkflowState:
        if state.handoff_packet is None or state.execute_output is None:
            raise ValueError("Execution output is required before review")
        if self.premium_provider is None:
            raise ValueError("premium_provider is required")
        prompt = build_review_prompt(state.request, state.handoff_packet, state.execute_output)
        decision = self.router.route(state.request, TaskPhase.REVIEW)
        state.review_output = self.premium_provider.generate(prompt, decision.selected_model)
        return state
