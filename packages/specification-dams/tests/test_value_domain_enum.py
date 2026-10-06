"""ValueDomain → LinkML enum compilation."""

from moex_dams.application.value_domain_enum import value_domain_to_linkml_enum


def test_enumerated_with_meaning():
    domain = {
        "element_id": "dams:vd/status",
        "name": "StatusEnum",
        "value_domain_kind": "enumerated",
        "permissible_values": [
            {
                "value_code": "active",
                "value_label": "Active",
                "meaning_term_ref": "skos:example/active",
            },
            {"value_code": "retired", "value_label": "Retired"},
        ],
    }
    out = value_domain_to_linkml_enum(domain)
    assert out is not None
    enum = out["enums"]["StatusEnum"]
    assert enum["permissible_values"]["active"]["meaning"] == "skos:example/active"


def test_dynamic_query_reachable_from():
    domain = {
        "name": "FiboBranch",
        "value_domain_kind": "reference_set",
        "dynamic_query": {
            "source_ontology": "fibo:",
            "source_nodes": ["fibo:LegalPerson"],
            "relationship_types": ["rdfs:subClassOf"],
            "include_self": True,
        },
    }
    out = value_domain_to_linkml_enum(domain)
    assert out is not None
    assert "reachable_from" in out["enums"]["FiboBranch"]
