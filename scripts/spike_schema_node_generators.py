"""Spike: nested inlined SchemaNode tree vs flat nodes + root_local_key.

Compares both representations across LinkML generators used in this repo:
JSON Schema, Pydantic, OWL, SHACL, DBML, plus a dams_to_graph-style walk.

Criteria (plan ADR-038):
  (a) nesting depth 4+
  (b) local_key as identifier/key for dict form uniqueness
  (c) round-trip without field loss

Writes docs/migration/data-structure-spike-report.md
"""

from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[1]
SCHEMA_DIR = REPO / "model-assets" / "specifications" / "moex-dams" / "0.1" / "schemas"

SPIKE_NESTED = """
id: https://data.moex.com/dams/spike/schema-node-nested/v0.1
name: schema_node_nested_spike
imports:
  - linkml:types
  - moex-types
  - moex-registries
  - moex-governance
  - moex-core
prefixes:
  linkml: https://w3id.org/linkml/
  dams: https://data.moex.com/dams/
default_prefix: dams
default_range: string

classes:
  SpikeNestedPackage:
    tree_root: true
    is_a: ModelPackage
    slots:
      - spike_structures_nested

  SpikeDataStructureNested:
    is_a: ModelElement
    slots:
      - schema_format
      - structure_version
      - root_node

  SpikeSchemaNodeNested:
    slots:
      - local_key
      - native_name
      - node_kind
      - children_nested
      - item_node_nested
      - native_type
      - required
      - description
    slot_usage:
      description:
        required: false

slots:
  spike_structures_nested:
    range: SpikeDataStructureNested
    multivalued: true
    inlined: true
    inlined_as_list: true
  schema_format:
    range: string
    required: true
  structure_version:
    range: SemVer
    required: true
  root_node:
    range: SpikeSchemaNodeNested
    inlined: true
    required: true
  local_key:
    range: string
    required: true
    identifier: true
  native_name:
    range: string
  node_kind:
    range: string
    required: true
  children_nested:
    range: SpikeSchemaNodeNested
    multivalued: true
    inlined: true
    inlined_as_list: true
  item_node_nested:
    range: SpikeSchemaNodeNested
    inlined: true
  native_type:
    range: string
  required:
    range: boolean
"""

SPIKE_FLAT = """
id: https://data.moex.com/dams/spike/schema-node-flat/v0.1
name: schema_node_flat_spike
imports:
  - linkml:types
  - moex-types
  - moex-registries
  - moex-governance
  - moex-core
prefixes:
  linkml: https://w3id.org/linkml/
  dams: https://data.moex.com/dams/
default_prefix: dams
default_range: string

classes:
  SpikeFlatPackage:
    tree_root: true
    is_a: ModelPackage
    slots:
      - spike_structures_flat

  SpikeDataStructureFlat:
    is_a: ModelElement
    slots:
      - schema_format
      - structure_version
      - root_local_key
      - nodes

  SpikeSchemaNodeFlat:
    slots:
      - local_key
      - native_name
      - node_kind
      - children_keys
      - item_node_key
      - native_type
      - required
      - description
    slot_usage:
      description:
        required: false

slots:
  spike_structures_flat:
    range: SpikeDataStructureFlat
    multivalued: true
    inlined: true
    inlined_as_list: true
  schema_format:
    range: string
    required: true
  structure_version:
    range: SemVer
    required: true
  root_local_key:
    range: string
    required: true
  nodes:
    range: SpikeSchemaNodeFlat
    multivalued: true
    inlined: true
    inlined_as_list: true
  local_key:
    range: string
    required: true
    identifier: true
  native_name:
    range: string
  node_kind:
    range: string
    required: true
  children_keys:
    range: string
    multivalued: true
  item_node_key:
    range: string
  native_type:
    range: string
  required:
    range: boolean
"""

