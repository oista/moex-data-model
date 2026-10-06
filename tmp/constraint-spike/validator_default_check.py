"""Spike (PR-C0): does `Validator(schema)` (no plugins, as used in scripts/validate-*.ps1) validate anything?"""
from __future__ import annotations

import sys
from importlib import metadata
from pathlib import Path

import yaml
from linkml.validator import Validator
from linkml.validator.plugins import JsonschemaValidationPlugin

REPO = Path(__file__).resolve().parents[2]
S = REPO / "model-assets/specifications/moex-dams/0.1/schemas/moex-dams.yaml"
EX = REPO / "model-assets/specifications/moex-dams/0.1/examples/client-contract-binding.yaml"

good = yaml.safe_load(EX.read_text(encoding="utf-8"))
bad = dict(good)
bad["totally_unknown_slot"] = 1
bad.pop("element_id", None)

print("python", sys.version.split()[0], "linkml", metadata.version("linkml"))
print("no plugins   | valid example :", len(Validator(S).validate(good, target_class="DataModelBinding").results), "results")
print("no plugins   | broken example:", len(Validator(S).validate(bad, target_class="DataModelBinding").results), "results")
plug = [JsonschemaValidationPlugin(closed=True)]
print("jsonschema   | valid example :", len(Validator(S, plug).validate(good, target_class="DataModelBinding").results), "results")
print("jsonschema   | broken example:", len(Validator(S, plug).validate(bad, target_class="DataModelBinding").results), "results")
