"""fmt — canonical YAML formatting check/write (LF, trailing newline, ruamel)."""

from __future__ import annotations

from io import StringIO
from pathlib import Path

from moex_repository_loader.loader import IMPLEMENTATIONS_REL


def _yaml():
    try:
        from ruamel.yaml import YAML
    except ImportError as exc:  # pragma: no cover - exercised when dep absent
        raise RuntimeError(
            "ruamel.yaml is required for moex-model fmt "
            "(present in the API image; install locally to run fmt outside CI)"
        ) from exc
    y = YAML(typ="rt")
    y.preserve_quotes = True
    y.explicit_start = False
    y.explicit_end = False
    y.width = 100
    y.indent(mapping=2, sequence=2, offset=0)
    return y


def canonical_bytes(text: str) -> bytes:
    """Round-trip YAML through ruamel and normalize line endings."""
    y = _yaml()
    data = y.load(text)
    buf = StringIO()
    y.dump(data, buf)
    out = buf.getvalue().replace("\r\n", "\n").replace("\r", "\n")
    if out and not out.endswith("\n"):
        out += "\n"
    return out.encode("utf-8")


def iter_yaml_files(repo_root: Path, paths: list[Path] | None = None) -> list[Path]:
    root = repo_root.resolve()
    if paths:
        out: list[Path] = []
        for p in paths:
            path = p if p.is_absolute() else root / p
            if path.is_file():
                out.append(path.resolve())
            elif path.is_dir():
                out.extend(sorted(path.rglob("*.yaml")))
                out.extend(sorted(path.rglob("*.yml")))
        return out
    base = root / IMPLEMENTATIONS_REL
    files = sorted(base.rglob("*.yaml")) + sorted(base.rglob("*.yml"))
    moex = root / ".moex"
    if moex.is_dir():
        files.extend(sorted(moex.rglob("*.yaml")))
        files.extend(sorted(moex.rglob("*.yml")))
    seen: set[Path] = set()
    unique: list[Path] = []
    for f in files:
        resolved = f.resolve()
        if resolved in seen:
            continue
        seen.add(resolved)
        unique.append(resolved)
    return unique


def check_or_write(
    repo_root: Path,
    *,
    write: bool = False,
    paths: list[Path] | None = None,
) -> tuple[int, str]:
    try:
        _yaml()
    except RuntimeError as exc:
        return 2, f"{exc}\n"
    files = iter_yaml_files(repo_root, paths)
    dirty: list[str] = []
    for path in files:
        original = path.read_bytes()
        try:
            text = original.decode("utf-8")
            formatted = canonical_bytes(text)
        except Exception as exc:  # noqa: BLE001 — report and continue
            return 1, f"fmt failed on {path}: {exc}\n"
        normalized_original = original.replace(b"\r\n", b"\n").replace(b"\r", b"\n")
        if normalized_original != formatted:
            try:
                rel = path.relative_to(repo_root.resolve()).as_posix()
            except ValueError:
                rel = path.as_posix()
            dirty.append(rel)
            if write:
                path.write_bytes(formatted)
    if not dirty:
        return 0, f"fmt OK files={len(files)}\n"
    action = "rewrote" if write else "need format"
    lines = [f"fmt {action} count={len(dirty)}:"]
    lines.extend(f"  {p}" for p in dirty)
    return (0 if write else 1), "\n".join(lines) + "\n"


def run_fmt(
    repo_root: Path,
    *,
    check: bool = False,
    write: bool = False,
    paths: list[Path] | None = None,
) -> tuple[int, str]:
    if check and write:
        return 2, "fmt: use either --check or --write, not both\n"
    if not check and not write:
        check = True
    return check_or_write(repo_root, write=write, paths=paths)
