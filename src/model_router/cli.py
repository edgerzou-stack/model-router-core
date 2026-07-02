from __future__ import annotations

import argparse
import json
import sys
import uuid

from pathlib import Path
import shutil

from .cli_blocks import render_phase_block
from .config import load_config
from .diagnostics import ReadinessState, diagnose
from .providers.mock_provider import MockProvider
from .registry import resolve_provider
from .state_store import StateStore
from .types import HandoffPacket, TaskRequest
from .workflow import WorkflowEngine


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="model-router")
    subparsers = parser.add_subparsers(dest="command", required=True)

    start = subparsers.add_parser("start")
    start.add_argument("--task", required=True)
    start.add_argument("--id", dest="task_id")
    start.add_argument("--context", default="")
    start.add_argument("--files", nargs="*", default=[])
    start.add_argument("--risk", nargs="*", default=[])

    approve = subparsers.add_parser("approve")
    approve.add_argument("--state", required=True)
    approve.add_argument("--goal", required=True)
    approve.add_argument("--in-scope", nargs="*", default=[])
    approve.add_argument("--out-of-scope", nargs="*", default=[])
    approve.add_argument("--constraints", nargs="*", default=[])
    approve.add_argument("--acceptance", nargs="*", default=[])
    approve.add_argument("--escalate-if", nargs="*", default=[])

    execute = subparsers.add_parser("execute")
    execute.add_argument("--state", required=True)

    review = subparsers.add_parser("review")
    review.add_argument("--state", required=True)

    show = subparsers.add_parser("show")
    show.add_argument("--state", required=True)

    init_cmd = subparsers.add_parser("init")
    init_cmd.add_argument("--force", action="store_true")

    doctor_cmd = subparsers.add_parser("doctor")

    run_cmd = subparsers.add_parser("run")
    run_cmd.add_argument("--task", required=True)
    run_cmd.add_argument("--id", dest="task_id")
    run_cmd.add_argument("--context", default="")
    run_cmd.add_argument("--files", nargs="*", default=[])
    run_cmd.add_argument("--risk", nargs="*", default=[])
    return parser


def make_engine(config=None) -> WorkflowEngine:
    if config is None:
        return WorkflowEngine(
            premium_provider=MockProvider("premium"),
            cheap_provider=MockProvider("cheap"),
        )
    return WorkflowEngine(
        premium_provider=resolve_provider(config, "premium"),
        cheap_provider=resolve_provider(config, "cheap"),
    )


def cmd_start(args: argparse.Namespace) -> int:
    engine = make_engine()
    store = StateStore()
    task_id = args.task_id or str(uuid.uuid4())
    request = TaskRequest(
        task_id=task_id,
        user_input=args.task,
        context_summary=args.context,
        files_in_scope=args.files,
        risk_flags=args.risk,
    )
    state = engine.start(request)
    path = store.save(state)
    print(render_phase_block("Plan Phase", [f"Task started: {task_id}", f"State file: {path}", "Plan generated.", "Human approval is required before execution."]))
    print(state.plan_output)
    return 0


def cmd_approve(args: argparse.Namespace) -> int:
    store = StateStore()
    state = store.load(args.state)
    handoff = HandoffPacket(
        goal=args.goal,
        files_in_scope=args.in_scope,
        out_of_scope=args.out_of_scope,
        constraints=args.constraints or ["Keep patch minimal"],
        acceptance_checks=args.acceptance or ["Approved work is completed"],
        escalate_if=args.escalate_if or ["Ambiguity appears"],
    )
    engine = make_engine()
    state = engine.approve_plan(state, handoff)
    path = store.save(state)
    print(f"Plan approved. Updated state: {path}")
    return 0


def cmd_execute(args: argparse.Namespace) -> int:
    store = StateStore()
    state = store.load(args.state)
    engine = make_engine()
    state = engine.execute(state)
    path = store.save(state)
    print(f"Execution finished. Updated state: {path}")
    print(state.execute_output)
    return 0


def cmd_review(args: argparse.Namespace) -> int:
    store = StateStore()
    state = store.load(args.state)
    engine = make_engine()
    state = engine.review(state)
    path = store.save(state)
    print(f"Review finished. Updated state: {path}")
    print(state.review_output)
    return 0




def cmd_init(args: argparse.Namespace) -> int:
    config_dir = Path("config")
    target = config_dir / "runtime.yaml"
    template = Path("config/runtime.example.yaml")
    config_dir.mkdir(parents=True, exist_ok=True)
    if target.exists() and not args.force:
        print(f"Config already exists: {target}")
        print("Use --force to overwrite it.")
        return 0
    if not template.exists():
        print(f"Template missing: {template}")
        return 2
    shutil.copyfile(template, target)
    print(render_phase_block("Initialization", [f"Created config: {target}", "Next step: export required environment variables.", "Then run: model-router doctor"]))
    return 0


def cmd_doctor(args: argparse.Namespace) -> int:
    report = diagnose()
    print(render_phase_block("Doctor", [f"Readiness: {report.state.value}", f"Config path: {report.config_path}"]))
    from .doctor import run_doctor
    print(run_doctor())
    return 0 if report.state is ReadinessState.READY else 2


def cmd_run(args: argparse.Namespace) -> int:
    report = diagnose()
    if report.state is not ReadinessState.READY:
        from .doctor import run_doctor
        print(run_doctor())
        print(render_phase_block("Run Blocked", ["Runtime is not ready.", "Fix setup issues before running tasks."]))
        return 2
    config = load_config()
    engine = make_engine(config)
    store = StateStore()
    task_id = args.task_id or str(uuid.uuid4())
    request = TaskRequest(
        task_id=task_id,
        user_input=args.task,
        context_summary=args.context,
        files_in_scope=args.files,
        risk_flags=args.risk,
    )
    state = engine.start(request)
    path = store.save(state)
    print(render_phase_block("Run Started", [f"Task started: {task_id}", f"State file: {path}", "Plan completed.", "Human approval is required before execution.", f"Next step: model-router approve --state {path} --goal <goal>"]))
    print(state.plan_output)
    return 0

def cmd_show(args: argparse.Namespace) -> int:
    store = StateStore()
    state = store.load(args.state)
    print(json.dumps({
        "task_id": state.request.task_id,
        "current_phase": state.current_phase.value,
        "approved": state.approved,
        "plan_output": state.plan_output,
        "execute_output": state.execute_output,
        "review_output": state.review_output,
        "handoff_packet": None if state.handoff_packet is None else {
            "goal": state.handoff_packet.goal,
            "files_in_scope": state.handoff_packet.files_in_scope,
            "out_of_scope": state.handoff_packet.out_of_scope,
            "constraints": state.handoff_packet.constraints,
            "acceptance_checks": state.handoff_packet.acceptance_checks,
            "escalate_if": state.handoff_packet.escalate_if,
        },
    }, ensure_ascii=False, indent=2))
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    command_map = {
        "start": cmd_start,
        "approve": cmd_approve,
        "execute": cmd_execute,
        "review": cmd_review,
        "show": cmd_show,
        "init": cmd_init,
        "doctor": cmd_doctor,
        "run": cmd_run,
    }
    return command_map[args.command](args)


if __name__ == "__main__":
    sys.exit(main())
