from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class TaskPhase(str, Enum):
    PLAN = "plan"
    EXECUTE = "execute"
    REVIEW = "review"


class TaskClass(str, Enum):
    P0_STRATEGIC = "p0_strategic"
    P1_COMPLEX_EXECUTION = "p1_complex_execution"
    P2_ROUTINE_EXECUTION = "p2_routine_execution"
    P3_COMMODITY = "p3_commodity"


@dataclass
class TaskRequest:
    task_id: str
    user_input: str
    context_summary: str = ""
    files_in_scope: list[str] = field(default_factory=list)
    risk_flags: list[str] = field(default_factory=list)
    requires_human_approval: bool = False
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class HandoffPacket:
    goal: str
    files_in_scope: list[str]
    out_of_scope: list[str]
    constraints: list[str]
    acceptance_checks: list[str]
    escalate_if: list[str]


@dataclass
class RoutingDecision:
    task_class: TaskClass
    phase: TaskPhase
    selected_provider: str
    selected_model: str
    reasoning: str
    escalation_triggers: list[str] = field(default_factory=list)
    requires_human_approval: bool = False


@dataclass
class WorkflowState:
    request: TaskRequest
    current_phase: TaskPhase = TaskPhase.PLAN
    approved: bool = False
    handoff_packet: HandoffPacket | None = None
    plan_output: str | None = None
    execute_output: str | None = None
    review_output: str | None = None
