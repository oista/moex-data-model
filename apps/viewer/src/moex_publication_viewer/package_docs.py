"""Owner-authored package docs: toc.yaml contract + markdown tree (ADR-028)."""

from __future__ import annotations

import logging
import re
from pathlib import Path
from typing import Any

import yaml

from moex_publication_viewer.models.manifest_models import ManifestSection
from moex_publication_viewer.models.publication_models import PublicationItem, PublicationSection
from moex_publication_viewer.normalizers.base import NormalizeError
from moex_publication_viewer.normalizers.helpers import section_meta
from moex_publication_viewer.normalizers.markdown_normalizer import render_markdown

logger = logging.getLogger(__name__)

CONSUMER_CONTEXT = "consumer-context.md"
TOC_NAME = "toc.yaml"
ADR_DIR = "adr"

ALLOWED_AUDIENCES = frozenset({"human", "agent", "both"})
ALLOWED_ROLES = frozenset({"contract", "explanation", "how-to", "example", "decision"})
ALLOWED_ADR_STATUS = frozenset({"proposed", "accepted", "superseded"})
ALLOWED_CHANGE_CLASS = frozenset({"breaking", "compatible", "governance", "modeling"})
REQUIRED_ADR_FIELDS = (
    "id",
    "title",
    "date",
    "status",
    "model_revision",
    "change_class",
)
BARE_PLATFORM_ADR = re.compile(r"^ADR-\d+$", re.IGNORECASE)


def split_frontmatter(raw: str) -> tuple[dict[str, Any], str]:
    """Return (frontmatter, body) for optional YAML ``---`` fence."""
    if not raw.startswith("---"):
        return {}, raw
    parts = raw.split("---", 2)
    if len(parts) < 3:
        return {}, raw
    meta = yaml.safe_load(parts[1]) or {}
    if not isinstance(meta, dict):
        return {}, parts[2].lstrip("\n")
    return meta, parts[2].lstrip("\n")


