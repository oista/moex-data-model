"""PR-2: LinkML module moex-repository-manifest loads, lints, and validates fixtures."""

from __future__ import annotations

import json
from pathlib import Path

import yaml
from linkml.linter.config.datamodel.config import RuleLevel
from linkml.linter.linter import Linter
from linkml_runtime.utils.schemaview import SchemaView

from moex_standard_linkml.validation import error_results, make_linkml_validator

REPO = Path(__file__).resolve().parents[2]
SCHEMA = (
    REPO
    / "model-assets"
    / "specifications"
    / "moex-repository-manifest"
    / "0.1"
    / "schemas"
    / "moex-repository-manifest.yaml"
)
EXAMPLES = SCHEMA.parents[1] / "examples"
LINT_CONFIG = REPO / ".linkmllint.yaml"


def test_schema_loads_and_has_tree_root() -> None:
    sv = SchemaView(str(SCHEMA))
    assert "RepositoryManifest" in sv.all_classes()
    assert sv.get_class("RepositoryManifest").tree_root is True
    assert "DocumentRef" in sv.all_classes()
    assert "RepositoryLockHeader" in sv.all_classes()
    assert "RepositoryLockEntry" in sv.all_classes()
    assert "package" in sv.get_enum("DocumentKindEnum").permissible_values


def test_schema_linter_no_errors() -> None:
    config: dict = {}
    if LINT_CONFIG.is_file():
        config = yaml.safe_load(LINT_CONFIG.read_text(encoding="utf-8")) or {}
    errors = [
        r
        for r in Linter(config).lint(str(SCHEMA))
        if getattr(r, "level", None) == RuleLevel.error
    ]
    assert errors == [], [getattr(e, "message", str(e)) for e in errors]


def test_valid_manifest_passes() -> None:
    data = yaml.safe_load((EXAMPLES / "valid-manifest.yaml").read_text(encoding="utf-8"))
    bad = error_results(
        make_linkml_validator(SCHEMA).validate(data, target_class="RepositoryManifest")
    )
    assert bad == []


def test_invalid_manifest_bad_owner_fails() -> None:
    data = yaml.safe_load(
        (EXAMPLES / "invalid-manifest-bad-owner.yaml").read_text(encoding="utf-8")
    )
    bad = error_results(
        make_linkml_validator(SCHEMA).validate(data, target_class="RepositoryManifest")
    )
    assert bad


def test_invalid_manifest_bad_path_fails() -> None:
    data = yaml.safe_load(
        (EXAMPLES / "invalid-manifest-bad-path.yaml").read_text(encoding="utf-8")
    )
    bad = error_results(
        make_linkml_validator(SCHEMA).validate(data, target_class="RepositoryManifest")
    )
    assert bad


def test_valid_lock_header_and_entry_pass() -> None:
    header = json.loads((EXAMPLES / "valid-lock-header.json").read_text(encoding="utf-8"))
    entry = json.loads((EXAMPLES / "valid-lock-entry.json").read_text(encoding="utf-8"))
    v = make_linkml_validator(SCHEMA)
    assert error_results(v.validate(header, target_class="RepositoryLockHeader")) == []
    assert error_results(v.validate(entry, target_class="RepositoryLockEntry")) == []


def test_invalid_lock_entry_hash_fails() -> None:
    entry = json.loads(
        (EXAMPLES / "invalid-lock-entry-hash.json").read_text(encoding="utf-8")
    )
    bad = error_results(
        make_linkml_validator(SCHEMA).validate(entry, target_class="RepositoryLockEntry")
    )
    assert bad


def test_not_under_dams_schemas_glob() -> None:
    """Guard: module must stay outside moex-dams/0.1/schemas (artifact generation)."""
    dams_schemas = (
        REPO
        / "model-assets"
        / "specifications"
        / "moex-dams"
        / "0.1"
        / "schemas"
    )
    assert SCHEMA.resolve().parent.resolve() != dams_schemas.resolve()
    assert not (dams_schemas / "moex-repository-manifest.yaml").exists()
