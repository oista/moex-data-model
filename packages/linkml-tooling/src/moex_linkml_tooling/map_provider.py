"""LinkmlMapProvider — ObjectTransformer + optional SQL backend (ADR-008)."""

from __future__ import annotations

import sqlite3
import tempfile
from pathlib import Path
from typing import Any, Literal

import yaml

from moex_modeling.conformance.domain import Diagnostic
from moex_modeling.mapping.public import (
    MappingPreview,
    MappingResult,
    TransformSpecMeta,
)
from moex_modeling.shared.enums import DiagnosticSeverity, TransformationKind

MapBackend = Literal["object", "sql"]

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
    if "object" in data and isinstance(data["object"], dict):
        return data
    return {"class": data.get("class") or data.get("source_type"), "object": data}


def _write_body(spec_path: Path, raw: dict[str, Any], body: dict[str, Any]) -> Path:
    if set(raw.keys()) - _MOEX_KEYS != set(body.keys()) or "moex" in raw:
        tmp = Path(tempfile.mkdtemp()) / "transform_body.yaml"
        tmp.write_text(
            yaml.safe_dump(body, sort_keys=False, allow_unicode=True),
            encoding="utf-8",
        )
        return tmp
    return spec_path


def _infer_source_class(body: dict[str, Any], sample_class: Any) -> str:
    if sample_class is not None:
        return str(sample_class)
    derivations = body.get("class_derivations") or {}
    if len(derivations) == 1:
        only = next(iter(derivations.values()))
        return str(
            (only.get("populated_from") if isinstance(only, dict) else None)
            or next(iter(derivations))
        )
    raise ValueError("sample must include 'class' for multi-class specs")


def _sql_quote_ident(name: str) -> str:
    if not name.replace("_", "").isalnum():
        raise ValueError(f"unsafe SQL identifier: {name!r}")
    return name


def _resolve_schema_path(spec_path: Path, relative: str) -> Path:
    """Resolve schema path relative to the transform YAML directory."""
    candidate = Path(relative)
    if candidate.is_absolute():
        return candidate
    return (spec_path.parent / candidate).resolve()


def _validate_schema_paths(
    *,
    spec_path: Path,
    moex: dict[str, Any],
    source_revision: str,
    target_revision: str,
) -> list[Diagnostic]:
    """
    Audit source_schema / target_schema paths.

    When revisions differ (migration), both paths are required.
    Declared paths must resolve to existing files (relative to the spec).
    """
    diagnostics: list[Diagnostic] = []
    source_rel = moex.get("source_schema")
    target_rel = moex.get("target_schema")
    migration = source_revision != target_revision

    if migration:
        if not source_rel:
            diagnostics.append(
                Diagnostic(
                    diagnostic_code="MAP-SPEC-003",
                    severity=DiagnosticSeverity.ERROR,
                    diagnostic_message=(
                        "migration requires moex.source_schema "
                        f"(revisions {source_revision!r} → {target_revision!r})"
                    ),
                )
            )
        if not target_rel:
            diagnostics.append(
                Diagnostic(
                    diagnostic_code="MAP-SPEC-003",
                    severity=DiagnosticSeverity.ERROR,
                    diagnostic_message=(
                        "migration requires moex.target_schema "
                        f"(revisions {source_revision!r} → {target_revision!r})"
                    ),
                )
            )

    for label, rel in (("source_schema", source_rel), ("target_schema", target_rel)):
        if not rel:
            continue
        resolved = _resolve_schema_path(spec_path, str(rel))
        if not resolved.is_file():
            diagnostics.append(
                Diagnostic(
                    diagnostic_code="MAP-SPEC-004",
                    severity=DiagnosticSeverity.ERROR,
                    diagnostic_message=(
                        f"moex.{label} does not resolve to a file: {rel!r} "
                        f"(looked at {resolved})"
                    ),
                )
            )
    return diagnostics


