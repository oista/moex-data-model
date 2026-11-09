"""ci-validate — validate every implementation from manifest; enforce warning budget."""

from __future__ import annotations

import json
import subprocess
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any
from xml.etree.ElementTree import Element, SubElement, tostring

import yaml

from moex_dams.application.assess import assess_implementation
from moex_modeling import DiagnosticSeverity, diagnostic_to_wire
from moex_model_cli.bootstrap import (
    SlicePaths,
    resolve_body_from_implementation_envelope,
)
from moex_repository_loader.loader import RepositoryLoader

SOFT_SEVERITIES = frozenset(
    {DiagnosticSeverity.WARNING, DiagnosticSeverity.INFO}
)
HARD_SEVERITIES = frozenset(
    {DiagnosticSeverity.ERROR, DiagnosticSeverity.FATAL}
)

DEFAULT_BASELINE_REL = Path(".moex") / "warning-baseline.yaml"


@dataclass(frozen=True)
class SoftFingerprint:
    implementation_id: str
    code: str
    subject: str

    def as_dict(self) -> dict[str, str]:
        return {
            "implementation_id": self.implementation_id,
            "code": self.code,
            "subject": self.subject,
        }

    @classmethod
    def from_dict(cls, raw: dict[str, Any]) -> SoftFingerprint:
        return cls(
            implementation_id=str(raw["implementation_id"]),
            code=str(raw["code"]),
            subject=str(raw.get("subject") or ""),
        )

    def key(self) -> tuple[str, str, str]:
        return (self.implementation_id, self.code, self.subject)


@dataclass
class ImplResult:
    implementation_id: str
    path: str
    overall: str
    is_conformant: bool
    hard: list[dict[str, Any]] = field(default_factory=list)
    soft: list[dict[str, Any]] = field(default_factory=list)
    soft_fps: list[SoftFingerprint] = field(default_factory=list)


# Solutions that currently pass full assess; others are reported but do not
# fail the gate until they are added here (Stage 1).
DEFAULT_GATE_IMPLEMENTATIONS = (
    "moex:implementation:crm:0.1.0",
    "moex:implementation:esed:0.1.0",
    "moex:implementation:mdm:0.1.0",
    "moex:implementation:ucd:0.1.0",
)


@dataclass
class Baseline:
    version: int
    fingerprints: list[SoftFingerprint]
    counts_by_code: dict[str, dict[str, int]]
    gate_implementations: list[str] = field(
        default_factory=lambda: list(DEFAULT_GATE_IMPLEMENTATIONS)
    )

    def fingerprint_set(self) -> set[tuple[str, str, str]]:
        return {fp.key() for fp in self.fingerprints}

    def count_for(self, implementation_id: str, code: str) -> int:
        return int(self.counts_by_code.get(implementation_id, {}).get(code, 0))

    def total_soft(self) -> int:
        return len(self.fingerprints)

    def is_gated(self, implementation_id: str) -> bool:
        return implementation_id in set(self.gate_implementations)

    def to_dict(self) -> dict[str, Any]:
        counts: dict[str, dict[str, int]] = {}
        for impl_id, by_code in sorted(self.counts_by_code.items()):
            counts[impl_id] = {
                code: count for code, count in sorted(by_code.items()) if count > 0
            }
        return {
            "version": self.version,
            "gate_implementations": list(self.gate_implementations),
            "fingerprints": [
                fp.as_dict()
                for fp in sorted(
                    self.fingerprints,
                    key=lambda f: (f.implementation_id, f.code, f.subject),
                )
            ],
            "counts_by_code": {
                impl_id: by_code
                for impl_id, by_code in sorted(counts.items())
                if by_code
            },
        }


def baseline_from_soft(
    fps: list[SoftFingerprint],
    *,
    version: int = 1,
    gate_implementations: list[str] | None = None,
) -> Baseline:
    counts: dict[str, dict[str, int]] = {}
    for fp in fps:
        by_code = counts.setdefault(fp.implementation_id, {})
        by_code[fp.code] = by_code.get(fp.code, 0) + 1
    # Deduplicate fingerprints (same triple once).
    unique = {fp.key(): fp for fp in fps}
    return Baseline(
        version=version,
        fingerprints=list(unique.values()),
        counts_by_code=counts,
        gate_implementations=list(
            gate_implementations
            if gate_implementations is not None
            else DEFAULT_GATE_IMPLEMENTATIONS
        ),
    )


