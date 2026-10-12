"""Frozen pydantic models mirroring moex-repository-manifest LinkML (drift-tested)."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class DocumentRef(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    id: str
    kind: Literal["package"]
    path: str
    version: str
    owner: str
    depends_on: tuple[str, ...] = ()


class RepositoryManifest(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    manifest_schema_version: str
    repository_id: str
    documents: tuple[DocumentRef, ...] = Field(min_length=1)


class RepositoryLockHeader(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    lock_schema_version: str


class RepositoryLockEntry(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    id: str
    content_hash: str


class LoadedDocument(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    ref: DocumentRef
    descriptor: dict
    body: dict
    content_hash: str
