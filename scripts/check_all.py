#!/usr/bin/env python3
"""Cross-platform Stage 0 check runner (Windows-friendly alternative to ``make check``).

Source of truth for *what* each step does remains the Makefile targets and the
PowerShell scripts they invoke. This module orchestrates the same sequence and
does not re-implement validation logic.

Mirrors Makefile ``check`` plus ``architecture-check`` and ``publish-gate``
(see Makefile targets ``check``, ``architecture-check``, ``publish-gate``):

1. generate-contracts          → scripts/generate-contracts.ps1
2. slice/CLI pytest            → apps/cli/scripts/check.ps1
3. validate-schemas            → scripts/validate-schemas.ps1
4. validate-examples           → scripts/validate-examples.ps1
5. validate-requirements       → scripts/validate-requirements.ps1
6. check-constraints           → scripts/check_constraint_matrix.py (ADR-045)
7. compare-golden              → scripts/compare-golden.ps1
8. architecture-check          → pytest + architecture_check.cli (Makefile)
9. publish-gate                → python -m moex_model_cli.gates.publish_gate

Usage (from repo root)::

    python scripts/check_all.py
    python scripts/check_all.py --keep-going
    python scripts/check_all.py --only compare-golden

Interpreter resolution: ``$PYTHON`` → ``py -< .python-version >`` →
``apps/cli/.venv`` → ``py -3.14`` / ``python3`` / ``python`` (3.11+).
"""

from __future__ import annotations

import argparse
import os
import platform
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

# Step ids must stay aligned with Makefile target names where they exist.
STEP_IDS = (
    "generate-contracts",
    "slice-cli",
    "validate-schemas",
    "validate-examples",
    "validate-requirements",
    "check-constraints",
    "compare-golden",
    "architecture-check",
    "publish-gate",
)


@dataclass(frozen=True)
class StepResult:
    step_id: str
    ok: bool
    seconds: float
    detail: str = ""


def _read_python_version_pin() -> str | None:
    pin = REPO_ROOT / ".python-version"
    if not pin.is_file():
        return None
    text = pin.read_text(encoding="utf-8").strip()
    return text or None


