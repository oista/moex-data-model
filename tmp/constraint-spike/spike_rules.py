"""Spike (PR-C0, ADR-045): what LinkML 1.11.1 does with `rules` per generator.

Builds one mini-schema (class ``T``) per case, runs

  * linkml-validate  (linkml.validator.Validator, default plugins - same call as scripts/validate-examples.ps1)
  * gen-json-schema  (JsonSchemaGenerator + jsonschema Draft 2019-09)
  * gen-pydantic     (PydanticGenerator + exec + model_validate)
  * gen-shacl        (ShaclGenerator + pyShACL on a hand-built RDF instance)

on valid and invalid instances and classifies the generator behaviour.
Nothing in model-assets/ or generated/ is touched; all output lives in this folder.

Usage (repo root): python tmp/constraint-spike/spike_rules.py
"""

from __future__ import annotations

import copy
import json
from importlib import metadata as importlib_metadata
import sys
import traceback
from pathlib import Path

import yaml
from jsonschema import Draft201909Validator
from rdflib import RDF, Graph, Literal, Namespace, URIRef
from rdflib.compare import graph_diff, to_isomorphic

HERE = Path(__file__).resolve().parent
CASES_DIR = HERE / "cases"
CASES_DIR.mkdir(exist_ok=True)
EX = Namespace("https://spike.example/")

SLOTS = {
    "kind": "string",
    "a": "string",
    "b": "string",
    "n1": "integer",
    "n2": "integer",
    "flag": "boolean",
}


def pres(slot, v="PRESENT"):
    return {slot: {"value_presence": v}}


def cond(**slots):
    return {"slot_conditions": slots}


def eq(v):
    return {"equals_string": v}