class LinkmlMapProvider:
    """
    MappingProvider implementation using linkml-map.

    Default backend is ObjectTransformer. SQL backend uses SQLCompiler + SQLite
    and only supports populated_from slot mappings (no expr).
    """

    def __init__(
        self,
        *,
        expression_allowlist: frozenset[str] | None = None,
        allow_unrestricted_eval: bool = False,
        backend: MapBackend = "object",
    ) -> None:
        self._expression_allowlist = expression_allowlist or frozenset()
        self._allow_unrestricted_eval = allow_unrestricted_eval
        self._backend: MapBackend = backend

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
            if self._backend == "sql":
                diagnostics.append(
                    Diagnostic(
                        diagnostic_code="MAP-SQL-001",
                        severity=DiagnosticSeverity.ERROR,
                        diagnostic_message=(
                            "SQL backend does not support expr: "
                            f"({len(exprs)} expression(s))"
                        ),
                    )
                )
            elif not meta.allow_unrestricted_eval:
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
        diagnostics.extend(
            _validate_schema_paths(
                spec_path=spec_path,
                moex=_moex,
                source_revision=meta.source_schema_revision,
                target_revision=meta.target_schema_revision,
            )
        )
        return diagnostics

    def preview(
        self,
        spec_path: Path,
        sample_path: Path,
        *,
        backend: MapBackend | None = None,
    ) -> MappingPreview:
        meta = self.load_spec_meta(spec_path)
        be = backend or self._backend
        prev = self._backend
        self._backend = be
        try:
            diags = self.validate_spec(spec_path)
        finally:
            self._backend = prev
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
            result = self.transform_sample(spec_path, sample_path, backend=be)
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

    def transform_sample(
        self,
        spec_path: Path,
        sample_path: Path,
        *,
        backend: MapBackend | None = None,
    ) -> MappingResult:
        be = backend or self._backend
        prev = self._backend
        self._backend = be
        try:
            meta = self.load_spec_meta(spec_path)
            diags = self.validate_spec(spec_path)
            if any(
                d.severity in {DiagnosticSeverity.ERROR, DiagnosticSeverity.FATAL}
                for d in diags
            ):
                return MappingResult(spec=meta, diagnostics=tuple(diags))

            raw = _load_yaml(spec_path)
            moex, body = _split_moex(raw)
            preserved = tuple(str(x) for x in (moex.get("preserved_semantics") or ()))
            lost = tuple(str(x) for x in (moex.get("lost_semantics") or ()))
            sample = _load_sample(sample_path)
            obj = sample["object"]
            if not isinstance(obj, dict):
                raise ValueError("sample object must be a mapping")
            source_class = _infer_source_class(body, sample.get("class"))
            body_path = _write_body(spec_path, raw, body)

            if be == "sql":
                mapped = self._transform_sql(
                    spec_path=spec_path,
                    moex=moex,
                    body=body,
                    body_path=body_path,
                    source_class=source_class,
                    obj=obj,
                )
            else:
                mapped = self._transform_object(
                    moex=moex,
                    body_path=body_path,
                    source_class=source_class,
                    obj=obj,
                    spec_path=spec_path,
                )

            return MappingResult(
                spec=meta,
                output=mapped,
                preserved_semantics=preserved,
                lost_semantics=lost,
                diagnostics=tuple(diags),
                round_trip_ok=None,
            )
        finally:
            self._backend = prev

    def _transform_object(
        self,
        *,
        moex: dict[str, Any],
        body_path: Path,
        source_class: str,
        obj: dict[str, Any],
        spec_path: Path,
    ) -> dict[str, Any]:
        try:
            from linkml_map.transformer.object_transformer import ObjectTransformer
        except ImportError as exc:  # pragma: no cover
            raise ImportError(
                "linkml-map is required for LinkmlMapProvider; "
                "install moex-linkml-tooling[map]"
            ) from exc

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
        return mapped

    def _transform_sql(
        self,
        *,
        spec_path: Path,
        moex: dict[str, Any],
        body: dict[str, Any],
        body_path: Path,
        source_class: str,
        obj: dict[str, Any],
    ) -> dict[str, Any]:
        try:
            from linkml_map.compiler.sql_compiler import SQLCompiler
            from linkml_map.transformer.object_transformer import ObjectTransformer
        except ImportError as exc:  # pragma: no cover
            raise ImportError(
                "linkml-map is required for SQL backend; "
                "install moex-linkml-tooling[map]"
            ) from exc

        if _collect_expr_strings(body):
            raise ValueError("SQL backend rejects specs with expr:")

        ot = ObjectTransformer(unrestricted_eval=False)
        source_schema = moex.get("source_schema")
        if source_schema:
            schema_path = Path(str(source_schema))
            if not schema_path.is_absolute():
                schema_path = (spec_path.parent / schema_path).resolve()
            ot.load_source_schema(str(schema_path))
        ot.load_transformer_specification(body_path)
        if ot.specification is None:
            raise ValueError("failed to load transformation specification")

        sc = SQLCompiler(source_schemaview=ot.source_schemaview)
        sc.new_table_when_transforming = False
        compiled = sc.compile(ot.specification)
        sql_text = (compiled.serialization or "").strip()
        if not sql_text:
            raise ValueError("SQLCompiler produced empty SQL")

        derivations = body.get("class_derivations") or {}
        if len(derivations) != 1:
            raise ValueError("SQL backend MVP supports exactly one class_derivation")
        target_class, cd = next(iter(derivations.items()))
        if not isinstance(cd, dict):
            raise ValueError("invalid class_derivation")
        populated_from = str(cd.get("populated_from") or target_class)
        slot_derivations = cd.get("slot_derivations") or {}
        target_cols = [
            str(slot)
            for slot, sd in slot_derivations.items()
            if not (isinstance(sd, dict) and sd.get("hide"))
        ]
        if not target_cols:
            raise ValueError("no target columns in slot_derivations")

        src_table = _sql_quote_ident(f"{populated_from}__src")
        tgt_table = _sql_quote_ident(str(target_class))
        source_cols = sorted(obj.keys())

        # Rewrite INSERT … FROM <populated_from> → FROM src; INSERT INTO target
        rewritten = sql_text
        rewritten = rewritten.replace(
            f"INSERT INTO {target_class}",
            f"INSERT INTO {tgt_table}",
        )
        rewritten = rewritten.replace(
            f" FROM {populated_from}",
            f" FROM {src_table}",
        )
        if "INSERT INTO" not in rewritten.upper():
            raise ValueError(f"unexpected SQLCompiler output: {sql_text!r}")

        conn = sqlite3.connect(":memory:")
        try:
            src_defs = ", ".join(f"{_sql_quote_ident(c)} TEXT" for c in source_cols)
            conn.execute(f"CREATE TABLE {src_table} ({src_defs})")
            placeholders = ", ".join("?" for _ in source_cols)
            col_list = ", ".join(_sql_quote_ident(c) for c in source_cols)
            conn.execute(
                f"INSERT INTO {src_table} ({col_list}) VALUES ({placeholders})",
                [None if obj[c] is None else str(obj[c]) for c in source_cols],
            )
            tgt_defs = ", ".join(f"{_sql_quote_ident(c)} TEXT" for c in target_cols)
            conn.execute(f"CREATE TABLE {tgt_table} ({tgt_defs})")
            conn.executescript(rewritten)
            cur = conn.execute(f"SELECT * FROM {tgt_table}")
            row = cur.fetchone()
            if row is None:
                return {}
            colnames = [d[0] for d in cur.description]
            return {colnames[i]: row[i] for i in range(len(colnames))}
        finally:
            conn.close()


__all__ = ["LinkmlMapProvider", "MapBackend"]
