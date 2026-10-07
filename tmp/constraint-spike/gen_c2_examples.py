"""PR-C2: prefix INV-xxx on rule descriptions; emit valid/invalid YAML fixtures.

Uses ruamel round-trip for schema edits. Examples go under
model-assets/specifications/moex-dams/0.1/examples/invariants/.
"""

from __future__ import annotations

import copy
import json
import sys
from pathlib import Path

from ruamel.yaml import YAML
from ruamel.yaml.comments import CommentedMap

REPO = Path(__file__).resolve().parents[2]
SCHEMA_DIR = REPO / "model-assets/specifications/moex-dams/0.1/schemas"
OUT_DIR = REPO / "model-assets/specifications/moex-dams/0.1/examples/invariants"
JS = json.loads(
    (REPO / "generated/artifacts/moex-dams/0.1/moex-dams.schema.json").read_text(
        encoding="utf-8"
    )
)
DEFS = JS["$defs"]

# Order matches constraint-matrix baseline / inventory --list-rules
BASELINE = [
    ("moex-core.yaml", "ConceptualProperty", 0, "INV-001"),
    ("moex-datatypes.yaml", "DataType", 0, "INV-002"),
    ("moex-datatypes.yaml", "DataType", 1, "INV-003"),
    ("moex-datatypes.yaml", "DataType", 2, "INV-004"),
    ("moex-datatypes.yaml", "DataType", 3, "INV-005"),
    ("moex-datatypes.yaml", "ValueDomain", 0, "INV-006"),
    ("moex-datatypes.yaml", "ValueDomain", 1, "INV-007"),
    ("moex-datatypes.yaml", "ValueDomain", 2, "INV-008"),
    ("moex-semantic.yaml", "ConceptualDomain", 0, "INV-009"),
    ("moex-structure.yaml", "DataStructure", 0, "INV-010"),
    ("moex-structure.yaml", "DataStructure", 1, "INV-011"),
    ("moex-structure.yaml", "SchemaNode", 0, "INV-012"),
    ("moex-structure.yaml", "SchemaNode", 1, "INV-013"),
    ("moex-structure.yaml", "SchemaNode", 2, "INV-014"),
    ("moex-technical.yaml", "DataCarrier", 0, "INV-015"),
    ("moex-technical.yaml", "AccessPoint", 0, "INV-016"),
    ("moex-technical.yaml", "AccessPoint", 1, "INV-017"),
]

GLOBAL_PICK = [0]


def _yaml() -> YAML:
    y = YAML(typ="rt")
    y.preserve_quotes = True
    y.indent(mapping=2, sequence=4, offset=2)
    y.width = 100
    return y


def synth(prop: dict, enum_pick: int = 0, depth: int = 0):
    if "$ref" in prop:
        name = prop["$ref"].split("/")[-1]
        target = DEFS[name]
        if "enum" in target:
            return target["enum"][(enum_pick + GLOBAL_PICK[0]) % len(target["enum"])]
        if target.get("type") == "object" and depth < 2:
            return base_instance(name, depth + 1)
        return f"{name}-x"
    if "anyOf" in prop:
        return synth(prop["anyOf"][0], enum_pick)
    t = prop.get("type")
    if isinstance(t, list):
        t = next((x for x in t if x != "null"), "string")
    if t == "array":
        return [synth(prop.get("items", {"type": "string"}), enum_pick)]
    if t == "boolean":
        return True
    if t == "integer":
        return 1
    if t == "number":
        return 1.0
    fmt = prop.get("format")
    if fmt in ("uri", "uriref", "uri-reference"):
        return "https://example.org/x"
    if "pattern" in prop:
        return "1.0.0" if "[1-9]" in prop["pattern"] else "x"
    return "x"


def base_instance(cls: str, depth: int = 0) -> dict:
    d = DEFS[cls]
    inst = {}
    for req in d.get("required", []):
        inst[req] = synth(d["properties"][req], 0, depth)
    return inst


def errs(cls: str, inst: dict) -> list[str]:
    from jsonschema import Draft201909Validator

    v = Draft201909Validator({"$defs": DEFS, "$ref": f"#/$defs/{cls}"})
    return [e.message[:160] for e in v.iter_errors(inst)]


def valid_base(cls: str) -> dict:
    for pick in range(0, 8):
        GLOBAL_PICK[0] = pick
        inst = base_instance(cls)
        if not errs(cls, inst):
            return inst
    GLOBAL_PICK[0] = 0
    return base_instance(cls)