# Depth-4 nested JSON-like tree: root → a → b → c → d (scalar)
def _node(
    local_key: str,
    *,
    native_name: str | None = None,
    node_kind: str = "object",
    children: list[dict[str, Any]] | None = None,
    children_keys: list[str] | None = None,
    native_type: str | None = None,
    required: bool | None = None,
    description: str | None = None,
    nested: bool = False,
) -> dict[str, Any]:
    n: dict[str, Any] = {
        "local_key": local_key,
        "native_name": native_name or local_key.rsplit(".", 1)[-1],
        "node_kind": node_kind,
        "description": description or f"node {local_key}",
    }
    if nested and children is not None:
        n["children_nested"] = children
    if not nested and children_keys is not None:
        n["children_keys"] = children_keys
    if native_type is not None:
        n["native_type"] = native_type
    if required is not None:
        n["required"] = required
    return n


NESTED_INSTANCE: dict[str, Any] = {
    "element_id": "dams:structure/spike/nested1",
    "name": "nested_depth4",
    "description": "spike nested structure",
    "lifecycle_status": "draft",
    "schema_format": "json_schema",
    "structure_version": "1.0.0",
    "root_node": _node(
        "root",
        nested=True,
        children=[
            _node(
                "a",
                nested=True,
                children=[
                    _node(
                        "a.b",
                        nested=True,
                        children=[
                            _node(
                                "a.b.c",
                                nested=True,
                                children=[
                                    _node(
                                        "a.b.c.d",
                                        nested=True,
                                        node_kind="scalar",
                                        native_type="string",
                                        required=True,
                                        description="leaf at depth 4",
                                    )
                                ],
                            )
                        ],
                    )
                ],
            )
        ],
    ),
}

FLAT_INSTANCE: dict[str, Any] = {
    "element_id": "dams:structure/spike/flat1",
    "name": "flat_depth4",
    "description": "spike flat structure",
    "lifecycle_status": "draft",
    "schema_format": "json_schema",
    "structure_version": "1.0.0",
    "root_local_key": "root",
    "nodes": [
        _node("root", children_keys=["a"]),
        _node("a", children_keys=["a.b"]),
        _node("a.b", children_keys=["a.b.c"]),
        _node("a.b.c", children_keys=["a.b.c.d"]),
        _node(
            "a.b.c.d",
            node_kind="scalar",
            native_type="string",
            required=True,
            description="leaf at depth 4",
        ),
    ],
}


def _append(lines: list[str], text: str) -> None:
    lines.append(text if text.endswith("\n") else text + "\n")


