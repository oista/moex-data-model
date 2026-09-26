"""Tests for RDF literal preference helpers."""

from rdflib import Literal

from ontology.constants import LABEL_JOIN
from ontology.literals import preferred_literal_values


def test_prefers_english_over_other_language():
    nodes = [
        Literal("Рабочий день", lang="ru"),
        Literal("Business Day", lang="en"),
    ]
    value, lang = preferred_literal_values(nodes)
    assert value == "Business Day"
    assert lang == "en"


def test_prefers_neutral_over_non_english():
    nodes = [
        Literal("Jour ouvrable", lang="fr"),
        Literal("Business Day"),
    ]
    value, lang = preferred_literal_values(nodes)
    assert value == "Business Day"
    assert lang is None


def test_multiple_english_labels_joined():
    nodes = [
        Literal("Calendar Period", lang="en"),
        Literal("Calendar Interval", lang="en"),
    ]
    value, lang = preferred_literal_values(nodes)
    assert lang == "en"
    parts = value.split(LABEL_JOIN)
    assert parts == ["Calendar Period", "Calendar Interval"]


def test_empty_nodes_returns_none():
    value, lang = preferred_literal_values([])
    assert value is None
    assert lang is None
