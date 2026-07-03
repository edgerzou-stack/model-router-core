from __future__ import annotations

from .policy import RoutingPolicy
from .types import RoutingDecision, TaskClass, TaskPhase, TaskRequest


class Router:
    def __init__(self, policy: RoutingPolicy | None = None, model_overrides: dict[str, tuple[str, str]] | None = None) -> None:
        self.policy = policy or RoutingPolicy()
        self.model_overrides = model_overrides or {}

    def route(self, request: TaskRequest, phase: TaskPhase) -> RoutingDecision:
        task_class = self.policy.classify(request)
        provider, model = self._select_provider(phase)
        reasoning = self._build_reasoning(task_class, phase, request)
        requires_human_approval = phase is TaskPhase.PLAN
        escalation_triggers = []
        if self.policy.requires_escalation(request):
            escalation_triggers.append("risk_or_ambiguity_detected")
        return RoutingDecision(
            task_class=task_class,
            phase=phase,
            selected_provider=provider,
            selected_model=model,
            reasoning=reasoning,
            escalation_triggers=escalation_triggers,
            requires_human_approval=requires_human_approval,
        )

    def _select_provider(self, phase: TaskPhase) -> tuple[str, str]:
        role = "premium" if phase in (TaskPhase.PLAN, TaskPhase.REVIEW) else "cheap"
        if role in self.model_overrides:
            return self.model_overrides[role]
        if role == "premium":
            return self.policy.premium_provider, self.policy.premium_model
        return self.policy.cheap_provider, self.policy.cheap_model

    def _build_reasoning(self, task_class: TaskClass, phase: TaskPhase, request: TaskRequest) -> str:
        if phase is TaskPhase.PLAN:
            return f"Route to premium planning for {task_class.value}."
        if phase is TaskPhase.EXECUTE:
            return f"Route to cheap execution for scoped task {request.task_id}."
        return f"Route to premium review for {task_class.value}."
