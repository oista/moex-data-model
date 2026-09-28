"""CURIE/URI identifier rules."""

from __future__ import annotations

from pathlib import Path

import yaml
from moex_standard_linkml.domain.body import LinkMLImplementationBody

from moex_dams.rules.identifiers import (
    build_dams_curie_resolver,
    check_identifiers,
    load_schema_prefix_map,
)


def test_load_schema_prefix_map_has_dams(dams_schema: Path) -> None:
    prefixes, default = load_schema_prefix_map(dams_schema)
    assert "dams" in prefixes
    assert prefixes["dams"].startswith("https://")
    assert default == "dams"


def test_trading_ids_pass_identifier_check(
    dams_schema: Path, trading_solution: Path
) -> None:
    resolver = build_dams_curie_resolver(dams_schema)
    data = yaml.safe_load(trading_solution.read_text(encoding="utf-8"))
    body = LinkMLImplementationBody(
        source_path=str(trading_solution),
        target_class="ModelPackage",
        data=data,
    )
    diags = check_identifiers(body, resolver=resolver)
    assert diags == ()


def test_unknown_prefix_emits_moex_id_001(dams_schema: Path) -> None:
    resolver = build_dams_curie_resolver(dams_schema)
    body = LinkMLImplementationBody(
        source_path="mini.yaml",
        target_class="ModelPackage",
        data={
            "element_id": "dams:model/mini/1.0.0",
            "name": "mini",
            "logical_entities": [
                {
                    "element_id": "zzz:logical/Bad",
                    "name": "Bad",
                    "attributes": [],
                }
            ],
        },
    )
    diags = check_identifiers(body, resolver=resolver)
    codes = [d.diagnostic_code for d in diags]
    assert "MOEX-ID-001" in codes
    assert any("zzz" in d.diagnostic_message for d in diags)
