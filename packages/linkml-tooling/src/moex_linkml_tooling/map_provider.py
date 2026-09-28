"""LinkmlMapProvider — ObjectTransformer behind MappingProvider (ADR-008)."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import yaml

from moex_modeling.conformance.domain import Diagnostic
from moex_modeling.mapping.public import (
    MappingPreview,
    MappingResult,
    TransformSpecMeta,
)
from moex_modeling.shared.enums import DiagnosticSeverity, TransformationKind

_MOEX_KEYS = {
    "moex_spec_id",
    "moex_source_schema_revision",
    "moex_target_schema_revision",
    "moex_transformation_kind",
    "moex_description",
    "moex_allow_unrestricted_eval",
    "moex_preserved_semantics",
    "moex_lost_semantics",
    "moex_source_schema",
    "moex_target_schema",
    "moex",
}

_EXPR_RE = re.compile(r"\bexpr\s*:", re.IGNORECASE)


def _as_source_type(value: Any) -> TransformationKind:
    if isinstance(value, TransformationKind):
        return value
    if value is None:
        return TransformationKind.PARTIAL
    return TransformationKind(str(value))


def _load_yaml(path: Path) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"transform spec must be a mapping: {path}")
    return data


def _split_moex(raw: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    """Return (moex_meta_flat, linkml_map_body)."""
    moex_block = raw.get("moex")
    flat: dict[str, Any] = {}
    if isinstance(moex_block, dict):
        flat.update(moex_block)
    for key in list(raw.keys()):
        if key.startswith("moex_") and key != "moex":
            flat[key.removeprefix("moex_")] = raw[key]
    body = {k: v for k, v in raw.items() if k not in _MOEX_KEYS}
    return flat, body


def _collect_expr_strings(node: Any, found: list[str] | None = None) -> list[str]:
    found = found if found is not None else []
    if isinstance(node, dict):
        for k, v in node.items():
            if k == "expr" and isinstance(v, str):
                found.append(v)
            else:
                _collect_expr_strings(v, found)
    elif isinstance(node, list):
        for item in node:
            _collect_expr_strings(item, found)
    return found


def _load_sample(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    if path.suffix.lower() in {".yaml", ".yml"}:
        data = yaml.safe_load(text)
    else:
        import json

        data = json.loads(text)
    if not isinstance(data, dict):
        raise ValueError(f"sample must be a mapping: {path}")
    # Optional wrapper: {class: Person, object: {...}}
    if "object" in data and isinstance(data["object"], dict):
        return data
    return {"class": data.get("class") or data.get("source_type"), "object": data}


class LinkmlMapProvider:
    """
    MappingProvider implementation using linkml-map ObjectTransformer only.

    Expression allowlist is empty by default; unrestricted_eval is never enabled
    on the transformer unless explicitly allowed *and* every expr is allowlisted.
    """

    def __init__(
        self,
        *,
        expression_allowlist: frozenset[str] | None = None,
        allow_unrestricted_eval: bool = False,
    ) -> None:
        self._expression_allowlist = expression_allowlist or frozenset()
        self._allow_unrestricted_eval = allow_unrestricted_eval

    def load_spec_meta(self, spec_path: Path) -> TransformSpecMeta:
        raw = _load_yaml(spec_path)
        moex, _body = _split_moex(raw)
        spec_id = moex.get("spec_id") or raw.get("id")
        source_rev = moex.get("source_schema_revision")
        target_rev = moex.get("target_schema_revision")
        if not spec_id or not source_rev or not target_rev:
            raise ValueError(
                f"{spec_path}: moex.spec_id, source_schema_revision, "
                "and target_schema_revision are required"
            )
        return TransformSpecMeta(
            spec_id=str(spec_id),
            source_schema_revision=str(source_rev),
            target_schema_revision=str(target_rev),
            transformation_kind=_as_source_type(moex.get("transformation_kind")),
            description=moex.get("description"),
            allow_unrestricted_eval=bool(
                moex.get("allow_unrestricted_eval", self._allow_unrestricted_eval)
            ),
        )

    def validate_spec(self, spec_path: Path) -> list[Diagnostic]:
        diagnostics: list[Diagnostic] = []
        try:
            meta = self.load_spec_meta(spec_path)
        except (OSError, ValueError, KeyError, TypeError) as exc:
            return [
                Diagnostic(
                    diagnostic_code="MAP-SPEC-001",
                    severity=DiagnosticSeverity.ERROR,
                    diagnostic_message=str(exc),
                )
            ]
        raw = _load_yaml(spec_path)
        _moex, body = _split_moex(raw)
        exprs = _collect_expr_strings(body)
        if exprs:
            if not meta.allow_unrestricted_eval:
                diagnostics.append(
                    Diagnostic(
                        diagnostic_code="MAP-EXPR-001",
                        severity=DiagnosticSeverity.ERROR,
                        diagnostic_message=(
                            "transform uses expr: but unrestricted eval is disabled "
                            f"({len(exprs)} expression(s))"
                        ),
                    )
                )
            else:
                banned = [e for e in exprs if e not in self._expression_allowlist]
                if banned:
                    diagnostics.append(
                        Diagnostic(
                            diagnostic_code="MAP-EXPR-002",
                            severity=DiagnosticSeverity.ERROR,
                            diagnostic_message=(
                                "expressions not on allowlist: "
                                + "; ".join(repr(b[:80]) for b in banned[:5])
                            ),
                        )
                    )
        if "class_derivations" not in body:
            diagnostics.append(
                Diagnostic(
                    diagnostic_code="MAP-SPEC-002",
                    severity=DiagnosticSeverity.ERROR,
                    diagnostic_message="missing class_derivations",
                )
            )
        return diagnostics

    def preview(self, spec_path: Path, sample_path: Path) -> MappingPreview:
        meta = self.load_spec_meta(spec_path)
        diags = self.validate_spec(spec_path)
        if any(
            d.severity in {DiagnosticSeverity.ERROR, DiagnosticSeverity.FATAL}
            for d in diags
        ):
            return MappingPreview(spec=meta, diagnostics=tuple(diags))
        raw = _load_yaml(spec_path)
        moex, _body = _split_moex(raw)
        preserved = tuple(moex.get("preserved_semantics") or ())
        lost = tuple(moex.get("lost_semantics") or ())
        try:
            result = self.transform_sample(spec_path, sample_path)
            return MappingPreview(
                spec=meta,
                preserved_semantics=preserved or result.preserved_semantics,
                lost_semantics=lost or result.lost_semantics,
                diagnostics=tuple(diags) + result.diagnostics,
                preview_payload=result.output,
            )
        except (OSError, ValueError, KeyError, TypeError, ImportError) as exc:
            return MappingPreview(
                spec=meta,
                preserved_semantics=preserved,
                lost_semantics=lost,
                diagnostics=tuple(diags)
                + (
                    Diagnostic(
                        diagnostic_code="MAP-PREVIEW-001",
                        severity=DiagnosticSeverity.ERROR,
                        diagnostic_message=str(exc),
                    ),
                ),
            )

    def transform_sample(self, spec_path: Path, sample_path: Path) -> MappingResult:
        meta = self.load_spec_meta(spec_path)
        diags = self.validate_spec(spec_path)
        if any(
            d.severity in {DiagnosticSeverity.ERROR, DiagnosticSeverity.FATAL}
            for d in diags
        ):
            return MappingResult(spec=meta, diagnostics=tuple(diags))

        try:
            from linkml_map.transformer.object_transformer import ObjectTransformer
        except ImportError as exc:  # pragma: no cover
            raise ImportError(
                "linkml-map is required for LinkmlMapProvider; "
                "install moex-linkml-tooling[map]"
            ) from exc

        raw = _load_yaml(spec_path)
        moex, body = _split_moex(raw)
        preserved = tuple(str(x) for x in (moex.get("preserved_semantics") or ()))
        lost = tuple(str(x) for x in (moex.get("lost_semantics") or ()))

        sample = _load_sample(sample_path)
        source_class = sample.get("class")
        obj = sample["object"]
        if not isinstance(obj, dict):
            raise ValueError("sample object must be a mapping")
        if source_class is None:
            # Infer single class_derivation populated_from
            derivations = body.get("class_derivations") or {}
            if len(derivations) == 1:
                only = next(iter(derivations.values()))
                source_class = (
                    only.get("populated_from")
                    if isinstance(only, dict)
                    else None
                ) or next(iter(derivations))
            else:
                raise ValueError("sample must include 'class' for multi-class specs")

        # Write body-only temp? ObjectTransformer can load from path; write sibling.
        body_path = spec_path
        # Prefer loading original if body is top-level compatible; else temp stripped file.
        if set(raw.keys()) - _MOEX_KEYS != set(body.keys()) or "moex" in raw:
            import tempfile

            tmp = Path(tempfile.mkdtemp()) / "transform_body.yaml"
            tmp.write_text(
                yaml.safe_dump(body, sort_keys=False, allow_unicode=True),
                encoding="utf-8",
            )
            body_path = tmp

        ot = ObjectTransformer(unrestricted_eval=False)
        source_schema = moex.get("source_schema")
        if source_schema:
            schema_path = Path(str(source_schema))
            if not schema_path.is_absolute():
                schema_path = (spec_path.parent / schema_path).resolve()
            ot.load_source_schema(str(schema_path))
        ot.load_transformer_specification(body_path)

        mapped = ot.map_object(obj, str(source_class))
        if not isinstance(mapped, dict):
            mapped = dict(mapped) if mapped is not None else {}

        return MappingResult(
            spec=meta,
            output=mapped,
            preserved_semantics=preserved,
            lost_semantics=lost,
            diagnostics=tuple(diags),
            round_trip_ok=None,
        )


__all__ = ["LinkmlMapProvider"]
