"""ADR-019 phase 2: publication contract semantic checks and hard fail."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from moex_publication_viewer.models.manifest_models import (
    ManifestSection,
    PublicationManifest,
    SourceSpec,
)
from moex_publication_viewer.models.publication_models import (
    PublicationModule,
    PublicationSection,
)
from moex_publication_viewer.publication_contract import (
    applies_when_active,
    assess_module_implements,
    count_semantic_entities,
    run_publication_contracts,
)
from moex_publication_viewer.validators import ValidationError, check_publication_contract_coverage


FIXTURE_MODEL = {
    "logical_entities": [
        {
            "element_id": "e1",
            "name": "E1",
            "attributes": [
                {"element_id": "a1", "name": "a1"},
                {"element_id": "a2", "name": "a2"},
            ],
        }
    ],
    "data_carriers": [
        {
            "element_id": "p1",
            "name": "P1",
            "asset_kind": "relational_table",
            "physical_fields": [
                {
                    "element_id": "f1",
                    "name": "f1",
                    "carrier_ref": "p1",
                }
            ],
        }
    ],
    "mappings": [{"element_id": "m1", "name": "M1", "mapping_type": "field_mapping"}],
}


def test_count_logical_entities_and_nested_attributes():
    assert count_semantic_entities(FIXTURE_MODEL, ["LogicalEntity"], select="logical_entities") == 1
    assert (
        count_semantic_entities(FIXTURE_MODEL, ["LogicalAttribute"], select="logical_entities")
        == 2
    )
    assert count_semantic_entities(FIXTURE_MODEL, ["DataCarrier"], select="data_carriers") == 1
    assert (
        count_semantic_entities(FIXTURE_MODEL, ["PhysicalField"], select="data_carriers") == 1
    )
    assert (
        count_semantic_entities(
            FIXTURE_MODEL,
            ["EntityPhysicalMapping", "AttributePhysicalMapping"],
            select="mappings",
        )
        == 1
    )


def test_applies_when_physical_skip(tmp_path: Path):
    manifest = PublicationManifest(
        module_id="moex:module:x",
        title="X",
        profile="implementation",
        sections=[
            ManifestSection(
                id="overview",
                title="O",
                type="markdown-doc",
                kind="overview",
                source=SourceSpec(format="markdown", path="README.md"),
                satisfies=["dams:overview"],
            )
        ],
    )
    module = PublicationModule(
        module_id="moex:module:x",
        title="X",
        profile="implementation",
        implements=[{"specification_ref": "moex-dams@0.1", "profile_ref": "demo"}],
        sections=[
            PublicationSection(
                id="overview",
                title="O",
                type="markdown-doc",
                kind="overview",
                satisfies=["dams:overview"],
                content="x",
            )
        ],
        manifest_path=str(tmp_path / "publish.yaml"),
    )
    assert applies_when_active("when physical objects are present", module, manifest) is False
    assert applies_when_active(None, module, manifest) is True


def test_hard_fail_on_missing_satisfies(tmp_path: Path):
    root = tmp_path
    dams = root / "model-assets" / "specifications" / "moex-dams" / "0.1"
    dams.mkdir(parents=True)
    (dams / "publication-requirements.yaml").write_text(
        """
version: "0.1"
profiles:
  - id: demo-profile
    requirements:
      - id: dams:logical-entities
        kind: required-semantic-content
        obligation: required
        min_occurs: 1
        expected_semantic_types: [LogicalEntity]
        accepted_section_kinds: [classes]
        accepted_renderers: [entity-table]
      - id: dams:overview
        kind: required-section
        obligation: required
        accepted_section_kinds: [overview]
        accepted_renderers: [markdown-doc]
