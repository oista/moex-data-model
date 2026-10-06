"""Compute / verify DataModelBinding.integrity_digest (ADR-034)."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterator

import yaml

_SKIP_KEYS = frozenset({"integrity_digest", "generated_at"})


@dataclass(frozen=True)
class DigestMismatch:
    path: Path
    element_id: str | None
    expected: str | None
    actual: str
    message: str


@dataclass(frozen=True)
class DigestMatch:
    path: Path
    element_id: str | None
    digest: str


def compute_binding_digest(binding: dict[str, Any]) -> str:
    """Canonical sha256 over binding body excluding digest and generated_at."""
    payload = {k: v for k, v in binding.items() if k not in _SKIP_KEYS}
    canonical = json.dumps(payload, sort_keys=True, ensure_ascii=False, default=str)
    return "sha256:" + hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def iter_binding_docs(root: Path) -> Iterator[tuple[Path, dict[str, Any]]]:
    """Yield YAML mappings that look like DataModelBinding instances."""
    roots = [
        root / "model-assets" / "specifications" / "moex-dams" / "0.1" / "examples",
        root / "model-assets" / "implementations",
    ]
    seen: set[Path] = set()
    for base in roots:
        if not base.is_dir():
            continue
        for path in sorted(base.rglob("*.yaml")):
            resolved = path.resolve()
            if resolved in seen:
                continue
            seen.add(resolved)
            try:
                data = yaml.safe_load(path.read_text(encoding="utf-8"))
            except Exception:
                continue
            if not isinstance(data, dict):
                continue
            # Single binding document
            if "integrity_digest" in data and "selections" in data:
                yield path, data
                continue
            # Collection on a repository / package
            for item in data.get("data_model_bindings") or []:
                if isinstance(item, dict) and "integrity_digest" in item:
                    yield path, item


def verify_digests(
    root: Path,
    *,
    model: str | None = None,
) -> tuple[list[DigestMatch], list[DigestMismatch]]:
    matches: list[DigestMatch] = []
    mismatches: list[DigestMismatch] = []
    for path, binding in iter_binding_docs(root):
        element_id = binding.get("element_id")
        if isinstance(element_id, str):
            eid = element_id
        else:
            eid = None
        if model:
            hay = f"{path.as_posix()}|{eid or ''}"
            if model not in hay:
                continue
        actual = compute_binding_digest(binding)
        expected = binding.get("integrity_digest")
        expected_s = str(expected) if expected is not None else None
        if expected_s == actual:
            matches.append(DigestMatch(path=path, element_id=eid, digest=actual))
        else:
            mismatches.append(
                DigestMismatch(
                    path=path,
                    element_id=eid,
                    expected=expected_s,
                    actual=actual,
                    message=(
                        f"integrity_digest mismatch for {eid or path.name}: "
                        f"stored={expected_s!r} computed={actual!r}"
                    ),
                )
            )
    return matches, mismatches


def write_digests(
    root: Path,
    *,
    model: str | None = None,
    allow_non_demo: bool = False,
) -> list[DigestMatch]:
    """Recompute and write digests. Non-example paths require allow_non_demo."""
    written: list[DigestMatch] = []
    examples_root = (
        root / "model-assets" / "specifications" / "moex-dams" / "0.1" / "examples"
    ).resolve()
    for path, binding in list(iter_binding_docs(root)):
        element_id = binding.get("element_id")
        eid = element_id if isinstance(element_id, str) else None
        if model:
            hay = f"{path.as_posix()}|{eid or ''}"
            if model not in hay:
                continue
        is_example = (
            examples_root in path.resolve().parents
            or path.resolve().parent == examples_root
        )
        if not is_example and not allow_non_demo:
            raise ValueError(
                f"refusing to write digest for non-demo binding {eid or path} "
                f"(pass --allow-non-demo-write; see ADR-034)"
            )
        digest = compute_binding_digest(binding)
        text = path.read_text(encoding="utf-8")
        if "integrity_digest:" not in text:
            raise ValueError(f"no integrity_digest field in {path}")
        # Surgical replace keeps surrounding YAML formatting.
        import re

        new_text, n = re.subn(
            r"(?m)^(\s*integrity_digest:\s*).*$",
            rf"\g<1>{digest}",
            text,
            count=1,
        )
        if n != 1:
            raise ValueError(f"could not rewrite integrity_digest in {path}")
        path.write_text(new_text, encoding="utf-8")
        written.append(DigestMatch(path=path, element_id=eid, digest=digest))
    return written


__all__ = [
    "DigestMatch",
    "DigestMismatch",
    "compute_binding_digest",
    "iter_binding_docs",
    "verify_digests",
    "write_digests",
]
