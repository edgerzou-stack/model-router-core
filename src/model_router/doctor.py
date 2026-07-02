from __future__ import annotations

from .cli_blocks import render_doctor_report
from .diagnostics import diagnose


def run_doctor(config_path: str = "config/runtime.yaml") -> str:
    return render_doctor_report(diagnose(config_path))
