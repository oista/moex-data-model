"""Apply inline edits to YAML/LinkML sources (serve mode only)."""

from __future__ import annotations

import hashlib
import json
import os
import re
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable

from ruamel.yaml import YAML

EDITABLE_FIELDS = frozenset({"description", "title", "aliases"})

_LIST_SEG = re.compile(r"^([A-Za-z_][\w-]*)\[([A-Za-z_][\w-]*)=(.*)\]$")
_MAP_SEG = re.compile(r"^[A-Za-z_][\w-]*$")


class EditError(Exception):
    """Base for edit failures with HTTP-oriented status."""

    def __init__(self, message: str, *, status: int = 422) -> None:
        super().__init__(message)
        self.status = status
        self.message = message


@dataclass(frozen=True)
class EditTarget:
    file: str
    yaml_path: str
    field: str
    base_hash: str

    def registry_key(self) -> tuple[str, str, str]:
        return (self.file, self.yaml_path, self.field)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> EditTarget:
        return cls(
            file=str(data["file"]),
            yaml_path=str(data["yaml_path"]),
            field=str(data["field"]),
            base_hash=str(data["base_hash"]),
        )

    def to_dict(self) -> dict[str, str]:
        return {
            "file": self.file,
            "yaml_path": self.yaml_path,
            "field": self.field,
            "base_hash": self.base_hash,
        }


@dataclass
class ApplyResult:
    ok: bool
    new_value: Any
    new_hash: str
    path: Path


def value_hash(value: Any) -> str:
    """SHA-256 of canonical JSON for the source value."""
    canonical = json.dumps(value, ensure_ascii=False, separators=(",", ":"), sort_keys=False)
    if isinstance(value, list):
        # list order is significant; keep as-is
        pass
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def make_edit_target(
    *,
    file: str,
    yaml_path: str,
    field: str,
    value: Any,
) -> dict[str, str]:
    if field not in EDITABLE_FIELDS:
        raise ValueError(f"field not editable: {field}")
    return EditTarget(
        file=file,
        yaml_path=yaml_path,
        field=field,
        base_hash=value_hash(value if value is not None else ""),
    ).to_dict()


def parse_yaml_path(path: str) -> list[tuple[str, str | None, str | None]]:
    """Parse ``a.b[key=val].c`` into segments.

    Each segment is ``(name, key_name|None, key_value|None)``.
    Map segments have key_name/key_value None.
    """
    if not path or not path.strip():
        raise EditError("empty yaml_path", status=422)
    parts = path.split(".")
    segs: list[tuple[str, str | None, str | None]] = []
    for part in parts:
        m = _LIST_SEG.match(part)
        if m:
            segs.append((m.group(1), m.group(2), m.group(3)))
            continue
        if _MAP_SEG.match(part):
            segs.append((part, None, None))
            continue
        raise EditError(f"invalid yaml_path segment: {part!r}", status=422)
    return segs


def resolve_under_root(root: Path, rel: str) -> Path:
    """Resolve ``rel`` under ``root``; reject escapes, symlinks leaving root, bad ext."""
    root = root.resolve()
    if not rel or rel.startswith("/") or rel.startswith("\\") or ".." in Path(rel).parts:
        raise EditError(f"path escapes root: {rel}", status=403)
    candidate = (root / rel).resolve()
    try:
        candidate.relative_to(root)
    except ValueError as exc:
        raise EditError(f"path escapes root: {rel}", status=403) from exc
    if candidate.suffix.lower() not in {".yaml", ".yml"}:
        raise EditError(f"unsupported extension: {candidate.suffix}", status=422)
    if not candidate.is_file():
        raise EditError(f"file not found: {rel}", status=404)
    # Reject if any symlink parent leaves root
    cur = candidate
    while True:
        if cur.is_symlink():
            real = cur.resolve()
            try:
                real.relative_to(root)
            except ValueError as exc:
                raise EditError(f"symlink escapes root: {rel}", status=403) from exc
        if cur == root or cur.parent == cur:
            break
        cur = cur.parent
    return candidate


