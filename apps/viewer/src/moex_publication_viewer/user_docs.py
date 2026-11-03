"""User documentation build and freshness check (ADR-057)."""

from __future__ import annotations

import re
import subprocess
import sys
import tempfile
from datetime import date, datetime
from pathlib import Path
from typing import Any

import yaml

from moex_publication_viewer.assets import VIEWER_ROOT, assemble_css, assemble_js
from moex_publication_viewer.build import build_search_index
from moex_publication_viewer.models.publication_models import (
    PublicationItem,
    PublicationModule,
    PublicationSection,
)
from moex_publication_viewer.normalizers.markdown_normalizer import render_markdown
from moex_publication_viewer.package_docs import split_frontmatter
from moex_publication_viewer.renderers.html_renderer import render_viewer
from moex_publication_viewer.user_docs_generated import (
    DESCRIPTIONS_REL,
    generated_specs,
    load_descriptions,
    render_generated,
)

MODULE_ID = "user-docs"
SECTION_ID = "pages"
USER_DOCS_REL = Path("docs") / "user"
MANIFEST_NAME = "user-docs.yaml"
TOC_NAME = "toc.yaml"
GLOSSARY_NAME = "glossary.yaml"
INDEX_NAME = "index.html"
DEFERRED_CHAPTER_ID = "not-yet-told"
DEFERRED_CHAPTER_TITLE = "Что ещё не рассказано"
DEFERRED_PAGE_ID = "accepted-not-told"
DEFERRED_PAGE_TITLE = "Принятые решения без страницы"
# ADR ids on these lines do not count as page coverage (ADR-057 D4).
WHERE_TO_READ_PREFIX = "Где прочитать"

GLOSSARY_LINK_RE = re.compile(r"\[([^\]]+)\]\(glossary:([A-Za-z0-9_-]+)\)")
MD_LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
ADR_MENTION_RE = re.compile(r"\bADR-\d+\b", re.IGNORECASE)
ADR_FILE_RE = re.compile(r"^ADR-(\d+)", re.IGNORECASE)


class UserDocsError(Exception):
    """Build or check failed with one or more messages."""

    def __init__(self, errors: list[str]) -> None:
        self.errors = list(errors)
        super().__init__("; ".join(self.errors))


def user_docs_dir(root: Path) -> Path:
    return root.resolve() / USER_DOCS_REL


def index_path(root: Path) -> Path:
    return user_docs_dir(root) / INDEX_NAME


def _load_yaml(path: Path) -> Any:
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise UserDocsError([f"{path}: cannot read: {exc}"]) from exc
    except Exception as exc:
        raise UserDocsError([f"{path}: cannot parse YAML: {exc}"]) from exc
    return data


def _require_mapping(data: Any, path: Path) -> dict[str, Any]:
    if not isinstance(data, dict):
        raise UserDocsError([f"{path}: root must be a mapping"])
    return data


def replace_glossary_links(
    body: str,
    term_ids: set[str],
    *,
    module_id: str = MODULE_ID,
    section_id: str = SECTION_ID,
) -> tuple[str, list[str]]:
    """Turn ``[label](glossary:id)`` into hash links before markdown render."""
    errors: list[str] = []

    def _repl(match: re.Match[str]) -> str:
        label, term_id = match.group(1), match.group(2)
        if term_id not in term_ids:
            errors.append(f"unknown glossary term id '{term_id}'")
            return match.group(0)
        href = f"#module={module_id}&section={section_id}&item={term_id}"
        return f"[{label}]({href})"

    return GLOSSARY_LINK_RE.sub(_repl, body), errors


def _term_labels(terms: list[dict[str, Any]]) -> dict[str, str]:
    labels: dict[str, str] = {}
    for term in terms:
        tid = str(term.get("id") or "").strip()
        if not tid:
            continue
        labels[tid] = str(term.get("term") or tid).strip() or tid
    return labels


def _draft_prefix() -> str:
    return render_markdown(
        "Черновик: человек ещё не сверил этот текст с источниками.\n\n"
    )


def _parse_review_state(meta: dict[str, Any], loc: str) -> tuple[date | None, bool, list[str]]:
    """Human `verified_at` or explicit `draft: true`. Not both, and not neither."""
    errors: list[str] = []
    if "draft" in meta and meta.get("draft") is not None and not isinstance(meta.get("draft"), bool):
        errors.append(f"{loc}: draft must be true or false")
        return None, False, errors
    draft = meta.get("draft") is True
    raw = meta.get("verified_at")
    has_verified = raw is not None and str(raw).strip() != ""
    if draft and has_verified:
        errors.append(f"{loc}: draft: true cannot be combined with verified_at")
        return None, True, errors
    if not draft and not has_verified:
        errors.append(f"{loc}: set verified_at after human review, or draft: true")
        return None, False, errors
    if draft:
        return None, True, errors
    verified, ver_errors = _parse_verified_at(raw, loc)
    errors.extend(ver_errors)
    return verified, False, errors


