"""Guard: DAMS code must not read/write the removed polymorphic ``mappings`` key.

ADR-046 PR-5 removed ``ModelPackage.mappings`` in favour of the typed
collections (``realizes_mappings``, ``entity_physical_mappings``,
``field_mappings``, ``aligns_with_mappings``). Readers go through
``moex_dams.mappings.iter_mappings``; writers pick a collection by
``mapping_type``.
"""

from __future__ import annotations

import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]

# ``["mappings"]``, ``.get("mappings")``, ``setdefault("mappings"``.
LEGACY_KEY_RE = re.compile(
    r"""get\(\s*["']mappings["']"""
    r"""|\[\s*["']mappings["']\s*\]"""
    r"""|setdefault\(\s*["']mappings["']"""
)

SCAN_GLOBS = (
    "packages/*/src/**/*.py",
    "apps/*/src/**/*.py",
    "tools/*/src/**/*.py",
    "scripts/*.py",
)

# Posix paths relative to the repo root where the literal is intentional.
ALLOWLIST = {
    # SSSOM / SKOS glossary files use their own top-level ``mappings`` list.
    "packages/semantic-mappings/src/moex_semantic_mappings/skos_glossary.py",
    "packages/semantic-mappings/src/moex_semantic_mappings/sssom_adapter.py",
    # One-shot migrations for pre-3.1.0 data (read legacy ``mappings`` only).
    "scripts/migrate_mapping_labels.py",
    "scripts/migrate_physical_field_to_schema_node.py",
}


def _scan() -> list[str]:
    offenders: list[str] = []
    for pattern in SCAN_GLOBS:
        for path in REPO.glob(pattern):
            rel = path.relative_to(REPO).as_posix()
            if rel in ALLOWLIST or ".venv" in path.parts:
                continue
            text = path.read_text(encoding="utf-8")
            for i, line in enumerate(text.splitlines(), start=1):
                if LEGACY_KEY_RE.search(line):
                    offenders.append(f"{rel}:{i}: {line.strip()}")
    return offenders


def test_no_legacy_mappings_key_in_code() -> None:
    offenders = _scan()
    assert not offenders, (
        "Legacy polymorphic 'mappings' key outside allowlist "
        "(use typed collections / iter_mappings):\n" + "\n".join(offenders)
    )


def test_allowlisted_files_exist() -> None:
    missing = [rel for rel in sorted(ALLOWLIST) if not (REPO / rel).is_file()]
    assert not missing, f"stale allowlist entries: {missing}"
