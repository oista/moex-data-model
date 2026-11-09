"""The models-repository path list covers model-assets and does not overlap."""

from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "scripts"))

from export_models_repo import (  # noqa: E402
    REPO_ROOT,
    TEMPLATE_DIR,
    load_paths,
    verify_steps,
)

MODEL_ASSETS = REPO_ROOT / "model-assets"


def test_every_model_assets_directory_has_one_owner() -> None:
    spec = load_paths()
    owned = {
        Path(rel).relative_to("model-assets").parts[0]
        for rel in (*spec["gitlab_owned"], *spec["code_owned"])
        if rel.startswith("model-assets/")
    }
    actual = {path.name for path in MODEL_ASSETS.iterdir() if path.is_dir()}
    assert actual == owned


def test_owners_do_not_overlap() -> None:
    spec = load_paths()
    gitlab = set(spec["gitlab_owned"])
    code = set(spec["code_owned"])
    assert not gitlab & code
    for left in gitlab:
        for right in code:
            assert left != right
            assert not left.startswith(right + "/")
            assert not right.startswith(left + "/")


def test_excluded_roots_are_not_exported_wholesale() -> None:
    spec = load_paths()
    exported = set(spec["gitlab_owned"]) | set(spec["code_owned"])
    assert not exported & set(spec["exclude"])
    under_packages = sorted(
        rel for rel in exported if rel == "packages" or rel.startswith("packages/")
    )
    assert under_packages == [
        "packages/ontology/publications",
        "packages/ontology/publish.yaml",
    ]


def test_root_templates_exist() -> None:
    spec = load_paths()
    for name in spec["root_files"]:
        assert (TEMPLATE_DIR / name).is_file(), name


def test_verify_runs_only_models_check_commands() -> None:
    template = (TEMPLATE_DIR / ".gitlab-ci.yml").read_text(encoding="utf-8")
    for cmd in verify_steps("python", Path("tree")):
        module = cmd[2]
        if module == "moex_model_cli":
            words = []
            for arg in cmd[3:]:
                if arg.startswith("--"):
                    break
                words.append(arg)
            needle = "moex-model " + " ".join(words)
        else:
            needle = f"python -m {module}"
        assert needle in template, needle
