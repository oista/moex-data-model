"""Flatten MOEX DAMS LinkML modules into one self-contained YAML dump.

Derived publication artifact for moex.hierarchy «Полная спецификация».
Canonical SoT remains the modular tree under
``model-assets/specifications/moex-dams/<ver>/schemas/``.
"""

from __future__ import annotations

from pathlib import Path

from linkml_runtime.dumpers import yaml_dumper
from linkml_runtime.utils.schemaview import SchemaView

_HEADER = (
    "# Generated: merged MOEX DAMS LinkML (all modules flattened).\n"
    "# Source of truth: model-assets/specifications/moex-dams/*/schemas/\n"
    "# Do not edit by hand — regenerated at viewer publication build.\n"
)


def dump_merged_dams_schema(schema_path: Path) -> str:
    """Return YAML text of the import-flattened DAMS schema.

    Uses a fresh SchemaView (not the viewer cache) because ``merge_imports``
    mutates the underlying SchemaDefinition.
    """
    path = Path(schema_path).resolve()
    if not path.is_file():
        raise FileNotFoundError(f"DAMS schema not found: {path}")
    sv = SchemaView(str(path))
    # Force load of imported elements, then materialize into schema.classes.
    _ = sv.all_classes()
    sv.merge_imports()
    schema = sv.schema
    # Self-contained dump: no import edges left.
    schema.imports = []
    body = yaml_dumper.dumps(schema)
    body = body.replace("\r\n", "\n").replace("\r", "\n")
    if not body.endswith("\n"):
        body += "\n"
    return _HEADER + body


def dams_schema_root_path(spec_dir: Path) -> Path:
    """``…/moex-dams/0.1`` → ``…/schemas/moex-dams.yaml``."""
    return Path(spec_dir) / "schemas" / "moex-dams.yaml"