def _adr_ids_in_text(text: str) -> set[str]:
    found: set[str] = set()
    for match in ADR_MENTION_RE.finditer(text):
        parsed = re.match(r"ADR-(\d+)$", match.group(0), re.IGNORECASE)
        if parsed:
            found.add(f"ADR-{int(parsed.group(1)):03d}")
    return found


def _body_for_adr_coverage(body: str) -> str:
    """Drop «Где прочитать…» lines; a tail link alone is not coverage."""
    lines = []
    for line in str(body or "").splitlines():
        if line.lstrip().startswith(WHERE_TO_READ_PREFIX):
            continue
        lines.append(line)
    return "\n".join(lines)


def _adr_rel_path(root: Path, adr_id: str) -> str | None:
    match = re.match(r"ADR-(\d+)$", adr_id, re.IGNORECASE)
    if not match:
        return None
    number = int(match.group(1))
    adr_dir = root.resolve() / "docs" / "adr"
    if not adr_dir.is_dir():
        return None
    matches = sorted(adr_dir.glob(f"ADR-{number:03d}*.md"))
    if not matches:
        return None
    return matches[0].relative_to(root.resolve()).as_posix()


def deferred_page_markdown(root: Path, rows: dict[str, str]) -> str:
    """Reader-facing page for ``toc.yaml`` ``not_covered``. Not a hand-written file."""
    lines = [
        f"# {DEFERRED_PAGE_TITLE}",
        "",
        "Эти решения уже приняты. На остальных страницах их ещё нет. "
        "Пока страницы нет, само решение действует: его читают в файле в `docs/adr/`.",
        "",
    ]
    for adr_id in sorted(rows, key=lambda item: int(item.split("-", 1)[1])):
        reason = rows[adr_id].strip()
        rel = _adr_rel_path(root, adr_id)
        if rel:
            lines.append(f"- [{adr_id}]({rel}) — {reason}")
        else:
            lines.append(f"- {adr_id} — {reason}")
    lines.append("")
    return "\n".join(lines)


def _insert_deferred_chapter(
    chapters: list[PublicationItem],
    root: Path,
    rows: dict[str, str],
) -> None:
    if not rows:
        return
    content = render_markdown(deferred_page_markdown(root, rows))
    page = PublicationItem(
        id=DEFERRED_PAGE_ID,
        title=DEFERRED_PAGE_TITLE,
        attributes={
            "kind": "doc_page",
            "generated_from": "toc.yaml:not_covered",
            "content": content,
        },
    )
    chapter = PublicationItem(
        id=f"group:{DEFERRED_CHAPTER_ID}",
        title=DEFERRED_CHAPTER_TITLE,
        attributes={"kind": "group", "role": "chapter"},
        children=[page],
    )
    glossary_at = next(
        (i for i, item in enumerate(chapters) if item.id == "group:glossary"),
        None,
    )
    if glossary_at is None:
        chapters.append(chapter)
    else:
        chapters.insert(glossary_at, chapter)


def _item_content_by_id(module: PublicationModule, item_id: str) -> str:
    def _walk(items: list[PublicationItem]) -> str:
        for item in items:
            if item.id == item_id:
                return str(item.attributes.get("content") or "")
            found = _walk(list(item.children))
            if found:
                return found
        return ""

    for section in module.sections:
        found = _walk(list(section.items))
        if found:
            return found
    return ""


def _deferred_visibility_errors(content: str, rows: dict[str, str]) -> list[str]:
    if not rows:
        return []
    if not content:
        return ["not_covered list is not shown on a page"]
    errors: list[str] = []
    for adr_id, reason in rows.items():
        if adr_id not in content or reason not in content:
            errors.append(
                f"{adr_id} is listed in not_covered but is not visible on the deferred page"
            )
    return errors


def _adr_ids_from_paths(paths: list[Path]) -> set[str]:
    found: set[str] = set()
    for path in paths:
        match = ADR_FILE_RE.match(path.name)
        if match:
            found.add(f"ADR-{int(match.group(1)):03d}")
    return found