def _ruamel() -> YAML:
    y = YAML(typ="rt")
    y.preserve_quotes = True
    y.width = 4096
    y.default_flow_style = False
    return y


def _navigate(doc: Any, segs: list[tuple[str, str | None, str | None]]) -> Any:
    """Return parent container and final key for the last segment.

    Returns ``(parent, final_key)`` where assignment is ``parent[final_key] = value``.
    For list segments the final key is the dict key name on the matched entry —
    wait, the last segment is always a field name (map seg). Intermediate list
    segs navigate into the matched dict.
    """
    if not segs:
        raise EditError("empty path", status=422)
    *head, last = segs
    if last[1] is not None:
        raise EditError("yaml_path must end with a field name", status=422)

    current: Any = doc
    for name, key_name, key_value in head:
        if not isinstance(current, dict) or name not in current:
            raise EditError(f"path not found at {name}", status=404)
        node = current[name]
        if key_name is None:
            current = node
            continue
        if not isinstance(node, list):
            raise EditError(f"expected list at {name}", status=422)
        match = None
        for item in node:
            if isinstance(item, dict) and str(item.get(key_name)) == key_value:
                match = item
                break
        if match is None:
            raise EditError(
                f"no list entry {name}[{key_name}={key_value}]",
                status=404,
            )
        current = match

    last_name = last[0]
    if not isinstance(current, dict):
        raise EditError("parent is not a mapping", status=422)
    return current, last_name


def get_value_at_path(doc: Any, yaml_path: str) -> Any:
    parent, key = _navigate(doc, parse_yaml_path(yaml_path))
    return parent.get(key)


def set_value_at_path(doc: Any, yaml_path: str, value: Any) -> None:
    parent, key = _navigate(doc, parse_yaml_path(yaml_path))
    parent[key] = value


def _sibling_titles(doc: Any, yaml_path: str) -> list[str]:
    """Titles of sibling list entries under the same parent list."""
    segs = parse_yaml_path(yaml_path)
    if len(segs) < 2 or segs[-1][0] != "title":
        return []
    # Find nearest list segment from the end
    *head, last = segs
    list_idx = None
    for i in range(len(head) - 1, -1, -1):
        if head[i][1] is not None:
            list_idx = i
            break
    if list_idx is None:
        return []

    current: Any = doc
    for name, key_name, key_value in head[:list_idx]:
        if not isinstance(current, dict) or name not in current:
            return []
        node = current[name]
        if key_name is None:
            current = node
            continue
        if not isinstance(node, list):
            return []
        match = next(
            (
                item
                for item in node
                if isinstance(item, dict) and str(item.get(key_name)) == key_value
            ),
            None,
        )
        if match is None:
            return []
        current = match

    list_name, list_key, list_val = head[list_idx]
    if not isinstance(current, dict) or list_name not in current:
        return []
    items = current[list_name]
    if not isinstance(items, list):
        return []
    titles: list[str] = []
    for item in items:
        if not isinstance(item, dict):
            continue
        if str(item.get(list_key)) == list_val:
            continue  # skip self
        t = item.get("title")
        if isinstance(t, str) and t.strip():
            titles.append(t.strip())
    return titles


def validate_new_value(
    doc: Any,
    yaml_path: str,
    field: str,
    new_value: Any,
) -> Any:
    if field == "title":
        if not isinstance(new_value, str) or not new_value.strip():
            raise EditError("title must be a non-empty string", status=422)
        cleaned = new_value.strip()
        siblings = _sibling_titles(doc, yaml_path)
        if cleaned in siblings:
            raise EditError(f"duplicate sibling title: {cleaned}", status=422)
        return cleaned
    if field == "description":
        if new_value is None:
            return ""
        if not isinstance(new_value, str):
            raise EditError("description must be a string", status=422)
        return new_value
    if field == "aliases":
        if isinstance(new_value, str):
            lines = [ln.strip() for ln in new_value.splitlines() if ln.strip()]
            return lines
        if isinstance(new_value, list):
            out = [str(x) for x in new_value]
            return out
        raise EditError("aliases must be a list or newline-separated string", status=422)
    raise EditError(f"field not editable: {field}", status=422)