def load_baseline(path: Path) -> Baseline:
    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError(f"baseline must be a mapping: {path}")
    fps = [
        SoftFingerprint.from_dict(item)
        for item in (raw.get("fingerprints") or [])
        if isinstance(item, dict)
    ]
    counts_raw = raw.get("counts_by_code") or {}
    counts: dict[str, dict[str, int]] = {}
    if isinstance(counts_raw, dict):
        for impl_id, by_code in counts_raw.items():
            if not isinstance(by_code, dict):
                continue
            counts[str(impl_id)] = {
                str(code): int(count) for code, count in by_code.items()
            }
    else:
        counts = baseline_from_soft(fps).counts_by_code
    gate_raw = raw.get("gate_implementations")
    gate = (
        [str(x) for x in gate_raw]
        if isinstance(gate_raw, list) and gate_raw
        else list(DEFAULT_GATE_IMPLEMENTATIONS)
    )
    return Baseline(
        version=int(raw.get("version") or 1),
        fingerprints=fps,
        counts_by_code=counts,
        gate_implementations=gate,
    )


def write_baseline(path: Path, baseline: Baseline) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        yaml.safe_dump(
            baseline.to_dict(),
            allow_unicode=True,
            sort_keys=False,
            default_flow_style=False,
        ),
        encoding="utf-8",
    )


def _soft_fp(implementation_id: str, wire: dict[str, Any]) -> SoftFingerprint:
    return SoftFingerprint(
        implementation_id=implementation_id,
        code=str(wire.get("code") or ""),
        subject=str(wire.get("element_id") or ""),
    )


def validate_all(repo_root: Path) -> list[ImplResult]:
    loader = RepositoryLoader(repo_root, verify_hashes=False)
    manifest = loader.load_manifest()
    schema = SlicePaths.resolve(root=repo_root).schema
    results: list[ImplResult] = []
    for ref in manifest.documents:
        envelope = loader.implementations_root / ref.path
        body = resolve_body_from_implementation_envelope(envelope)
        slice_result = assess_implementation(
            schema_path=schema,
            implementation_path=body,
            implementation_id=ref.id,
        )
        hard: list[dict[str, Any]] = []
        soft: list[dict[str, Any]] = []
        soft_fps: list[SoftFingerprint] = []
        for assessment in slice_result.report.assessments:
            for diag in assessment.diagnostics:
                wire = diagnostic_to_wire(diag)
                if diag.severity in HARD_SEVERITIES:
                    hard.append(wire)
                elif diag.severity in SOFT_SEVERITIES:
                    soft.append(wire)
                    soft_fps.append(_soft_fp(ref.id, wire))
        results.append(
            ImplResult(
                implementation_id=ref.id,
                path=ref.path,
                overall=slice_result.report.overall_result.value,
                is_conformant=slice_result.report.is_conformant,
                hard=hard,
                soft=soft,
                soft_fps=soft_fps,
            )
        )
    return results


def compare_to_baseline(
    results: list[ImplResult],
    baseline: Baseline,
) -> list[str]:
    """Return human-readable problems. Empty means OK.

    Hard errors and soft-budget growth only fail the gate for implementations
    listed in ``baseline.gate_implementations``. Other packages are still
    validated and appear in the JSON/JUnit report.
    """
    problems: list[str] = []
    known = baseline.fingerprint_set()
    observed_counts: dict[str, Counter[str]] = {}
    for result in results:
        gated = baseline.is_gated(result.implementation_id)
        if result.hard and gated:
            for diag in result.hard:
                problems.append(
                    f"error {result.implementation_id} "
                    f"{diag.get('code')}: {diag.get('message')}"
                )
        counter = observed_counts.setdefault(result.implementation_id, Counter())
        for fp in result.soft_fps:
            counter[fp.code] += 1
            if gated and fp.key() not in known:
                problems.append(
                    f"new soft diagnostic {fp.implementation_id} "
                    f"{fp.code} subject={fp.subject!r}"
                )
    for impl_id, counter in observed_counts.items():
        if not baseline.is_gated(impl_id):
            continue
        for code, count in counter.items():
            budget = baseline.count_for(impl_id, code)
            if count > budget:
                problems.append(
                    f"soft count grew {impl_id} {code}: {count} > baseline {budget}"
                )
    return problems