def _posix(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def _load_toc(docs_dir: Path) -> tuple[dict[str, Any] | None, list[str]]:
    toc_path = docs_dir / TOC_NAME
    if not toc_path.is_file():
        return None, [f"{toc_path}: missing {TOC_NAME}"]
    try:
        data = yaml.safe_load(toc_path.read_text(encoding="utf-8"))
    except Exception as exc:
        return None, [f"{toc_path}: cannot parse YAML: {exc}"]
    if not isinstance(data, dict):
        return None, [f"{toc_path}: root must be a mapping"]
    return data, []


def validate_package_docs(docs_dir: Path) -> tuple[list[str], list[str]]:
    """Validate ``docs/toc.yaml`` plus reserved ``docs/adr/`` records."""
    errors: list[str] = []
    warnings: list[str] = []
    toc, load_errors = _load_toc(docs_dir)
    errors.extend(load_errors)
    if toc is None:
        return errors, warnings

    pages = toc.get("pages")
    if not isinstance(pages, list) or not pages:
        errors.append(f"{docs_dir / TOC_NAME}: pages must be a non-empty list")
        pages = []

    entry = toc.get("entry_for_agents")
    if not isinstance(entry, str) or not entry.strip():
        errors.append(f"{docs_dir / TOC_NAME}: entry_for_agents is required")
        entry = ""

    listed: dict[str, dict[str, Any]] = {}
    for i, page in enumerate(pages):
        loc = f"{docs_dir / TOC_NAME}: pages[{i}]"
        if not isinstance(page, dict):
            errors.append(f"{loc}: must be a mapping")
            continue
        page_id = str(page.get("id") or "").strip()
        rel = str(page.get("path") or "").strip()
        title = str(page.get("title") or "").strip()
        audience = str(page.get("audience") or "").strip()
        role = str(page.get("role") or "").strip()
        if not page_id:
            errors.append(f"{loc}: id is required")
        if not rel:
            errors.append(f"{loc}: path is required")
            continue
        if not title:
            errors.append(f"{loc}: title is required")
        if audience not in ALLOWED_AUDIENCES:
            errors.append(f"{loc}: audience must be one of {sorted(ALLOWED_AUDIENCES)}")
        if role not in ALLOWED_ROLES:
            errors.append(f"{loc}: role must be one of {sorted(ALLOWED_ROLES)}")
        if rel in listed:
            errors.append(f"{loc}: duplicate path '{rel}'")
        listed[rel] = page
        target = (docs_dir / rel).resolve()
        try:
            target.relative_to(docs_dir.resolve())
        except ValueError:
            errors.append(f"{loc}: path '{rel}' escapes docs/")
            continue
        if not target.is_file():
            errors.append(f"{docs_dir / TOC_NAME}: missing path '{rel}'")

    if CONSUMER_CONTEXT not in listed or not (docs_dir / CONSUMER_CONTEXT).is_file():
        errors.append(f"{docs_dir / CONSUMER_CONTEXT}: required when package docs are present")
    elif str(listed[CONSUMER_CONTEXT].get("role") or "") != "contract":
        errors.append(f"{docs_dir / TOC_NAME}: {CONSUMER_CONTEXT} must have role: contract")

    if entry and entry not in listed:
        errors.append(f"{docs_dir / TOC_NAME}: entry_for_agents '{entry}' is not a listed page")

    md_files = {
        _posix(p, docs_dir)
        for p in docs_dir.rglob("*.md")
        if p.is_file()
    }
    for rel in sorted(md_files - set(listed)):
        if rel.startswith(f"{ADR_DIR}/"):
            errors.append(f"{docs_dir / rel}: model ADR must be listed in {TOC_NAME}")
        else:
            warnings.append(f"{docs_dir / rel}: markdown file is not listed in {TOC_NAME}")

    adr_root = docs_dir / ADR_DIR
    if adr_root.is_dir():
        for adr_path in sorted(adr_root.rglob("*.md")):
            rel = _posix(adr_path, docs_dir)
            page = listed.get(rel)
            if page is not None and str(page.get("role") or "") != "decision":
                errors.append(f"{docs_dir / TOC_NAME}: '{rel}' must have role: decision")
            try:
                raw = adr_path.read_text(encoding="utf-8")
            except OSError as exc:
                errors.append(f"{adr_path}: cannot read: {exc}")
                continue
            meta, _body = split_frontmatter(raw)
            if not meta:
                errors.append(f"{rel}: model ADR requires YAML frontmatter")
                continue
            missing = [f for f in REQUIRED_ADR_FIELDS if not str(meta.get(f) or "").strip()]
            if missing:
                errors.append(f"{rel}: missing frontmatter fields: {', '.join(missing)}")
            status = str(meta.get("status") or "").strip()
            if status and status not in ALLOWED_ADR_STATUS:
                errors.append(f"{rel}: status must be one of {sorted(ALLOWED_ADR_STATUS)}")
            change = str(meta.get("change_class") or "").strip()
            if change and change not in ALLOWED_CHANGE_CLASS:
                errors.append(
                    f"{rel}: change_class must be one of {sorted(ALLOWED_CHANGE_CLASS)}"
                )
            adr_id = str(meta.get("id") or "").strip()
            if adr_id and BARE_PLATFORM_ADR.match(adr_id):
                errors.append(
                    f"{rel}: id '{adr_id}' collides with platform docs/adr/; "
                    "use a package-scoped id"
                )
            if status == "superseded" and not str(meta.get("superseded_by") or "").strip():
                errors.append(f"{rel}: status superseded requires superseded_by")

    return errors, warnings


def _page_item(page: dict[str, Any], docs_dir: Path) -> PublicationItem:
    rel = str(page["path"])
    raw = (docs_dir / rel).read_text(encoding="utf-8")
    _meta, body = split_frontmatter(raw)
    html = render_markdown(body)
    applies = page.get("applies_to") or []
    if not isinstance(applies, list):
        applies = [applies]
    return PublicationItem(
        id=str(page["id"]),
        title=str(page.get("title") or page["id"]),
        attributes={
            "path": rel,
            "audience": page.get("audience"),
            "role": page.get("role"),
            "applies_to": [str(a) for a in applies],
            "content": html,
            "kind": "doc_page",
        },
    )


def build_doc_items(docs_dir: Path, toc: dict[str, Any]) -> tuple[list[PublicationItem], str]:
    """Build TOC items (Decisions grouped) and HTML for ``entry_for_agents``."""
    pages = [p for p in toc.get("pages") or [] if isinstance(p, dict)]
    entry = str(toc.get("entry_for_agents") or CONSUMER_CONTEXT)
    entry_html = ""
    leading: list[PublicationItem] = []
    decisions: list[PublicationItem] = []
    for page in pages:
        item = _page_item(page, docs_dir)
        if str(page.get("path") or "") == entry:
            entry_html = str(item.attributes.get("content") or "")
        if str(page.get("role") or "") == "decision":
            decisions.append(item)
        else:
            leading.append(item)
    items = list(leading)
    if decisions:
        items.append(
            PublicationItem(
                id="group:decisions",
                title="Decisions",
                description="Model ADR records for this package.",
                attributes={"kind": "group", "role": "decision"},
                children=decisions,
            )
        )
    return items, entry_html


class PackageDocsNormalizer:
    """Normalize ``docs/toc.yaml`` into a markdown-doc section with a page tree."""

    def normalize(self, section: ManifestSection, source_path: Path) -> PublicationSection:
        docs_dir = source_path.parent
        errors, warnings = validate_package_docs(docs_dir)
        for warning in warnings:
            logger.warning("%s", warning)
        if errors:
            raise NormalizeError("; ".join(errors))
        toc, load_errors = _load_toc(docs_dir)
        if toc is None:
            raise NormalizeError("; ".join(load_errors))
        items, entry_html = build_doc_items(docs_dir, toc)
        return PublicationSection(
            **section_meta(section),
            items=items,
            content=entry_html,
            attributes={
                "entry_for_agents": toc.get("entry_for_agents"),
                "page_count": sum(1 for p in toc.get("pages") or [] if isinstance(p, dict)),
            },
        )
