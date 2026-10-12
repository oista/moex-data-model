"""ADR index README status column must match each ADR frontmatter status."""

from __future__ import annotations

import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
ADR_DIR = REPO / "docs" / "adr"
README = ADR_DIR / "README.md"

ROW_RE = re.compile(
    r"^\|\s*\[ADR-(\d{3})\]\((ADR-\d{3}-[^)]+\.md)\)\s*\|\s*[^|]*\|\s*(\w+)\s*\|",
    re.MULTILINE,
)
STATUS_RE = re.compile(r"^status:\s*(\S+)", re.MULTILINE)


def _frontmatter_status(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        raise AssertionError(f"{path.name}: missing YAML frontmatter")
    end = text.find("\n---\n", 4)
    assert end > 0, f"{path.name}: unclosed frontmatter"
    match = STATUS_RE.search(text[4:end])
    assert match, f"{path.name}: no status in frontmatter"
    return match.group(1)


def test_adr_readme_status_matches_frontmatter() -> None:
    readme = README.read_text(encoding="utf-8")
    rows = {num: (link, status) for num, link, status in ROW_RE.findall(readme)}
    assert rows, "no ADR rows found in docs/adr/README.md"

    adr_files = sorted(ADR_DIR.glob("ADR-*.md"))
    assert adr_files, "no ADR-*.md files"

    missing_in_readme: list[str] = []
    mismatches: list[str] = []
    for path in adr_files:
        match = re.match(r"ADR-(\d{3})-", path.name)
        if match is None:
            continue
        num = match.group(1)
        fm_status = _frontmatter_status(path)
        if num not in rows:
            missing_in_readme.append(path.name)
            continue
        link, readme_status = rows[num]
        if link != path.name:
            mismatches.append(f"ADR-{num}: README link {link} != {path.name}")
        if readme_status != fm_status:
            mismatches.append(
                f"ADR-{num}: README status {readme_status!r} != frontmatter {fm_status!r}"
            )

    extra_in_readme = sorted(set(rows) - {re.match(r"ADR-(\d{3})-", p.name).group(1) for p in adr_files if re.match(r"ADR-(\d{3})-", p.name)})
    assert not missing_in_readme, f"ADRs missing from README: {missing_in_readme}"
    assert not extra_in_readme, f"README rows without ADR files: {extra_in_readme}"
    assert not mismatches, "ADR README / frontmatter mismatches:\n" + "\n".join(mismatches)


def test_accepted_adrs_do_not_claim_superseded_by_modeling_architecture() -> None:
    offenders: list[str] = []
    for path in sorted(ADR_DIR.glob("ADR-*.md")):
        text = path.read_text(encoding="utf-8")
        if not text.startswith("---\n"):
            continue
        end = text.find("\n---\n", 4)
        fm = text[4:end]
        status_m = STATUS_RE.search(fm)
        if not status_m or status_m.group(1) != "Accepted":
            continue
        if re.search(r"^superseded_by:\s*MODELING_ARCHITECTURE\.md\s*$", fm, re.M):
            offenders.append(path.name)
    assert not offenders, (
        "Accepted ADRs must not use superseded_by: MODELING_ARCHITECTURE.md:\n"
        + "\n".join(offenders)
    )
