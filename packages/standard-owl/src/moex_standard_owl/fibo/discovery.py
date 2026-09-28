"""Discover RDF files under selected FIBO domain directories."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path

from moex_standard_owl.fibo.constants import EXAMPLES_DOMAIN, SKIP_DIR_NAMES

logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class DiscoveredFile:
    path: Path
    module_path: str  # relative to source root, POSIX-style
    domain: str


def discover_rdf_files(
    source_root: Path,
    domains: list[str],
    *,
    include_examples: bool = False,
) -> list[DiscoveredFile]:
    """
    Find ``.rdf`` files only inside selected top-level domain directories.

    Skips ``.github``, ``etc``, and other service directories.
    Root-level About/Load files outside domains are never included.
    ``EXMP`` is included only when ``include_examples`` is True or
    ``EXMP`` is explicitly listed in ``domains``.
    """
    effective = list(domains)
    if include_examples and EXAMPLES_DOMAIN not in effective:
        effective.append(EXAMPLES_DOMAIN)
    if not include_examples:
        effective = [d for d in effective if d != EXAMPLES_DOMAIN]

    found: list[DiscoveredFile] = []
    for domain in effective:
        domain_dir = source_root / domain
        if not domain_dir.is_dir():
            logger.warning("Domain directory missing, skipping: %s", domain_dir)
            continue
        logger.info("Scanning domain %s under %s", domain, domain_dir)
        for rdf_path in sorted(domain_dir.rglob("*.rdf")):
            if not rdf_path.is_file():
                continue
            if _should_skip(rdf_path, source_root):
                continue
            rel = rdf_path.relative_to(source_root).as_posix()
            found.append(
                DiscoveredFile(path=rdf_path, module_path=rel, domain=domain)
            )

    found.sort(key=lambda f: f.module_path)
    logger.info("Found %d RDF file(s) across %d domain(s)", len(found), len(effective))
    return found


def _should_skip(path: Path, source_root: Path) -> bool:
    try:
        relative = path.relative_to(source_root)
    except ValueError:
        return True
    for part in relative.parts[:-1]:  # exclude filename
        if part in SKIP_DIR_NAMES or part.startswith("."):
            return True
    return False
