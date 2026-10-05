# -*- coding: utf-8 -*-
from pathlib import Path

ROOT = Path(__file__).resolve().parent if False else Path.cwd()

# Agent docs
replacements = [
    ("PhysicalObjects.csv", "DataCarriers.csv"),
    ("PhysicalObjects", "DataCarriers"),
    ("object_kind", "asset_kind"),
    (
        "PhysicalObjectKindEnum",
        "DataCarrierKindEnum / AccessPointKindEnum / "
        "DataContainerKindEnum / ExecutionAssetKindEnum",
    ),
    ("physical object", "technical asset (DataCarrier)"),
    ("physical objects", "technical assets (DataCarriers)"),
    ("PhysicalObject", "DataCarrier"),
    ("native_schema_ref", "structure_ref"),
]
for rel in [
    "docs/agents/er-dictionary-model-contract.md",
    "docs/agents/pdf-to-er-dictionary.md",
]:
    p = ROOT / rel
    t = p.read_text(encoding="utf-8")
    for a, b in replacements:
        t = t.replace(a, b)
    p.write_text(t, encoding="utf-8")
    left = [
        i
        for i, l in enumerate(t.splitlines(), 1)
        if "PhysicalObject" in l or "physical_objects" in l
    ]
    print(rel, "left", left)

# linkml_architecture
p = ROOT / "docs/architecture/linkml_architecture.md"
t = p.read_text(encoding="utf-8")
t = t.replace(
    "У каждого `PhysicalObject` определены `system_ref`, `technology` и `native_schema_ref`.",
    "У каждого `DataCarrier` / `TechnicalAsset` определены `system_ref`, "
    "`technology` и `structure_ref` (или эквивалент по подклассу).",
)
t = t.replace(
    "- PhysicalObject.",
    "- TechnicalAsset (`DataCarrier`, `AccessPoint`, `DataContainer`, `ExecutionAsset`).",
)
p.write_text(t, encoding="utf-8")
print("linkml arch", "PhysicalObject" in t)

# IT requirements
p = ROOT / "docs/architecture/IT_SOLUTION_MODEL_REQUIREMENTS.md"
t = p.read_text(encoding="utf-8")
t = t.replace("PhysicalObject", "TechnicalAsset")
p.write_text(t, encoding="utf-8")
print("IT req", "PhysicalObject" in t, "physical_objects" in t)

# MOEX draft spec
p = ROOT / "docs/MOEX Data Model Specification v0.1 на основе LinkML.md"
t = p.read_text(encoding="utf-8")
banner = (
    "\n> **Superseded physical layer (2026-10-05):** the flat class/collection "
    "in this draft is replaced by `TechnicalAsset` hierarchy "
    "(`DataCarrier`, `AccessPoint`, `DataContainer`, `ExecutionAsset`) per "
    "ADR-031 / ADR-032 / ADR-033. Prefer those ADRs and `moex-technical.yaml` "
    "over any remaining draft excerpts below.\n"
)
if "Superseded physical layer" not in t:
    lines = t.splitlines(True)
    lines.insert(1, banner)
    t = "".join(lines)
t = t.replace("PhysicalObject", "TechnicalAsset")
t = t.replace("physical_objects", "data_carriers")
p.write_text(t, encoding="utf-8")
print("MOEX spec", "PhysicalObject" in t, "physical_objects" in t)

# solution profile
p = ROOT / "model-assets/implementations/solutions/solution-xlsx.profile.yaml"
t = p.read_text(encoding="utf-8")
t = t.replace("object_kind: view", "asset_kind: relational_view")
t = t.replace("object_kind: table", "asset_kind: relational_table")
p.write_text(t, encoding="utf-8")
print("sol profile object_kind left", "object_kind" in t)