CASES = [
    dict(id="c01-required-post", title="pre kind=X => post a required:true",
         rules=[dict(preconditions=cond(kind=eq("X")), postconditions=cond(a={"required": True}))],
         valid=[{"kind": "X", "a": "v"}, {"kind": "Y"}], invalid=[{"kind": "X"}]),
    dict(id="c02-presence-post", title="pre kind=X => post a value_presence PRESENT",
         rules=[dict(preconditions=cond(kind=eq("X")), postconditions=cond(**pres("a")))],
         valid=[{"kind": "X", "a": "v"}, {"kind": "Y"}], invalid=[{"kind": "X"}]),
    dict(id="c03-absent-post", title="pre kind=X => post a value_presence ABSENT",
         rules=[dict(preconditions=cond(kind=eq("X")), postconditions=cond(**pres("a", "ABSENT")))],
         valid=[{"kind": "X"}, {"kind": "Y", "a": "v"}], invalid=[{"kind": "X", "a": "v"}]),
    dict(id="c04-pre-presence", title="pre a PRESENT => post kind=X (DataType pattern)",
         rules=[dict(preconditions=cond(**pres("a")), postconditions=cond(kind=eq("X")))],
         valid=[{"a": "v", "kind": "X"}, {"kind": "Y"}], invalid=[{"a": "v", "kind": "Y"}]),
    dict(id="c05-anyof-pre", title="pre kind any_of(X,Y) => a PRESENT and b ABSENT (SchemaNode pattern)",
         rules=[dict(preconditions=cond(kind={"any_of": [eq("X"), eq("Y")]}),
                     postconditions=cond(**pres("a"), **pres("b", "ABSENT")))],
         valid=[{"kind": "X", "a": "v"}, {"kind": "Z", "b": "v"}],
         invalid=[{"kind": "X"}, {"kind": "Y", "a": "v", "b": "v"}]),
    dict(id="c06-anyof-post", title="pre a PRESENT => post kind any_of(X,Y)",
         rules=[dict(preconditions=cond(**pres("a")), postconditions=cond(kind={"any_of": [eq("X"), eq("Y")]}))],
         valid=[{"a": "v", "kind": "X"}, {"kind": "Z"}], invalid=[{"a": "v", "kind": "Z"}]),
    dict(id="c07-boolean-equals-string", title="pre kind=X => post flag equals_string 'true' on boolean slot (ConceptualProperty pattern)",
         rules=[dict(preconditions=cond(kind=eq("X")), postconditions=cond(flag=eq("true")))],
         valid=[{"kind": "X", "flag": True}, {"kind": "Y", "flag": False}],
         invalid=[{"kind": "X", "flag": False}, {"kind": "X"}]),
    dict(id="c08-pattern-post", title="pre kind=X => post a pattern ^A",
         rules=[dict(preconditions=cond(kind=eq("X")), postconditions=cond(a={"pattern": "^A"}))],
         valid=[{"kind": "X", "a": "AB"}, {"kind": "Y", "a": "BB"}], invalid=[{"kind": "X", "a": "BB"}]),
    dict(id="c09-elseconditions", title="pre kind=X => a PRESENT else b PRESENT",
         rules=[dict(preconditions=cond(kind=eq("X")), postconditions=cond(**pres("a")),
                     elseconditions=cond(**pres("b")))],
         valid=[{"kind": "X", "a": "v"}, {"kind": "Y", "b": "v"}], invalid=[{"kind": "X"}, {"kind": "Y"}]),
    dict(id="c10-bidirectional", title="kind=X <=> a PRESENT (bidirectional)",
         rules=[dict(preconditions=cond(kind=eq("X")), postconditions=cond(**pres("a")), bidirectional=True)],
         valid=[{"kind": "X", "a": "v"}, {"kind": "Y"}, {}], invalid=[{"kind": "X"}, {"kind": "Y", "a": "v"}]),
    dict(id="c11a-inapplicable-rule-field", title="rule-level `inapplicable: true` (does the field exist?)",
         rules=[dict(preconditions=cond(kind=eq("X")), postconditions=cond(**pres("a")), inapplicable=True)],
         valid=[{"kind": "X", "a": "v"}], invalid=[{"kind": "X"}]),
    dict(id="c11b-inapplicable-slot-cond", title="slot_conditions a: inapplicable: true",
         rules=[dict(preconditions=cond(kind=eq("X")), postconditions=cond(a={"inapplicable": True}))],
         valid=[{"kind": "X"}], invalid=[{"kind": "X", "a": "v"}]),
    dict(id="c11c-deactivated", title="rule with deactivated: true (control: must be ignored by every generator)",
         rules=[dict(preconditions=cond(kind=eq("X")), postconditions=cond(**pres("a")), deactivated=True)],
         valid=[{"kind": "X"}], invalid=[]),
    dict(id="c12-compare-slots", title="compare two slots: post n2 equals_expression '{n1}'",
         rules=[dict(preconditions=cond(**pres("n1")), postconditions=cond(n2={"equals_expression": "{n1}"}))],
         valid=[{"n1": 1, "n2": 1}], invalid=[{"n1": 1, "n2": 2}]),
    dict(id="c13-const-compare", title="control: constant comparison post n2 minimum_value 5",
         rules=[dict(preconditions=cond(kind=eq("X")), postconditions=cond(n2={"minimum_value": 5}))],
         valid=[{"kind": "X", "n2": 6}], invalid=[{"kind": "X", "n2": 1}]),
    dict(id="c14-exactly-one-of", title="class-level exactly_one_of(a required | b required) (not a rule)",
         class_extra=dict(exactly_one_of=[cond(a={"required": True}), cond(b={"required": True})]),
         rules=[], valid=[{"a": "v"}, {"b": "v"}], invalid=[{}, {"a": "v", "b": "v"}]),
]


def build_schema(case: dict, with_rules: bool = True) -> dict:
    cls: dict = {"attributes": {s: {"range": r} for s, r in SLOTS.items()}}
    if with_rules and case.get("rules"):
        cls["rules"] = copy.deepcopy(case["rules"])
    if with_rules and case.get("class_extra"):
        cls.update(copy.deepcopy(case["class_extra"]))
    return {
        "id": "https://spike.example/schema",
        "name": "spike",
        "prefixes": {"ex": "https://spike.example/", "linkml": "https://w3id.org/linkml/"},
        "default_prefix": "ex",
        "default_range": "string",
        "imports": ["linkml:types"],
        "classes": {"T": cls},
    }