def _term_page_markdown(
    term: dict[str, Any],
    term_ids: set[str],
    term_labels: dict[str, str] | None = None,
) -> tuple[str, list[str]]:
    term_id = str(term.get("id") or "").strip()
    name = str(term.get("term") or term_id).strip()
    short = str(term.get("short") or "").strip()
    explanation = str(term.get("explanation") or "").strip()
    see_also = term.get("see_also") or []
    if not isinstance(see_also, list):
        see_also = [see_also]
    labels = term_labels or {}
    errors: list[str] = []
    lines = [f"# {name}", ""]
    if short:
        lines.extend([short, ""])
    if explanation:
        lines.extend([explanation, ""])
    if see_also:
        lines.append("См. также:")
        lines.append("")
        for ref in see_also:
            rid = str(ref).strip()
            if not rid:
                continue
            if rid not in term_ids:
                errors.append(f"glossary '{term_id}': see_also unknown id '{rid}'")
                continue
            lines.append(f"- [{labels.get(rid) or rid}](glossary:{rid})")
        lines.append("")
    body = "\n".join(lines)
    body, link_errors = replace_glossary_links(body, term_ids)
    errors.extend(link_errors)
    return body, errors


def _page_html_from_markdown(
    body: str,
    term_ids: set[str],
    *,
    source_label: str,
) -> tuple[str, list[str]]:
    replaced, errors = replace_glossary_links(body, term_ids)
    if errors:
        return "", [f"{source_label}: {e}" for e in errors]
    return render_markdown(replaced), []


def _load_glossary(docs_dir: Path) -> tuple[list[dict[str, Any]], set[str], list[str]]:
    path = docs_dir / GLOSSARY_NAME
    if not path.is_file():
        return [], set(), [f"{path}: missing"]
    data = _require_mapping(_load_yaml(path), path)
    terms = data.get("terms")
    if not isinstance(terms, list):
        return [], set(), [f"{path}: terms must be a list"]
    out: list[dict[str, Any]] = []
    ids: set[str] = set()
    errors: list[str] = []
    for i, term in enumerate(terms):
        loc = f"{path}: terms[{i}]"
        if not isinstance(term, dict):
            errors.append(f"{loc}: must be a mapping")
            continue
        tid = str(term.get("id") or "").strip()
        if not tid:
            errors.append(f"{loc}: id is required")
            continue
        if tid in ids:
            errors.append(f"{loc}: duplicate id '{tid}'")
            continue
        ids.add(tid)
        out.append(term)
    return out, ids, errors


def _load_toc(docs_dir: Path) -> tuple[dict[str, Any], list[str]]:
    path = docs_dir / TOC_NAME
    if not path.is_file():
        return {}, [f"{path}: missing"]
    data = _require_mapping(_load_yaml(path), path)
    chapters = data.get("chapters")
    if not isinstance(chapters, list) or not chapters:
        return data, [f"{path}: chapters must be a non-empty list"]
    return data, []


def _load_manifest(docs_dir: Path) -> tuple[dict[str, Any], list[str]]:
    path = docs_dir / MANIFEST_NAME
    if not path.is_file():
        return {}, [f"{path}: missing"]
    data = _require_mapping(_load_yaml(path), path)
    errors: list[str] = []
    if not str(data.get("module_id") or "").strip():
        errors.append(f"{path}: module_id is required")
    if not str(data.get("title") or "").strip():
        errors.append(f"{path}: title is required")
    return data, errors


def _parse_verified_at(raw: Any, loc: str) -> tuple[date | None, list[str]]:
    text = str(raw or "").strip()
    if not text:
        return None, [f"{loc}: verified_at is required"]
    try:
        return date.fromisoformat(text), []
    except ValueError:
        return None, [f"{loc}: verified_at must be YYYY-MM-DD"]


def _validate_sources(
    sources: Any,
    *,
    root: Path,
    loc: str,
) -> tuple[list[Path], list[str]]:
    errors: list[str] = []
    if not isinstance(sources, list) or not sources:
        return [], [f"{loc}: sources must be a non-empty list"]
    resolved: list[Path] = []
    root_res = root.resolve()
    for i, src in enumerate(sources):
        rel = str(src or "").strip().replace("\\", "/")
        if not rel:
            errors.append(f"{loc}: sources[{i}] is empty")
            continue
        path = (root_res / rel).resolve()
        try:
            path.relative_to(root_res)
        except ValueError:
            errors.append(f"{loc}: sources[{i}] escapes repository root: {rel}")
            continue
        if not path.is_file():
            errors.append(f"{loc}: sources[{i}] missing file: {rel}")
            continue
        resolved.append(path)
    return resolved, errors


