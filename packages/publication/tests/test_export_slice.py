"""Publication projection from vertical slice."""

from __future__ import annotations

import json
from pathlib import Path

from moex_dams import assess_implementation
from moex_publication import (
    build_publication_module,
    build_slice_projection,
    export_slice_projection,
)


def test_build_publication_module(dams_schema: Path, mdm_solution: Path) -> None:
    result = assess_implementation(
        schema_path=dams_schema,
        implementation_path=mdm_solution,
        implementation_id="moex:implementation:mdm:0.1.0",
    )
    module = build_publication_module(result)
    assert module.module_id == "moex:module:vertical-slice"
    section_ids = {s.id for s in module.sections}
    assert "summary" in section_ids
    assert "graph-nodes" in section_ids
    nodes_section = next(s for s in module.sections if s.id == "graph-nodes")
    assert any(i.id == "dams:logical/mdm/ENTERPRISE" for i in nodes_section.items)
    assert any(
        i.id == "dams:mapping/mdm/map_ENTERPRISE_ENTERPRISE_ID" for i in nodes_section.items
    )


def test_export_slice_json(
    dams_schema: Path,
    mdm_solution: Path,
    tmp_path: Path,
) -> None:
    out = tmp_path / "vertical_slice.json"
    result = export_slice_projection(
        schema_path=dams_schema,
        implementation_path=mdm_solution,
        out_path=out,
        implementation_id="moex:implementation:mdm:0.1.0",
    )
    assert out.is_file()
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data["summary"]["is_conformant"] is True
    assert data["summary"]["package_id"] == "dams:model/mdm/0.1.0"
    assert any(n["id"] == "dams:logical/mdm/ENTERPRISE" for n in data["nodes"])
    assert data["module"]["module_id"] == "moex:module:vertical-slice"
    assert build_slice_projection(result)["summary"]["revision"] == data["summary"][
        "revision"
    ]
    assert "model_assessment" in data
    assert isinstance(data["model_assessment"], list)
    for row in data["model_assessment"]:
        assert row["status"] in ("pass", "fail", "warn")
        assert "diagnostic_code" in row
        assert row["diagnostic_code"].startswith("DAMS-REQ-") or row[
            "diagnostic_code"
        ].startswith("DAMS-")
