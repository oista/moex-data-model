"""Tests for CurieUriResolver expand/compact."""

from __future__ import annotations

from moex_modeling import CurieUriResolver


def test_expand_and_compact_round_trip() -> None:
    r = CurieUriResolver(
        prefixes={
            "dams": "https://data.moex.com/dams/",
            "linkml": "https://w3id.org/linkml/",
        },
        default_prefix="dams",
    )
    assert r.expand("dams:model/trading/1.0.0") == (
        "https://data.moex.com/dams/model/trading/1.0.0"
    )
    assert r.compact("https://data.moex.com/dams/model/trading/1.0.0") == (
        "dams:model/trading/1.0.0"
    )
    assert r.expand("https://data.moex.com/dams/x") == "https://data.moex.com/dams/x"
    assert r.expand("bare-local") == "https://data.moex.com/dams/bare-local"


def test_unknown_prefix() -> None:
    r = CurieUriResolver(prefixes={"dams": "https://data.moex.com/dams/"})
    assert r.expand("moex:spec:dams") is None
    assert r.unknown_prefix("moex:spec:dams") == "moex"
    assert r.unknown_prefix("dams:ok") is None
    assert r.unknown_prefix("https://example.com/x") is None
    assert r.is_expandable("dams:ok") is True
    assert r.is_expandable("unknown:x") is False


def test_longest_prefix_wins_on_compact() -> None:
    r = CurieUriResolver(
        prefixes={
            "dams": "https://data.moex.com/dams/",
            "damsv": "https://data.moex.com/dams/v0.1/",
        }
    )
    assert r.compact("https://data.moex.com/dams/v0.1/Thing") == "damsv:Thing"
