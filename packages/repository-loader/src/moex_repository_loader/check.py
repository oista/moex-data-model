"""Repository integrity checks (check-manifest)."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

import yaml

from moex_repository_loader.loader import IMPLEMENTATIONS_REL, RepositoryLoader
from moex_repository_loader.lock import lock_update_hint, verify_lock

OWNER_RE = re.compile(r"^@[\w.-]+(/[\w.-]+)?$")

ORPHAN_ALLOW_NAMES = frozenset(
    {
        "manifest.yaml",
        "manifest.lock",
        "publish.yaml",
        "solution-xlsx.profile.yaml",
        "moex-dams-full.yaml",
        # ontology catalog stubs under implementations/ontologies/
        "application.yaml",
        "corporate.yaml",
        "fibo.yaml",
        "moex-data.yaml",
        "moex-hr.yaml",
        "prov-o.yaml",
        # enterprise conceptual siblings
        "controlled-vocabularies.yaml",
        "data-types.yaml",
        "relation-terms.yaml",
        # draft import sidecar
        "inference-evidence.json",
    }
)
ORPHAN_ALLOW_DIR_NAMES = frozenset({"publications"})


@dataclass(frozen=True)
class CheckProblem:
    code: str
    message: str


def _is_allowed_orphan(rel_posix: str) -> bool:
    name = Path(rel_posix).name
    if name in ORPHAN_ALLOW_NAMES:
        return True
    parts = Path(rel_posix).parts
    if any(p in ORPHAN_ALLOW_DIR_NAMES for p in parts):
        return True
    if name == "publish.yaml":
        return True
    return False


def check_linkml_manifest(repo_root: Path) -> list[CheckProblem]:
    from moex_standard_linkml.validation import error_results, make_linkml_validator

    schema = (
        repo_root
        / "model-assets"
        / "specifications"
        / "moex-repository-manifest"
        / "0.1"
        / "schemas"
        / "moex-repository-manifest.yaml"
    )
    manifest_path = repo_root / IMPLEMENTATIONS_REL / "manifest.yaml"
    data = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    bad = error_results(
        make_linkml_validator(schema).validate(data, target_class="RepositoryManifest")
    )
    return [
        CheckProblem("linkml", f"manifest LinkML validation: {item}") for item in bad
    ]


def check_unique_ids_and_paths(loader: RepositoryLoader) -> list[CheckProblem]:
    problems: list[CheckProblem] = []
    seen: set[str] = set()
    root = loader.implementations_root.resolve()
    for ref in loader.load_manifest().documents:
        if ref.id in seen:
            problems.append(CheckProblem("unique_id", f"duplicate document id: {ref.id}"))
        seen.add(ref.id)
        if not OWNER_RE.match(ref.owner):
            problems.append(
                CheckProblem("owner", f"{ref.id}: invalid owner {ref.owner!r}")
            )
        rel = Path(ref.path)
        if ".." in rel.parts or rel.is_absolute():
            problems.append(
                CheckProblem("path", f"{ref.id}: path escapes root: {ref.path}")
            )
            continue
        full = (root / ref.path).resolve()
        try:
            full.relative_to(root)
        except ValueError:
            problems.append(
                CheckProblem("path", f"{ref.id}: path escapes root: {ref.path}")
            )
            continue
        if not full.is_file():
            problems.append(
                CheckProblem("path", f"{ref.id}: missing file: {ref.path}")
            )
    return problems


def check_depends_on(loader: RepositoryLoader) -> list[CheckProblem]:
    problems: list[CheckProblem] = []
    ids = set(loader.document_ids())
    for ref in loader.load_manifest().documents:
        for dep in ref.depends_on:
            if dep not in ids:
                problems.append(
                    CheckProblem(
                        "depends_on",
                        f"{ref.id}: depends_on unknown id {dep}",
                    )
                )
    return problems


def check_package_cycles(loader: RepositoryLoader) -> list[CheckProblem]:
    graph = {ref.id: list(ref.depends_on) for ref in loader.load_manifest().documents}
    visiting: set[str] = set()
    done: set[str] = set()
    problems: list[CheckProblem] = []

    def dfs(node: str, stack: list[str]) -> None:
        if node in done:
            return
        if node in visiting:
            cycle = " -> ".join(stack[stack.index(node) :] + [node])
            problems.append(CheckProblem("cycle", f"package dependency cycle: {cycle}"))
            return
        visiting.add(node)
        for nxt in graph.get(node, []):
            if nxt in graph:
                dfs(nxt, stack + [node])
        visiting.remove(node)
        done.add(node)

    for node in sorted(graph):
        dfs(node, [])
    return problems


def check_hashes(loader: RepositoryLoader) -> list[CheckProblem]:
    expected = loader.compute_all_hashes()
    msgs = verify_lock(loader.lock_path(), expected)
    out = [CheckProblem("hash", m) for m in msgs]
    if out:
        out.append(CheckProblem("hash", lock_update_hint()))
    return out


def check_orphans(loader: RepositoryLoader) -> list[CheckProblem]:
    problems: list[CheckProblem] = []
    root = loader.implementations_root
    indexed_envs = {
        ref.path.replace("\\", "/") for ref in loader.load_manifest().documents
    }
    # Every implementation.yaml must be indexed.
    for path in sorted(root.rglob("implementation.yaml")):
        rel = path.relative_to(root).as_posix()
        if rel not in indexed_envs:
            problems.append(
                CheckProblem("orphan", f"implementation.yaml not in manifest: {rel}")
            )
    # YAML files that are neither indexed envelopes, body_refs, nor allow-listed.
    body_paths: set[str] = set()
    for ref in loader.load_manifest().documents:
        env = yaml.safe_load((root / ref.path).read_text(encoding="utf-8"))
        if isinstance(env, dict):
            body = env.get("body_ref") or env.get("implementation_body")
            if body:
                body_paths.add((Path(ref.path).parent / str(body)).as_posix())

    for path in sorted(root.rglob("*.yaml")):
        rel = path.relative_to(root).as_posix()
        if rel in indexed_envs or rel in body_paths:
            continue
        if _is_allowed_orphan(rel):
            continue
        problems.append(CheckProblem("orphan", f"yaml outside manifest allow-list: {rel}"))
    return problems


def run_checks(repo_root: Path) -> list[CheckProblem]:
    loader = RepositoryLoader(repo_root, verify_hashes=False)
    problems: list[CheckProblem] = []
    problems.extend(check_linkml_manifest(repo_root))
    problems.extend(check_unique_ids_and_paths(loader))
    problems.extend(check_depends_on(loader))
    problems.extend(check_package_cycles(loader))
    problems.extend(check_hashes(loader))
    problems.extend(check_orphans(loader))
    return problems
