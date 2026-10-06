"""Spike (PR-C0): the 17 real LinkML rules of the DAMS schema vs the committed JSON Schema.

For every rule (file, class, index) synthesises
  base      - minimal instance of the class that satisfies required slots,
  satisfy   - base + rule precondition true + postcondition true,
  violate   - base + rule precondition true + postcondition false,
and validates them against generated/artifacts/moex-dams/0.1/moex-dams.schema.json
(the golden JSON Schema produced by gen-json-schema from the project schema).

A rule is "unsatisfiable" if `satisfy` is rejected by the generated JSON Schema.
Nothing in the repo is modified; results go to tmp/constraint-spike/real-rules.json.
"""

from __future__ import annotations

import copy
import json
import sys
from pathlib import Path

import yaml
from jsonschema import Draft201909Validator

REPO = Path(__file__).resolve().parents[2]
SCHEMA_DIR = REPO / "model-assets" / "specifications" / "moex-dams" / "0.1" / "schemas"
JS = json.loads((REPO / "generated" / "artifacts" / "moex-dams" / "0.1" / "moex-dams.schema.json").read_text(encoding="utf-8"))
DEFS = JS["$defs"]


GLOBAL_PICK = [0]


def synth(prop: dict, enum_pick: int = 0, depth: int = 0):
    """Synthesise a value for a JSON-Schema property."""
    if "$ref" in prop:
        name = prop["$ref"].split("/")[-1]
        target = DEFS[name]
        if "enum" in target:
            return target["enum"][(enum_pick + GLOBAL_PICK[0]) % len(target["enum"])]
        if target.get("type") == "object" and depth < 2:
            return base_instance(name, depth + 1)
        return f"{name}-x"  # reference by identifier
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


def valid_base(cls: str) -> dict:
    """Pick the first enum rotation whose minimal instance is accepted by the JSON Schema."""
    for pick in range(0, 8):
        GLOBAL_PICK[0] = pick
        inst = base_instance(cls)
        if not errs(cls, inst):
            return inst
    GLOBAL_PICK[0] = 0
    return base_instance(cls)


def present_value(cls: str, slot: str, avoid=None):
    p = DEFS[cls]["properties"][slot]
    for i in range(0, 8):
        v = synth(p, i)
        if avoid is None or v not in avoid:
            return v
    return synth(p)


def cond_values(cls: str, slot: str, cond: dict) -> list:
    """Values satisfying a slot condition (list of candidates)."""
    if "equals_string" in cond:
        v = cond["equals_string"]
        t = DEFS[cls]["properties"][slot].get("type")
        return [v]
    if "any_of" in cond:
        return [c["equals_string"] for c in cond["any_of"] if "equals_string" in c]
    if cond.get("value_presence") == "PRESENT" or cond.get("required") is True:
        return [present_value(cls, slot)]
    return []


def violating_value(cls: str, slot: str, cond: dict):
    if "equals_string" in cond or "any_of" in cond:
        ok = set(cond_values(cls, slot, cond))
        p = DEFS[cls]["properties"][slot]
        for i in range(0, 12):
            v = synth(p, i)
            if v not in ok:
                return v, True
        return None, True
    return None, False


def apply_pre(cls: str, inst: dict, pre: dict):
    for slot, cond in pre["slot_conditions"].items():
        if cond.get("value_presence") == "ABSENT":
            inst.pop(slot, None)
            continue
        vals = cond_values(cls, slot, cond)
        if vals:
            inst[slot] = vals[0]


def build_satisfy(cls, base, rule):
    inst = copy.deepcopy(base)
    apply_pre(cls, inst, rule["preconditions"])
    for slot, cond in rule["postconditions"]["slot_conditions"].items():
        if cond.get("value_presence") == "ABSENT":
            inst.pop(slot, None)
        else:
            vals = cond_values(cls, slot, cond)
            if vals:
                inst[slot] = vals[0]
    return inst


def build_violate(cls, base, rule):
    """One instance per postcondition slot, each violating only that slot."""
    outs = []
    for slot, cond in rule["postconditions"]["slot_conditions"].items():
        inst = copy.deepcopy(base)
        apply_pre(cls, inst, rule["preconditions"])
        for s2, c2 in rule["postconditions"]["slot_conditions"].items():  # satisfy others
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
        else:
            v, ok = violating_value(cls, slot, cond)
            if not ok:
                continue
            inst[slot] = v
        outs.append((slot, inst))
    absent = [s for s, c in rule["postconditions"]["slot_conditions"].items() if c.get("value_presence") == "ABSENT"]
    if len(absent) > 1:  # all forbidden slots present at once
        inst = copy.deepcopy(base)
        apply_pre(cls, inst, rule["preconditions"])
        for s2, c2 in rule["postconditions"]["slot_conditions"].items():
            if c2.get("value_presence") == "ABSENT":
                inst[s2] = present_value(cls, s2)
            else:
                v = cond_values(cls, s2, c2)
                if v:
                    inst[s2] = v[0]
        outs.append(("ALL:" + "+".join(absent), inst))
    return outs


def validator_for(cls):
    return Draft201909Validator({"$defs": DEFS, "$ref": f"#/$defs/{cls}"})


def errs(cls, inst):
    return [e.message[:110] for e in validator_for(cls).iter_errors(inst)]


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    rows = []
    for path in sorted(SCHEMA_DIR.glob("*.yaml")):
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        for cname, body in (data.get("classes") or {}).items():
            for idx, rule in enumerate((body or {}).get("rules") or []):
                if cname not in DEFS:
                    rows.append({"file": path.name, "class": cname, "index": idx, "error": "class not in JSON Schema"})
                    continue
                base = valid_base(cname)
                base_errs = errs(cname, base)
                sat = build_satisfy(cname, base, rule)
                sat_errs = errs(cname, sat)
                viol = []
                for slot, inst in build_violate(cname, base, rule):
                    viol.append({"slot": slot, "rejected": bool(errs(cname, inst)), "errors": errs(cname, inst)[:2]})
                rows.append({
                    "file": path.name, "class": cname, "index": idx, "description": rule.get("description"),
                    "base_ok": not base_errs, "base_errors": base_errs[:2],
                    "satisfy_ok": not sat_errs, "satisfy_errors": sat_errs[:2],
                    "violations": viol,
                })
    (Path(__file__).parent / "real-rules.json").write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
    print("| file | class | # | base ok | satisfy accepted | violations rejected | note |")
    print("|---|---|---|---|---|---|---|")
    for r in rows:
        if "error" in r:
            print(f"| {r['file']} | {r['class']} | {r['index']} | - | - | - | {r['error']} |")
            continue
        vr = ",".join(f"{v['slot']}:{'Y' if v['rejected'] else 'N'}" for v in r["violations"]) or "-"
        note = ""
        if not r["base_ok"]:
            note += "BASE INVALID " + "; ".join(r["base_errors"]) + " "
        if not r["satisfy_ok"]:
            note += "SATISFY REJECTED " + "; ".join(r["satisfy_errors"])
        print(f"| {r['file']} | {r['class']} | {r['index']} | {r['base_ok']} | {r['satisfy_ok']} | {vr} | {note} |")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