def present_value(cls: str, slot: str):
    p = DEFS[cls]["properties"][slot]
    for i in range(0, 8):
        return synth(p, i)


def cond_values(cls: str, slot: str, cond: dict) -> list:
    if "equals_string" in cond:
        return [cond["equals_string"]]
    if "any_of" in cond:
        return [c["equals_string"] for c in cond["any_of"] if "equals_string" in c]
    if cond.get("value_presence") == "PRESENT" or cond.get("required") is True:
        return [present_value(cls, slot)]
    return []


def apply_pre(cls: str, inst: dict, pre: dict) -> None:
    for slot, cond in (pre.get("slot_conditions") or {}).items():
        if cond.get("value_presence") == "ABSENT":
            inst.pop(slot, None)
            continue
        vals = cond_values(cls, slot, cond)
        if vals:
            # boolean: write real bool when slot is boolean
            prop = DEFS[cls]["properties"].get(slot, {})
            t = prop.get("type")
            if t == "boolean" or (isinstance(t, list) and "boolean" in t):
                if vals[0] in ("true", "True", True):
                    inst[slot] = True
                    continue
                if vals[0] in ("false", "False", False):
                    inst[slot] = False
                    continue
            inst[slot] = vals[0]


def build_satisfy(cls, base, rule):
    inst = copy.deepcopy(base)
    apply_pre(cls, inst, rule.get("preconditions") or {})
    for slot, cond in (rule.get("postconditions") or {}).get("slot_conditions", {}).items():
        if cond.get("value_presence") == "ABSENT":
            inst.pop(slot, None)
        else:
            vals = cond_values(cls, slot, cond)
            if vals:
                prop = DEFS[cls]["properties"].get(slot, {})
                t = prop.get("type")
                if t == "boolean" or (isinstance(t, list) and "boolean" in t):
                    if vals[0] in ("true", "True", True):
                        inst[slot] = True
                        continue
                inst[slot] = vals[0]
    return inst


def build_violate(cls, base, rule):
    posts = (rule.get("postconditions") or {}).get("slot_conditions") or {}
    absent = [s for s, c in posts.items() if c.get("value_presence") == "ABSENT"]
    # Prefer multi-ABSENT full violation when weakened single-slot would pass
    if len(absent) > 1:
        inst = copy.deepcopy(base)
        apply_pre(cls, inst, rule.get("preconditions") or {})
        for s2, c2 in posts.items():
            if c2.get("value_presence") == "ABSENT":
                inst[s2] = present_value(cls, s2)
            else:
                v = cond_values(cls, s2, c2)
                if v:
                    inst[s2] = v[0]
        return inst, "all-absent-present"
    # Single postcondition violation
    for slot, cond in posts.items():
        inst = copy.deepcopy(base)
        apply_pre(cls, inst, rule.get("preconditions") or {})
        for s2, c2 in posts.items():
            if s2 == slot:
                continue
            if c2.get("value_presence") == "ABSENT":
                inst.pop(s2, None)
            else:
                v = cond_values(cls, s2, c2)
                if v:
                    inst[s2] = v[0]
        if cond.get("value_presence") == "ABSENT":
            inst[slot] = present_value(cls, slot)
        elif cond.get("value_presence") == "PRESENT" or cond.get("required") is True:
            inst.pop(slot, None)
        elif "equals_string" in cond or "any_of" in cond:
            ok = set(cond_values(cls, slot, cond))
            for i in range(12):
                v = synth(DEFS[cls]["properties"][slot], i)
                if v not in ok:
                    inst[slot] = v
                    break
        return inst, slot
    return copy.deepcopy(base), "none"


def dump_inst(path: Path, inv: str, cls: str, kind: str, inst: dict) -> None:
    doc = CommentedMap()
    doc.yaml_set_start_comment(
        f"{inv} {kind} fixture for LinkML class {cls} (ADR-045 / PR-C2). "
        f"Do not use as production data."
    )
    for k, v in inst.items():
        doc[k] = v
    y = YAML()
    y.default_flow_style = False
    y.indent(mapping=2, sequence=4, offset=2)
    with path.open("w", encoding="utf-8", newline="\n") as fh:
        y.dump(doc, fh)