def _try_executable(cmd: list[str]) -> str | None:
    try:
        proc = subprocess.run(
            cmd,
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
    except (OSError, FileNotFoundError):
        return None
    if proc.returncode != 0:
        return None
    path = (proc.stdout or "").strip().splitlines()
    if not path:
        return None
    exe = path[0].strip()
    return exe if exe and Path(exe).exists() else None


def _cli_venv_python() -> str | None:
    for rel in (
        Path("apps/cli/.venv/Scripts/python.exe"),
        Path("apps/cli/.venv/bin/python"),
        Path("apps/cli/.venv/bin/python3"),
    ):
        candidate = REPO_ROOT / rel
        if candidate.is_file():
            return str(candidate)
    return None


def resolve_python() -> str:
    """Pick a usable interpreter; prefer pin / PYTHON / existing CLI venv."""
    env = os.environ.get("PYTHON", "").strip()
    if env:
        # Allow ``PYTHON="py -3.14"`` (Makefile style) or a bare executable path.
        parts = env.split()
        if len(parts) == 1 and Path(parts[0]).exists():
            return parts[0]
        probed = _try_executable([*parts, "-c", "import sys; print(sys.executable)"])
        if probed:
            return probed
        raise SystemExit(f"PYTHON={env!r} did not resolve to a usable interpreter")

    pin = _read_python_version_pin()
    if pin:
        probed = _try_executable(
            ["py", f"-{pin}", "-c", "import sys; print(sys.executable)"]
        )
        if probed:
            return probed

    venv_py = _cli_venv_python()
    if venv_py:
        return venv_py

    for ver in ("3.14", "3.13", "3.12", "3.11"):
        probed = _try_executable(
            ["py", f"-{ver}", "-c", "import sys; print(sys.executable)"]
        )
        if probed:
            return probed

    for name in ("python3", "python"):
        probed = _try_executable(
            [name, "-c", "import sys; print(sys.executable)"]
        )
        if probed:
            # Enforce 3.11+ like scripts/lib.ps1 Find-Python311.
            check = subprocess.run(
                [
                    probed,
                    "-c",
                    "import sys; raise SystemExit(0 if sys.version_info >= (3, 11) else 1)",
                ],
                check=False,
            )
            if check.returncode == 0:
                return probed

    raise SystemExit(
        "Python 3.11+ not found. Set PYTHON, install py launcher, or create "
        "apps/cli/.venv (see scripts/lib.ps1)."
    )


def _pwsh() -> list[str]:
    if platform.system() == "Windows":
        return ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass"]
    return ["pwsh", "-NoProfile", "-ExecutionPolicy", "Bypass"]


def _run_ps1(script_rel: str, *, env: dict[str, str] | None = None) -> int:
    script = REPO_ROOT / script_rel
    if not script.is_file():
        print(f"MISSING script: {script}", file=sys.stderr)
        return 2
    cmd = [*_pwsh(), "-File", str(script)]
    print(f"+ {' '.join(cmd)}")
    proc = subprocess.run(cmd, cwd=str(REPO_ROOT), env=env, check=False)
    return int(proc.returncode)


def _run_python_module(python: str, module: str, *args: str) -> int:
    cmd = [python, "-m", module, *args]
    print(f"+ {' '.join(cmd)}")
    proc = subprocess.run(cmd, cwd=str(REPO_ROOT), check=False)
    return int(proc.returncode)


def _run_python_script(python: str, script_rel: str, *args: str) -> int:
    script = REPO_ROOT / script_rel
    if not script.is_file():
        print(f"MISSING script: {script}", file=sys.stderr)
        return 2
    cmd = [python, str(script), *args]
    print(f"+ {' '.join(cmd)}")
    proc = subprocess.run(cmd, cwd=str(REPO_ROOT), check=False)
    return int(proc.returncode)


def _run_pytest(python: str, *paths: str) -> int:
    cmd = [python, "-m", "pytest", *paths, "-q"]
    print(f"+ {' '.join(cmd)}")
    proc = subprocess.run(cmd, cwd=str(REPO_ROOT), check=False)
    return int(proc.returncode)


def run_step(step_id: str, python: str) -> StepResult:
    """Execute one check step. Return codes mirror the underlying scripts."""
    t0 = time.perf_counter()
    code = 1
    detail = ""
    try:
        if step_id == "generate-contracts":
            # Makefile: generate-contracts
            code = _run_ps1("scripts/generate-contracts.ps1")
        elif step_id == "slice-cli":
            # Makefile check step 2 / apps/cli/scripts/check.ps1
            code = _run_ps1("apps/cli/scripts/check.ps1")
        elif step_id == "validate-schemas":
            # Makefile: validate-schemas
            code = _run_ps1("scripts/validate-schemas.ps1")
        elif step_id == "validate-examples":
            # Makefile: validate-examples
            code = _run_ps1("scripts/validate-examples.ps1")
        elif step_id == "validate-requirements":
            # Makefile: validate-requirements
            code = _run_ps1("scripts/validate-requirements.ps1")
        elif step_id == "check-constraints":
            # Makefile: check-constraints (ADR-045)
            code = _run_python_script(python, "scripts/check_constraint_matrix.py")
        elif step_id == "compare-golden":
            # Makefile: compare-golden
            code = _run_ps1("scripts/compare-golden.ps1")
        elif step_id == "architecture-check":
            # Makefile: architecture-check (also partially inside validate-schemas.ps1)
            install = subprocess.run(
                [
                    python,
                    "-m",
                    "pip",
                    "install",
                    "-q",
                    "-e",
                    str(REPO_ROOT / "tools/architecture-check[dev]"),
                ],
                cwd=str(REPO_ROOT),
                check=False,
            )
            if install.returncode != 0:
                code = int(install.returncode)
            else:
                code_pytest = _run_pytest(python, "tools/architecture-check/tests")
                if code_pytest != 0:
                    code = code_pytest
                else:
                    code = _run_python_module(
                        python, "architecture_check.cli", "--root", str(REPO_ROOT)
                    )
        elif step_id == "publish-gate":
            # Makefile: publish-gate
            code = _run_python_module(python, "moex_model_cli.gates.publish_gate")
        else:
            detail = f"unknown step {step_id!r}"
            code = 2
    except OSError as exc:
        detail = str(exc)
        code = 2
    elapsed = time.perf_counter() - t0
    return StepResult(
        step_id=step_id,
        ok=(code == 0),
        seconds=elapsed,
        detail=detail or f"exit={code}",
    )


def _print_table(results: list[StepResult]) -> None:
    width = max(len(s) for s in STEP_IDS)
    print()
    print(f"{'STEP':<{width}}  STATUS   TIME")
    print(f"{'-' * width}  -------  --------")
    for r in results:
        status = "OK" if r.ok else "FAIL"
        print(f"{r.step_id:<{width}}  {status:<7}  {r.seconds:7.1f}s")
    failed = [r for r in results if not r.ok]
    print()
    if failed:
        print(f"check_all FAILED ({len(failed)} step(s))")
    else:
        print("check_all OK")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Run Stage 0 checks (Makefile check + architecture-check + publish-gate).",
    )
    parser.add_argument(
        "--keep-going",
        action="store_true",
        help="Run all selected steps even after a failure; exit 1 if any failed.",
    )
    parser.add_argument(
        "--only",
        metavar="STEP",
        choices=STEP_IDS,
        help=f"Run a single step. Choices: {', '.join(STEP_IDS)}",
    )
    args = parser.parse_args(argv)

    python = resolve_python()
    print(f"check_all: python={python}")
    print(f"check_all: root={REPO_ROOT}")

    selected = [args.only] if args.only else list(STEP_IDS)
    results: list[StepResult] = []
    exit_code = 0

    for step_id in selected:
        print()
        print(f"=== {step_id} ===")
        result = run_step(step_id, python)
        results.append(result)
        if result.ok and step_id == "slice-cli":
            venv_py = _cli_venv_python()
            if venv_py and venv_py != python:
                python = venv_py
                print(f"check_all: python={python} (cli venv after slice-cli)")
        if not result.ok:
            exit_code = 1
            print(f"FAIL {step_id}: {result.detail}", file=sys.stderr)
            if not args.keep_going:
                _print_table(results)
                return exit_code

    _print_table(results)
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
