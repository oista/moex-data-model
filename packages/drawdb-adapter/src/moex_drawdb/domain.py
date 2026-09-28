"""Domain types for DBML projection round-trip."""

from __future__ import annotations

from enum import Enum
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

Profile = Literal["logical", "physical"]


class RejectCode(str, Enum):
    ELEMENT_ID_REWRITE = "element_id_rewrite"
    UNSUPPORTED = "unsupported"
    MISSING_END = "missing_end"


class ProjectedColumn(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    name: str
    type_name: str
    required: bool = False
    element_id: str | None = None
    note: str | None = None


class ProjectedTable(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    name: str
    element_id: str | None = None
    object_kind: str | None = None
    title: str | None = None
    columns: tuple[ProjectedColumn, ...] = ()


class ProjectedRef(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    name: str | None = None
    source_table: str
    source_column: str
    target_table: str
    target_column: str
    element_id: str | None = None


class ProjectedDiagram(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    tables: tuple[ProjectedTable, ...] = ()
    refs: tuple[ProjectedRef, ...] = ()


class PatchOpKind(str, Enum):
    ADD_ENTITY = "add_entity"
    UPDATE_ENTITY = "update_entity"
    DELETE_ENTITY = "delete_entity"
    ADD_ATTRIBUTE = "add_attribute"
    UPDATE_ATTRIBUTE = "update_attribute"
    DELETE_ATTRIBUTE = "delete_attribute"
    ADD_RELATIONSHIP = "add_relationship"
    UPDATE_RELATIONSHIP = "update_relationship"
    DELETE_RELATIONSHIP = "delete_relationship"
    ADD_PHYSICAL_OBJECT = "add_physical_object"
    UPDATE_PHYSICAL_OBJECT = "update_physical_object"
    DELETE_PHYSICAL_OBJECT = "delete_physical_object"
    ADD_FIELD = "add_field"
    UPDATE_FIELD = "update_field"
    DELETE_FIELD = "delete_field"
    ADD_MAPPING_REF = "add_mapping_ref"
    DELETE_MAPPING_REF = "delete_mapping_ref"


class PatchOp(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    kind: PatchOpKind
    path: str
    payload: dict[str, Any] = Field(default_factory=dict)


class RejectedOp(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    code: RejectCode
    message: str
    path: str | None = None


class ModelPatch(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    profile: Profile
    ops: tuple[PatchOp, ...] = ()
    rejected: tuple[RejectedOp, ...] = ()
