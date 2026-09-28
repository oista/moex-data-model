"""map — SSSOM load / LinkML binding extract (ADR-008: not linkml-map engine)."""

from __future__ import annotations

import json
from pathlib import Path

from moex_model_cli.bootstrap import SlicePaths
from moex_semantic_mappings.linkml_extractor import extract_linkml_bindings
from moex_semantic_mappings.sssom_adapter import load_sssom_yaml


def run_map(
    paths: SlicePaths,
    *,
    sssom: Path | None = None,
    extract_schema: Path | None = None,
    as_json: bool = False,
) -> tuple[int, str]:
    if (sssom is None) == (extract_schema is None):
        # both None or both set
        if sssom is not None and extract_schema is not None:
            return (
                2,
                "moex-model map: use either --sssom or --extract-schema, not both "
                "(linkml-map engine = Stage 7 / ADR-008)\n",
            )
        return (
            2,
            "moex-model map requires --sssom PATH or --extract-schema PATH "
            "(SSSOM / LinkML extract; linkml-map engine = Stage 7 / ADR-008)\n",
        )

    if sssom is not None:
        path = sssom if sssom.is_absolute() else (paths.root / sssom).resolve()
        if not path.is_file():
            return 1, f"SSSOM file not found: {path}\n"
        try:
            mapping_set = load_sssom_yaml(path)
        except (OSError, ValueError, KeyError, TypeError) as exc:
            return 1, f"SSSOM load failed: {exc}\n"
        if as_json:
            payload = {
                "mapping_set_id": mapping_set.mapping_set_id,
                "mapping_set_version": mapping_set.mapping_set_version,
                "license": mapping_set.license,
                "bindings": [b.model_dump(mode="json") for b in mapping_set.mappings],
            }
            return 0, json.dumps(payload, indent=2, ensure_ascii=False) + "\n"
        return (
            0,
            f"map sssom={path.name} set_id={mapping_set.mapping_set_id} "
            f"version={mapping_set.mapping_set_version} "
            f"bindings={len(mapping_set.mappings)}\n",
        )

    assert extract_schema is not None
    path = (
        extract_schema
        if extract_schema.is_absolute()
        else (paths.root / extract_schema).resolve()
    )
    if not path.is_file():
        return 1, f"schema not found: {path}\n"
    try:
        bindings = extract_linkml_bindings(path)
    except (OSError, ValueError, TypeError) as exc:
        return 1, f"LinkML extract failed: {exc}\n"
    if as_json:
        payload = {
            "schema": str(path),
            "bindings": [b.model_dump(mode="json") for b in bindings],
        }
        return 0, json.dumps(payload, indent=2, ensure_ascii=False) + "\n"
    predicates: dict[str, int] = {}
    for b in bindings:
        predicates[b.predicate] = predicates.get(b.predicate, 0) + 1
    pred_summary = ", ".join(f"{k}={v}" for k, v in sorted(predicates.items()))
    return (
        0,
        f"map extract-schema={path.name} bindings={len(bindings)}"
        + (f" ({pred_summary})" if pred_summary else "")
        + "\n",
    )
