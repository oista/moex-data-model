"""Explorer breadcrumb trail from PublicationItem ancestor chains.

UI mirrors this rule in ``viewer.js`` (``explorerCrumbPath``). Keep both in sync.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel

from moex_publication_viewer.models.publication_models import (
    ExplorerItemKind,
    PublicationItem,
)

CrumbKind = ExplorerItemKind | Literal["module", "unknown"]


class CrumbSegment(BaseModel):
    id: str
    title: str
    kind: CrumbKind


def _item_kind(item: PublicationItem) -> CrumbKind:
    raw = (item.attributes or {}).get("kind")
    if isinstance(raw, str) and raw:
        return raw  # type: ignore[return-value]
    return "unknown"


def _label(item: PublicationItem) -> str:
    return (item.title or item.id or "").strip()


def explorer_crumb(
    module_title: str,
    ancestors: list[PublicationItem],
    item: PublicationItem,
    *,
    module_id: str = "",
) -> list[CrumbSegment]:
    """Build breadcrumb segments: module + every ancestor + item.

    Consecutive duplicate titles are collapsed (e.g. Overview group wrapping
    an Overview section_ref). Empty labels are skipped.
    """
    segments: list[CrumbSegment] = []

    def push(seg: CrumbSegment) -> None:
        title = (seg.title or "").strip()
        if not title:
            return
        if segments and segments[-1].title == title:
            return
        segments.append(seg.model_copy(update={"title": title}))

    push(
        CrumbSegment(
            id=module_id or "module",
            title=(module_title or "").strip(),
            kind="module",
        )
    )
    for anc in ancestors or []:
        push(
            CrumbSegment(
                id=anc.id,
                title=_label(anc),
                kind=_item_kind(anc),
            )
        )
    push(
        CrumbSegment(
            id=item.id,
            title=_label(item),
            kind=_item_kind(item),
        )
    )
    return segments


def explorer_crumb_text(
    module_title: str,
    ancestors: list[PublicationItem],
    item: PublicationItem,
    *,
    module_id: str = "",
) -> str:
    """Joined trail for assertions and non-HTML consumers."""
    return " / ".join(
        s.title for s in explorer_crumb(module_title, ancestors, item, module_id=module_id)
    )


def find_explorer_item_with_ancestors(
    roots: list[PublicationItem],
    item_id: str,
) -> tuple[PublicationItem, list[PublicationItem]] | None:
    """Locate ``item_id`` and return ``(item, ancestors)`` (ancestors exclude item)."""

    def walk(
        nodes: list[PublicationItem],
        ancestors: list[PublicationItem],
    ) -> tuple[PublicationItem, list[PublicationItem]] | None:
        for node in nodes or []:
            if node.id == item_id:
                return node, ancestors
            hit = walk(node.children or [], ancestors + [node])
            if hit is not None:
                return hit
        return None

    return walk(roots, [])
