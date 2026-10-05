from __future__ import annotations

import sys
import traceback
from pathlib import Path

from linkml_runtime import SchemaView
from linkml_runtime.dumpers.rdflib_dumper import RDFLibDumper
from linkml_runtime.loaders import yaml_loader
from pyshacl import validate

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "generated" / "artifacts" / "moex-dams" / "0.1" / "python"))
from moex_dams import ModelPackage  # noqa: E402

schema = REPO / "model-assets/specifications/moex-dams/0.1/schemas/moex-dams.yaml"
mini = REPO / "tmp/spike_mini_package.yaml"
mini.write_text(
    """
element_id: dams:model/spike/1.0.0
name: spike_package
title: Spike package
description: Minimal ModelPackage for SHACL spike.
lifecycle_status: draft
api_version: dams.moex/v0.1
model_version: 1.0.0
implementation_scope: solution
""",
    encoding="utf-8",
)

sv = SchemaView(str(schema))
try:
    obj = yaml_loader.load(str(mini), target_class=ModelPackage)
    print("loaded", type(obj), getattr(obj, "element_id", None))
except Exception as e:
    print("LOAD FAIL", type(e), e)
    traceback.print_exc()
    raise SystemExit(1)

dumper = RDFLibDumper()
try:
    g = dumper.as_rdf_graph(obj, schemaview=sv)
    print("triples", len(g))
    print(g.serialize(format="turtle")[:1200])
except Exception as e:
    print("DUMP FAIL", type(e), e)
    traceback.print_exc()
    raise SystemExit(1)

shapes = (REPO / "generated/artifacts/moex-dams/0.1/moex-dams.shacl.ttl").read_text(
    encoding="utf-8"
)
conforms, _report_g, report_text = validate(
    data_graph=g,
    shacl_graph=shapes,
    inference="none",
    abort_on_first=False,
    meta_shacl=False,
    advanced=False,
    js=False,
    debug=False,
)
print("CONFORMS", conforms)
print(report_text[:3000])

from rdflib import Namespace

DAMS = Namespace("https://data.moex.com/dams/")
for triple in list(g.triples((None, DAMS.lifecycle_status, None))):
    g.remove(triple)
bad_conforms, _, bad_report = validate(
    data_graph=g,
    shacl_graph=shapes,
    inference="none",
    abort_on_first=False,
)
print("INVALID_CONFORMS", bad_conforms)
assert conforms and not bad_conforms
print("spike go: RDFLibDumper + pySHACL valid/invalid OK")
