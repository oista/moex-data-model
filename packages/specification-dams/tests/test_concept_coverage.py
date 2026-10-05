"""Informational concept coverage report."""

from moex_dams.application.concept_coverage import compute_concept_coverage


def test_coverage_ratio_and_critical():
    pkgs = [
        {
            "name": "a",
            "solution_ref": "a",
            "conceptual_properties": [
                {"element_id": "dams:concept/C/p", "name": "p"},
                {"element_id": "dams:concept/C/orphan", "name": "orphan"},
            ],
            "logical_entities": [
                {
                    "attributes": [
                        {
                            "element_id": "dams:a/1",
                            "name": "inn",
                            "logical_type": "string",
                            "concept_ref": "dams:concept/C/p",
                        },
                        {
                            "element_id": "dams:a/2",
                            "name": "x",
                            "logical_type": "string",
                            "critical_data_element": True,
                        },
                    ]
                }
            ],
        },
        {
            "name": "b",
            "solution_ref": "b",
            "logical_entities": [
                {
                    "attributes": [
                        {
                            "element_id": "dams:b/1",
                            "name": "inn",
                            "logical_type": "string",
                        }
                    ]
                }
            ],
        },
    ]
    report = compute_concept_coverage(pkgs)
    assert report["attribute_count"] == 3
    assert report["with_concept_ref"] == 1
    assert "dams:a/2" in report["critical_without_concept_ref"]
    assert "dams:concept/C/orphan" in report["orphan_conceptual_properties"]
    assert any(c["name"] == "inn" for c in report["cross_solution_candidates"])