def _check_markdown_file_links(
    body: str,
    *,
    page_path: Path,
    root: Path,
    loc: str,
) -> list[str]:
    errors: list[str] = []
    root_res = root.resolve()
    for match in MD_LINK_RE.finditer(body):
        target = match.group(2).strip()
        if not target or target.startswith(("http://", "https://", "mailto:", "glossary:")):
            continue
        if target.startswith("#"):
            continue
        path_part = target.split("#", 1)[0]
        if not path_part:
            continue
        candidates = [
            (page_path.parent / path_part).resolve(),
            (root_res / path_part).resolve(),
        ]
        ok = False
        for candidate in candidates:
            try:
                candidate.relative_to(root_res)
            except ValueError:
                continue
            if candidate.is_file() or candidate.is_dir():
                ok = True
                break
        if not ok:
            errors.append(f"{loc}: broken link '{target}'")
    return errors


def _read_page(
    docs_dir: Path,
    page: dict[str, Any],
    *,
    root: Path,
    term_ids: set[str],
    toc_id: str,
) -> tuple[PublicationItem | None, list[str], list[str], list[Path], date | None, str, bool]:
    """Return item, errors, warnings, source paths, verified_at, body, draft."""
    errors: list[str] = []
    warnings: list[str] = []
    rel = str(page.get("path") or "").strip().replace("\\", "/")
    title = str(page.get("title") or "").strip()
    page_id = str(page.get("id") or "").strip()
    loc = f"{docs_dir / TOC_NAME}: page '{toc_id or page_id or rel}'"
    if not page_id:
        errors.append(f"{loc}: id is required")
    if page_id and toc_id and page_id != toc_id:
        errors.append(f"{loc}: id '{page_id}' does not match toc id '{toc_id}'")
    if not rel:
        errors.append(f"{loc}: path is required")
        return None, errors, warnings, [], None, "", False
    if not title:
        errors.append(f"{loc}: title is required")
    path = (docs_dir / rel).resolve()
    try:
        path.relative_to(docs_dir.resolve())
    except ValueError:
        errors.append(f"{loc}: path escapes docs/user: {rel}")
        return None, errors, warnings, [], None, "", False
    if not path.is_file():
        errors.append(f"{loc}: missing markdown '{rel}'")
        return None, errors, warnings, [], None, "", False
    try:
        raw = path.read_text(encoding="utf-8")
    except OSError as exc:
        errors.append(f"{path}: cannot read: {exc}")
        return None, errors, warnings, [], None, "", False
    meta, body = split_frontmatter(raw)
    fm_id = str(meta.get("id") or "").strip()
    if not fm_id:
        errors.append(f"{rel}: frontmatter id is required")
    elif page_id and fm_id != page_id:
        errors.append(f"{rel}: frontmatter id '{fm_id}' does not match toc id '{page_id}'")
    sources, src_errors = _validate_sources(meta.get("sources"), root=root, loc=rel)
    errors.extend(src_errors)
    verified, draft, review_errors = _parse_review_state(meta, rel)
    errors.extend(review_errors)
    errors.extend(
        _check_markdown_file_links(body, page_path=path, root=root, loc=rel)
    )
    content, link_errors = _page_html_from_markdown(body, term_ids, source_label=rel)
    errors.extend(link_errors)
    if errors:
        return None, errors, warnings, sources, verified, body, draft
    if draft:
        content = _draft_prefix() + content
    item = PublicationItem(
        id=page_id or fm_id,
        title=title or page_id or fm_id,
        attributes={
            "kind": "doc_page",
            "path": rel,
            "content": content,
            "sources": [str(s.relative_to(root.resolve()).as_posix()) for s in sources],
            "verified_at": verified.isoformat() if verified else None,
            "draft": draft,
        },
    )
    return item, errors, warnings, sources, verified, body, draft


def _glossary_items(
    terms: list[dict[str, Any]],
    term_ids: set[str],
    *,
    root: Path,
) -> tuple[list[PublicationItem], list[str], list[str], list[tuple[list[Path], date | None]]]:
    errors: list[str] = []
    warnings: list[str] = []
    items: list[PublicationItem] = []
    source_meta: list[tuple[list[Path], date | None]] = []
    labels = _term_labels(terms)
    for term in terms:
        tid = str(term.get("id") or "").strip()
        loc = f"{GLOSSARY_NAME}:{tid}"
        name = str(term.get("term") or "").strip()
        short = str(term.get("short") or "").strip()
        explanation = str(term.get("explanation") or "").strip()
        if not name:
            errors.append(f"{loc}: term is required")
        if not short:
            errors.append(f"{loc}: short is required")
        if not explanation:
            errors.append(f"{loc}: explanation is required")
        sources, src_errors = _validate_sources(term.get("sources"), root=root, loc=loc)
        errors.extend(src_errors)
        verified, draft, review_errors = _parse_review_state(term, loc)
        errors.extend(review_errors)
        md, md_errors = _term_page_markdown(term, term_ids, labels)
        errors.extend([f"{loc}: {e}" for e in md_errors])
        if md_errors or src_errors or review_errors or not name:
            source_meta.append((sources, None))
            continue
        content = render_markdown(md)
        if draft:
            content = _draft_prefix() + content
        items.append(
            PublicationItem(
                id=tid,
                title=name,
                description=short,
                attributes={
                    "kind": "doc_page",
                    "content": content,
                    "short": short,
                    "sources": [
                        str(s.relative_to(root.resolve()).as_posix()) for s in sources
                    ],
                    "verified_at": verified.isoformat() if verified else None,
                    "draft": draft,
                },
            )
        )
        source_meta.append((sources, verified))
    return items, errors, warnings, source_meta


