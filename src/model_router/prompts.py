from __future__ import annotations

from .policy import RoutingPolicy
from .types import HandoffPacket, TaskRequest


def build_plan_prompt(request: TaskRequest, policy: RoutingPolicy) -> str:
    constraints = "\n".join(f"- {item}" for item in policy.default_constraints)
    files = ", ".join(request.files_in_scope) if request.files_in_scope else "None specified"
    return (
        "You are the planning model.\n"
        "Clarify the task, list risks, define scope and out-of-scope, and produce a handoff packet.\n"
        f"Task ID: {request.task_id}\n"
        f"User input: {request.user_input}\n"
        f"Context: {request.context_summary or 'N/A'}\n"
        f"Files in scope: {files}\n"
        "Constraints:\n"
        f"{constraints}\n"
        "Output sections: Scope, Out-of-scope, Risks, Acceptance checks, Handoff packet."
    )


def build_execute_prompt(request: TaskRequest, handoff: HandoffPacket) -> str:
    return (
        "You are the low-cost execution model.\n"
        "Implement only the approved scoped task.\n"
        "Do not redesign the solution.\n"
        "If ambiguity appears, stop and report escalation reasons.\n"
        f"Goal: {handoff.goal}\n"
        f"Files in scope: {', '.join(handoff.files_in_scope) or 'None specified'}\n"
        f"Out of scope: {', '.join(handoff.out_of_scope) or 'None specified'}\n"
        f"Constraints: {'; '.join(handoff.constraints)}\n"
        f"Acceptance checks: {'; '.join(handoff.acceptance_checks)}\n"
        f"Escalate if: {'; '.join(handoff.escalate_if)}\n"
        f"Original user input: {request.user_input}"
    )


def build_review_prompt(request: TaskRequest, handoff: HandoffPacket, execute_output: str) -> str:
    return (
        "You are the review model.\n"
        "Check the result against the plan and detect scope creep, regressions, and incorrect assumptions.\n"
        f"Goal: {handoff.goal}\n"
        f"Acceptance checks: {'; '.join(handoff.acceptance_checks)}\n"
        f"Execution output: {execute_output}\n"
        f"Original request: {request.user_input}"
    )
