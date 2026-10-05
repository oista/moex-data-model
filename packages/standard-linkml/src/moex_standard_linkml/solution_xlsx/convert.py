"""High-level convert API (no moex_dams imports)."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from moex_standard_linkml.ingest.validate import ValidationResult, validate_model_package
from moex_standard_linkml.solution_xlsx.build import build_package
from moex_standard_linkml.solution_xlsx.diagnostics import (
    Diagnostic,
    Severity,
    strict_promote_warnings,
)
from moex_standard_linkml.solution_xlsx.envelope import build_solution_envelope
from moex_standard_linkml.solution_xlsx.profile import (
    SolutionXlsxProfile,
    load_solution_profile,
)
from moex_standard_linkml.solution_xlsx.report import (
    exit_code_for,
    format_console,
    write_report,
)
from moex_standard_linkml.solution_xlsx.rules import run_rules
from moex_standard_linkml.solution_xlsx.scaffold import write_publish_if_missing
from moex_standard_linkml.solution_xlsx.source import SourceError, load_solution_ir
from moex_standard_linkml.solution_xlsx.trace import TraceMap
from moex_standard_linkml.solution_xlsx.writer import write_yaml_safe


@dataclass
class ConvertResult:
    package: dict[str, Any] | None
    envelope: dict[str, Any] | None
    diagnostics: list[Diagnostic] = field(default_factory=list)
    trace: TraceMap = field(default_factory=TraceMap)
    package_path: Path | None = None
    envelope_path: Path | None = None
    publish_path: Path | None = None
    report_md: Path | None = None
    report_json: Path | None = None
    validation: ValidationResult | None = None
    io_skipped: bool = False
    src_system: str = ""
    slug: str = ""
    source_filename: str = ""
    source_sha256: str = ""

    @property
    def exit_code(self) -> int:
        return exit_code_for(self.diagnostics, io_skipped=self.io_skipped)


def convert_solution(
    *,
    xlsx: Path,
    profile: SolutionXlsxProfile | Path,
    src_system: str,
    out_dir: Path,
    report_dir: Path | None = None,
    force: bool = False,
    strict: bool = False,
    schema: Path | None = None,
    skip_validate: bool = False,
    write_publish: bool = True,
) -> ConvertResult:
    """Convert one SrcSystem from xlsx into solution YAML artifacts."""
    if not isinstance(profile, SolutionXlsxProfile):
        profile = load_solution_profile(profile)

    system = profile.system_for(src_system)
    if system is None:
        return ConvertResult(
            package=None,
            envelope=None,
            diagnostics=[
                Diagnostic(
                    code="SXI-SRC-002",
                    severity=Severity.ERROR,
                    message_ru=f"Неизвестная система '{src_system}' в профиле.",
                    remediation="Добавьте systems[] или исправьте --system.",
                )
            ],
            src_system=src_system,
        )

    report_dir = report_dir or (out_dir / "_import_report")
    report_dir.mkdir(parents=True, exist_ok=True)

    try:
        ir = load_solution_ir(xlsx, profile, src_system=src_system)
    except SourceError as exc:
        diags = [
            Diagnostic(
                code="SXI-SRC-001",
                severity=Severity.ERROR,
                message_ru=str(exc),
                remediation="Проверьте путь к xlsx и профиль листов.",
            )
        ]
        md, js = write_report(
            report_dir,
            title=f"Import {src_system}",
            diagnostics=diags,
        )
        return ConvertResult(
            package=None,
            envelope=None,
            diagnostics=diags,
            report_md=md,
            report_json=js,
            src_system=src_system,
            slug=system.slug,
        )

    diagnostics = run_rules(ir, profile, system)
    if strict:
        diagnostics = strict_promote_warnings(diagnostics)

    package, mapper_diags, trace, _map_result = build_package(ir, profile, system)
    diagnostics = list(diagnostics) + mapper_diags

    package_filename = f"{system.slug}-solution-model.yaml"
    package_path = out_dir / package_filename
    envelope_path = out_dir / "implementation.yaml"

    # Serialize to compute digest / write
    import yaml

    package_text = yaml.safe_dump(
        package, sort_keys=False, allow_unicode=True, default_flow_style=False
    )
    package_bytes = package_text.encode("utf-8")

    envelope = build_solution_envelope(
        profile=profile,
        system=system,
        package_filename=package_filename,
        package_bytes=package_bytes,
        source_filename=ir.source_filename,
        source_sha256=ir.source_sha256,
    )

    written_pkg, io_diag1 = write_yaml_safe(
        package, package_path, force=force, report_dir=report_dir
    )
    written_env, io_diag2 = write_yaml_safe(
        envelope, envelope_path, force=force, report_dir=report_dir, header_comment=True
    )
    io_skipped = False
    for d in (io_diag1, io_diag2):
        if d is not None:
            diagnostics.append(d)
            io_skipped = True

    publish_path = None
    if write_publish:
        publish_path = write_publish_if_missing(
            out_dir, system, package_filename=package_filename, force=False
        )

    validation = None
    if schema is not None and not skip_validate and written_pkg.is_file():
        validation = validate_model_package(written_pkg, schema)
        if not validation.ok:
            diagnostics.append(
                Diagnostic(
                    code="SXI-VAL-001",
                    severity=Severity.ERROR,
                    message_ru="LinkML validation ModelPackage не прошла.",
                    remediation=validation.stderr or validation.stdout or "см. validation",
                )
            )
            (report_dir / "validation.txt").write_text(
                validation.report, encoding="utf-8"
            )

    extras = {
        "system": system.src_system,
        "slug": system.slug,
        "source": ir.source_filename,
        "source_sha256": ir.source_sha256,
        "logical_entities": len(package.get("logical_entities") or []),
        "attributes": sum(
            len(e.get("attributes") or [])
            for e in (package.get("logical_entities") or [])
        ),
        "data_carriers": len(package.get("data_carriers") or []),
        "data_containers": len(package.get("data_containers") or []),
        "access_points": len(package.get("access_points") or []),
        "execution_assets": len(package.get("execution_assets") or []),
        "src_only_rows": len(ir.src_only),
        "package_path": str(written_pkg),
        "envelope_path": str(written_env),
    }
    md, js = write_report(
        report_dir,
        title=f"Import {system.src_system} → {system.slug}",
        diagnostics=diagnostics,
        extras=extras,
    )

    return ConvertResult(
        package=package,
        envelope=envelope,
        diagnostics=diagnostics,
        trace=trace,
        package_path=written_pkg,
        envelope_path=written_env,
        publish_path=publish_path,
        report_md=md,
        report_json=js,
        validation=validation,
        io_skipped=io_skipped,
        src_system=system.src_system,
        slug=system.slug,
        source_filename=ir.source_filename,
        source_sha256=ir.source_sha256,
    )


def convert_console_summary(result: ConvertResult) -> str:
    parts = [format_console(result.diagnostics)]
    if result.report_md:
        parts.append(f"report: {result.report_md}\n")
    if result.package_path:
        parts.append(f"package: {result.package_path}\n")
    return "".join(parts)
