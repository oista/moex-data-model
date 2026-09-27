"""Frontmatter and cross-doc consistency checks for docs/architecture."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import yaml
from linkml_runtime.utils.schemaview import SchemaView

REQUIRED_FRONTMATTER_KEYS = ("status", "version", "normative", "supersedes", "superseded_by")
ROOT_MARKERS = (
    re.compile(r"root_type[:\s*`]+([A-Za-z_][A-Za-z0-9_]*)", re.IGNORECASE),
    re.compile(r"tree_root[^\n]*`([A-Za-z_][A-Za-z0-9_]*)`", re.IGNORECASE),
    re.compile(
        r"spec root type[^\n]*`([A-Za-z_][A-Za-z0-9_]*)`",
        re.IGNORECASE,
    ),
    re.compile(
        r"\*\*spec root type\*\*[^\n]*`([A-Za-z_][A-Za-z0-9_]*)`",
        re.IGNORECASE,
    ),
)


def parse_frontmatter(text: str) -> tuple[dict[str, Any] | None, str]:
    if not text.startswith("---"):
        return None, text
    end = text.find("\n---", 3)
    if end < 0:
        return None, text
    block = text[3:end].strip()
    body = text[end + 4 :].lstrip("\n")
    data = yaml.safe_load(block) or {}
    if not isinstance(data, dict):
        return None, text
    return data, body


def iter_architecture_markdown(docs_dir: Path) -> list[Path]:
    return sorted(docs_dir.glob("*.md"))


def check_normative_unique(docs_dir: Path) -> list[str]:
    errors: list[str] = []
    normative_files: list[str] = []
    for path in iter_architecture_markdown(docs_dir):
        text = path.read_text(encoding="utf-8")
        meta, _ = parse_frontmatter(text)
        if meta is None:
            errors.append(f"{path.name}: missing YAML frontmatter")
            continue
        for key in REQUIRED_FRONTMATTER_KEYS:
            if key not in meta:
                errors.append(f"{path.name}: frontmatter missing key {key!r}")
        if meta.get("normative") is True:
            normative_files.append(path.name)
    if len(normative_files) != 1:
        errors.append(
            "expected exactly one normative:true document, "
            f"found {len(normative_files)}: {normative_files}"
        )
    return errors


def schema_tree_root(schema_path: Path) -> str | None:
    sv = SchemaView(str(schema_path))
    for name, cls in (sv.all_classes() or {}).items():
        if getattr(cls, "tree_root", False):
            return name
    return None


def extract_documented_root_types(normative_body: str) -> set[str]:
    found: set[str] = set()
    for pattern in ROOT_MARKERS:
        for match in pattern.finditer(normative_body):
            found.add(match.group(1))
    # Explicit prose form used in MODELING_ARCHITECTURE.md
    for match in re.finditer(
        r"`MOEXModelRepository`|MOEXModelRepository",
        normative_body,
    ):
        found.add("MOEXModelRepository")
    return found


def check_dams_root_alignment(
    docs_dir: Path,
    dams_schema: Path,
) -> list[str]:
    errors: list[str] = []
    normative_path: Path | None = None
    for path in iter_architecture_markdown(docs_dir):
        meta, body = parse_frontmatter(path.read_text(encoding="utf-8"))
        if meta and meta.get("normative") is True:
            normative_path = path
            normative_body = body
            break
    if normative_path is None:
        return ["no normative document found for root_type check"]

    actual = schema_tree_root(dams_schema)
    if actual is None:
        return [f"{dams_schema}: no class with tree_root: true"]

    documented = extract_documented_root_types(normative_body)
    if actual not in documented:
        errors.append(
            f"schema tree_root {actual!r} not mentioned as spec root in "
            f"{normative_path.name}; documented candidates={sorted(documented)}"
        )
    # Guard against the old wrong claim that ModelPackage is the tree_root
    if re.search(
        r"root type[^\n]*`ModelPackage`|root = `ModelPackage`",
        normative_body,
        re.IGNORECASE,
    ) and actual != "ModelPackage":
        errors.append(
            f"{normative_path.name} still claims ModelPackage as root type, "
            f"but schema tree_root is {actual!r}"
        )
    return errors


def check_docs(docs_dir: Path, dams_schema: Path) -> list[str]:
    return check_normative_unique(docs_dir) + check_dams_root_alignment(
        docs_dir, dams_schema
    )
