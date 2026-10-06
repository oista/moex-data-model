"""Ensure transitional model tags stay within the ADR-043 registry."""

from __future__ import annotations

import re
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[2]
MODEL_ASSETS = REPO / "model-assets"

# Registry from docs/adr/ADR-043-transitional-tags-registry.md
ALLOWED_TRANSITIONAL_TAGS = frozenset({"transitional"})

# Heuristic: values that look like unnamed transitional markers.
FORBIDDEN_TAG_PATTERN = re.compile(
    r"^(transitional[-_].+|legacy[-_].+|tmp[-_].+|todo[-_].+)$",
    re.IGNORECASE,
)

# publish.yaml catalog tags are out of scope (viewer section labels).
SKIP_NAME_SUFFIXES = ("publish.yaml",)


def _iter_model_yaml() -> list[Path]:
    out: list[Path] = []
    if not MODEL_ASSETS.is_dir():
        return out
    for path in MODEL_ASSETS.rglob("*.yaml"):
        if path.name in SKIP_NAME_SUFFIXES or path.name.endswith(".publish.yaml"):
            continue
        out.append(path)
    return sorted(out)


def _collect_tags(node: object, acc: list[str]) -> None:
    if isinstance(node, dict):
        tags = node.get("tags")
        if isinstance(tags, list):
            for t in tags:
                if isinstance(t, str):
                    acc.append(t)
        elif isinstance(tags, str):
            acc.append(tags)
        for v in node.values():
            _collect_tags(v, acc)
    elif isinstance(node, list):
        for item in node:
            _collect_tags(item, acc)


def test_transitional_tags_are_registered() -> None:
    unknown: list[str] = []
    forbidden: list[str] = []
    seen_allowed = 0
    for path in _iter_model_yaml():
        try:
            data = yaml.safe_load(path.read_text(encoding="utf-8"))
        except Exception:
            continue
        tags: list[str] = []
        _collect_tags(data, tags)
        rel = path.relative_to(REPO).as_posix()
        for tag in tags:
            if tag in ALLOWED_TRANSITIONAL_TAGS:
                seen_allowed += 1
                continue
            if FORBIDDEN_TAG_PATTERN.match(tag):
                forbidden.append(f"{rel}: {tag}")
            # Other tags (domain labels) are allowed; only transitional-like names
            # must be registered.
            if tag.startswith("transitional") and tag not in ALLOWED_TRANSITIONAL_TAGS:
                unknown.append(f"{rel}: {tag}")
    assert not forbidden, "forbidden transitional-like tags:\n" + "\n".join(forbidden)
    assert not unknown, "unregistered transitional tags:\n" + "\n".join(unknown)
    assert seen_allowed > 0, "expected at least one registered transitional tag in model-assets"