def write_schema(case: dict, with_rules: bool = True) -> Path:
    suffix = "" if with_rules else ".norules"
    path = CASES_DIR / f"{case['id']}{suffix}.yaml"
    path.write_text(yaml.safe_dump(build_schema(case, with_rules), allow_unicode=True, sort_keys=False), encoding="utf-8")
    return path


def short(exc: BaseException) -> str:
    msg = f"{type(exc).__name__}: {exc}".replace("\n", " ")
    return msg[:160]


# ---- channels ----------------------------------------------------------------------
def ch_validator(schema: Path, instance: dict) -> str:
    from linkml.validator import Validator
    from linkml.validator.plugins import JsonschemaValidationPlugin

    # NB: Validator(schema) WITHOUT plugins validates nothing (validation_plugins=None).
    report = Validator(str(schema), [JsonschemaValidationPlugin(closed=True)]).validate(instance, target_class="T")
    errs = [r for r in report.results if "ERROR" in str(getattr(r, "severity", r)).upper()]
    return "violation" if errs else "ok"


_JS_CACHE: dict[str, dict] = {}


def json_schema(schema: Path) -> dict:
    key = str(schema)
    if key not in _JS_CACHE:
        from linkml.generators.jsonschemagen import JsonSchemaGenerator

        _JS_CACHE[key] = json.loads(JsonSchemaGenerator(str(schema), not_closed=False, metadata=False).serialize())
    return _JS_CACHE[key]


def ch_jsonschema(schema: Path, instance: dict) -> str:
    js = json_schema(schema)
    validator = Draft201909Validator({"$defs": js["$defs"], "$ref": "#/$defs/T"})
    return "violation" if list(validator.iter_errors(instance)) else "ok"


_PY_CACHE: dict[str, tuple[str, type]] = {}


def pydantic_model(schema: Path):
    key = str(schema)
    if key not in _PY_CACHE:
        from linkml.generators.pydanticgen import PydanticGenerator

        text = PydanticGenerator(str(schema), metadata=False).serialize()
        ns: dict = {}
        exec(compile(text, f"<pydantic:{schema.name}>", "exec"), ns)  # noqa: S102 - spike only
        _PY_CACHE[key] = (text, ns["T"])
    return _PY_CACHE[key]


def ch_pydantic(schema: Path, instance: dict) -> str:
    _, model = pydantic_model(schema)
    try:
        model(**instance)
    except Exception:  # noqa: BLE001 - pydantic ValidationError
        return "violation"
    return "ok"


_SHACL_CACHE: dict[str, Graph] = {}


def shacl_graph(schema: Path) -> Graph:
    key = str(schema)
    if key not in _SHACL_CACHE:
        from linkml.generators.shaclgen import ShaclGenerator

        g = Graph()
        g.parse(data=ShaclGenerator(str(schema), metadata=False).serialize(), format="turtle")
        _SHACL_CACHE[key] = g
    return _SHACL_CACHE[key]


def ch_shacl(schema: Path, instance: dict) -> str:
    from pyshacl import validate

    data = Graph()
    node = URIRef("https://spike.example/inst1")
    data.add((node, RDF.type, EX.T))
    for slot, value in instance.items():
        data.add((node, EX[slot], Literal(value)))
    shapes = Graph()
    shapes += shacl_graph(schema)  # pySHACL mutates the shapes graph (adds RDFS axioms): validate a copy
    conforms, _, _ = validate(data, shacl_graph=shapes, inference="none")
    return "ok" if conforms else "violation"


CHANNELS = {
    "linkml-validate": ch_validator,
    "gen-json-schema": ch_jsonschema,
    "gen-pydantic": ch_pydantic,
    "gen-shacl+pyshacl": ch_shacl,
}


def classify(valid_res: list[str], invalid_res: list[str]) -> str:
    if any(r.startswith("CRASH") for r in valid_res + invalid_res):
        return "CRASH"
    if any(r == "violation" for r in valid_res):
        return "WRONG (valid rejected)"
    if not invalid_res:
        return "n/a (no invalid)"
    bad = [r for r in invalid_res if r == "violation"]
    if len(bad) == len(invalid_res):
        return "APPLIES"
    if bad:
        return "PARTIAL"
    return "IGNORES"


