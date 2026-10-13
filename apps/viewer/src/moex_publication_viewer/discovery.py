"""Discover publish.yaml files under a repository root (ADR-054)."""

from __future__ import annotations

from pathlib import Path

import yaml

SKIP_DIR_NAMES = {
    ".git",
    ".venv",
    "venv",
    "dist",
    "node_modules",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    "egg-info",
}

IMPLEMENTATIONS_REL = Path("model-assets") / "implementations"
MANIFEST_NAME = "manifest.yaml"


def _should_skip(path: Path) -> bool:
    return any(
        part in SKIP_DIR_NAMES or part.endswith(".egg-info") for part in path.parts
    )


def rglob_publish_paths(root: Path) -> list[Path]:
    """Return sorted paths to publish.yaml via filesystem walk (skip ignored dirs)."""
    root = root.resolve()
    found: list[Path] = []
    for path in root.rglob("publish.yaml"):
        if not path.is_file():
            continue
        if _should_skip(path):
            continue
        found.append(path)
    return sorted(found)


def discover_implementation_publish_paths(root: Path) -> list[Path] | None:
    """Publish modules for packages indexed in repository manifest (ADR-054 D3).

    For each ``kind: package`` DocumentRef whose path ends with
    ``implementation.yaml``, look for a sibling ``publish.yaml``. Returns
    ``None`` when ``manifest.yaml`` is absent (caller falls back to rglob).
    """
    root = root.resolve()
    impl_root = root / IMPLEMENTATIONS_REL
    manifest_path = impl_root / MANIFEST_NAME
    if not manifest_path.is_file():
        return None
    raw = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        return None
    found: list[Path] = []
    for item in raw.get("documents") or []:
        if not isinstance(item, dict):
            continue
        if item.get("kind") != "package":
            continue
        env_rel = str(item.get("path") or "").replace("\\", "/")
        if not env_rel.endswith("implementation.yaml"):
            continue
        publish = (impl_root / Path(env_rel).parent / "publish.yaml").resolve()
        if publish.is_file():
            found.append(publish)
    return sorted(found)


def implementation_publish_paths_via_rglob(root: Path) -> list[Path]:
    """Subset of rglob publish.yaml that live under model-assets/implementations/."""
    root = root.resolve()
    impl_root = (root / IMPLEMENTATIONS_REL).resolve()
    if not impl_root.is_dir():
        return []
    return [
        p
        for p in rglob_publish_paths(root)
        if _is_under(p, impl_root)
    ]


def _is_under(path: Path, parent: Path) -> bool:
    try:
        path.resolve().relative_to(parent)
        return True
    except ValueError:
        return False


def discover_manifest_paths(root: Path) -> list[Path]:
    """Return sorted paths to publish.yaml for the publication viewer.

    Under ``model-assets/implementations/``, prefer paths derived from the
    repository manifest (ADR-054). Outside that tree, keep ``rglob``. When the
    manifest is missing, fall back to full rglob.
    """
    root = root.resolve()
    rglob_all = rglob_publish_paths(root)
    derived = discover_implementation_publish_paths(root)
    if derived is None:
        return rglob_all
    impl_root = (root / IMPLEMENTATIONS_REL).resolve()
    outside = [p for p in rglob_all if not _is_under(p, impl_root)]
    return sorted({*outside, *derived})