def baseline_grew(old: Baseline, new: Baseline) -> list[str]:
    problems: list[str] = []
    if new.total_soft() > old.total_soft():
        problems.append(
            f"baseline fingerprint count grew: {old.total_soft()} -> {new.total_soft()}"
        )
    old_counts = old.counts_by_code
    for impl_id, by_code in new.counts_by_code.items():
        for code, count in by_code.items():
            prev = int(old_counts.get(impl_id, {}).get(code, 0))
            if count > prev:
                problems.append(
                    f"baseline count grew {impl_id} {code}: {prev} -> {count}"
                )
    return problems


def load_baseline_from_git(repo_root: Path, ref: str, rel: Path) -> Baseline | None:
    """Load baseline file content from a git revision. None if missing."""
    posix = rel.as_posix()
    try:
        proc = subprocess.run(
            ["git", "show", f"{ref}:{posix}"],
            cwd=repo_root,
            capture_output=True,
            text=True,
            check=False,
        )
    except OSError:
        return None
    if proc.returncode != 0 or not proc.stdout.strip():
        return None
    raw = yaml.safe_load(proc.stdout)
    if not isinstance(raw, dict):
        return None
    fps = [
        SoftFingerprint.from_dict(item)
        for item in (raw.get("fingerprints") or [])
        if isinstance(item, dict)
    ]
    counts_raw = raw.get("counts_by_code") or {}
    counts: dict[str, dict[str, int]] = {}
    if isinstance(counts_raw, dict):
        for impl_id, by_code in counts_raw.items():
            if isinstance(by_code, dict):
                counts[str(impl_id)] = {
                    str(code): int(count) for code, count in by_code.items()
                }
    gate_raw = raw.get("gate_implementations")
    gate = (
        [str(x) for x in gate_raw]
        if isinstance(gate_raw, list) and gate_raw
        else list(DEFAULT_GATE_IMPLEMENTATIONS)
    )
    return Baseline(
        version=int(raw.get("version") or 1),
        fingerprints=fps,
        counts_by_code=counts or baseline_from_soft(fps).counts_by_code,
        gate_implementations=gate,
    )


def results_to_payload(results: list[ImplResult], problems: list[str]) -> dict[str, Any]:
    return {
        "implementations": [
            {
                "implementation_id": r.implementation_id,
                "path": r.path,
                "overall": r.overall,
                "is_conformant": r.is_conformant,
                "errors": r.hard,
                "soft": r.soft,
                "soft_count": len(r.soft_fps),
            }
            for r in results
        ],
        "problems": problems,
        "ok": not problems,
    }


def write_junit(path: Path, results: list[ImplResult], problems: list[str]) -> None:
    suites = Element("testsuites")
    for result in results:
        suite = SubElement(
            suites,
            "testsuite",
            name=result.implementation_id,
            tests=str(max(1, len(result.hard) + len(result.soft_fps))),
            failures=str(len(result.hard)),
        )
        if not result.hard and not result.soft_fps:
            SubElement(suite, "testcase", name="conformant", classname=result.implementation_id)
            continue
        for diag in result.hard:
            case = SubElement(
                suite,
                "testcase",
                name=str(diag.get("code") or "error"),
                classname=result.implementation_id,
            )
            failure = SubElement(case, "failure", message=str(diag.get("message") or ""))
            failure.text = str(diag.get("element_id") or "")
        for fp, diag in zip(result.soft_fps, result.soft, strict=False):
            case = SubElement(
                suite,
                "testcase",
                name=f"{fp.code}:{fp.subject}",
                classname=result.implementation_id,
            )
            # Soft diagnostics already in baseline are skipped; new ones marked later.
            if any(
                p.startswith(f"new soft diagnostic {fp.implementation_id} {fp.code}")
                and fp.subject in p
                for p in problems
            ):
                failure = SubElement(
                    case,
                    "failure",
                    message="new soft diagnostic outside baseline",
                )
                failure.text = str(diag.get("message") or "")
            else:
                skipped = SubElement(case, "skipped")
                skipped.set("message", "budgeted soft diagnostic")
    if problems:
        suite = SubElement(
            suites,
            "testsuite",
            name="baseline",
            tests=str(len(problems)),
            failures=str(len(problems)),
        )
        for problem in problems:
            case = SubElement(suite, "testcase", name=problem[:120], classname="baseline")
            failure = SubElement(case, "failure", message=problem)
            failure.text = problem
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(tostring(suites, encoding="utf-8", xml_declaration=True))


