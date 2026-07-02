from __future__ import annotations

from .diagnostics import DiagnosticReport


def render_doctor_report(report: DiagnosticReport) -> str:
    lines = [
        "---",
        "> ### Runtime Readiness",
        f"> **State**: {report.state.value.upper()}",
        f"> **Config Path**: {report.config_path}",
    ]
    for message in report.messages:
        lines.append(f"> - {message}")
    if report.missing_env_vars:
        lines.append("> **Missing Env Vars**:")
        for item in report.missing_env_vars:
            lines.append(f"> - {item}")
    return "\n".join(lines)


def render_phase_block(title: str, summary: list[str]) -> str:
    lines = ["---", f"> ### {title}"]
    for item in summary:
        lines.append(f"> - {item}")
    return "\n".join(lines)