def load_yaml_rt(path: Path) -> Any:
    y = _ruamel()
    with path.open("r", encoding="utf-8") as fh:
        return y.load(fh)


def dump_yaml_rt(path: Path, data: Any) -> None:
    y = _ruamel()
    fd, tmp_name = tempfile.mkstemp(
        suffix=path.suffix, prefix=path.stem + ".", dir=str(path.parent)
    )
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as fh:
            y.dump(data, fh)
        Path(tmp_name).replace(path)
    except Exception:
        try:
            Path(tmp_name).unlink(missing_ok=True)
        except OSError:
            pass
        raise


def apply_edit(
    root: Path,
    target: EditTarget | dict[str, Any],
    new_value: Any,
    registry: dict[tuple[str, str, str], EditTarget] | set[tuple[str, str, str]],
    *,
    rebuild: Callable[[], None] | None = None,
) -> ApplyResult:
    """Write ``new_value`` at ``target``, optionally rebuild; rollback on failure."""
    if isinstance(target, dict):
        target = EditTarget.from_dict(target)
    if target.field not in EDITABLE_FIELDS:
        raise EditError(f"field not editable: {target.field}", status=422)

    key = target.registry_key()
    if key not in registry:
        raise EditError("unknown edit target", status=404)

    path = resolve_under_root(root, target.file)
    original = path.read_bytes()

    try:
        doc = load_yaml_rt(path)
    except Exception as exc:
        raise EditError(f"cannot parse YAML: {exc}", status=422) from exc

    current = get_value_at_path(doc, target.yaml_path)
    # Missing key: treat as empty string / empty list for hash compare
    if current is None and target.field == "aliases":
        current_for_hash: Any = []
    elif current is None:
        current_for_hash = ""
    else:
        current_for_hash = current

    if value_hash(current_for_hash) != target.base_hash:
        raise EditError(
            "base_hash mismatch; reload and retry",
            status=409,
        )

    cleaned = validate_new_value(doc, target.yaml_path, target.field, new_value)
    set_value_at_path(doc, target.yaml_path, cleaned)

    try:
        dump_yaml_rt(path, doc)
    except Exception as exc:
        path.write_bytes(original)
        raise EditError(f"write failed: {exc}", status=422) from exc

    if rebuild is not None:
        try:
            rebuild()
        except Exception as exc:
            path.write_bytes(original)
            raise EditError(f"rebuild failed: {exc}", status=422) from exc

    return ApplyResult(
        ok=True,
        new_value=cleaned,
        new_hash=value_hash(cleaned),
        path=path,
    )


def collect_edit_registry(modules: list[Any]) -> dict[tuple[str, str, str], EditTarget]:
    """Walk PublicationModule items and collect edit_targets maps."""
    registry: dict[tuple[str, str, str], EditTarget] = {}

    def walk(item: Any) -> None:
        targets = getattr(item, "edit_targets", None)
        if targets is None and isinstance(item, dict):
            targets = item.get("edit_targets")
        if isinstance(targets, dict):
            for et in targets.values():
                if isinstance(et, dict) and et.get("file") and et.get("yaml_path") and et.get("field"):
                    target = EditTarget.from_dict(et)
                    registry[target.registry_key()] = target
        children = getattr(item, "children", None)
        if children is None and isinstance(item, dict):
            children = item.get("children")
        for child in children or []:
            walk(child)

    for mod in modules:
        sections = getattr(mod, "sections", None)
        if sections is None and isinstance(mod, dict):
            sections = mod.get("sections")
        for sec in sections or []:
            items = getattr(sec, "items", None)
            if items is None and isinstance(sec, dict):
                items = sec.get("items")
            for item in items or []:
                walk(item)
    return registry
