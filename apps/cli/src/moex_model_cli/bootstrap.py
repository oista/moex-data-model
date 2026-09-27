"""Composition root: default asset paths. No domain rules."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

DAMS_SPEC_DIR = Path("model-assets") / "specifications" / "moex-dams" / "0.1"
DEFAULT_SCHEMA = DAMS_SPEC_DIR / "schemas" / "moex-dams.yaml"
DEFAULT_SPECIFICATION_ENVELOPE = DAMS_SPEC_DIR / "specification.yaml"

TRADING_IMPL_DIR = (
    Path("model-assets") / "implementations" / "solutions" / "trading-platform"
)
DEFAULT_IMPLEMENTATION = TRADING_IMPL_DIR / "trading-solution-model.yaml"
DEFAULT_IMPLEMENTATION_ENVELOPE = TRADING_IMPL_DIR / "implementation.yaml"
DEFAULT_SLICE_JSON = TRADING_IMPL_DIR / "publications" / "vertical_slice.json"

DEFAULT_STANDARD_ENVELOPE = (
    Path("model-assets") / "standards" / "linkml" / "1.x" / "standard.yaml"
)

MARKER = DEFAULT_SCHEMA


def find_repo_root(start: Path | None = None) -> Path:
    cur = (start or Path.cwd()).resolve()
    for candidate in [cur, *cur.parents]:
        if (candidate / MARKER).is_file():
            return candidate
    return cur


def _load_yaml(path: Path) -> dict[str, Any]:
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError(f"expected mapping in {path}")
    return raw


def resolve_schema_from_specification_envelope(envelope_path: Path) -> Path:
    """Resolve schema_body relative to the specification envelope directory."""
    data = _load_yaml(envelope_path)
    rel = data.get("schema_body")
    if not isinstance(rel, str) or not rel:
        raise ValueError(f"{envelope_path}: missing schema_body")
    path = (envelope_path.parent / rel).resolve()
    if not path.is_file():
        raise FileNotFoundError(f"schema_body not found: {path}")
    return path


def resolve_body_from_implementation_envelope(envelope_path: Path) -> Path:
    """Resolve implementation_body relative to the implementation envelope."""
    data = _load_yaml(envelope_path)
    rel = data.get("implementation_body") or data.get("body_ref")
    if not isinstance(rel, str) or not rel:
        raise ValueError(f"{envelope_path}: missing implementation_body")
    path = (envelope_path.parent / rel).resolve()
    if not path.is_file():
        raise FileNotFoundError(f"implementation_body not found: {path}")
    return path


@dataclass(frozen=True)
class SlicePaths:
    root: Path
    schema: Path
    implementation: Path

    @classmethod
    def resolve(
        cls,
        *,
        root: Path | None = None,
        schema: Path | None = None,
        implementation: Path | None = None,
    ) -> SlicePaths:
        base = find_repo_root(root) if root is None else root.resolve()

        if schema is not None:
            schema_path = schema if schema.is_absolute() else (base / schema).resolve()
        else:
            spec_env = base / DEFAULT_SPECIFICATION_ENVELOPE
            if spec_env.is_file():
                schema_path = resolve_schema_from_specification_envelope(spec_env)
            else:
                schema_path = (base / DEFAULT_SCHEMA).resolve()

        if implementation is not None:
            impl_path = (
                implementation
                if implementation.is_absolute()
                else (base / implementation).resolve()
            )
        else:
            impl_env = base / DEFAULT_IMPLEMENTATION_ENVELOPE
            if impl_env.is_file():
                impl_path = resolve_body_from_implementation_envelope(impl_env)
            else:
                impl_path = (base / DEFAULT_IMPLEMENTATION).resolve()

        return cls(root=base, schema=schema_path, implementation=impl_path)
