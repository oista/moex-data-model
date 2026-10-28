"""ADR-049: EffectiveGovernanceView materialize / check."""

from __future__ import annotations

from pathlib import Path

from moex_dams.governance.materialize import (
    build_governance_view,
    check_governance_view,
    dump_governance_view,
    materialize_governance_view,
)


def test_build_governance_view_from_inline_package(tmp_path: Path) -> None:
    body = {
        "element_id": "dams:model/gov-mat/1",
        "name": "gov_mat",
        "data_owner_ref": "org:role/OWNER",
        "governance_classification": "internal",
        "policy_refs": ["pol:P1"],
        "logical_entities": [
            {
                "element_id": "dams:logical/gov-mat/E",
                "name": "E",
                "data_class": "master_data",
                "source_system_refs": ["eam:system/S"],
                "attributes": [],
            }
        ],
    }
    view, findings = build_governance_view([(body, {})], as_of="2026-10-12")
    assert view["as_of"] == "2026-10-12"
    assert view["input_digest"].startswith("sha256:")
    assert "dams:model/gov-mat/1" in view["package_refs"]
    assert any(e["element_ref"] == "dams:model/gov-mat/1" for e in view["elements"])
    assert findings == []
    # Inline-only cascade slots must not leak into EffectiveGovernanceView.
    for el in view["elements"]:
        names = {row["slot_name"] for row in el.get("slots") or []}
        assert "data_class" not in names
        assert "source_system_refs" not in names
    text = dump_governance_view(view)
    assert "EffectiveGovernanceView" in text or "as_of" in text


def test_materialize_and_check_roundtrip(tmp_path: Path) -> None:
    pkg = tmp_path / "pkg.yaml"
    pkg.write_text(
        "\n".join(
            [
                "element_id: dams:model/gov-rt/1",
                "name: gov_rt",
                "data_owner_ref: org:role/OWNER",
                "governance_classification: internal",
            ]
        ),
        encoding="utf-8",
    )
    # Point repo_root at tmp with as_of config + generated path layout.
    as_of_dir = (
        tmp_path
        / "model-assets"
        / "specifications"
        / "moex-governance-view"
        / "0.1"
    )
    as_of_dir.mkdir(parents=True)
    (as_of_dir / "as_of.txt").write_text("2026-10-12\n", encoding="utf-8")
    out, _view, _findings = materialize_governance_view(
        tmp_path, package_paths=[pkg], write=True
    )
    assert out.is_file()
    errors = check_governance_view(tmp_path, package_paths=[pkg])
    assert errors == []
