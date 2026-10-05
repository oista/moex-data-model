# -*- coding: utf-8 -*-
"""Update UML puml files: PhysicalObject → TechnicalAsset hierarchy."""
from pathlib import Path

ROOT = Path.cwd()

# 01-core-data-model.puml
p = ROOT / "docs/architecture/uml/01-core-data-model.puml"
t = p.read_text(encoding="utf-8")
old = '''package "Физический уровень" #FCE5CD {
  class PhysicalObject {
    +solution_ref : ITSolution [0..1]
    +system_ref : ITSystem [1]
    +object_kind : PhysicalObjectKindEnum [1]
    +qualified_name : string [1]
    +technology : string [1]
    +native_schema_ref : uri [1]
    +direction : FlowDirectionEnum [1]
    +mapping_coverage_status : MappingCoverageStatusEnum [0..1]
    +mapping_rationale : string [0..1]
  }
  class PhysicalField {
    +physical_object_ref : PhysicalObject [1]
    +native_name : string [1]
    +native_type : string [1]
    +required : boolean [1]
    +ordinal_position : integer [0..1]
    +schema_path : string [0..1]
    +mapping_coverage_status : MappingCoverageStatusEnum [0..1]
    +mapping_rationale : string [0..1]
  }
}'''
new = '''package "Технический уровень (TechnicalAsset)" #FCE5CD {
  abstract class TechnicalAsset {
    +asset_namespace : string [1]
    +qualified_name : string [1]
    +system_ref : ITSystem [1]
    +asset_kind : enum [1]
    +technology : string [0..1]
    +direction : FlowDirectionEnum [0..1]
    +solution_ref : ITSolution [0..1]
  }
  class DataCarrier {
    +structure_ref : uri [0..1]
    +mapping_coverage_status : MappingCoverageStatusEnum [0..1]
  }
  class AccessPoint
  class DataContainer
  class ExecutionAsset
  class PhysicalField {
    +carrier_ref : DataCarrier [1]
    +native_name : string [1]
    +native_type : string [1]
    +required : boolean [1]
    +ordinal_position : integer [0..1]
    +schema_path : string [0..1]
  }
}'''
if old not in t:
    print("01 package block miss")
else:
    t = t.replace(old, new)
t = t.replace("ModelElement <|-- PhysicalObject", "ModelElement <|-- TechnicalAsset\nTechnicalAsset <|-- DataCarrier\nTechnicalAsset <|-- AccessPoint\nTechnicalAsset <|-- DataContainer\nTechnicalAsset <|-- ExecutionAsset")
t = t.replace(
    "PhysicalObject \"0..*\" --> \"1\" ITSystem : system_ref\nPhysicalObject \"0..*\" --> \"0..1\" ITSolution : solution_ref\nPhysicalObject \"1\" *-- \"0..*\" PhysicalField : physical_fields",
    "TechnicalAsset \"0..*\" --> \"1\" ITSystem : system_ref\nTechnicalAsset \"0..*\" --> \"0..1\" ITSolution : solution_ref\nDataCarrier \"1\" *-- \"0..*\" PhysicalField : physical_fields",
)
t = t.replace(
    """note bottom of PhysicalObject
  technology and native_schema_ref are required
  string/uri slots — not typed classes.
end note""",
    """note bottom of TechnicalAsset
  Collections: data_carriers, access_points,
  data_containers, execution_assets (ADR-031).
  Identity: asset_namespace + qualified_name.
end note""",
)
p.write_text(t, encoding="utf-8")
print("01 left", "PhysicalObject" in t, "physical_objects" in t)

# 02-solution-model-governance.puml — simpler global replace may break; do targeted
p = ROOT / "docs/architecture/uml/02-solution-model-governance.puml"
t = p.read_text(encoding="utf-8")
t = t.replace("PhysicalObjectKindEnum", "DataCarrierKindEnum")
t = t.replace("PhysicalObject", "DataCarrier")
t = t.replace("physical_objects", "data_carriers")
t = t.replace("physical_object_refs", "carrier_refs")
t = t.replace("+object_kind", "+asset_kind")
p.write_text(t, encoding="utf-8")
print("02 left", "PhysicalObject" in t, "physical_objects" in t)

# all_model_modules.puml
p = ROOT / "docs/architecture/uml/all_model_modules.puml"
t = p.read_text(encoding="utf-8")
t = t.replace("class PhysicalObject", "class TechnicalAsset\n  class DataCarrier")
t = t.replace("ModelElement <|-- PhysicalObject", "ModelElement <|-- TechnicalAsset\nTechnicalAsset <|-- DataCarrier")
t = t.replace("ModelPackage \"1\" *-- \"0..*\" PhysicalObject : physical_objects",
              "ModelPackage \"1\" *-- \"0..*\" DataCarrier : data_carriers")
t = t.replace("PhysicalObject \"1\" *-- \"0..*\" PhysicalField : physical_fields",
              "DataCarrier \"1\" *-- \"0..*\" PhysicalField : physical_fields")
t = t.replace("PhysicalObject \"0..*\" --> \"1\" ITSystem : system_ref",
              "TechnicalAsset \"0..*\" --> \"1\" ITSystem : system_ref")
p.write_text(t, encoding="utf-8")
print("all left", "PhysicalObject" in t, "physical_objects" in t)
