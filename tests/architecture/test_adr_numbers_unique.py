"""ADR files under docs/adr/ must have unique numbers (ADR-NNN-*.md)."""

from __future__ import annotations

import re
from collections import defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
ADR_DIR = REPO / "docs" / "adr"
ADR_FILE_RE = re.compile(r"^ADR-(\d{3})-.+\.md$", re.IGNORECASE)


def test_adr_numbers_are_unique() -> None:
    by_number: dict[str, list[str]] = defaultdict(list)
    for path in sorted(ADR_DIR.glob("ADR-*.md")):
        match = ADR_FILE_RE.match(path.name)
        if match is None:
            continue
        by_number[match.group(1)].append(path.name)

    duplicates = {n: names for n, names in by_number.items() if len(names) > 1}
    assert not duplicates, (
        "duplicate ADR numbers:\n"
        + "\n".join(
            f"  ADR-{n}: {', '.join(names)}"
            for n, names in sorted(duplicates.items())
        )
    )