def artifact_effect(case: dict) -> dict:
    """Does the generator output differ from the same schema without rules?"""
    eff: dict[str, str] = {}
    with_p, without_p = write_schema(case, True), write_schema(case, False)
    try:
        eff["gen-json-schema"] = "differs" if json_schema(with_p)["$defs"] != json_schema(without_p)["$defs"] else "identical"
    except Exception as exc:  # noqa: BLE001
        eff["gen-json-schema"] = "CRASH " + short(exc)
    try:
        pw = pydantic_model(with_p)[0].replace(with_p.name, "X")
        pn = pydantic_model(without_p)[0].replace(without_p.name, "X")
        if pw == pn:
            eff["gen-pydantic"] = "identical"
        else:
            # rules end up only inside the linkml_meta ClassVar (documentation); fields/validators identical
            eff["gen-pydantic"] = "differs (linkml_meta only)" if "'rules'" in pw and "'rules'" not in pn else "differs"
    except Exception as exc:  # noqa: BLE001
        eff["gen-pydantic"] = "CRASH " + short(exc)
    try:
        _, only_w, only_n = graph_diff(to_isomorphic(shacl_graph(with_p)), to_isomorphic(shacl_graph(without_p)))
        eff["gen-shacl"] = "differs" if (len(only_w) or len(only_n)) else "identical"
    except Exception as exc:  # noqa: BLE001
        eff["gen-shacl"] = "CRASH " + short(exc)
    try:
        from linkml.generators.owlgen import OwlSchemaGenerator

        def owl(path: Path) -> Graph:
            g = Graph()
            g.parse(data=OwlSchemaGenerator(str(path), metadata=False).serialize(), format="turtle")
            for t in [t for t in g if "generation_date" in str(t[1]) or "generatedAtTime" in str(t[1])]:
                g.remove(t)
            return g

        _, ow, on = graph_diff(to_isomorphic(owl(with_p)), to_isomorphic(owl(without_p)))
        eff["gen-owl"] = "differs" if (len(ow) or len(on)) else "identical"
    except Exception as exc:  # noqa: BLE001
        eff["gen-owl"] = "CRASH " + short(exc)
    return eff


def run() -> list[dict]:
    results = []
    for case in CASES:
        schema = write_schema(case, True)
        row = {"id": case["id"], "title": case["title"], "channels": {}, "detail": {}}
        for name, fn in CHANNELS.items():
            vres, ires = [], []
            for inst in case["valid"]:
                try:
                    vres.append(fn(schema, inst))
                except Exception as exc:  # noqa: BLE001
                    vres.append("CRASH " + short(exc))
            for inst in case["invalid"]:
                try:
                    ires.append(fn(schema, inst))
                except Exception as exc:  # noqa: BLE001
                    ires.append("CRASH " + short(exc))
            row["channels"][name] = classify(vres, ires)
            row["detail"][name] = {"valid": vres, "invalid": ires}
        row["artifact_effect"] = artifact_effect(case)
        results.append(row)
    return results


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    import linkml
    import linkml_runtime
    import pyshacl

    meta = {
        "python": sys.version.split()[0],
        "linkml": importlib_metadata.version("linkml"),
        "linkml_runtime": importlib_metadata.version("linkml-runtime"),
        "pyshacl": importlib_metadata.version("pyshacl"),
    }
    results = run()
    (HERE / "results.json").write_text(json.dumps({"meta": meta, "cases": results}, ensure_ascii=False, indent=2), encoding="utf-8")
    print(meta)
    names = list(CHANNELS)
    print("| case | " + " | ".join(names) + " |")
    print("|---|" + "---|" * len(names))
    for r in results:
        print(f"| {r['id']} | " + " | ".join(r["channels"][n] for n in names) + " |")
    print()
    for r in results:
        print(r["id"], r["artifact_effect"])
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception:  # noqa: BLE001
        traceback.print_exc()
        raise SystemExit(1)
