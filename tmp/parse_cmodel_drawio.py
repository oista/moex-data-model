"""Parse CModel_content04.drawio into structured CDM inventory."""
from __future__ import annotations

import html
import json
import os
import re
from collections import defaultdict

PATH = r"f:\!PASSPORT\!H_DATASC\!Data Architecture\MOEX_DataModel\MOEX Data Model Standart\enterpise_cdm_src\CModel_content04.drawio"
OUTPATH = r"c:\Users\bons1\IdeaProjects\moex-data-model\tmp\cmodel_content04_inventory.json"


def unescape(v: str) -> str:
    if not v:
        return ""
    return html.unescape(v.replace("&nbsp;", " ")).strip()


def get_attr(attrs: str, name: str) -> str | None:
    mm = re.search(rf'{name}="([^"]*)"', attrs)
    return mm.group(1) if mm else None


def parse_cells(block: str) -> dict[str, str]:
    cells: dict[str, str] = {}
    for m in re.finditer(r"<mxCell id=\"([^\"]+)\"([^/]*?)(?:/>|>\s*<mxGeometry)", block, re.DOTALL):
        cid, attrs = m.group(1), m.group(2)
        if cid not in cells or len(attrs) > len(cells[cid]):
            cells[cid] = attrs
    return cells


def find_table_ancestor(cid: str | None, id_to_parent: dict[str, str | None], table_ids: set[str]) -> str | None:
    seen: set[str] = set()
    while cid and cid not in seen:
        seen.add(cid)
        if cid in table_ids:
            return cid
        cid = id_to_parent.get(cid)  # type: ignore[assignment]
    return None


