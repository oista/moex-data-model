"""Normalize Mermaid erDiagram markdown (+ sibling SVG) for viewer."""

from __future__ import annotations

import re
from pathlib import Path

from moex_publication_viewer.models.manifest_models import ManifestSection
from moex_publication_viewer.models.publication_models import PublicationSection
from moex_publication_viewer.normalizers.base import NormalizeError
from moex_publication_viewer.normalizers.helpers import section_meta

_SCRIPT_RE = re.compile(r"<script\b[^>]*>.*?</script>", re.IGNORECASE | re.DOTALL)
_MERMAID_FENCE_RE = re.compile(r"```mermaid\s*(.*?)```", re.IGNORECASE | re.DOTALL)


def _extract_mermaid_source(raw: str) -> str:
    m = _MERMAID_FENCE_RE.search(raw)
    if m:
        return m.group(1).strip() + "\n"
    stripped = raw.lstrip()
    if stripped.startswith("erDiagram"):
        return stripped if stripped.endswith("\n") else stripped + "\n"
    return raw.strip() + "\n"


def _sanitize_svg(svg: str) -> str:
    cleaned = _SCRIPT_RE.sub("", svg)
    # Keep only from first <svg to last </svg>
    start = cleaned.lower().find("<svg")
    end = cleaned.lower().rfind("</svg>")
    if start >= 0 and end > start:
        return cleaned[start : end + len("</svg>")].strip()
    return cleaned.strip()


class MermaidDiagramNormalizer:
    """Load ``*.erd.md``; embed sibling ``*.erd.svg`` when present."""

    def normalize(self, section: ManifestSection, source_path: Path) -> PublicationSection:
        try:
            raw = source_path.read_text(encoding="utf-8")
        except OSError as exc:
            raise NormalizeError(f"cannot read mermaid diagram {source_path}: {exc}") from exc

        mermaid_source = _extract_mermaid_source(raw)
        svg_path = source_path.with_suffix(".svg")
        content = ""
        svg_missing = True
        if svg_path.is_file():
            try:
                content = _sanitize_svg(svg_path.read_text(encoding="utf-8"))
                svg_missing = not bool(content)
            except OSError:
                content = ""
                svg_missing = True

        meta = section_meta(section)
        return PublicationSection(
            **meta,
            items=[],
            content=content,
            attributes={
                "mermaid_source": mermaid_source,
                "svg_missing": svg_missing,
            },
        )
