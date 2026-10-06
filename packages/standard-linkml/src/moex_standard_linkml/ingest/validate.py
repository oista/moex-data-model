"""Validate ModelPackage YAML (linkml Validator, UTF-8-safe on Windows)."""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

import yaml


@dataclass
class ValidationResult:
    ok: bool
    returncode: int
    stdout: str
    stderr: str
    command: list[str]

    @property
    def report(self) -> str:
        parts = [
            f"$ {' '.join(self.command)}",
            f"exit={self.returncode}",
        ]
        if self.stdout.strip():
            parts.append("--- stdout ---")
            parts.append(self.stdout.rstrip())
        if self.stderr.strip():
            parts.append("--- stderr ---")
            parts.append(self.stderr.rstrip())
        return "\n".join(parts) + "\n"


def validate_model_package(
    package_path: Path | str,
    schema_path: Path | str,
    *,
    target_class: str = "ModelPackage",
    prefer_cli: bool = False,
) -> ValidationResult:
    """
    Validate a ModelPackage instance against the DAMS schema.

    Uses the in-process ``linkml.validator.Validator`` by default so YAML is
    read as UTF-8 (``linkml-validate`` on Windows opens files with the ANSI
    code page and fails on Cyrillic descriptions). Pass ``prefer_cli=True``
    to force the subprocess form with ``PYTHONUTF8=1``.
    """
    package_path = Path(package_path)
    schema_path = Path(schema_path)
    if prefer_cli:
        return _validate_via_cli(package_path, schema_path, target_class)
    return _validate_inprocess(package_path, schema_path, target_class)


def _validate_inprocess(
    package_path: Path,
    schema_path: Path,
    target_class: str,
) -> ValidationResult:
    command = [
        "linkml.validator.Validator",
        "-s",
        str(schema_path),
        "--target-class",
        target_class,
        str(package_path),
    ]
    try:
        from moex_standard_linkml.validation import (
            error_results,
            make_linkml_validator,
        )
    except ImportError as exc:
        return ValidationResult(
            ok=False,
            returncode=2,
            stdout="",
            stderr=f"linkml.validator unavailable: {exc}",
            command=command,
        )

    try:
        instance = yaml.safe_load(package_path.read_text(encoding="utf-8"))
        validator = make_linkml_validator(schema_path)
        report = validator.validate(instance, target_class)
    except Exception as exc:  # noqa: BLE001 — surface as validation failure
        return ValidationResult(
            ok=False,
            returncode=1,
            stdout="",
            stderr=f"{type(exc).__name__}: {exc}",
            command=command,
        )

    results = error_results(report)
    if not results:
        return ValidationResult(
            ok=True,
            returncode=0,
            stdout="No validation problems found.",
            stderr="",
            command=command,
        )

    lines = []
    for item in results:
        severity = getattr(item, "severity", None) or "ERROR"
        message = getattr(item, "message", None) or str(item)
        lines.append(f"[{severity}] {message}")
    return ValidationResult(
        ok=False,
        returncode=1,
        stdout="",
        stderr="\n".join(lines),
        command=command,
    )


def _validate_via_cli(
    package_path: Path,
    schema_path: Path,
    target_class: str,
) -> ValidationResult:
    command = _resolve_validate_command(schema_path, package_path, target_class)
    env = {**os.environ, "PYTHONUTF8": "1", "PYTHONIOENCODING": "utf-8"}
    proc = subprocess.run(
        command,
        capture_output=True,
        text=True,
        check=False,
        env=env,
    )
    return ValidationResult(
        ok=proc.returncode == 0,
        returncode=proc.returncode,
        stdout=proc.stdout or "",
        stderr=proc.stderr or "",
        command=command,
    )


def _resolve_validate_command(
    schema_path: Path,
    package_path: Path,
    target_class: str,
) -> list[str]:
    exe = shutil.which("linkml-validate")
    if exe:
        return [
            exe,
            "-s",
            str(schema_path),
            "--target-class",
            target_class,
            str(package_path),
        ]
    return [
        sys.executable,
        "-m",
        "linkml.validator.cli",
        "-s",
        str(schema_path),
        "--target-class",
        target_class,
        str(package_path),
    ]
