from __future__ import annotations

from dataclasses import dataclass, field

from .types import TaskClass, TaskRequest


@dataclass
class RoutingPolicy:
    premium_provider: str = "mock-premium"
    premium_model: str = "gpt-plan-review-stub"
    cheap_provider: str = "mock-cheap"
    cheap_model: str = "deepseek-execute-stub"
    strategic_keywords: tuple[str, ...] = (
        "plan",
        "strategy",
        "architecture",
        "design",
        "review",
        "tradeoff",
        "ambiguous",
    )
    high_risk_keywords: tuple[str, ...] = (
        "auth",
        "billing",
        "payment",
        "delete data",
        "security",
        "migration",
        "permission",
    )
    routine_keywords: tuple[str, ...] = (
        "rename",
        "refactor",
        "update",
        "convert",
        "format",
        "rewrite",
        "implement",
    )
    escalation_risk_flags: tuple[str, ...] = (
        "ambiguous",
        "high_risk",
        "cross_boundary",
        "auth_billing_data",
    )
    default_constraints: list[str] = field(
        default_factory=lambda: [
            "Do not change unrelated files.",
            "Keep the patch minimal.",
            "Escalate ambiguity instead of guessing.",
        ]
    )

    def classify(self, request: TaskRequest) -> TaskClass:
        text = self._normalize(request)
        if self._contains_any(text, self.high_risk_keywords) or self._has_escalation_flag(request):
            return TaskClass.P0_STRATEGIC
        if self._contains_any(text, self.strategic_keywords):
            return TaskClass.P1_COMPLEX_EXECUTION
        if self._contains_any(text, self.routine_keywords):
            return TaskClass.P2_ROUTINE_EXECUTION
        return TaskClass.P3_COMMODITY

    def requires_escalation(self, request: TaskRequest) -> bool:
        text = self._normalize(request)
        return self._contains_any(text, self.high_risk_keywords) or self._has_escalation_flag(request)

    def _normalize(self, request: TaskRequest) -> str:
        return " ".join(
            [request.user_input, request.context_summary, " ".join(request.risk_flags)]
        ).lower()

    def _contains_any(self, text: str, keywords: tuple[str, ...]) -> bool:
        return any(keyword in text for keyword in keywords)

    def _has_escalation_flag(self, request: TaskRequest) -> bool:
        return any(flag in self.escalation_risk_flags for flag in request.risk_flags)