""",
        encoding="utf-8",
    )
    pub = root / "impl"
    pub.mkdir()
    model = pub / "model.yaml"
    model.write_text("logical_entities: []\n", encoding="utf-8")
    (pub / "README.md").write_text("# hi\n", encoding="utf-8")
    manifest_path = pub / "publish.yaml"
    manifest_path.write_text(
        yaml.safe_dump(
            {
                "module_id": "moex:module:x",
                "kind": "publication_module",
                "title": "X",
                "profile": "implementation",
                "implements": [
                    {
                        "specification_ref": "moex-dams@0.1",
                        "profile_ref": "demo-profile",
                    }
                ],
                "sections": [
                    {
                        "id": "overview",
                        "title": "O",
                        "kind": "overview",
                        "type": "markdown-doc",
                        "satisfies": ["dams:overview"],
                        "source": {"format": "markdown", "path": "README.md"},
                    },
                    {
                        "id": "logical",
                        "title": "L",
                        "kind": "classes",
                        "type": "entity-table",
                        "satisfies": ["dams:logical-entities"],
                        "source": {
                            "format": "yaml",
                            "path": "model.yaml",
                            "select": "logical_entities",
                        },
                    },
                ],
            }
        ),
        encoding="utf-8",
    )
    module = PublicationModule(
        module_id="moex:module:x",
        title="X",
        profile="implementation",
        implements=[
            {"specification_ref": "moex-dams@0.1", "profile_ref": "demo-profile"}
        ],
        sections=[
            PublicationSection(
                id="overview",
                title="O",
                type="markdown-doc",
                kind="overview",
                satisfies=["dams:overview"],
                content="x",
            ),
            PublicationSection(
                id="logical",
                title="L",
                type="entity-table",
                kind="classes",
                satisfies=["dams:logical-entities"],
                items=[],
            ),
        ],
        manifest_path=str(manifest_path),
    )
    with pytest.raises(ValidationError) as exc:
        check_publication_contract_coverage([module], root, hard_fail=True)
    assert any("logical-entities" in e for e in exc.value.errors)


def test_ok_when_semantic_content_present(tmp_path: Path):
    root = tmp_path
    dams = root / "model-assets" / "specifications" / "moex-dams" / "0.1"
    dams.mkdir(parents=True)
    (dams / "publication-requirements.yaml").write_text(
        """
version: "0.1"
profiles:
  - id: demo-profile
    requirements:
      - id: dams:logical-entities
        kind: required-semantic-content
        obligation: required
        min_occurs: 1
        expected_semantic_types: [LogicalEntity]
        accepted_section_kinds: [classes]
        accepted_renderers: [entity-table]
      - id: dams:declared-binding
        kind: required-binding
        obligation: required
""",
        encoding="utf-8",
    )
    pub = root / "impl"
    pub.mkdir()
    (pub / "model.yaml").write_text(
        yaml.safe_dump(FIXTURE_MODEL),
        encoding="utf-8",
    )
    manifest_path = pub / "publish.yaml"
    manifest_path.write_text(
        yaml.safe_dump(
            {
                "module_id": "moex:module:ok",
                "kind": "publication_module",
                "title": "OK",
                "profile": "implementation",
                "implements": [
                    {
                        "specification_ref": "moex-dams@0.1",
                        "profile_ref": "demo-profile",
                    }
                ],
                "sections": [
                    {
                        "id": "logical",
                        "title": "L",
                        "kind": "classes",
                        "type": "entity-table",
                        "satisfies": ["dams:logical-entities"],
                        "source": {
                            "format": "yaml",
                            "path": "model.yaml",
                            "select": "logical_entities",
                        },
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    module = PublicationModule(
        module_id="moex:module:ok",
        title="OK",
        implements=[
            {"specification_ref": "moex-dams@0.1", "profile_ref": "demo-profile"}
        ],
        sections=[
            PublicationSection(
                id="logical",
                title="L",
                type="entity-table",
                kind="classes",
                satisfies=["dams:logical-entities"],
            )
        ],
        manifest_path=str(manifest_path),
    )
    reports, warnings = run_publication_contracts(
        [module], root, hard_fail=True, dist_dir=None
    )
    assert len(reports) == 1
    assert reports[0].overall_publication_status == "conformant"
    assert (pub / "publications" / "publication_conformance.json").is_file()
    assert warnings == []


def test_draft_status_when_conformance_target_draft(tmp_path: Path):
    root = tmp_path
    dams = root / "model-assets" / "specifications" / "moex-dams" / "0.1"
    dams.mkdir(parents=True)
    (dams / "publication-requirements.yaml").write_text(
        """
version: "0.1"
profiles:
  - id: demo-profile
    requirements:
      - id: dams:declared-binding
        kind: required-binding
        obligation: required