def write_codequality(
    path: Path,
    results: list[ImplResult],
    problems: list[str],
    *,
    gate_implementations: list[str] | None = None,
) -> None:
    gated = set(gate_implementations or DEFAULT_GATE_IMPLEMENTATIONS)
    findings: list[dict[str, Any]] = []
    for result in results:
        if result.implementation_id not in gated:
            continue
        for diag in result.hard:
            findings.append(
                {
                    "description": str(diag.get("message") or diag.get("code")),
                    "check_name": str(diag.get("code") or "error"),
                    "fingerprint": f"{result.implementation_id}|{diag.get('code')}|{diag.get('element_id') or ''}",
                    "severity": "critical",
                    "location": {
                        "path": result.path,
                        "lines": {"begin": int(diag.get("line") or 1)},
                    },
                }
            )
        for fp, diag in zip(result.soft_fps, result.soft, strict=False):
            if not any(
                p.startswith(f"new soft diagnostic {fp.implementation_id} {fp.code}")
                and fp.subject in p
                for p in problems
            ):
                continue
            findings.append(
                {
                    "description": str(diag.get("message") or fp.code),
                    "check_name": fp.code,
                    "fingerprint": f"{fp.implementation_id}|{fp.code}|{fp.subject}",
                    "severity": "minor",
                    "location": {
                        "path": result.path,
                        "lines": {"begin": int(diag.get("line") or 1)},
                    },
                }
            )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(findings, indent=2) + "\n", encoding="utf-8")


def run_ci_validate(
    repo_root: Path,
    *,
    baseline_path: Path | None = None,
    write_baseline_flag: bool = False,
    check_baseline_growth: bool = False,
    growth_base_ref: str | None = None,
    junit_path: Path | None = None,
    codequality_path: Path | None = None,
    as_json: bool = False,
) -> tuple[int, str]:
    root = repo_root.resolve()
    baseline_file = (
        baseline_path
        if baseline_path is not None
        else root / DEFAULT_BASELINE_REL
    )
    if baseline_path is not None and not baseline_path.is_absolute():
        baseline_file = (root / baseline_path).resolve()

    results = validate_all(root)
    all_soft = [fp for result in results for fp in result.soft_fps]

    if write_baseline_flag:
        baseline = baseline_from_soft(all_soft)
        write_baseline(baseline_file, baseline)
        msg = (
            f"wrote baseline {baseline_file.relative_to(root).as_posix()} "
            f"fingerprints={baseline.total_soft()}\n"
        )
        return 0, msg

    if not baseline_file.is_file():
        return 1, f"baseline missing: {baseline_file}\n"

    baseline = load_baseline(baseline_file)
    problems = compare_to_baseline(results, baseline)

    if check_baseline_growth:
        ref = growth_base_ref or ""
        if not ref:
            return 1, "check-baseline-growth requires --growth-base-ref\n"
        old = load_baseline_from_git(
            root, ref, baseline_file.relative_to(root)
        )
        if old is not None:
            problems.extend(baseline_grew(old, baseline))

    if junit_path is not None:
        out = junit_path if junit_path.is_absolute() else root / junit_path
        write_junit(out, results, problems)
    if codequality_path is not None:
        out = (
            codequality_path
            if codequality_path.is_absolute()
            else root / codequality_path
        )
        write_codequality(
            out,
            results,
            problems,
            gate_implementations=baseline.gate_implementations,
        )

    payload = results_to_payload(results, problems)
    if as_json:
        text = json.dumps(payload, indent=2) + "\n"
    else:
        lines = [
            f"ci-validate implementations={len(results)} "
            f"soft={sum(len(r.soft_fps) for r in results)} "
            f"problems={len(problems)}"
        ]
        for problem in problems:
            lines.append(f"  FAIL {problem}")
        if not problems:
            lines.append("ci-validate OK")
        text = "\n".join(lines) + "\n"
    return (1 if problems else 0), text