def _probe_generators(label: str, schema_path: Path, top_class: str, lines: list[str]) -> dict[str, Any]:
    from linkml.generators.dbmlgen import DBMLGenerator
    from linkml.generators.jsonschemagen import JsonSchemaGenerator
    from linkml.generators.owlgen import OwlSchemaGenerator
    from linkml.generators.pydanticgen import PydanticGenerator
    from linkml.generators.shaclgen import ShaclGenerator
    from linkml_runtime.utils.schemaview import SchemaView

    result: dict[str, Any] = {"label": label, "ok": True}
    _append(lines, f"\n## {label}\n")

    try:
        sv = SchemaView(str(schema_path))
        _append(lines, f"- SchemaView load: OK (classes={len(sv.all_classes())})")
        result["classes"] = len(sv.all_classes())
    except Exception as exc:  # noqa: BLE001
        _append(lines, f"- SchemaView load: FAIL — `{exc}`")
        result["ok"] = False
        return result

    # JSON Schema
    try:
        js = JsonSchemaGenerator(
            str(schema_path),
            include_range_class_descendants=True,
            top_class=top_class,
        ).serialize()
        data = json.loads(js)
        defs = data.get("$defs") or data.get("definitions") or {}
        text = json.dumps(data)
        has_ref = '"$ref"' in text
        has_defs = bool(defs)
        _append(
            lines,
            f"- gen-json-schema: OK; $defs={len(defs)}; has_$ref={has_ref}; "
            f"has_defs={has_defs}",
        )
        # Look for SchemaNode-like class in defs
        node_keys = [k for k in defs if "SchemaNode" in k or "Node" in k]
        _append(lines, f"  - node-related $defs: {node_keys[:8]}")
        if node_keys:
            frag = defs[node_keys[0]]
            _append(lines, f"  - first node def keys: {list(frag.keys())[:12]}")
            props = frag.get("properties") or {}
            for slot in ("children_nested", "children_keys", "item_node_nested", "item_node_key", "local_key"):
                if slot in props:
                    _append(lines, f"  - property `{slot}`: `{json.dumps(props[slot])[:220]}`")
        result["json_schema_ok"] = True
        result["json_schema_has_ref"] = has_ref
    except Exception as exc:  # noqa: BLE001
        _append(lines, f"- gen-json-schema: FAIL — `{exc}`")
        result["json_schema_ok"] = False
        result["ok"] = False

    # Pydantic
    try:
        py_code = PydanticGenerator(str(schema_path)).serialize()
        _append(lines, f"- gen-pydantic: OK ({len(py_code)} chars)")
        for needle in ("children_nested", "children_keys", "local_key", "root_node", "root_local_key", "nodes"):
            if needle in py_code:
                idx = py_code.find(needle)
                snip = py_code[max(0, idx - 40) : idx + 120].replace("\n", " ")
                _append(lines, f"  - pydantic `{needle}`: `{snip}`")
        result["pydantic_ok"] = True
        result["pydantic_code"] = py_code
    except Exception as exc:  # noqa: BLE001
        _append(lines, f"- gen-pydantic: FAIL — `{exc}`")
        result["pydantic_ok"] = False
        result["ok"] = False

    # OWL
    try:
        owl = OwlSchemaGenerator(str(schema_path)).serialize()
        _append(lines, f"- gen-owl: OK ({len(owl)} chars); mentions SchemaNode={('SchemaNode' in owl)}")
        result["owl_ok"] = True
    except Exception as exc:  # noqa: BLE001
        _append(lines, f"- gen-owl: FAIL — `{exc}`")
        result["owl_ok"] = False

    # SHACL
    try:
        shacl = ShaclGenerator(str(schema_path)).serialize()
        _append(lines, f"- gen-shacl: OK ({len(shacl)} chars)")
        result["shacl_ok"] = True
    except Exception as exc:  # noqa: BLE001
        _append(lines, f"- gen-shacl: FAIL — `{exc}`")
        result["shacl_ok"] = False

    # DBML (may skip recursive / non-relational gracefully)
    try:
        dbml = DBMLGenerator(str(schema_path)).serialize()
        _append(lines, f"- gen-dbml: OK ({len(dbml)} chars)")
        result["dbml_ok"] = True
    except Exception as exc:  # noqa: BLE001
        _append(lines, f"- gen-dbml: FAIL (acceptable for structure spike) — `{exc}`")
        result["dbml_ok"] = False

    return result