""",
        encoding="utf-8",
    )
    pub = root / "impl"
    pub.mkdir()
    manifest_path = pub / "publish.yaml"
    manifest_path.write_text(
        yaml.safe_dump(
            {
                "module_id": "moex:module:draft",
                "kind": "publication_module",
                "title": "D",
                "profile": "implementation",
                "conformance_status": "draft-conformant",
                "implements": [
                    {
                        "specification_ref": "moex-dams@0.1",
                        "profile_ref": "demo-profile",
                        "conformance_target": "draft",
                    }
                ],
                "sections": [],
            }
        ),
        encoding="utf-8",
    )
    module = PublicationModule(
        module_id="moex:module:draft",
        title="D",
        conformance_status="draft-conformant",
        implements=[
            {
                "specification_ref": "moex-dams@0.1",
                "profile_ref": "demo-profile",
                "conformance_target": "draft",
            }
        ],
        sections=[],
        manifest_path=str(manifest_path),
    )
    reports, _ = run_publication_contracts([module], root, hard_fail=True)
    assert reports[0].overall_publication_status == "draft-conformant"


def test_repo_mdm_and_csv_draft_assess():
    root = Path(__file__).resolve().parents[3]
    mdm_pub = (
        root
        / "model-assets"
        / "implementations"
        / "solutions"
        / "mdm"
        / "publish.yaml"
    )
    if not mdm_pub.is_file():
        pytest.skip("repo mdm publish.yaml missing")
    from moex_publication_viewer.build import compile_modules

    modules = compile_modules(root, enforce_publication_contract=True, dist_dir=None)
    ids = {m.module_id for m in modules}
    assert "moex:module:mdm-solution" in ids
    assert "moex:module:client-accounts-csv-draft" in ids
    mdm = next(m for m in modules if m.module_id == "moex:module:mdm-solution")
    reports = assess_module_implements(mdm, root)
    assert reports
    assert reports[0].overall_publication_status in (
        "conformant",
        "partially-conformant",
        "draft-conformant",
    )
    assert all(
        r.result_status != "fail" or r.obligation != "required"
        for r in reports[0].requirement_results
    )


def test_adr019_does_not_validate_body_identity_ownership_mapping(tmp_path: Path):
    """ADR-019 is presence/satisfies only — missing body fields must not fail contract."""
    root = tmp_path
    dams = root / "model-assets" / "specifications" / "moex-dams" / "0.1"
    dams.mkdir(parents=True)
    (dams / "publication-requirements.yaml").write_text(
        """
version: "0.1"
profiles:
  - id: demo-profile
    requirements:
      - id: dams:logical-entities
        kind: required-semantic-content
        obligation: required
        min_occurs: 1
        expected_semantic_types: [LogicalEntity]
        accepted_section_kinds: [classes]
        accepted_renderers: [entity-table]
      - id: dams:declared-binding
        kind: required-binding
        obligation: required
""",
        encoding="utf-8",
    )
    pub = root / "impl"
    pub.mkdir()
    # Minimal entity: no identity_rule, ownership, or mapping_coverage_status
    body = {
        "logical_entities": [
            {
                "element_id": "e1",
                "name": "E1",
                "attributes": [{"element_id": "a1", "name": "a1"}],
            }
        ]
    }
    (pub / "model.yaml").write_text(yaml.safe_dump(body), encoding="utf-8")
    manifest_path = pub / "publish.yaml"
    manifest_path.write_text(
        yaml.safe_dump(
            {
                "module_id": "moex:module:body-gap",
                "kind": "publication_module",
                "title": "Body gap OK for ADR-019",
                "profile": "implementation",
                "implements": [
                    {
                        "specification_ref": "moex-dams@0.1",
                        "profile_ref": "demo-profile",
                    }
                ],
                "sections": [
                    {
                        "id": "logical",
                        "title": "L",
                        "kind": "classes",
                        "type": "entity-table",
                        "satisfies": ["dams:logical-entities"],
                        "source": {
                            "format": "yaml",
                            "path": "model.yaml",
                            "select": "logical_entities",
                        },
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    module = PublicationModule(
        module_id="moex:module:body-gap",
        title="Body gap OK for ADR-019",
        implements=[
            {"specification_ref": "moex-dams@0.1", "profile_ref": "demo-profile"}
        ],
        sections=[
            PublicationSection(
                id="logical",
                title="L",
                type="entity-table",
                kind="classes",
                satisfies=["dams:logical-entities"],
            )
        ],
        manifest_path=str(manifest_path),
    )
    reports, warnings = run_publication_contracts(
        [module], root, hard_fail=True, dist_dir=None
    )
    assert len(reports) == 1
    assert reports[0].overall_publication_status == "conformant"
    assert warnings == []


def test_model_assessment_section_kind_accepted():
    section = ManifestSection(
        id="model-assessment",
        title="Оценка",
        type="entity-table",
        kind="model-assessment",
        source=SourceSpec(format="json", path="publications/vertical_slice.json", select="model_assessment"),
    )
    assert section.kind == "model-assessment"
