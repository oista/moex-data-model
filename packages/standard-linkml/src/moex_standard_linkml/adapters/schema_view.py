"""SchemaView loader adapter."""

from __future__ import annotations

from pathlib import Path
from typing import Any


def load_schema_view(schema_path: Path | str) -> Any:
    from linkml_runtime.utils.schemaview import SchemaView

    return SchemaView(str(schema_path))


def tree_root_class(schema_view: Any) -> str | None:
    for name, cls in (schema_view.all_classes() or {}).items():
        if getattr(cls, "tree_root", False):
            return name
    return None