def _prepare_generated(
    root: Path,
    toc: dict[str, Any],
) -> tuple[dict[str, str], list[str], list[str]]:
    """Markdown for ``generated:`` pages, plus errors and warnings."""
    specs = generated_specs(toc)
    errors: list[str] = []
    warnings: list[str] = []
    path = root.resolve() / DESCRIPTIONS_REL
    groups: dict[str, dict[str, str]] | None = None
    state = "absent"
    if path.is_file():
        raw, groups, load_errors = load_descriptions(path)
        errors.extend(load_errors)
        if raw is None:
            state = "broken"
        else:
            state = "ready"
            _verified, draft, review_errors = _parse_review_state(
                raw, DESCRIPTIONS_REL.as_posix()
            )
            errors.extend(review_errors)
            if draft and not review_errors:
                warnings.append(
                    f"{DESCRIPTIONS_REL.as_posix()}: draft, verified_at is not set"
                )
    markdown, gen_errors = render_generated(
        root,
        specs,
        groups,
        descriptions_state=state,
    )
    errors.extend(gen_errors)
    return markdown, errors, warnings


def _generated_item(
    page: dict[str, Any],
    markdown: str,
    *,
    docs_dir: Path,
    root: Path,
    term_ids: set[str],
) -> tuple[PublicationItem | None, list[str]]:
    errors: list[str] = []
    page_id = str(page.get("id") or "").strip()
    title = str(page.get("title") or "").strip()
    kind = str(page.get("generated") or "").strip()
    loc = f"{docs_dir / TOC_NAME}: page '{page_id or kind}'"
    errors.extend(
        _check_markdown_file_links(
            markdown,
            page_path=docs_dir / TOC_NAME,
            root=root,
            loc=loc,
        )
    )
    content, link_errors = _page_html_from_markdown(
        markdown, term_ids, source_label=loc
    )
    errors.extend(link_errors)
    if errors:
        return None, errors
    item = PublicationItem(
        id=page_id or kind,
        title=title or page_id or kind,
        attributes={
            "kind": "doc_page",
            "generated": kind,
            "content": content,
            "sources": [],
            "verified_at": None,
            "draft": False,
        },
    )
    return item, errors


