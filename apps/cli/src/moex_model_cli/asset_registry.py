"""Filesystem ImplementationCatalog over model-assets/implementations/**/implementation.yaml."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

import yaml

from moex_model_cli.bootstrap import (
    find_repo_root,
    resolve_body_from_implementation_envelope,
    resolve_schema_from_specification_envelope,
)
from moex_modeling.assets.domain import (
    AssetResolutionError,
    ImplementationAsset,
    ImplementationNotFound,
    PublicationTarget,
    slug_and_version_from_id,
)

logger = logging.getLogger(__name__)

IMPLEMENTATIONS_REL = Path("model-assets") / "implementations"
ENVELOPE_NAME = "implementation.yaml"
PUBLISH_NAME = "publish.yaml"


def _load_yaml(path: Path) -> dict[str, Any]:
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError(f"expected mapping in {path}")
    return raw


def _ensure_under_root(path: Path, root: Path, *, label: str) -> Path:
    resolved = path.resolve()
    root_resolved = root.resolve()
    try:
        resolved.relative_to(root_resolved)
    except ValueError as exc:
        raise AssetResolutionError(
            f"{label} escapes repository root: {resolved}"
        ) from exc
    return resolved


def _optional_str(data: dict[str, Any], key: str) -> str | None:
    value = data.get(key)
    if value is None:
        return None
    text = str(value).strip()
    return text or None


class CatalogBuildError(RuntimeError):
    """Duplicate id/slug or fatal registry construction failure."""


class FilesystemImplementationCatalog:
    """Scan envelopes once; resolve by coordinate or presentation slug."""

    def __init__(self, root: Path | None = None) -> None:
        self._root = find_repo_root(root) if root is None else root.resolve()
        self._by_id: dict[str, ImplementationAsset] = {}
        self._by_slug: dict[str, ImplementationAsset] = {}
        self._ordered: list[ImplementationAsset] = []
        self._build()

    @property
    def root(self) -> Path:
        return self._root

    def list(self) -> tuple[ImplementationAsset, ...]:
        return tuple(self._ordered)

    def resolve(self, token: str) -> ImplementationAsset:
        key = (token or "").strip()
        if not key:
            raise ImplementationNotFound("empty implementation token")
        asset = self._by_id.get(key) or self._by_slug.get(key)
        if asset is None:
            raise ImplementationNotFound(f"unknown implementation: {token}")
        return asset

    def load_body(self, token: str) -> str:
        asset = self.resolve(token)
        path = _ensure_under_root(asset.body_path, self._root, label="body_path")
        if not path.is_file():
            raise AssetResolutionError(f"implementation body not found: {path}")
        return path.read_text(encoding="utf-8")

    def resolve_schema(self, token: str) -> Path:
        asset = self.resolve(token)
        if asset.specification_envelope_path is None:
            raise AssetResolutionError(
                f"{asset.id}: missing specification_envelope (cannot resolve schema)"
            )
        spec_env = _ensure_under_root(
            asset.specification_envelope_path,
            self._root,
            label="specification_envelope",
        )
        try:
            schema = resolve_schema_from_specification_envelope(spec_env)
        except (OSError, ValueError, FileNotFoundError) as exc:
            raise AssetResolutionError(str(exc)) from exc
        return _ensure_under_root(schema, self._root, label="schema_path")

    def publication_target(self, token: str) -> PublicationTarget:
        asset = self.resolve(token)
        body = _ensure_under_root(asset.body_path, self._root, label="body_path")
        try:
            rel = body.relative_to(self._root).as_posix()
        except ValueError as exc:
            raise AssetResolutionError(
                f"body_path escapes repository root: {body}"
            ) from exc
        return PublicationTarget(
            repo_path=rel,
            manifest_path=asset.publication_manifest_path,
        )

    def _build(self) -> None:
        base = self._root / IMPLEMENTATIONS_REL
        if not base.is_dir():
            return
        for envelope in sorted(base.rglob(ENVELOPE_NAME)):
            if not envelope.is_file():
                continue
            try:
                asset = self._load_asset(envelope)
            except CatalogBuildError:
                raise
            except Exception as exc:  # noqa: BLE001 — skip broken envelopes
                logger.warning("skipping envelope %s: %s", envelope, exc)
                continue
            if asset.id in self._by_id:
                raise CatalogBuildError(
                    f"duplicate implementation id {asset.id!r}: "
                    f"{self._by_id[asset.id].envelope_path} and {asset.envelope_path}"
                )
            if asset.slug in self._by_slug:
                raise CatalogBuildError(
                    f"duplicate implementation slug {asset.slug!r}: "
                    f"{self._by_slug[asset.slug].envelope_path} and {asset.envelope_path}"
                )
            self._by_id[asset.id] = asset
            self._by_slug[asset.slug] = asset
            self._ordered.append(asset)

    def _load_asset(self, envelope_path: Path) -> ImplementationAsset:
        data = _load_yaml(envelope_path)
        impl_id = _optional_str(data, "id")
        if not impl_id:
            raise ValueError(f"{envelope_path}: missing id")
        try:
            slug, version_from_id = slug_and_version_from_id(impl_id)
        except ValueError as exc:
            raise ValueError(f"{envelope_path}: {exc}") from exc
        version = _optional_str(data, "version") or version_from_id
        title = (
            _optional_str(data, "name")
            or _optional_str(data, "title")
            or impl_id
        )
        kind = _optional_str(data, "implementation_kind") or ""
        profile = _optional_str(data, "implementation_profile")
        level = _optional_str(data, "dams_model_level")

        try:
            body_path = resolve_body_from_implementation_envelope(envelope_path)
        except (OSError, ValueError, FileNotFoundError) as exc:
            raise ValueError(str(exc)) from exc
        body_path = _ensure_under_root(body_path, self._root, label="body_path")

        spec_rel = _optional_str(data, "specification_envelope")
        spec_path: Path | None = None
        if spec_rel:
            candidate = (envelope_path.parent / spec_rel).resolve()
            if candidate.is_file():
                spec_path = _ensure_under_root(
                    candidate, self._root, label="specification_envelope"
                )

        publish = envelope_path.parent / PUBLISH_NAME
        publish_path = (
            _ensure_under_root(publish, self._root, label="publish.yaml")
            if publish.is_file()
            else None
        )

        return ImplementationAsset(
            id=impl_id,
            slug=slug,
            title=title,
            version=version,
            implementation_kind=kind,
            implementation_profile=profile,
            dams_model_level=level,
            envelope_path=_ensure_under_root(
                envelope_path, self._root, label="envelope_path"
            ),
            body_path=body_path,
            specification_envelope_path=spec_path,
            publication_manifest_path=publish_path,
        )


__all__ = [
    "CatalogBuildError",
    "FilesystemImplementationCatalog",
]
