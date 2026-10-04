"""Markdown normalizer."""

from __future__ import annotations

import re
from pathlib import Path

import markdown

from moex_publication_viewer.models.manifest_models import ManifestSection
from moex_publication_viewer.models.publication_models import PublicationSection
from moex_publication_viewer.normalizers.base import NormalizeError
from moex_publication_viewer.normalizers.helpers import section_meta

_TABLE_RE = re.compile(r"<table\b[^>]*>.*?</table>", re.IGNORECASE | re.DOTALL)


def wrap_markdown_tables(html: str) -> str:
    """Wrap bare HTML tables in .table-scroll for responsive overflow."""

    def _wrap_block(match: re.Match[str]) -> str:
        table = match.group(0)
        open_tag_end = table.find(">")
        open_tag = table[: open_tag_end + 1]
        if "data-table" not in open_tag:
            if 'class="' in open_tag:
                table = table.replace('class="', 'class="data-table ', 1)
            else:
                table = table.replace("<table", '<table class="data-table"', 1)
        return f'<div class="table-scroll">{table}</div>'

    return _TABLE_RE.sub(_wrap_block, html)


class MarkdownNormalizer:
    def normalize(self, section: ManifestSection, source_path: Path) -> PublicationSection:
        try:
            raw = source_path.read_text(encoding="utf-8")
        except OSError as exc:
            raise NormalizeError(f"cannot read markdown {source_path}: {exc}") from exc

        body = raw
        if raw.startswith("---"):
            parts = raw.split("---", 2)
            if len(parts) >= 3:
                body = parts[2].lstrip("\n")

        html = markdown.markdown(body, extensions=["fenced_code", "tables"])
        html = wrap_markdown_tables(html)
        return PublicationSection(**section_meta(section), items=[], content=html)