def _round_trip(
    label: str,
    schema_path: Path,
    class_name: str,
    instance: dict[str, Any],
    py_code: str,
    lines: list[str],
    tmp: Path,
) -> bool:
    _append(lines, f"\n### Round-trip ({label})\n")
    if not py_code:
        _append(lines, "- SKIP: no pydantic code")
        return False
    mod_path = tmp / f"{label.replace(' ', '_')}.py"
    mod_path.write_text(py_code, encoding="utf-8")
    try:
        spec = importlib.util.spec_from_file_location(f"spike_{label}", mod_path)
        assert spec and spec.loader
        mod = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = mod
        spec.loader.exec_module(mod)
        cls = getattr(mod, class_name, None)
        if cls is None:
            _append(lines, f"- FAIL: class `{class_name}` missing in pydantic module")
            return False
        obj = cls(**instance)
        dumped = obj.model_dump(exclude_none=True) if hasattr(obj, "model_dump") else obj.dict()
        # Criterion (a): depth / leaf present
        leaf_ok = False
        if "root_node" in dumped:
            # walk nested
            node = dumped.get("root_node") or {}
            depth = 0
            while node:
                depth += 1
                kids = node.get("children_nested") or []
                if not kids:
                    leaf_ok = (
                        node.get("local_key") == "a.b.c.d"
                        and node.get("native_type") == "string"
                        and node.get("description") == "leaf at depth 4"
                    )
                    break
                node = kids[0] if isinstance(kids[0], dict) else {}
            _append(lines, f"- nested walk depth={depth}; leaf fields preserved={leaf_ok}")
            depth_ok = depth >= 4
        else:
            nodes = dumped.get("nodes") or []
            keys = {n.get("local_key") for n in nodes if isinstance(n, dict)}
            leaf = next((n for n in nodes if n.get("local_key") == "a.b.c.d"), None)
            leaf_ok = bool(
                leaf
                and leaf.get("native_type") == "string"
                and leaf.get("description") == "leaf at depth 4"
            )
            # reconstruct depth via children_keys
            by_key = {n["local_key"]: n for n in nodes if n.get("local_key")}
            depth = 0
            cur = dumped.get("root_local_key")
            seen: set[str] = set()
            while cur and cur not in seen:
                seen.add(cur)
                depth += 1
                n = by_key.get(cur) or {}
                kids = n.get("children_keys") or []
                cur = kids[0] if kids else None
            _append(
                lines,
                f"- flat node count={len(nodes)}; keys={sorted(keys)}; "
                f"reconstructed depth={depth}; leaf fields preserved={leaf_ok}",
            )
            depth_ok = depth >= 4 and "a.b.c.d" in keys

        # Criterion (b): local_key uniqueness in dict form
        if "nodes" in dumped:
            keys_list = [n.get("local_key") for n in dumped["nodes"]]
            unique = len(keys_list) == len(set(keys_list))
            _append(lines, f"- local_key unique in nodes list: {unique}")
        else:
            # collect all local_keys from nested tree
            found: list[str] = []

            def walk(n: dict[str, Any]) -> None:
                if not isinstance(n, dict):
                    return
                if n.get("local_key"):
                    found.append(str(n["local_key"]))
                for c in n.get("children_nested") or []:
                    walk(c)
                if n.get("item_node_nested"):
                    walk(n["item_node_nested"])

            walk(dumped.get("root_node") or {})
            unique = len(found) == len(set(found))
            _append(lines, f"- local_key unique in nested tree: {unique} (count={len(found)})")

        ok = depth_ok and leaf_ok and unique
        _append(lines, f"- round-trip criteria (a)(b)(c): {'PASS' if ok else 'FAIL'}")
        return ok
    except Exception as exc:  # noqa: BLE001
        _append(lines, f"- round-trip FAIL — `{exc}`")
        return False


def _graph_walk_flat(instance: dict[str, Any], lines: list[str]) -> None:
    """Simulate dams_to_graph edge construction for flat representation."""
    _append(lines, "\n## dams_to_graph-style walk (flat)\n")
    nodes = {n["local_key"]: n for n in instance["nodes"]}
    edges: list[tuple[str, str, str]] = []
    for key, n in nodes.items():
        for child in n.get("children_keys") or []:
            edges.append((key, "child", child))
        if n.get("item_node_key"):
            edges.append((key, "item", n["item_node_key"]))
    _append(lines, f"- nodes={len(nodes)}; edges={len(edges)}")
    for e in edges:
        _append(lines, f"  - {e[0]} -[{e[1]}]-> {e[2]}")
    # cycle check
    visited: set[str] = set()
    stack: set[str] = set()

    def dfs(k: str) -> bool:
        if k in stack:
            return True
        if k in visited:
            return False
        visited.add(k)
        stack.add(k)
        n = nodes.get(k) or {}
        for c in n.get("children_keys") or []:
            if dfs(c):
                return True
        if n.get("item_node_key") and dfs(n["item_node_key"]):
            return True
        stack.remove(k)
        return False

    cyclic = dfs(instance["root_local_key"])
    _append(lines, f"- cycle detected: {cyclic}")


