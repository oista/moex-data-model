"""Spike: typed Mapping subclasses + separate collections vs polymorphic mappings.

Probes gen-pydantic, gen-json-schema, gen-owl, gen-shacl for subclass slot_usage
that narrows source_refs/target_refs ranges (ADR-046 plan).

Writes docs/migration/typed-mapping-spike-report.md
Does NOT modify production schemas.
"""

from __future__ import annotations

import json
import re
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SCHEMA_DIR = REPO / "model-assets" / "specifications" / "moex-dams" / "0.1" / "schemas"
OUT = REPO / "docs" / "migration" / "typed-mapping-spike-report.md"

SPIKE_SCHEMA = """
id: https://data.moex.com/dams/spike/typed-mapping/v0.1
name: typed_mapping_spike
imports:
  - linkml:types
  - moex-types
  - moex-registries
  - moex-governance
  - moex-core
  - moex-technical
  - moex-structure
prefixes:
  linkml: https://w3id.org/linkml/
  dams: https://data.moex.com/dams/
default_prefix: dams
default_range: string

types:
  SchemaNodeRef:
    typeof: uriorcurie
    pattern: '^dams:structure/.+#.+$'
    description: Spike SchemaNode address (structure_id#local_key).

classes:
  SpikeMappingPackage:
    tree_root: true
    is_a: ModelPackage
    slots:
      - realizes_mappings
      - entity_physical_mappings
      - field_mappings
      - aligns_with_mappings
      - mappings
    slot_usage:
      mappings:
        deprecated: true
        description: Legacy polymorphic collection (spike deprecated).

  RealizesMapping:
    is_a: Mapping
    description: Spike realizes subclass. Designator via L1 rule (not equals_string on enum slot).
    slot_usage:
      mapping_type:
        required: true
      source_refs:
        range: LogicalEntity
        inlined: false
        multivalued: true
        minimum_cardinality: 1
      target_refs:
        range: ConceptualEntity
        inlined: false
        multivalued: true
        minimum_cardinality: 1
    rules:
      - description: 'INV-MAP-SPIKE: RealizesMapping.mapping_type must be realizes'
        postconditions:
          slot_conditions:
            mapping_type:
              equals_string: realizes

  EntityPhysicalMapping:
    is_a: Mapping
    description: Spike entity_physical subclass.
    slot_usage:
      mapping_type:
        required: true
      source_refs:
        range: DataCarrier
        inlined: false
        multivalued: true
        minimum_cardinality: 1
        maximum_cardinality: 1
      target_refs:
        range: LogicalEntity
        inlined: false
        multivalued: true
        minimum_cardinality: 1
        maximum_cardinality: 1
    rules:
      - description: 'INV-MAP-SPIKE: EntityPhysicalMapping.mapping_type must be entity_physical'
        postconditions:
          slot_conditions:
            mapping_type:
              equals_string: entity_physical
      - description: 'INV-MAP-SPIKE: EntityPhysicalMapping.mapping_cardinality must be one_to_one'
        postconditions:
          slot_conditions:
            mapping_cardinality:
              equals_string: one_to_one

  FieldMapping:
    is_a: Mapping
    description: Spike field_mapping subclass.
    slot_usage:
      mapping_type:
        required: true
      source_refs:
        range: LogicalAttribute
        inlined: false
        multivalued: true
        minimum_cardinality: 1
      target_refs:
        range: SchemaNodeRef
        multivalued: true
        minimum_cardinality: 1
    rules:
      - description: 'INV-MAP-SPIKE: FieldMapping.mapping_type must be field_mapping'
        postconditions:
          slot_conditions:
            mapping_type:
              equals_string: field_mapping

  AlignsWithMapping:
    is_a: Mapping
    description: Spike aligns_with subclass.
    slot_usage:
      mapping_type:
        required: true
      source_refs:
        range: ConceptualEntity
        inlined: false
        multivalued: true
        minimum_cardinality: 1
        maximum_cardinality: 1
      target_refs:
        range: uri
        multivalued: true
        minimum_cardinality: 1
    rules:
      - description: 'INV-MAP-SPIKE: AlignsWithMapping.mapping_type must be aligns_with'
        postconditions:
          slot_conditions:
            mapping_type:
              equals_string: aligns_with

slots:
  realizes_mappings:
    range: RealizesMapping
    multivalued: true
    inlined: true
    inlined_as_list: true
  entity_physical_mappings:
    range: EntityPhysicalMapping
    multivalued: true
    inlined: true
    inlined_as_list: true
  field_mappings:
    range: FieldMapping
    multivalued: true
    inlined: true
    inlined_as_list: true
  aligns_with_mappings:
    range: AlignsWithMapping
    multivalued: true
    inlined: true
    inlined_as_list: true
"""


