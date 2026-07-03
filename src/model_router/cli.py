from __future__ import annotations

import argparse
import json
import sys
import uuid

from pathlib import Path
import shutil

from .cli_blocks import render_error_block, render_phase_block, render_playbook_block
from .config import load_config
from .diagnostics import ReadinessState, diagnose
from .providers.mock_provider import MockProvider
from .registry import resolve_provider
from .state_store import StateStore
from .types import HandoffPacket, TaskRequest
from .workflow import WorkflowEngine
from .exceptions import ProviderRequestError


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
    from .router import Router
    router = Router(
        model_overrides={
            "premium": (config.roles["premium"].provider, config.roles["premium"].model),
            "cheap": (config.roles["cheap"].provider, config.roles["cheap"].model),
        },
    )
    return WorkflowEngine(
        router=router,
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
    try:
        state = engine.start(request)
    except ProviderRequestError as exc:
        details = [f"Provider: {exc.provider}", f"Model: {exc.model}"]
        if exc.status_code is not None:
            details.append(f"HTTP status: {exc.status_code}")
        if exc.response_excerpt:
            details.append(f"Response excerpt: {exc.response_excerpt}")
        print(render_error_block("Plan Failed", details))
        return 2
    path = store.save(state)
    print(render_playbook_block("Plan Phase", [f"Task started: {task_id}", "Plan generated."], [f"State file: {path}", "Waiting for explicit human approval before execution."], [f"Run: model-router approve --state {path} --goal <goal>"]))
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
    config = load_config() if Path("config/runtime.yaml").exists() else None
    engine = make_engine(config)
    state = engine.approve_plan(state, handoff)
    path = store.save(state)
    print(render_playbook_block("Approval Recorded", ["Plan approved."], [f"State file updated: {path}", "Task is now ready for execute."], [f"Run: model-router execute --state {path}"]))
    return 0


def cmd_execute(args: argparse.Namespace) -> int:
    store = StateStore()
    state = store.load(args.state)
    config = load_config() if Path("config/runtime.yaml").exists() else None
    engine = make_engine(config)
    try:
        state = engine.execute(state)
    except ProviderRequestError as exc:
        details = [f"Provider: {exc.provider}", f"Model: {exc.model}"]
        if exc.status_code is not None:
            details.append(f"HTTP status: {exc.status_code}")
        if exc.response_excerpt:
            details.append(f"Response excerpt: {exc.response_excerpt}")
        print(render_error_block("Execute Failed", details))
        return 2
    path = store.save(state)
    print(render_playbook_block("Execute Phase", ["Execution finished."], [f"State file updated: {path}", "Execution result captured for review."], [f"Run: model-router review --state {path}"]))
    print(state.execute_output)
    return 0


def cmd_review(args: argparse.Namespace) -> int:
    store = StateStore()
    state = store.load(args.state)
    config = load_config() if Path("config/runtime.yaml").exists() else None
    engine = make_engine(config)
    try:
        state = engine.review(state)
    except ProviderRequestError as exc:
        details = [f"Provider: {exc.provider}", f"Model: {exc.model}"]
        if exc.status_code is not None:
            details.append(f"HTTP status: {exc.status_code}")
        if exc.response_excerpt:
            details.append(f"Response excerpt: {exc.response_excerpt}")
        print(render_error_block("Review Failed", details))
        return 2
    path = store.save(state)
    print(render_playbook_block("Review Phase", ["Review finished."], [f"State file updated: {path}", "Review result captured."], [f"Inspect: model-router show --state {path}"]))
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
    print(render_playbook_block("Initialization", [f"Created config: {target}"], ["Local runtime template is now present."], ["Export required environment variables.", "Then run: model-router doctor"]))
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
    try:
        state = engine.start(request)
    except ProviderRequestError as exc:
        details = [f"Provider: {exc.provider}", f"Model: {exc.model}"]
        if exc.status_code is not None:
            details.append(f"HTTP status: {exc.status_code}")
        if exc.response_excerpt:
            details.append(f"Response excerpt: {exc.response_excerpt}")
        print(render_error_block("Plan Failed", details))
        return 2
    path = store.save(state)
    print(render_playbook_block("Run Started", [f"Task started: {task_id}", "Plan completed."], [f"State file: {path}", "Human approval is required before execution."], [f"Run: model-router approve --state {path} --goal <goal>"]))
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
