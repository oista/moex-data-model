"""Tests for ER scene + layout projections."""

from __future__ import annotations

import json
from pathlib import Path

from moex_dams.projection.er_layout import (
    merge_layout,
    seed_layout,
    validate_layout,
    write_or_merge_layout,
)
from moex_dams.projection.er_scene import project_model_package_to_er_scene
from moex_dams.projection.mermaid_er import MERMAID_CONFIG_PATH, write_er_diagram_artifact

MINI = {
    "element_id": "dams:model/mini/1.0.0",
    "name": "mini_model",
    "logical_entities": [
        {
            "element_id": "dams:logical/mini/Client",
            "name": "TradingClient",
            "title": "Client",
            "attributes": [
                {
                    "element_id": "dams:logical/mini/Client/clientId",
                    "name": "clientId",
                    "data_type_ref": "dams:datatype/identifier",
                    "required": True,
                },
                {
                    "element_id": "dams:logical/mini/Client/fullName",
                    "name": "fullName",
                    "title": "Full name",
                    "data_type_ref": "dams:datatype/string",
                },
            ],
        },
        {
            "element_id": "dams:logical/mini/Account",
            "name": "Account",
            "attributes": [
                {
                    "element_id": "dams:logical/mini/Account/accountId",
                    "name": "accountId",
                    "data_type_ref": "dams:datatype/identifier",
                    "required": True,
                },
                {
                    "element_id": "dams:logical/mini/Account/clientId",
                    "name": "clientId",
                    "data_type_ref": "dams:datatype/identifier",
                    "required": True,
                },
            ],
        },
    ],
    "relationships": [
        {
            "element_id": "dams:rel/mini/Account-Client",
            "name": "Account_owned_by_Client",
            "source_entity_ref": "dams:logical/mini/Account",
            "target_entity_ref": "dams:logical/mini/Client",
            "source_role": "clientId",
            "source_min_cardinality": 0,
            "source_max_cardinality": 999999,
            "target_min_cardinality": 0,
            "target_max_cardinality": 1,
        },
    ],
}


def test_scene_logical_nodes_and_edges():
    scene = project_model_package_to_er_scene(MINI, profile="logical")
    assert scene["version"] == 1
    assert scene["profile"] == "logical"
    names = {n["name"] for n in scene["nodes"]}
    assert "TradingClient" in names
    assert "Account" in names
    client = next(n for n in scene["nodes"] if n["name"] == "TradingClient")
    assert client["element_id"] == "dams:logical/mini/Client"
    assert any(c["name"] == "clientId" and "PK" in c["keys"] for c in client["columns"])
    assert len(scene["edges"]) == 1
    edge = scene["edges"][0]
    assert edge["element_id"] == "dams:rel/mini/Account-Client"
    assert edge["source"] == "Account"
    assert edge["target"] == "TradingClient"
    assert edge["source_cardinality"] == "zeroOrMore"
    assert edge["target_cardinality"] == "zeroOrOne"


def test_seed_layout_deterministic():
    scene = project_model_package_to_er_scene(MINI, profile="logical")
    a = seed_layout(scene, profile="logical")
    b = seed_layout(scene, profile="logical")
    assert a == b
    assert "dams:logical/mini/Client" in a["nodes"]
    assert a["nodes"]["dams:logical/mini/Client"]["color"] == "#4285F4"
    assert validate_layout(a) == []


def test_merge_keeps_positions_adds_and_drops(tmp_path: Path):
    scene = project_model_package_to_er_scene(MINI, profile="logical")
    layout_path = tmp_path / "logical.layout.json"
    first = write_or_merge_layout(
        scene=scene, layout_path=layout_path, profile="logical", reset=True
    )
    first["nodes"]["dams:logical/mini/Client"]["x"] = 999
    first["nodes"]["dams:logical/mini/Client"]["color"] = "#ff0000"
    layout_path.write_text(json.dumps(first), encoding="utf-8")

    # Add a third entity and drop Account from scene
    extended = {
        **MINI,
        "logical_entities": [
            MINI["logical_entities"][0],
            {
                "element_id": "dams:logical/mini/Contact",
                "name": "Contact",
                "attributes": [
                    {
                        "element_id": "dams:logical/mini/Contact/id",
                        "name": "id",
                        "data_type_ref": "dams:datatype/identifier",
                    }
                ],
            },
        ],
        "relationships": [],
    }
    scene2 = project_model_package_to_er_scene(extended, profile="logical")
    merged = write_or_merge_layout(
        scene=scene2, layout_path=layout_path, profile="logical", reset=False
    )
    assert merged["nodes"]["dams:logical/mini/Client"]["x"] == 999
    assert merged["nodes"]["dams:logical/mini/Client"]["color"] == "#ff0000"
    assert "dams:logical/mini/Contact" in merged["nodes"]
    assert "dams:logical/mini/Account" not in merged["nodes"]


def test_write_er_diagram_writes_scene_and_layout(tmp_path: Path):
    impl = tmp_path / "model.yaml"
    import yaml

    impl.write_text(yaml.dump(MINI), encoding="utf-8")
    out = tmp_path / "publications" / "logical.erd.md"
    write_er_diagram_artifact(
        implementation_path=impl,
        out_md=out,
        profile="logical",
        reset_layout=True,
    )
    scene_path = tmp_path / "publications" / "logical.scene.json"
    layout_path = tmp_path / "publications" / "logical.layout.json"
    assert scene_path.is_file()
    assert layout_path.is_file()
    scene = json.loads(scene_path.read_text(encoding="utf-8"))
    assert scene["nodes"]
    # Second write without reset must keep user position
    layout = json.loads(layout_path.read_text(encoding="utf-8"))
    layout["nodes"]["dams:logical/mini/Client"]["x"] = 1234
    layout_path.write_text(json.dumps(layout), encoding="utf-8")
    write_er_diagram_artifact(
        implementation_path=impl,
        out_md=out,
        profile="logical",
        reset_layout=False,
    )
    layout2 = json.loads(layout_path.read_text(encoding="utf-8"))
    assert layout2["nodes"]["dams:logical/mini/Client"]["x"] == 1234


def test_mermaid_config_present():
    assert MERMAID_CONFIG_PATH.is_file()
    cfg = json.loads(MERMAID_CONFIG_PATH.read_text(encoding="utf-8"))
    assert cfg["theme"] == "base"
    assert "themeCSS" in cfg
    assert "--erd-" in cfg["themeCSS"]


def test_merge_layout_unit():
    scene = project_model_package_to_er_scene(MINI, profile="logical")
    seed = seed_layout(scene, profile="logical")
    existing = {
        "version": 1,
        "profile": "logical",
        "nodes": {
            "dams:logical/mini/Client": {"x": 10, "y": 20, "color": "#abcabc"},
            "ghost": {"x": 1, "y": 2},
        },
        "edges": {
            "dams:rel/mini/Account-Client": {"points": [{"x": 5, "y": 6}]},
            "gone": {"points": [{"x": 0, "y": 0}]},
        },
    }
    merged = merge_layout(existing, scene, profile="logical")
    assert merged["nodes"]["dams:logical/mini/Client"]["x"] == 10
    assert "ghost" not in merged["nodes"]
    assert "dams:logical/mini/Account" in merged["nodes"]
    assert "dams:rel/mini/Account-Client" in merged["edges"]
    assert "gone" not in merged["edges"]
