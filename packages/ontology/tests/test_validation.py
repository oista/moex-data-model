"""Validation-focused tests."""

from pathlib import Path

import pytest

from ontology.fibo.constants import ALL_DOMAINS
from ontology.validation import ValidationError, validate_domains, validate_source_path


def test_validate_domains_rejects_unknown():
    with pytest.raises(ValidationError, match="Unknown domain"):
        validate_domains(["FND", "XYZ"], allowed=ALL_DOMAINS)


def test_validate_source_missing(tmp_path: Path):
    with pytest.raises(ValidationError, match="does not exist"):
        validate_source_path(tmp_path / "nope")
