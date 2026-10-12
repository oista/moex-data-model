from __future__ import annotations

import textwrap
from pathlib import Path

import yaml

from moex_repository_loader.check import (
    check_depends_on,
    check_hashes,
    check_orphans,
    check_package_cycles,
    check_unique_ids_and_paths,
    run_checks,
)
from moex_repository_loader.loader import RepositoryLoader
from moex_repository_loader.lock import write_lock

REPO = Path(__file__).resolve().parents[3]


def _write_mini_repo(tmp: Path, *, depends: list[str] | None = None, owner: str = "@moex/a") -> Path:
    impl = tmp / "model-assets" / "implementations"
    pkg = impl / "pkg"
    pkg.mkdir(parents=True)
    (pkg / "body.yaml").write_text(
        "element_id: dams:model/pkg\nname: pkg\n",
        encoding="utf-8",
    )
    (pkg / "implementation.yaml").write_text(
        textwrap.dedent(
            """\
            id: moex:implementation:pkg:0.1
            version: 0.1
            body_ref: body.yaml
            content_digest: sha256:dead
            revision: dead
            """
        ),
        encoding="utf-8",
    )
    doc = {
        "id": "moex:implementation:pkg:0.1",
        "kind": "package",
        "path": "pkg/implementation.yaml",
        "version": "0.1",
        "owner": owner,
    }
    if depends is not None:
        doc["depends_on"] = depends
    manifest = {
        "manifest_schema_version": "0.1.0",
        "repository_id": "moex:repository:test",
        "documents": [doc],
    }
    (impl / "manifest.yaml").write_text(
        yaml.dump(manifest, allow_unicode=True, sort_keys=False),
        encoding="utf-8",
    )
    loader = RepositoryLoader(tmp, verify_hashes=False)
    write_lock(loader.lock_path(), loader.compute_all_hashes())
    return tmp


def test_real_repo_check_ok() -> None:
    assert run_checks(REPO) == []


def test_depends_on_missing_id(tmp_path: Path) -> None:
    root = _write_mini_repo(tmp_path, depends=["moex:implementation:missing:0.1"])
    loader = RepositoryLoader(root, verify_hashes=False)
    problems = check_depends_on(loader)
    assert any(p.code == "depends_on" for p in problems)


def test_depends_on_ok(tmp_path: Path) -> None:
    root = _write_mini_repo(tmp_path, depends=[])
    loader = RepositoryLoader(root, verify_hashes=False)
    assert check_depends_on(loader) == []


def test_hash_mismatch(tmp_path: Path) -> None:
    root = _write_mini_repo(tmp_path)
    loader = RepositoryLoader(root, verify_hashes=False)
    write_lock(
        loader.lock_path(),
        {loader.document_ids()[0]: "sha256:" + ("0" * 64)},
    )
    problems = check_hashes(loader)
    assert any(p.code == "hash" for p in problems)
    assert any("lock update" in p.message for p in problems)


def test_hash_ok(tmp_path: Path) -> None:
    root = _write_mini_repo(tmp_path)
    loader = RepositoryLoader(root, verify_hashes=False)
    assert check_hashes(loader) == []


def test_orphan_implementation(tmp_path: Path) -> None:
    root = _write_mini_repo(tmp_path)
    orphan = root / "model-assets" / "implementations" / "other"
    orphan.mkdir()
    (orphan / "implementation.yaml").write_text("id: x\nbody_ref: b.yaml\n", encoding="utf-8")
    loader = RepositoryLoader(root, verify_hashes=False)
    problems = check_orphans(loader)
    assert any(p.code == "orphan" and "other" in p.message for p in problems)


def test_no_orphan_when_allowlisted(tmp_path: Path) -> None:
    root = _write_mini_repo(tmp_path)
    (root / "model-assets" / "implementations" / "publish.yaml").write_text(
        "kind: publication_module\n", encoding="utf-8"
    )
    loader = RepositoryLoader(root, verify_hashes=False)
    assert check_orphans(loader) == []


def test_cycle_detected(tmp_path: Path) -> None:
    impl = tmp_path / "model-assets" / "implementations"
    for name, dep in (("a", "moex:implementation:b:0.1"), ("b", "moex:implementation:a:0.1")):
        d = impl / name
        d.mkdir(parents=True)
        (d / "body.yaml").write_text(f"element_id: dams:model/{name}\n", encoding="utf-8")
        (d / "implementation.yaml").write_text(
            f"id: moex:implementation:{name}:0.1\nversion: 0.1\nbody_ref: body.yaml\n",
            encoding="utf-8",
        )
    manifest = {
        "manifest_schema_version": "0.1.0",
        "repository_id": "moex:repository:test",
        "documents": [
            {
                "id": "moex:implementation:a:0.1",
                "kind": "package",
                "path": "a/implementation.yaml",
                "version": "0.1",
                "owner": "@moex/a",
                "depends_on": ["moex:implementation:b:0.1"],
            },
            {
                "id": "moex:implementation:b:0.1",
                "kind": "package",
                "path": "b/implementation.yaml",
                "version": "0.1",
                "owner": "@moex/a",
                "depends_on": ["moex:implementation:a:0.1"],
            },
        ],
    }
    (impl / "manifest.yaml").write_text(yaml.dump(manifest), encoding="utf-8")
    loader = RepositoryLoader(tmp_path, verify_hashes=False)
    write_lock(loader.lock_path(), loader.compute_all_hashes())
    problems = check_package_cycles(loader)
    assert any(p.code == "cycle" for p in problems)


def test_no_cycle(tmp_path: Path) -> None:
    root = _write_mini_repo(tmp_path, depends=[])
    loader = RepositoryLoader(root, verify_hashes=False)
    assert check_package_cycles(loader) == []


def test_bad_owner(tmp_path: Path) -> None:
    root = _write_mini_repo(tmp_path, owner="not-a-handle")
    loader = RepositoryLoader(root, verify_hashes=False)
    problems = check_unique_ids_and_paths(loader)
    assert any(p.code == "owner" for p in problems)


def test_unique_paths_ok(tmp_path: Path) -> None:
    root = _write_mini_repo(tmp_path)
    loader = RepositoryLoader(root, verify_hashes=False)
    assert check_unique_ids_and_paths(loader) == []
