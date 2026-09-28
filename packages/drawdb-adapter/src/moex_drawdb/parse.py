"""Subset DBML parser for MOEX projection (Table / column / Note / Ref)."""

from __future__ import annotations

import re

from moex_drawdb.domain import (
    ProjectedColumn,
    ProjectedDiagram,
    ProjectedRef,
    ProjectedTable,
)

_TABLE_RE = re.compile(
    r"Table\s+(\w+)\s*(?:\[([^\]]*)\])?\s*\{",
    re.MULTILINE,
)
_REF_RE = re.compile(
    r"Ref\s+(\w+)?\s*:?\s*(\w+)\.(\w+)\s*>\s*(\w+)\.(\w+)(?:\s*//\s*element_id=(\S+))?",
    re.MULTILINE,
)
_COL_RE = re.compile(
    r"^\s*(\w+)\s+(\w+)(?:\s*\[([^\]]*)\])?\s*$",
    re.MULTILINE,
)
_NOTE_RE = re.compile(r"Note:\s*'((?:\\'|[^'])*)'", re.MULTILINE)
_ELEMENT_ID_RE = re.compile(r"element_id=([^\s;']+)")
_OBJECT_KIND_RE = re.compile(r"object_kind=([^\s;']+)")


def _unescape(note: str) -> str:
    return note.replace("\\'", "'")


def _parse_settings(settings: str | None) -> tuple[bool, str | None]:
    required = False
    note: str | None = None
    if not settings:
        return required, note
    for part in settings.split(","):
        part = part.strip()
        if part == "not null":
            required = True
        elif part.startswith("note:"):
            m = re.search(r"note:\s*'((?:\\'|[^'])*)'", part)
            if m:
                note = _unescape(m.group(1))
    return required, note


def _title_from_table_note(note: str | None) -> str | None:
    if not note:
        return None
    # "element_id=…; Title" or just title bits after element_id
    bits = [b.strip() for b in note.split(";") if b.strip()]
    titles = [b for b in bits if not b.startswith("element_id=") and not b.startswith("object_kind=")]
    return titles[0] if titles else None


def parse_dbml(text: str) -> ProjectedDiagram:
    """Parse MOEX-projected DBML into tables and refs."""
    tables: list[ProjectedTable] = []
    # Find table bodies by brace matching after Table header
    for m in _TABLE_RE.finditer(text):
        tname = m.group(1)
        start = m.end()
        depth = 1
        i = start
        while i < len(text) and depth:
            if text[i] == "{":
                depth += 1
            elif text[i] == "}":
                depth -= 1
            i += 1
        body = text[start : i - 1]
        note_m = _NOTE_RE.search(body)
        table_note = _unescape(note_m.group(1)) if note_m else None
        eid = None
        kind = None
        if table_note:
            em = _ELEMENT_ID_RE.search(table_note)
            if em:
                eid = em.group(1)
            km = _OBJECT_KIND_RE.search(table_note)
            if km:
                kind = km.group(1)
        columns: list[ProjectedColumn] = []
        for cm in _COL_RE.finditer(body):
            cname, ctype, settings = cm.group(1), cm.group(2), cm.group(3)
            if cname == "Note":
                continue
            required, col_note = _parse_settings(settings)
            col_eid = None
            if col_note:
                em = _ELEMENT_ID_RE.search(col_note)
                if em:
                    col_eid = em.group(1)
                elif ":" in col_note and " " not in col_note.strip():
                    # projection stores bare element_id as column note
                    col_eid = col_note.strip()
            columns.append(
                ProjectedColumn(
                    name=cname,
                    type_name=ctype,
                    required=required,
                    element_id=col_eid,
                    note=col_note,
                )
            )
        tables.append(
            ProjectedTable(
                name=tname,
                element_id=eid,
                object_kind=kind,
                title=_title_from_table_note(table_note),
                columns=tuple(columns),
            )
        )

    refs: list[ProjectedRef] = []
    for rm in _REF_RE.finditer(text):
        refs.append(
            ProjectedRef(
                name=rm.group(1),
                source_table=rm.group(2),
                source_column=rm.group(3),
                target_table=rm.group(4),
                target_column=rm.group(5),
                element_id=rm.group(6),
            )
        )

    return ProjectedDiagram(tables=tuple(tables), refs=tuple(refs))