def compile_user_docs_module(root: Path) -> PublicationModule:
    """Compile docs/user into a single PublicationModule. Raises UserDocsError."""
    root = root.resolve()
    docs_dir = user_docs_dir(root)
    errors: list[str] = []
    if not docs_dir.is_dir():
        raise UserDocsError([f"{docs_dir}: missing directory"])

    manifest, man_errors = _load_manifest(docs_dir)
    errors.extend(man_errors)
    toc, toc_errors = _load_toc(docs_dir)
    errors.extend(toc_errors)
    terms, term_ids, gloss_errors = _load_glossary(docs_dir)
    errors.extend(gloss_errors)
    not_covered, nc_errors = _not_covered_map(toc)
    errors.extend(nc_errors)
    if errors:
        raise UserDocsError(errors)

    chapters_out: list[PublicationItem] = []
    entry_html = ""
    bodies_for_scan: list[str] = []
    generated_md, gen_errors, _gen_warnings = _prepare_generated(root, toc)
    errors.extend(gen_errors)

    for chapter in toc.get("chapters") or []:
        if not isinstance(chapter, dict):
            errors.append(f"{TOC_NAME}: chapter must be a mapping")
            continue
        ch_id = str(chapter.get("id") or "").strip()
        ch_title = str(chapter.get("title") or "").strip()
        if not ch_id or not ch_title:
            errors.append(f"{TOC_NAME}: chapter id and title are required")
            continue
        children: list[PublicationItem] = []
        if ch_id == "glossary":
            g_items, g_errors, _g_warn, _meta = _glossary_items(
                terms, term_ids, root=root
            )
            errors.extend(g_errors)
            children.extend(g_items)
            for term in terms:
                bodies_for_scan.append(str(term.get("explanation") or ""))
                bodies_for_scan.append(str(term.get("short") or ""))
        else:
            pages = chapter.get("pages") or []
            if not isinstance(pages, list):
                errors.append(f"{TOC_NAME}: chapter '{ch_id}' pages must be a list")
                continue
            for page in pages:
                if not isinstance(page, dict):
                    errors.append(f"{TOC_NAME}: page must be a mapping")
                    continue
                toc_id = str(page.get("id") or "").strip()
                if "generated" in page:
                    body = generated_md.get(toc_id, "")
                    if not body:
                        continue
                    item, page_errors = _generated_item(
                        page,
                        body,
                        docs_dir=docs_dir,
                        root=root,
                        term_ids=term_ids,
                    )
                    errors.extend(page_errors)
                    if item is not None:
                        children.append(item)
                        if not entry_html:
                            entry_html = str(item.attributes.get("content") or "")
                    continue
                item, page_errors, _warn, _sources, _verified, body, _draft = _read_page(
                    docs_dir,
                    page,
                    root=root,
                    term_ids=term_ids,
                    toc_id=toc_id,
                )
                errors.extend(page_errors)
                bodies_for_scan.append(body)
                if item is not None:
                    children.append(item)
                    if not entry_html:
                        entry_html = str(item.attributes.get("content") or "")
        chapters_out.append(
            PublicationItem(
                id=f"group:{ch_id}",
                title=ch_title,
                attributes={"kind": "group", "role": "chapter"},
                children=children,
            )
        )

    if errors:
        raise UserDocsError(errors)
    _insert_deferred_chapter(chapters_out, root, not_covered)

    module_id = str(manifest.get("module_id") or MODULE_ID).strip()
    title = str(manifest.get("title") or "Документация продукта").strip()
    description = str(manifest.get("description") or "").strip() or None

    section = PublicationSection(
        id=SECTION_ID,
        title=str(manifest.get("section_title") or "Страницы"),
        type="markdown-doc",
        kind="documentation",
        items=chapters_out,
        content=entry_html,
        attributes={
            "page_count": sum(len(c.children) for c in chapters_out),
            "scan_text": "\n".join(bodies_for_scan),
        },
    )
    return PublicationModule(
        module_id=module_id,
        title=title,
        description=description,
        icon=str(manifest.get("icon") or "").strip() or None,
        order=int(manifest.get("order") or 0),
        sections=[section],
        manifest_path=str((docs_dir / MANIFEST_NAME).relative_to(root).as_posix()),
    )


def build_user_docs(root: Path, out_path: Path | None = None) -> Path:
    """Build docs/user/index.html. Does not call the main publication build()."""
    root = root.resolve()
    module = compile_user_docs_module(root)
    modules = [module]
    search_index = build_search_index(modules)
    css_text = assemble_css()
    js_text = assemble_js()
    html = render_viewer(
        modules,
        search_index,
        VIEWER_ROOT,
        catalog=None,
        inline_css=css_text,
        inline_js=js_text,
    )
    target = out_path if out_path is not None else index_path(root)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(html, encoding="utf-8", newline="\n")
    return target


def list_accepted_adr_ids(root: Path) -> list[str]:
    adr_dir = root.resolve() / "docs" / "adr"
    ids: list[str] = []
    if not adr_dir.is_dir():
        return ids
    for path in sorted(adr_dir.glob("ADR-*.md")):
        try:
            raw = path.read_text(encoding="utf-8")
        except OSError:
            continue
        meta, _body = split_frontmatter(raw)
        if str(meta.get("status") or "").strip() != "Accepted":
            continue
        match = ADR_FILE_RE.match(path.stem)
        if not match:
            continue
        ids.append(f"ADR-{int(match.group(1)):03d}")
    return ids


def _not_covered_map(toc: dict[str, Any]) -> tuple[dict[str, str], list[str]]:
    errors: list[str] = []
    raw = toc.get("not_covered") or []
    if raw is None:
        raw = []
    if not isinstance(raw, list):
        return {}, [f"{TOC_NAME}: not_covered must be a list"]
    out: dict[str, str] = {}
    for i, row in enumerate(raw):
        loc = f"{TOC_NAME}: not_covered[{i}]"
        if not isinstance(row, dict):
            errors.append(f"{loc}: must be a mapping")
            continue
        adr = str(row.get("adr") or "").strip().upper()
        reason = str(row.get("reason") or "").strip()
        if not adr:
            errors.append(f"{loc}: adr is required")
            continue
        match = re.match(r"ADR-(\d+)$", adr, re.IGNORECASE)
        if match:
            adr = f"ADR-{int(match.group(1)):03d}"
        if not reason:
            errors.append(f"{loc}: reason is required for {adr}")
            continue
        if re.search(r"\bPR-\d+\b", reason, re.IGNORECASE):
            errors.append(
                f"{loc}: reason for {adr} must describe the product, not a future PR"
            )
            continue
        out[adr] = reason
    return out, errors