def main() -> None:
    with open(PATH, "r", encoding="utf-8") as f:
        content = f.read()

    diagrams = re.findall(r'<diagram name="([^"]*)" id="([^"]*)"', content)
    diagram_blocks = re.findall(
        r'<diagram name="([^"]*)" id="([^"]*)">(.*?)</diagram>', content, re.DOTALL
    )

    all_entities: list[dict] = []
    all_edges: list[dict] = []
    all_swimlanes: list[dict] = []
    all_notes: list[dict] = []
    fill_colors: dict[str, set[str]] = defaultdict(set)
    global_id_to_parent: dict[str, str | None] = {}
    global_id_to_value: dict[str, str] = {}

    for dname, _did, block in diagram_blocks:
        cells = parse_cells(block)
        id_to_value: dict[str, str] = {}
        id_to_parent: dict[str, str | None] = {}
        for cid, attrs in cells.items():
            val = unescape(get_attr(attrs, "value") or "")
            parent = get_attr(attrs, "parent")
            id_to_value[cid] = val
            id_to_parent[cid] = parent
            global_id_to_parent[cid] = parent
            global_id_to_value[cid] = val

        tables: list[dict] = []
        for cid, attrs in cells.items():
            if get_attr(attrs, "vertex") != "1":
                continue
            style = get_attr(attrs, "style") or ""
            val = unescape(get_attr(attrs, "value") or "")
            if "shape=table;" not in style or not val:
                continue
            fill_m = re.search(r"fillColor=([^;]+)", style)
            fc = fill_m.group(1) if fill_m else None
            if fc:
                fill_colors[fc].add(val)
            tables.append(
                {
                    "id": cid,
                    "name": val,
                    "parent": get_attr(attrs, "parent"),
                    "fillColor": fc,
                    "strokeColor": (re.search(r"strokeColor=([^;]+)", style) or [None, None])[1],
                    "page": dname,
                }
            )

        table_ids = {t["id"] for t in tables}
        table_names = {t["name"] for t in tables}

        for cid, attrs in cells.items():
            if get_attr(attrs, "vertex") != "1":
                continue
            style = get_attr(attrs, "style") or ""
            val = unescape(get_attr(attrs, "value") or "")
            if not val or val in ("PK", "FK"):
                continue
            is_swimlane = "swimlane" in style and "tableRow" not in style
            is_folder = "shape=folder" in style
            is_group = "container=1" in style and "shape=table" not in style and "tableRow" not in style
            if is_swimlane or is_folder or (is_group and len(val) > 2):
                all_swimlanes.append(
                    {"name": val, "id": cid, "page": dname, "style_snippet": style[:150]}
                )

        entity_attrs: dict[str, list[dict]] = defaultdict(list)
        row_to_key: dict[str, str | None] = {}
        for cid, attrs in cells.items():
            style = get_attr(attrs, "style") or ""
            if "shape=partialRectangle" not in style:
                continue
            val = unescape(get_attr(attrs, "value") or "")
            row_id = get_attr(attrs, "parent")
            if val in ("PK", "FK") and row_id:
                row_to_key[row_id] = val
            elif val and val not in ("PK", "FK"):
                tbl = find_table_ancestor(row_id, id_to_parent, table_ids)
                if tbl:
                    entity_attrs[tbl].append(
                        {
                            "name": val,
                            "key": row_to_key.get(row_id or ""),
                            "data_type": None,
                        }
                    )

        for t in tables:
            all_entities.append(
                {
                    "page": dname,
                    "name": t["name"],
                    "id": t["id"],
                    "fillColor": t["fillColor"],
                    "strokeColor": t["strokeColor"],
                    "attributes": entity_attrs.get(t["id"], []),
                }
            )

        for cid, attrs in cells.items():
            if get_attr(attrs, "edge") != "1":
                continue
            src = get_attr(attrs, "source")
            tgt = get_attr(attrs, "target")
            label = unescape(get_attr(attrs, "value") or "")
            style = get_attr(attrs, "style") or ""
            all_edges.append(
                {
                    "page": dname,
                    "id": cid,
                    "source_id": src,
                    "target_id": tgt,
                    "source_label": id_to_value.get(src or "", src),
                    "target_label": id_to_value.get(tgt or "", tgt),
                    "label": label,
                    "cardinality_hint": label if re.search(r"[\*0-9]", label) else None,
                    "style": style[:250] if style else None,
                }
            )

        for cid, attrs in cells.items():
            style = get_attr(attrs, "style") or ""
            val = unescape(get_attr(attrs, "value") or "")
            if get_attr(attrs, "vertex") != "1" or len(val) < 4:
                continue
            if val in table_names:
                continue
            if "shape=table" in style or "partialRectangle" in style or "tableRow" in style:
                continue
            if (
                "text" in style
                or "shape=note" in style
                or "shape=callout" in style
                or ("html=1" in style and "edgeLabel" not in style and "swimlane" not in style)
            ):
                all_notes.append({"page": dname, "text": val[:800]})

    table_by_id = {e["id"]: e["name"] for e in all_entities}

    def resolve_entity_name(cell_id: str | None) -> str | None:
        if not cell_id:
            return None
        if cell_id in table_by_id:
            return table_by_id[cell_id]
        cid = cell_id
        seen: set[str] = set()
        while cid and cid not in seen:
            seen.add(cid)
            if cid in table_by_id:
                return table_by_id[cid]
            cid = global_id_to_parent.get(cid)
        v = global_id_to_value.get(cell_id or "", "")
        return v if v and v not in ("PK", "FK", "") else None

    for e in all_edges:
        e["source_entity"] = resolve_entity_name(e["source_id"])
        e["target_entity"] = resolve_entity_name(e["target_id"])

    # infer FK relationships from attributes referencing other entity names
    entity_names = {e["name"] for e in all_entities}
    fk_rels: list[dict] = []
    for ent in all_entities:
        for attr in ent["attributes"]:
            if attr.get("key") != "FK":
                continue
            tgt = attr["name"]
            # match by entity name or common PK attribute label
            matched = None
            for en in entity_names:
                if tgt == en or tgt in en or en.startswith(tgt.split()[0]):
                    matched = en
                    break
            fk_rels.append(
                {
                    "page": ent["page"],
                    "from_entity": ent["name"],
                    "via_attribute": attr["name"],
                    "to_entity_guess": matched,
                }
            )

    out = {
        "source_file": PATH,
        "file_size_bytes": os.path.getsize(PATH),
        "diagrams": [{"name": n, "id": i} for n, i in diagrams],
        "summary": {
            "entity_count": len(all_entities),
            "edge_count": len(all_edges),
            "inferred_fk_count": len(fk_rels),
            "swimlane_group_count": len(all_swimlanes),
            "note_count": len(all_notes),
            "distinct_fill_colors": len(fill_colors),
        },
        "fill_color_domains": {k: sorted(v) for k, v in sorted(fill_colors.items())},
        "entities": all_entities,
        "edges": all_edges,
        "inferred_fk_relationships": fk_rels,
        "swimlanes_groups": all_swimlanes,
        "notes_legend": all_notes,
    }

    os.makedirs(os.path.dirname(OUTPATH), exist_ok=True)
    with open(OUTPATH, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=2)

    print(json.dumps(out["summary"], indent=2))
    print("diagrams:", [d["name"] for d in out["diagrams"]])
    print("WROTE", OUTPATH)


if __name__ == "__main__":
    main()
