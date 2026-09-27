"""Normalizer registry."""

from __future__ import annotations

from moex_publication_viewer.normalizers.csv_normalizer import CsvNormalizer
from moex_publication_viewer.normalizers.json_normalizer import JsonNormalizer
from moex_publication_viewer.normalizers.linkml_normalizer import LinkmlNormalizer
from moex_publication_viewer.normalizers.markdown_normalizer import MarkdownNormalizer
from moex_publication_viewer.normalizers.yaml_normalizer import YamlNormalizer

_REGISTRY = {
    "yaml": YamlNormalizer(),
    "json": JsonNormalizer(),
    "csv": CsvNormalizer(),
    "markdown": MarkdownNormalizer(),
    "linkml-yaml": LinkmlNormalizer(),
}


def get_normalizer(fmt: str):
    if fmt not in _REGISTRY:
        raise KeyError(fmt)
    return _REGISTRY[fmt]