def _collect_page_records(
    root: Path,
) -> tuple[
    dict[str, Any],
    list[dict[str, Any]],
    list[str],
    list[str],
]:
    """Load toc + page/glossary records for check without full HTML build."""
    docs_dir = user_docs_dir(root)
    errors: list[str] = []
    warnings: list[str] = []
    toc, toc_errors = _load_toc(docs_dir)
    errors.extend(toc_errors)
    terms, term_ids, gloss_errors = _load_glossary(docs_dir)
    errors.extend(gloss_errors)
    if errors:
        return toc, [], errors, warnings

    generated_md, gen_errors, gen_warnings = _prepare_generated(root, toc)
    errors.extend(gen_errors)
    warnings.extend(gen_warnings)

    records: list[dict[str, Any]] = []
    for chapter in toc.get("chapters") or []:
        if not isinstance(chapter, dict):
            continue
        ch_id = str(chapter.get("id") or "").strip()
        if ch_id == "glossary":
            for term in terms:
                tid = str(term.get("id") or "").strip()
                loc = f"{GLOSSARY_NAME}:{tid}"
                sources, src_errors = _validate_sources(
                    term.get("sources"), root=root, loc=loc
                )
                errors.extend(src_errors)
                verified, draft, review_errors = _parse_review_state(term, loc)
                errors.extend(review_errors)
                see_also = term.get("see_also") or []
                if not isinstance(see_also, list):
                    see_also = [see_also]
                for ref in see_also:
                    rid = str(ref).strip()
                    if rid and rid not in term_ids:
                        errors.append(f"{loc}: see_also unknown id '{rid}'")
                body = "\n".join(
                    [
                        str(term.get("term") or ""),
                        str(term.get("short") or ""),
                        str(term.get("explanation") or ""),
                    ]
                )
                records.append(
                    {
                        "kind": "term",
                        "id": tid,
                        "body": body,
                        "sources": sources,
                        "verified_at": verified,
                        "draft": draft,
                        "path": docs_dir / GLOSSARY_NAME,
                    }
                )
            continue
        for page in chapter.get("pages") or []:
            if not isinstance(page, dict):
                continue
            toc_id = str(page.get("id") or "").strip()
            if "generated" in page:
                records.append(
                    {
                        "kind": "generated",
                        "id": toc_id,
                        "body": generated_md.get(toc_id, ""),
                        "sources": [],
                        "verified_at": None,
                        "draft": False,
                        "generated": True,
                        "path": docs_dir / TOC_NAME,
                        "ok": toc_id in generated_md,
                    }
                )
                continue
            item, page_errors, page_warnings, sources, verified, body, draft = _read_page(
                docs_dir,
                page,
                root=root,
                term_ids=term_ids,
                toc_id=toc_id,
            )
            errors.extend(page_errors)
            warnings.extend(page_warnings)
            # Still record body for ADR scan when possible
            records.append(
                {
                    "kind": "page",
                    "id": toc_id,
                    "body": body,
                    "sources": sources,
                    "verified_at": verified,
                    "draft": draft,
                    "path": (docs_dir / str(page.get("path") or "")),
                    "ok": item is not None,
                }
            )
    return toc, records, errors, warnings


def _git_commit_date(root: Path, path: Path) -> date | None:
    try:
        proc = subprocess.run(
            [
                "git",
                "-C",
                str(root),
                "log",
                "-1",
                "--format=%cI",
                "--",
                str(path),
            ],
            check=False,
            capture_output=True,
            text=True,
        )
    except OSError:
        return None
    if proc.returncode != 0:
        return None
    text = (proc.stdout or "").strip()
    if not text:
        return None
    try:
        return datetime.fromisoformat(text).date()
    except ValueError:
        return None


