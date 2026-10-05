"""Architecture catalog load and validation tests."""

from pathlib import Path

import pytest
import yaml

from moex_publication_viewer.catalog_loader import load_architecture_catalog
from moex_publication_viewer.models.catalog_models import ArchitectureCatalog, CatalogNode
from moex_publication_viewer.validators import ValidationError, validate_architecture_catalog


def test_validate_duplicate_id():
    catalog = ArchitectureCatalog(
        nodes=[
            CatalogNode(id="a", role="reference_specification", title="A"),
            CatalogNode(id="a", role="reference_specification", title="A2"),
        ]
    )
    with pytest.raises(ValidationError) as exc:
        validate_architecture_catalog(catalog, set())
    assert "duplicate node id" in str(exc.value)


def test_validate_unknown_conforms_to():
    catalog = ArchitectureCatalog(
        nodes=[
            CatalogNode(
                id="impl",
                role="specification_implementation",
                title="Impl",
                conforms_to="missing-spec",
            )
        ]
    )
    with pytest.raises(ValidationError) as exc:
        validate_architecture_catalog(catalog, set())
    assert "unknown id" in str(exc.value)


def test_validate_unknown_module_id():
    catalog = ArchitectureCatalog(
        nodes=[
            CatalogNode(
                id="spec",
                role="reference_specification",
                title="Spec",
                module_id="moex:module:nope",
            )
        ]
    )
    with pytest.raises(ValidationError) as exc:
        validate_architecture_catalog(catalog, {"moex:module:other"})
    assert "unknown module_id" in str(exc.value)


def test_validate_conforms_to_must_be_specification():
    catalog = ArchitectureCatalog(
        nodes=[
            CatalogNode(id="a", role="specification_implementation", title="A"),
            CatalogNode(
                id="b",
                role="specification_implementation",
                title="B",
                conforms_to="a",
            ),
        ]
    )
    with pytest.raises(ValidationError) as exc:
        validate_architecture_catalog(catalog, set())
    assert "not a reference_specification" in str(exc.value)


def test_load_repo_catalog():
    repo = Path(__file__).resolve().parents[3]
    catalog = load_architecture_catalog(repo)
    assert catalog is not None
    by_id = {n.id: n for n in catalog.nodes}
    assert "moex-dams" in by_id
    assert by_id["trading-solution"].conforms_to == "moex-dams"
    assert by_id["moex-dams"].role == "reference_specification"
    assert by_id["moex-fibo-profile"].role == "reference_specification"
    assert by_id["moex-fibo-profile"].module_id == "moex:module:fibo-profile"
    assert by_id["moex:ontology:fibo"].role == "specification_implementation"
    assert by_id["moex:ontology:fibo"].conforms_to == "moex-fibo-profile"
    # Empty ontology stubs are not shown in the architecture tree
    assert "moex:ontology:corporate" not in by_id
    assert "moex:ontology:prov-o" not in by_id
    assert "moex:ontology:moex-hr" not in by_id
    assert "moex:ontology:moex-data" not in by_id
    assert "moex:ontology:application" not in by_id
    # No modeling_standard nodes in the tree catalog
    assert all(n.role != "modeling_standard" for n in catalog.nodes)


def test_repo_catalog_passes_validation_with_modules():
    repo = Path(__file__).resolve().parents[3]
    catalog = load_architecture_catalog(repo)
    assert catalog is not None
    module_ids = {
        "moex:module:dams",
        "moex:module:dsp",
        "moex:module:fibo",
        "moex:module:fibo-profile",
        "moex:module:fibo-application",
        "moex:module:enterprise-conceptual",
        "moex:module:hierarchy",
        "moex:module:trading-solution",
        "moex:module:mdm-solution",
        "moex:module:ucd-solution",
        "moex:module:crm-solution",
        "moex:module:esed-solution",
        "moex:module:client-accounts-csv-draft",
        "moex:module:ontology-catalog",
        "moex:module:external-alignment",
        "moex:module:trading-participant-core",
    }
    validate_architecture_catalog(catalog, module_ids)


def test_repo_catalog_includes_external_alignment_nodes():
    repo = Path(__file__).resolve().parents[3]
    catalog = load_architecture_catalog(repo)
    assert catalog is not None
    by_id = {n.id: n for n in catalog.nodes}
    assert by_id["moex-external-alignment"].role == "reference_specification"
    assert by_id["moex-trading-participant-core"].module_id == (
        "moex:module:trading-participant-core"
    )
    assert by_id["moex-fibo-party-scope"].conforms_to == "moex-external-alignment"


def test_repo_catalog_includes_enterprise_conceptual():
    repo = Path(__file__).resolve().parents[3]
    catalog = load_architecture_catalog(repo)
    assert catalog is not None
    by_id = {n.id: n for n in catalog.nodes}
    assert by_id["moex-enterprise-conceptual-model"].module_id == (
        "moex:module:enterprise-conceptual"
    )
    assert by_id["moex-enterprise-conceptual-model"].conforms_to == "moex-dams"


def test_repo_catalog_includes_hierarchy_view():
    repo = Path(__file__).resolve().parents[3]
    catalog = load_architecture_catalog(repo)
    assert catalog is not None
    by_id = {n.id: n for n in catalog.nodes}
    assert by_id["moex-hierarchy"].module_id == "moex:module:hierarchy"
    assert by_id["moex-hierarchy"].conforms_to == "moex-dams"
    assert by_id["moex-hierarchy"].contract_exempt is True


def test_repo_catalog_includes_fibo_application_impl():
    repo = Path(__file__).resolve().parents[3]
    catalog = load_architecture_catalog(repo)
    assert catalog is not None
    by_id = {n.id: n for n in catalog.nodes}
    assert by_id["moex-fibo-application"].role == "specification_implementation"
    assert by_id["moex-fibo-application"].conforms_to == "moex-fibo-profile"
    assert by_id["moex-fibo-application"].module_id == "moex:module:fibo-application"
    assert "upstream" in (by_id["moex:ontology:fibo"].description or "").lower() or (
        "preview index" in (by_id["moex:ontology:fibo"].title or "").lower()
    )


def test_tmp_catalog_roundtrip(tmp_path: Path):
    catalog_dir = (
        tmp_path
        / "model-assets"
        / "specifications"
        / "moex-dams"
        / "0.1"
    )
    catalog_dir.mkdir(parents=True)
    path = catalog_dir / "architecture-catalog.yaml"
    path.write_text(
        yaml.dump(
            {
                "kind": "architecture_catalog",
                "version": "1",
                "nodes": [
                    {
                        "id": "spec-a",
                        "role": "reference_specification",
                        "title": "Spec A",
                        "expressed_in": "LinkML",
                        "module_id": "moex:module:a",
                    },
                    {
                        "id": "impl-a",
                        "role": "specification_implementation",
                        "title": "Impl A",
                        "conforms_to": "spec-a",
                        "module_id": "moex:module:b",
                    },
                ],
            }
        ),
        encoding="utf-8",
    )
    catalog = load_architecture_catalog(tmp_path)
    assert catalog is not None
    validate_architecture_catalog(
        catalog, {"moex:module:a", "moex:module:b"}
    )
    assert catalog.nodes[1].conforms_to == "spec-a"