def prefix_descriptions() -> None:
    by_file: dict[str, list[tuple[str, int, str]]] = {}
    for fname, cname, idx, inv in BASELINE:
        by_file.setdefault(fname, []).append((cname, idx, inv))
    y = _yaml()
    for fname, items in by_file.items():
        path = SCHEMA_DIR / fname
        data = y.load(path.read_text(encoding="utf-8"))
        for cname, idx, inv in items:
            rule = data["classes"][cname]["rules"][idx]
            desc = str(rule.get("description") or "")
            prefix = f"{inv}: "
            if not desc.startswith(prefix) and not desc.startswith(f"{inv} "):
                rule["description"] = prefix + desc
        with path.open("w", encoding="utf-8", newline="\n") as fh:
            y.dump(data, fh)
        print(f"prefixed {fname}: {len(items)} rules")


def emit_examples() -> list[dict]:
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    y = _yaml()
    report = []
    for fname, cname, idx, inv in BASELINE:
        data = y.load((SCHEMA_DIR / fname).read_text(encoding="utf-8"))
        rule = data["classes"][cname]["rules"][idx]
        # strip INV prefix noise for builders — conditions unchanged
        base = valid_base(cname)
        satisfy = build_satisfy(cname, base, rule)
        violate, how = build_violate(cname, base, rule)
        sat_errs = errs(cname, satisfy)
        vio_errs = errs(cname, violate)
        valid_path = OUT_DIR / f"{inv}.valid.yaml"
        invalid_path = OUT_DIR / f"{inv}.invalid.yaml"
        # INV-001: satisfy rejected (boolean equals_string defect) — still write;
        # mark in report. Prefer base (no identifying) as "valid" if it passes.
        if sat_errs and not errs(cname, base):
            dump_inst(valid_path, inv, cname, "valid(base)", base)
            valid_note = "used base (satisfy unsatisfiable)"
        else:
            dump_inst(valid_path, inv, cname, "valid", satisfy)
            valid_note = "satisfy"
        dump_inst(invalid_path, inv, cname, "invalid", violate)
        report.append(
            {
                "id": inv,
                "class": cname,
                "valid_ok": not errs(
                    cname,
                    _load_simple(valid_path),
                ),
                "invalid_rejected": bool(vio_errs),
                "invalid_how": how,
                "satisfy_errors": sat_errs[:3],
                "violate_errors": vio_errs[:3],
                "valid_note": valid_note,
            }
        )
        print(
            f"{inv} class={cname} valid_ok={report[-1]['valid_ok']} "
            f"invalid_rejected={report[-1]['invalid_rejected']} how={how}"
        )
    return report


def _load_simple(path: Path) -> dict:
    import yaml as pyyaml

    return pyyaml.safe_load(path.read_text(encoding="utf-8"))


def write_manifest(report: list[dict]) -> None:
    man = CommentedMap()
    man["title"] = "L1 invariant fixtures (PR-C2)"
    cases = []
    for fname, cname, idx, inv in BASELINE:
        row = next(r for r in report if r["id"] == inv)
        cases.append(
            {
                "id": inv,
                "target_class": cname,
                "schema_file": fname,
                "rule_index": idx,
                "valid": f"{inv}.valid.yaml",
                "invalid": f"{inv}.invalid.yaml",
                "valid_ok": row["valid_ok"],
                "invalid_rejected": row["invalid_rejected"],
                "notes": row["valid_note"],
            }
        )
    man["cases"] = cases
    path = OUT_DIR / "manifest.yaml"
    y = YAML()
    y.default_flow_style = False
    y.indent(mapping=2, sequence=4, offset=2)
    with path.open("w", encoding="utf-8", newline="\n") as fh:
        y.dump(man, fh)
    print(f"wrote {path.relative_to(REPO)}")


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    prefix_descriptions()
    report = emit_examples()
    write_manifest(report)
    bad = [r for r in report if not r["invalid_rejected"]]
    unsat = [r for r in report if r["satisfy_errors"] and r["valid_note"].startswith("used base")]
    print(f"summary: {len(report)} fixtures; invalid_not_rejected={len(bad)}; satisfy_unsat={len(unsat)}")
    out = REPO / "tmp/constraint-spike/c2_fixture_report.json"
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"wrote {out.relative_to(REPO)}")
    return 0 if not bad else 2


if __name__ == "__main__":
    raise SystemExit(main())
