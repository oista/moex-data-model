"""map — SSSOM / LinkML extract / linkml-map transform (ADR-008)."""

from __future__ import annotations

import json
from pathlib import Path

from moex_model_cli.bootstrap import SlicePaths
from moex_modeling.shared.enums import DiagnosticSeverity
from moex_semantic_mappings.linkml_extractor import extract_linkml_bindings
from moex_semantic_mappings.sssom_adapter import load_sssom_yaml


def run_map(
    paths: SlicePaths,
    *,
    sssom: Path | None = None,
    extract_schema: Path | None = None,
    transform: Path | None = None,
    preview: Path | None = None,
    sample: Path | None = None,
    as_json: bool = False,
) -> tuple[int, str]:
    modes = [
        sssom is not None,
        extract_schema is not None,
        transform is not None,
    ]
    if sum(modes) != 1:
        return (
            2,
            "moex-model map requires exactly one of "
            "--sssom, --extract-schema, or --transform\n",
        )

    if transform is not None:
        return _run_transform(
            paths,
            transform=transform,
            preview=preview,
            sample=sample,
            as_json=as_json,
        )

    if preview is not None or sample is not None:
        return (
            2,
            "moex-model map: --preview/--sample only apply with --transform\n",
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


def _run_transform(
    paths: SlicePaths,
    *,
    transform: Path,
    preview: Path | None,
    sample: Path | None,
    as_json: bool,
) -> tuple[int, str]:
    if (preview is None) == (sample is None):
        if preview is not None and sample is not None:
            return 2, "moex-model map --transform: use either --preview or --sample\n"
        return (
            2,
            "moex-model map --transform requires --preview PATH or --sample PATH\n",
        )

    try:
        from moex_linkml_tooling.map_provider import LinkmlMapProvider
    except ImportError:
        return (
            1,
            "moex-model map --transform requires moex-linkml-tooling[map]\n",
        )

    spec = transform if transform.is_absolute() else (paths.root / transform).resolve()
    sample_path = preview or sample
    assert sample_path is not None
    sample_resolved = (
        sample_path if sample_path.is_absolute() else (paths.root / sample_path).resolve()
    )
    if not spec.is_file():
        return 1, f"transform spec not found: {spec}\n"
    if not sample_resolved.is_file():
        return 1, f"sample not found: {sample_resolved}\n"

    provider = LinkmlMapProvider()
    if preview is not None:
        result = provider.preview(spec, sample_resolved)
        payload = result.model_dump(mode="json")
        fatal = any(
            d.severity in {DiagnosticSeverity.ERROR, DiagnosticSeverity.FATAL}
            for d in result.diagnostics
        )
        text = (
            json.dumps(payload, indent=2, ensure_ascii=False) + "\n"
            if as_json
            else (
                f"map transform preview spec={result.spec.spec_id} "
                f"src={result.spec.source_schema_revision} "
                f"tgt={result.spec.target_schema_revision} "
                f"preserved={len(result.preserved_semantics)} "
                f"lost={len(result.lost_semantics)} "
                f"diagnostics={len(result.diagnostics)}\n"
            )
        )
        return (1 if fatal else 0), text

    result = provider.transform_sample(spec, sample_resolved)
    fatal = any(
        d.severity in {DiagnosticSeverity.ERROR, DiagnosticSeverity.FATAL}
        for d in result.diagnostics
    )
    if as_json:
        return (1 if fatal else 0), json.dumps(
            result.model_dump(mode="json"), indent=2, ensure_ascii=False
        ) + "\n"
    return (
        (1 if fatal else 0),
        f"map transform sample spec={result.spec.spec_id} "
        f"keys={sorted(result.output.keys())} "
        f"diagnostics={len(result.diagnostics)}\n",
    )
