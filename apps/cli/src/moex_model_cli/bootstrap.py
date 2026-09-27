"""Composition root: default asset paths. No domain rules."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

DEFAULT_SCHEMA = Path("model_src") / "schemas" / "moex-dams.yaml"
DEFAULT_IMPLEMENTATION = Path("model_src") / "examples" / "trading-solution-model.yaml"
DEFAULT_SLICE_JSON = (
    Path("model_src") / "examples" / "publications" / "vertical_slice.json"
)
MARKER = DEFAULT_SCHEMA


def find_repo_root(start: Path | None = None) -> Path:
    cur = (start or Path.cwd()).resolve()
    for candidate in [cur, *cur.parents]:
        if (candidate / MARKER).is_file():
            return candidate
    return cur


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
        schema_path = schema if schema is not None else base / DEFAULT_SCHEMA
        impl_path = (
            implementation
            if implementation is not None
            else base / DEFAULT_IMPLEMENTATION
        )
        if not schema_path.is_absolute():
            schema_path = (base / schema_path).resolve()
        if not impl_path.is_absolute():
            impl_path = (base / impl_path).resolve()
        return cls(root=base, schema=schema_path, implementation=impl_path)
