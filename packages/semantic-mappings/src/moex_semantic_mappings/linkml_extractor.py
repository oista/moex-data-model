"""Extract LinkML class_uri / slot_uri / meaning / *_mappings as bindings."""

from __future__ import annotations

from pathlib import Path

from linkml_runtime import SchemaView

from moex_semantic_mappings.mapping import SemanticBinding, SemanticResourceRef

MAPPING_SLOTS = (
    ("exact_mappings", "skos:exactMatch"),
    ("close_mappings", "skos:closeMatch"),
    ("related_mappings", "skos:relatedMatch"),
    ("broad_mappings", "skos:broadMatch"),
    ("narrow_mappings", "skos:narrowMatch"),
)


def extract_linkml_bindings(
    schema_path: Path,
    *,
    mapping_set_id: str = "moex:mappings:linkml-inline",
) -> list[SemanticBinding]:
    sv = SchemaView(str(schema_path))
    bindings: list[SemanticBinding] = []

    for class_name, cls in sv.all_classes().items():
        subject = SemanticResourceRef(
            id=cls.class_uri or f"linkml:{class_name}",
            kind="linkml_class",
            label=cls.title or class_name,
        )
        if cls.class_uri:
            bindings.append(
                SemanticBinding(
                    subject=SemanticResourceRef(
                        id=f"linkml:{class_name}",
                        kind="linkml_class",
                        label=cls.title or class_name,
                    ),
                    predicate="linkml:class_uri",
                    object=SemanticResourceRef(
                        id=cls.class_uri,
                        kind="ontology_entity",
                        label=None,
                    ),
                    justification="semapv:ManualMappingCuration",
                    confidence=1.0,
                    author=None,
                    status="approved",
                    mapping_set_id=mapping_set_id,
                )
            )
        for slot_name, predicate in MAPPING_SLOTS:
            values = getattr(cls, slot_name, None) or []
            for value in values:
                bindings.append(
                    SemanticBinding(
                        subject=SemanticResourceRef(
                            id=f"linkml:{class_name}",
                            kind="linkml_class",
                            label=cls.title or class_name,
                        ),
                        predicate=predicate,
                        object=SemanticResourceRef(
                            id=str(value),
                            kind="ontology_entity",
                            label=None,
                        ),
                        justification="semapv:LexicalMatching",
                        confidence=None,
                        author=None,
                        status="approved",
                        mapping_set_id=mapping_set_id,
                    )
                )

    for slot_name, slot in sv.all_slots().items():
        if slot.slot_uri:
            bindings.append(
                SemanticBinding(
                    subject=SemanticResourceRef(
                        id=f"linkml:{slot_name}",
                        kind="linkml_slot",
                        label=slot.title or slot_name,
                    ),
                    predicate="linkml:slot_uri",
                    object=SemanticResourceRef(
                        id=slot.slot_uri,
                        kind="ontology_entity",
                        label=None,
                    ),
                    justification="semapv:ManualMappingCuration",
                    confidence=1.0,
                    author=None,
                    status="approved",
                    mapping_set_id=mapping_set_id,
                )
            )
        for map_slot, predicate in MAPPING_SLOTS:
            values = getattr(slot, map_slot, None) or []
            for value in values:
                bindings.append(
                    SemanticBinding(
                        subject=SemanticResourceRef(
                            id=f"linkml:{slot_name}",
                            kind="linkml_slot",
                            label=slot.title or slot_name,
                        ),
                        predicate=predicate,
                        object=SemanticResourceRef(
                            id=str(value),
                            kind="ontology_entity",
                            label=None,
                        ),
                        justification="semapv:LexicalMatching",
                        confidence=None,
                        author=None,
                        status="approved",
                        mapping_set_id=mapping_set_id,
                    )
                )

    for enum_name, enum in sv.all_enums().items():
        for pv_name, pv in (enum.permissible_values or {}).items():
            meaning = getattr(pv, "meaning", None)
            if meaning:
                bindings.append(
                    SemanticBinding(
                        subject=SemanticResourceRef(
                            id=f"linkml:{enum_name}.{pv_name}",
                            kind="linkml_enum_value",
                            label=getattr(pv, "title", None) or pv_name,
                        ),
                        predicate="linkml:meaning",
                        object=SemanticResourceRef(
                            id=str(meaning),
                            kind="ontology_entity",
                            label=None,
                        ),
                        justification="semapv:ManualMappingCuration",
                        confidence=1.0,
                        author=None,
                        status="approved",
                        mapping_set_id=mapping_set_id,
                    )
                )

    return bindings
