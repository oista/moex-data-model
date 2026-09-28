"""ROBOT JAR invocation helpers."""

from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path


DEFAULT_ROBOT_VERSION = "1.9.5"


class RobotNotAvailableError(RuntimeError):
    """Raised when neither ROBOT JAR nor ``robot`` on PATH is usable."""


def resolve_robot_command(
    *,
    jar_path: Path | None = None,
    cache_dir: Path | None = None,
    version: str = DEFAULT_ROBOT_VERSION,
) -> list[str]:
    """
    Resolve argv prefix to run ROBOT.

    Preference: explicit jar → ``ROBOT_JAR`` env → cache jar → ``robot`` on PATH.
    """
    if jar_path is not None:
        if not jar_path.is_file():
            raise RobotNotAvailableError(f"ROBOT JAR not found: {jar_path}")
        return ["java", "-jar", str(jar_path)]

    env_jar = os.environ.get("ROBOT_JAR")
    if env_jar:
        path = Path(env_jar)
        if path.is_file():
            return ["java", "-jar", str(path)]

    if cache_dir is not None:
        cached = cache_dir / f"robot-{version}.jar"
        if cached.is_file():
            return ["java", "-jar", str(cached)]

    which = shutil.which("robot")
    if which:
        return [which]

    raise RobotNotAvailableError(
        "ROBOT not available: set ROBOT_JAR, place jar in cache, or install robot on PATH"
    )


def robot_extract(
    *,
    input_ontology: Path,
    term_file: Path,
    output: Path,
    method: str = "BOT",
    jar_path: Path | None = None,
    cache_dir: Path | None = None,
    version: str = DEFAULT_ROBOT_VERSION,
) -> None:
    """Run ``robot extract`` and write ``output``."""
    cmd = resolve_robot_command(jar_path=jar_path, cache_dir=cache_dir, version=version)
    output.parent.mkdir(parents=True, exist_ok=True)
    full = [
        *cmd,
        "extract",
        "--method",
        method,
        "--input",
        str(input_ontology),
        "--term-file",
        str(term_file),
        "--output",
        str(output),
    ]
    proc = subprocess.run(
        full,
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    if proc.returncode != 0:
        raise RuntimeError(
            f"robot extract failed ({proc.returncode}): {proc.stderr or proc.stdout}"
        )


def robot_available(
    *,
    jar_path: Path | None = None,
    cache_dir: Path | None = None,
    version: str = DEFAULT_ROBOT_VERSION,
) -> bool:
    try:
        resolve_robot_command(jar_path=jar_path, cache_dir=cache_dir, version=version)
        return True
    except RobotNotAvailableError:
        return False
