from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from architecture_check.kernel_policy import check_extension_policy

REPO_ROOT = Path(__file__).resolve().parents[3]
KERNEL = REPO_ROOT / "docs" / "architecture" / "modeling-kernel.yaml"


def test_real_kernel_passes_extension_policy():
    assert KERNEL.is_file()
    assert check_extension_policy(KERNEL) == []


def test_detects_linkml_class_when_policy_set(tmp_path: Path):
    bad = {
        "id": "https://example.com/bad",
        "name": "bad_kernel",
        "prefixes": {"linkml": "https://w3id.org/linkml/"},
        "imports": ["linkml:types"],
        "settings": {
            "extension_policy": "standard-specific-bodies-live-in-provider-schemas"
        },
        "classes": {
            "SpecificationImplementation": {
                "attributes": {"id": {"range": "string"}},
            },
            "LinkMLImplementation": {
                "is_a": "SpecificationImplementation",
            },
        },
    }
    path = tmp_path / "bad.yaml"
    path.write_text(yaml.dump(bad), encoding="utf-8")
    violations = check_extension_policy(path)
    assert "LinkMLImplementation" in violations