def main() -> int:
    lines: list[str] = []
    _append(lines, "# DataStructure / SchemaNode generator spike report")
    _append(lines, "Date: auto-generated by `scripts/spike_schema_node_generators.py`")
    _append(
        lines,
        "Compares **nested inlined** SchemaNode tree vs **flat** `nodes` + `root_local_key`.",
    )

    nested_path = SCHEMA_DIR / "_spike_schema_node_nested.yaml"
    flat_path = SCHEMA_DIR / "_spike_schema_node_flat.yaml"
    nested_path.write_text(SPIKE_NESTED.strip() + "\n", encoding="utf-8")
    flat_path.write_text(SPIKE_FLAT.strip() + "\n", encoding="utf-8")
    tmp = Path(tempfile.mkdtemp(prefix="sn-spike-"))

    try:
        nested = _probe_generators(
            "Variant Nested: inlined tree (`root_node` / `children_nested`)",
            nested_path,
            "SpikeNestedPackage",
            lines,
        )
        flat = _probe_generators(
            "Variant Flat: `nodes` + `root_local_key` + string edges",
            flat_path,
            "SpikeFlatPackage",
            lines,
        )

        nested_rt = _round_trip(
            "nested",
            nested_path,
            "SpikeDataStructureNested",
            NESTED_INSTANCE,
            nested.get("pydantic_code") or "",
            lines,
            tmp,
        )
        flat_rt = _round_trip(
            "flat",
            flat_path,
            "SpikeDataStructureFlat",
            FLAT_INSTANCE,
            flat.get("pydantic_code") or "",
            lines,
            tmp,
        )

        _graph_walk_flat(FLAT_INSTANCE, lines)

        _append(lines, "\n## Criteria summary\n")
        _append(lines, f"- Nested generators ok={nested.get('ok')}; round-trip={nested_rt}")
        _append(lines, f"- Flat generators ok={flat.get('ok')}; round-trip={flat_rt}")
        _append(lines, f"- Nested json_schema $ref={nested.get('json_schema_has_ref')}")
        _append(lines, f"- Flat json_schema $ref={flat.get('json_schema_has_ref')}")

        _append(lines, "\n## Decision\n")
        # Plan preference: flat unless flat is blocked
        if flat.get("ok") and flat_rt:
            _append(
                lines,
                "**Chosen: Flat (`nodes` + `root_local_key`).** "
                "Meets criteria (a) depth 4+, (b) unique `local_key`, (c) round-trip field preservation. "
                "Edges as string `local_key` refs align with CURIE `structure_id#local_key`, "
                "SQL storage, semantic diff, and Mapping. "
                "Nested inlined tree may also generate, but is inferior for diff/SQL/CURIE "
                "and forces unavoidable inlining (no global identifier on SchemaNode).",
            )
            decision = "FLAT"
        elif nested.get("ok") and nested_rt:
            _append(
                lines,
                "**Fallback: Nested inlined tree** — flat variant failed generators or round-trip; "
                "document blockers above.",
            )
            decision = "NESTED"
        else:
            _append(lines, "**BLOCKED:** neither variant passed. Investigate generator failures.")
            decision = "BLOCKED"
        _append(lines, f"\nDecision code: `{decision}`\n")
    finally:
        for p in (nested_path, flat_path):
            if p.exists():
                p.unlink()

    out = REPO / "docs" / "migration" / "data-structure-spike-report.md"
    out.write_text("".join(lines), encoding="utf-8")
    print(f"Wrote {out}")
    print("".join(lines))
    return 0 if "Decision code: `FLAT`" in "".join(lines) or "Decision code: `NESTED`" in "".join(lines) else 1


if __name__ == "__main__":
    raise SystemExit(main())