def check_user_docs(root: Path) -> tuple[list[str], list[str]]:
    """Validate sources, links, ADR coverage, and committed HTML freshness."""
    root = root.resolve()
    errors: list[str] = []
    warnings: list[str] = []

    docs_dir = user_docs_dir(root)
    if not docs_dir.is_dir():
        return [f"{docs_dir}: missing directory"], warnings

    _manifest, man_errors = _load_manifest(docs_dir)
    errors.extend(man_errors)

    toc, records, collect_errors, collect_warnings = _collect_page_records(root)
    errors.extend(collect_errors)
    warnings.extend(collect_warnings)

    not_covered, nc_errors = _not_covered_map(toc)
    errors.extend(nc_errors)

    if not_covered and not errors:
        try:
            module = compile_user_docs_module(root)
        except UserDocsError as exc:
            errors.extend(exc.errors)
        else:
            content = _item_content_by_id(module, DEFERRED_PAGE_ID)
            errors.extend(_deferred_visibility_errors(content, not_covered))

    scan_blob = "\n".join(
        _body_for_adr_coverage(str(r.get("body") or ""))
        for r in records
        if not r.get("generated") and r.get("kind") != "term"
    )
    mentioned = {m.group(0).upper() for m in ADR_MENTION_RE.finditer(scan_blob)}
    mentioned_norm = set()
    for mid in mentioned:
        match = re.match(r"ADR-(\d+)$", mid, re.IGNORECASE)
        if match:
            mentioned_norm.add(f"ADR-{int(match.group(1)):03d}")

    for adr_id in list_accepted_adr_ids(root):
        if adr_id in mentioned_norm:
            continue
        if adr_id in not_covered:
            continue
        errors.append(
            f"Accepted {adr_id} is not mentioned in docs/user pages and not listed "
            f"in toc.yaml not_covered"
        )

    for record in records:
        if record.get("draft"):
            warnings.append(f"{record.get('id')}: draft, verified_at is not set")
        if record.get("generated"):
            continue
        mentioned_here = _adr_ids_in_text(str(record.get("body") or ""))
        in_sources = _adr_ids_from_paths(record.get("sources") or [])
        for adr_id in sorted(mentioned_here - in_sources):
            warnings.append(
                f"{record.get('id')}: mentions {adr_id} but it is not in sources"
            )

    git_ok = True
    try:
        probe = subprocess.run(
            ["git", "-C", str(root), "rev-parse", "--is-inside-work-tree"],
            check=False,
            capture_output=True,
            text=True,
        )
        if probe.returncode != 0:
            git_ok = False
    except OSError:
        git_ok = False
    if not git_ok:
        warnings.append("git unavailable; skipping verified_at freshness warnings")
    else:
        for record in records:
            if record.get("draft"):
                continue
            verified: date | None = record.get("verified_at")
            if verified is None:
                continue
            for src in record.get("sources") or []:
                commit_day = _git_commit_date(root, src)
                if commit_day is None:
                    continue
                if commit_day > verified:
                    rel = src.relative_to(root).as_posix()
                    warnings.append(
                        f"{record.get('id')}: source {rel} changed in git after "
                        f"verified_at {verified.isoformat()} ({commit_day.isoformat()})"
                    )

    # Fresh HTML must match committed index.html
    committed = index_path(root)
    if not committed.is_file():
        errors.append(f"{committed}: missing; run build-user-docs and commit the result")
    elif not errors:
        # Only compare when sources already compile
        try:
            with tempfile.TemporaryDirectory(prefix="user-docs-check-") as tmp:
                fresh = Path(tmp) / INDEX_NAME
                build_user_docs(root, out_path=fresh)
                left = committed.read_text(encoding="utf-8").replace("\r\n", "\n")
                right = fresh.read_text(encoding="utf-8").replace("\r\n", "\n")
                if left != right:
                    errors.append(
                        f"{committed}: does not match a fresh build; "
                        "run build-user-docs and commit docs/user/index.html"
                    )
        except UserDocsError as exc:
            errors.extend(exc.errors)

    return errors, warnings


def main_build(argv: list[str] | None = None) -> int:
    import argparse

    parser = argparse.ArgumentParser(prog="build-user-docs")
    parser.add_argument("--root", type=Path, default=Path.cwd())
    args = parser.parse_args(argv)
    try:
        out = build_user_docs(args.root)
    except UserDocsError as exc:
        print("build-user-docs failed:", file=sys.stderr)
        for err in exc.errors:
            print(f"  - {err}", file=sys.stderr)
        return 1
    print(f"Wrote {out}")
    return 0


def main_check(argv: list[str] | None = None) -> int:
    import argparse

    parser = argparse.ArgumentParser(prog="check-user-docs")
    parser.add_argument("--root", type=Path, default=Path.cwd())
    args = parser.parse_args(argv)
    errors, warnings = check_user_docs(args.root)
    for warning in warnings:
        print(f"warning: {warning}", file=sys.stderr)
    if errors:
        print("check-user-docs failed:", file=sys.stderr)
        for err in errors:
            print(f"  - {err}", file=sys.stderr)
        return 1
    print("check-user-docs OK")
    return 0