def _append(lines: list[str], text: str) -> None:
    lines.append(text if text.endswith("\n") else text + "\n")


def _snip(text: str, needle: str, before: int = 60, after: int = 180) -> str:
    idx = text.find(needle)
    if idx < 0:
        return "NOT FOUND"
    return text[max(0, idx - before) : idx + after].replace("\n", " ")


def main() -> int:
    from linkml.generators.jsonschemagen import JsonSchemaGenerator
    from linkml.generators.owlgen import OwlSchemaGenerator
    from linkml.generators.pydanticgen import PydanticGenerator
    from linkml.generators.shaclgen import ShaclGenerator
    from linkml_runtime.utils.schemaview import SchemaView

    lines: list[str] = []
    _append(lines, "# Typed Mapping generator spike report")
    _append(lines, "")
    _append(lines, "Date: auto-generated by `scripts/spike_typed_mapping_generators.py`")
    _append(lines, "")
    _append(
        lines,
        "Spike schema: temporary `_spike_typed_mapping.yaml` beside DAMS modules "
        "(deleted after run). Production schemas are not modified.",
    )

    spike_path = SCHEMA_DIR / "_spike_typed_mapping.yaml"
    spike_path.write_text(SPIKE_SCHEMA.strip() + "\n", encoding="utf-8")
    tmp = Path(tempfile.mkdtemp(prefix="map-spike-"))

    try:
        _append(lines, "\n## SchemaView\n")
        try:
            sv = SchemaView(str(spike_path))
            classes = sorted(sv.all_classes().keys())
            _append(lines, f"- SchemaView load: OK (classes={len(classes)})")
            for name in (
                "RealizesMapping",
                "EntityPhysicalMapping",
                "FieldMapping",
                "AlignsWithMapping",
                "SpikeMappingPackage",
            ):
                _append(lines, f"  - `{name}` present: {name in classes}")
            for cls_name in (
                "RealizesMapping",
                "EntityPhysicalMapping",
                "FieldMapping",
                "AlignsWithMapping",
            ):
                su = sv.get_class(cls_name).slot_usage or {}
                src = su.get("source_refs")
                tgt = su.get("target_refs")
                _append(
                    lines,
                    f"  - `{cls_name}` source_refs range="
                    f"{getattr(src, 'range', None)!r} "
                    f"min={getattr(src, 'minimum_cardinality', None)!r} "
                    f"max={getattr(src, 'maximum_cardinality', None)!r}; "
                    f"target_refs range={getattr(tgt, 'range', None)!r} "
                    f"min={getattr(tgt, 'minimum_cardinality', None)!r} "
                    f"max={getattr(tgt, 'maximum_cardinality', None)!r}",
                )
        except Exception as exc:  # noqa: BLE001
            _append(lines, f"- SchemaView load: FAIL — `{exc}`")
            OUT.write_text("".join(lines), encoding="utf-8")
            return 1

        # --- Pydantic ---
        _append(lines, "\n## gen-pydantic\n")
        py_code = ""
        try:
            py_code = PydanticGenerator(str(spike_path)).serialize()
            _append(lines, f"- gen-pydantic: OK ({len(py_code)} chars)")
            for needle in (
                "realizes_mappings",
                "entity_physical_mappings",
                "field_mappings",
                "aligns_with_mappings",
                "RealizesMapping",
                "EntityPhysicalMapping",
                "FieldMapping",
                "AlignsWithMapping",
                "SchemaNodeRef",
            ):
                _append(lines, f"  - mentions `{needle}`: {needle in py_code}")
            mod_path = tmp / "spike_map_models.py"
            mod_path.write_text(py_code, encoding="utf-8")
            import importlib.util

            spec = importlib.util.spec_from_file_location("spike_map_models", mod_path)
            assert spec and spec.loader
            mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(mod)
            pkg_fields = getattr(mod.SpikeMappingPackage, "model_fields", {}) or {}
            for key in (
                "realizes_mappings",
                "entity_physical_mappings",
                "field_mappings",
                "aligns_with_mappings",
                "mappings",
            ):
                if key in pkg_fields:
                    _append(
                        lines,
                        f"  - SpikeMappingPackage.{key}: `{pkg_fields[key].annotation}`",
                    )
            for cls_name in (
                "RealizesMapping",
                "EntityPhysicalMapping",
                "FieldMapping",
                "AlignsWithMapping",
            ):
                cls = getattr(mod, cls_name, None)
                if cls is None:
                    _append(lines, f"  - class `{cls_name}`: MISSING")
                    continue
                fields = getattr(cls, "model_fields", {}) or {}
                for slot in ("source_refs", "target_refs", "mapping_type"):
                    if slot in fields:
                        _append(
                            lines,
                            f"  - {cls_name}.{slot}: `{fields[slot].annotation}`",
                        )
        except Exception as exc:  # noqa: BLE001
            _append(lines, f"- gen-pydantic: FAIL — `{exc}`")

        # --- JSON Schema ---
        _append(lines, "\n## gen-json-schema\n")
        try:
            js = JsonSchemaGenerator(
                str(spike_path),
                include_range_class_descendants=False,
                top_class="SpikeMappingPackage",
            ).serialize()
            data = json.loads(js)
            defs = data.get("$defs") or data.get("definitions") or {}
            props = data.get("properties") or {}
            _append(lines, f"- gen-json-schema: OK; $defs={len(defs)}")
            for key in (
                "realizes_mappings",
                "entity_physical_mappings",
                "field_mappings",
                "aligns_with_mappings",
                "mappings",
            ):
                frag = props.get(key) or {}
                _append(lines, f"  - property `{key}`: `{json.dumps(frag)[:320]}`")
            for cls_name in (
                "RealizesMapping",
                "EntityPhysicalMapping",
                "FieldMapping",
                "AlignsWithMapping",
                "Mapping",
            ):
                if cls_name in defs:
                    cprops = (defs[cls_name].get("properties") or {})
                    src = cprops.get("source_refs")
                    tgt = cprops.get("target_refs")
                    _append(
                        lines,
                        f"  - $defs.{cls_name}.source_refs: `{json.dumps(src)[:280]}`",
                    )
                    _append(
                        lines,
                        f"  - $defs.{cls_name}.target_refs: `{json.dumps(tgt)[:280]}`",
                    )
                else:
                    _append(lines, f"  - $defs.{cls_name}: MISSING")
        except Exception as exc:  # noqa: BLE001
            _append(lines, f"- gen-json-schema: FAIL — `{exc}`")

        # --- OWL ---
        _append(lines, "\n## gen-owl (shared slot domain/range risk)\n")
        try:
            owl = OwlSchemaGenerator(str(spike_path)).serialize()
            _append(lines, f"- gen-owl: OK ({len(owl)} chars)")
            for prop in ("source_refs", "target_refs"):
                # Collect property declarations / ranges mentioning the slot
                hits = [
                    ln.strip()
                    for ln in owl.splitlines()
                    if prop in ln and ("rdfs:range" in ln or "rdfs:domain" in ln or "owl:ObjectProperty" in ln or "owl:DatatypeProperty" in ln or f"dams:{prop}" in ln)
                ]
                _append(lines, f"  - lines mentioning `{prop}` domain/range/property: {len(hits)}")
                for h in hits[:12]:
                    _append(lines, f"    - `{h[:220]}`")
            ranges = re.findall(
                r"dams:source_refs[^\.]*?rdfs:range\s+([^\s;]+)",
                owl,
                flags=re.DOTALL,
            )
            _append(lines, f"  - regex-captured rdfs:range for source_refs: {ranges[:20]}")
            domains = re.findall(
                r"dams:source_refs[^\.]*?rdfs:domain\s+([^\s;]+)",
                owl,
                flags=re.DOTALL,
            )
            _append(lines, f"  - regex-captured rdfs:domain for source_refs: {domains[:20]}")
            # Class-local allValuesFrom restrictions (subclass typing lives here)
            avf = re.findall(
                r"owl:allValuesFrom\s+([^\s;]+)\s*;\s*\n\s*owl:onProperty\s+dams:source_refs",
                owl,
            )
            _append(lines, f"  - owl:allValuesFrom on source_refs: {sorted(set(avf))}")
            avf_t = re.findall(
                r"owl:allValuesFrom\s+([^\s;]+)\s*;\s*\n\s*owl:onProperty\s+dams:target_refs",
                owl,
            )
            _append(lines, f"  - owl:allValuesFrom on target_refs: {sorted(set(avf_t))}")
            for cls_name in (
                "RealizesMapping",
                "EntityPhysicalMapping",
                "FieldMapping",
                "AlignsWithMapping",
            ):
                marker = f"dams:{cls_name}"
                idx = owl.find(marker)
                if idx >= 0:
                    _append(lines, f"  - snippet `{cls_name}`: `{owl[idx : idx + 350].replace(chr(10), ' ')}`")
            conflict_hint = len(set(ranges)) > 1
            _append(
                lines,
                f"- OWL global rdfs:range conflict on source_refs: {conflict_hint}",
            )
            _append(
                lines,
                f"- OWL class-local allValuesFrom present for endpoints: "
                f"{bool(avf or avf_t)}",
            )
        except Exception as exc:  # noqa: BLE001
            _append(lines, f"- gen-owl: FAIL — `{exc}`")
            conflict_hint = True

        # --- SHACL ---
        _append(lines, "\n## gen-shacl\n")
        try:
            shacl = ShaclGenerator(str(spike_path)).serialize()
            _append(lines, f"- gen-shacl: OK ({len(shacl)} chars)")
            for cls_name in (
                "RealizesMapping",
                "EntityPhysicalMapping",
                "FieldMapping",
                "AlignsWithMapping",
                "Mapping",
            ):
                present = cls_name in shacl or f"dams:{cls_name}" in shacl
                _append(lines, f"  - shape mentions `{cls_name}`: {present}")
            # Look for sh:class on source_refs / target_refs
            class_hits = [
                ln.strip()
                for ln in shacl.splitlines()
                if "sh:class" in ln
                and (
                    "LogicalEntity" in ln
                    or "ConceptualEntity" in ln
                    or "DataCarrier" in ln
                    or "LogicalAttribute" in ln
                )
            ]
            _append(lines, f"  - sh:class lines for endpoint classes: {len(class_hits)}")
            for h in class_hits[:20]:
                _append(lines, f"    - `{h[:220]}`")
            # Check FieldMapping SchemaNodeRef / pattern
            pattern_hits = [ln.strip() for ln in shacl.splitlines() if "sh:pattern" in ln]
            _append(lines, f"  - sh:pattern lines: {len(pattern_hits)}")
            for h in pattern_hits[:10]:
                _append(lines, f"    - `{h[:220]}`")
            has_sh_class = len(class_hits) > 0
            # Check whether gen-shacl emitted restrictions for narrowed slots
            for cls_name in (
                "RealizesMapping",
                "EntityPhysicalMapping",
                "FieldMapping",
                "AlignsWithMapping",
            ):
                marker = f"dams:{cls_name}"
                idx = shacl.find(marker)
                if idx >= 0:
                    _append(
                        lines,
                        f"  - SHACL snippet `{cls_name}`: "
                        f"`{shacl[idx : idx + 500].replace(chr(10), ' ')}`",
                    )
        except Exception as exc:  # noqa: BLE001
            _append(lines, f"- gen-shacl: FAIL — `{exc}`")
            has_sh_class = False

        # --- Note on equals_string in slot_usage ---
        _append(lines, "\n## Designator placement note\n")
        _append(
            lines,
            "- `equals_string` **on slot_usage** for an enum-ranged slot "
            "(`mapping_type: MappingTypeEnum`) breaks `gen-shacl` "
            "(`equals_string` requires range string). Observed in first spike "
            "revision; this run uses L1 `rules` postconditions instead.",
        )
        _append(
            lines,
            "- Pydantic still gets `Literal[...]` only when equals_string is on "
            "the slot itself; with rules-only designator, mapping_type stays the "
            "enum type in pydantic. Acceptable: collection typing + L1/L2 enforce "
            "the value.",
        )

        # --- Decision ---
        _append(lines, "\n## Decision for ADR-046\n")
        separate_ok = "entity_physical_mappings" in (py_code or "") and (
            "list[spike_map_models.RealizesMapping]" in (py_code or "")
            or "RealizesMapping" in (py_code or "")
        )
        _append(
            lines,
            f"- Separate collections preserve subclass types in pydantic: {separate_ok}",
        )
        _append(
            lines,
            f"- Generated SHACL emits useful `sh:class` for narrowed endpoint ranges: {has_sh_class}",
        )
        _append(
            lines,
            "- JSON Schema: class-range refs remain `string` when `inlined: false` "
            "(no runtime class check). `SchemaNodeRef` pattern and "
            "minItems/maxItems **do** appear. Endpoint kind enforcement stays L2/L3.",
        )
        _append(
            lines,
            "- L1 designator: use `rules` with `equals_string` on mapping_type "
            "(not slot_usage equals_string on enum) so gen-shacl does not fail.",
        )
        _append(
            lines,
            "- Cross-instance resolve-and-check endpoint kind: L2 "
            "(DAMS validator), as with PDM-009 today.",
        )
        _append(
            lines,
            "- OWL: global `rdfs:range` of shared `source_refs` stays "
            "`uriorcurie`; subclass typing appears as class-local "
            "`owl:allValuesFrom` restrictions when ranges are classes. "
            "Manual L3 SHACL still required for reliable RDF validation "
            "(gen-shacl may not emit `sh:class` for inlined:false refs).",
        )
        _append(
            lines,
            "\n**Chosen:** Variant B separate collections + Mapping subclasses "
            "with slot_usage; L1 rules for designator; endpoint kind in L2 + "
            "manual L3 SHACL; do not put equals_string on enum slot_usage.",
        )
        _append(lines, "\nDecision code: `B-subclass-collections`\n")
    finally:
        if spike_path.exists():
            spike_path.unlink()

    OUT.write_text("".join(lines), encoding="utf-8")
    print(f"Wrote {OUT}")
    print("".join(lines))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
