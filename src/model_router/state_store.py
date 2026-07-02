from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
from typing import Any

from .types import HandoffPacket, TaskPhase, TaskRequest, WorkflowState


class StateStore:
    def __init__(self, root: str | Path = ".runs") -> None:
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)

    def path_for(self, task_id: str) -> Path:
        return self.root / f"{task_id}.json"

    def save(self, state: WorkflowState) -> Path:
        payload = {
            "request": asdict(state.request),
            "current_phase": state.current_phase.value,
            "approved": state.approved,
            "handoff_packet": asdict(state.handoff_packet) if state.handoff_packet else None,
            "plan_output": state.plan_output,
            "execute_output": state.execute_output,
            "review_output": state.review_output,
        }
        path = self.path_for(state.request.task_id)
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        return path

    def load(self, path: str | Path) -> WorkflowState:
        data: dict[str, Any] = json.loads(Path(path).read_text(encoding="utf-8"))
        request = TaskRequest(**data["request"])
        handoff = HandoffPacket(**data["handoff_packet"]) if data["handoff_packet"] else None
        return WorkflowState(
            request=request,
            current_phase=TaskPhase(data["current_phase"]),
            approved=data["approved"],
            handoff_packet=handoff,
            plan_output=data.get("plan_output"),
            execute_output=data.get("execute_output"),
            review_output=data.get("review_output"),
        )
