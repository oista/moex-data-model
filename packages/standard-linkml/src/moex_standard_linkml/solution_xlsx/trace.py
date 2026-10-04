"""element_id / entity.attr → SourceRef trace for assess merge."""

from __future__ import annotations

from dataclasses import dataclass, field

from moex_standard_linkml.solution_xlsx.diagnostics import SourceRef


@dataclass
class TraceMap:
    entity_refs: dict[str, SourceRef] = field(default_factory=dict)  # name → ref
    attribute_refs: dict[str, SourceRef] = field(default_factory=dict)  # Entity.attr
    element_ids: dict[str, SourceRef] = field(default_factory=dict)  # CURIE → ref

    def bind_entity(self, name: str, ref: SourceRef) -> None:
        self.entity_refs[name] = ref

    def bind_attribute(self, entity: str, attr: str, ref: SourceRef) -> None:
        self.attribute_refs[f"{entity}.{attr}"] = ref

    def bind_element(self, element_id: str, ref: SourceRef) -> None:
        self.element_ids[element_id] = ref

    def resolve(self, token: str | None) -> SourceRef | None:
        if not token:
            return None
        if token in self.element_ids:
            return self.element_ids[token]
        if token in self.attribute_refs:
            return self.attribute_refs[token]
        if token in self.entity_refs:
            return self.entity_refs[token]
        # Try suffix match on CURIE
        for eid, ref in self.element_ids.items():
            if eid.endswith("/" + token) or eid.endswith(token):
                return ref
        return None

    def populate_from_package(self, package: dict) -> None:
        """After mapping, attach CURIEs from package structure."""
        for ent in package.get("logical_entities") or []:
            name = ent.get("name")
            eid = ent.get("element_id")
            if name and eid and name in self.entity_refs:
                self.bind_element(str(eid), self.entity_refs[name])
            for attr in ent.get("attributes") or []:
                aname = attr.get("name")
                aeid = attr.get("element_id")
                key = f"{name}.{aname}" if name and aname else None
                if key and aeid and key in self.attribute_refs:
                    self.bind_element(str(aeid), self.attribute_refs[key])
