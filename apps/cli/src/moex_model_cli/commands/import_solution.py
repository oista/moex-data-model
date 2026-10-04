"""import-solution — Object/ObjectAttribute xlsx → DAMS solution (ADR-022)."""

from __future__ import annotations

from pathlib import Path

from moex_model_cli.bootstrap import SlicePaths
from moex_standard_linkml.solution_xlsx.convert import convert_solution
from moex_standard_linkml.solution_xlsx.diagnostics import Diagnostic, Severity
from moex_standard_linkml.solution_xlsx.report import write_report
from moex_standard_linkml.solution_xlsx.trace import TraceMap


def _merge_assess_diagnostics(
    *,
    schema: Path,
    package_path: Path,
    implementation_id: str,
    trace: TraceMap,
) -> tuple[list[Diagnostic], object | None]:
    """Run moex_dams assess and map findings to SXI-style diagnostics."""
    from moex_dams.application.assess import assess_implementation

    result = assess_implementation(
        schema_path=schema,
        implementation_path=package_path,
        implementation_id=implementation_id,
    )
    out: list[Diagnostic] = []
    for assessment in result.report.assessments:
        for d in assessment.diagnostics:
            sev_raw = getattr(d.severity, "value", str(d.severity)).lower()
            if sev_raw in {"fatal"}:
                sev = Severity.ERROR
            elif sev_raw in {"error"}:
                sev = Severity.ERROR
            elif sev_raw in {"warning"}:
                sev = Severity.WARNING
            else:
                sev = Severity.INFO
            subject = getattr(d, "subject_ref", None) or getattr(d, "element_id", None)
            subject_s = str(subject) if subject else None
            code = getattr(d, "diagnostic_code", None) or "DAMS-ASSESS"
            msg = getattr(d, "diagnostic_message", None) or str(d)
            rem = ""
            details = getattr(d, "details", None) or []
            for det in details:
                if getattr(det, "detail_key", None) == "remediation":
                    rem = str(det.detail_value)
            out.append(
                Diagnostic(
                    code=f"ASSESS:{code}",
                    severity=sev,
                    message_ru=msg,
                    remediation=rem or "См. it-solution-requirements / formal_checks.",
                    source_ref=trace.resolve(subject_s),
                    element_ref=subject_s,
                )
            )
    return out, result


def _export_slice(
    *,
    schema: Path,
    package_path: Path,
    out_json: Path,
    implementation_id: str,
) -> None:
    from moex_publication.application.build_publication import export_slice_projection

    out_json.parent.mkdir(parents=True, exist_ok=True)
    export_slice_projection(
        schema_path=schema,
        implementation_path=package_path,
        out_path=out_json,
        implementation_id=implementation_id,
    )


def run_import_solution(
    paths: SlicePaths,
    *,
    xlsx: Path,
    system: str,
    profile: Path | None = None,
    out: Path | None = None,
    report_dir: Path | None = None,
    force: bool = False,
    strict: bool = False,
    skip_validate: bool = False,
    skip_assess: bool = False,
    skip_export: bool = False,
) -> tuple[int, str]:
    root = paths.root
    xlsx_path = xlsx if xlsx.is_absolute() else (root / xlsx).resolve()
    if not xlsx_path.is_file():
        return 2, f"xlsx not found: {xlsx_path}\n"

    profile_path = profile or (
        root
        / "model-assets"
        / "implementations"
        / "solutions"
        / "solution-xlsx.profile.yaml"
    )
    if not profile_path.is_absolute():
        profile_path = (root / profile_path).resolve()
    if not profile_path.is_file():
        return 2, f"profile not found: {profile_path}\n"

    # Resolve slug early via profile for default out dir
    from moex_standard_linkml.solution_xlsx.profile import load_solution_profile

    prof = load_solution_profile(profile_path)
    sys_cfg = prof.system_for(system)
    if sys_cfg is None:
        known = ", ".join(s.src_system for s in prof.systems)
        return 2, f"unknown --system {system!r}; expected one of: {known}\n"

    out_dir = out or (
        root / "model-assets" / "implementations" / "solutions" / sys_cfg.slug
    )
    if not out_dir.is_absolute():
        out_dir = (root / out_dir).resolve()

    report = report_dir or (root / "tmp" / "solution-import" / sys_cfg.slug)
    if not report.is_absolute():
        report = (root / report).resolve()

    schema = paths.schema
    result = convert_solution(
        xlsx=xlsx_path,
        profile=prof,
        src_system=system,
        out_dir=out_dir,
        report_dir=report,
        force=force,
        strict=strict,
        schema=schema if not skip_validate else None,
        skip_validate=skip_validate,
        write_publish=True,
    )

    lines = [
        f"import-solution system={result.src_system} slug={result.slug}",
        f"package={result.package_path}",
        f"envelope={result.envelope_path}",
    ]

    if result.package_path is None or result.package is None:
        write_report(
            report,
            title=f"Import {system} FAILED",
            diagnostics=result.diagnostics,
        )
        return result.exit_code or 1, "\n".join(lines) + "\n" + "\n".join(
            str(d) for d in result.diagnostics[:30]
        ) + "\n"

    impl_id = (
        (result.envelope or {}).get("id")
        or f"moex:implementation:{result.slug}:0.1.0"
    )

    all_diags = list(result.diagnostics)

    if not skip_assess and schema is not None and schema.is_file():
        try:
            assess_diags, slice_result = _merge_assess_diagnostics(
                schema=schema,
                package_path=result.package_path,
                implementation_id=str(impl_id),
                trace=result.trace,
            )
            all_diags.extend(assess_diags)
            if slice_result is not None:
                lines.append(
                    f"assess overall={slice_result.report.overall_result.value} "
                    f"diagnostics={len(assess_diags)}"
                )
        except Exception as exc:  # noqa: BLE001 — surface in report
            all_diags.append(
                Diagnostic(
                    code="ASSESS:ERROR",
                    severity=Severity.ERROR,
                    message_ru=f"assess failed: {exc}",
                    remediation="Проверьте schema/package и зависимости moex-dams.",
                )
            )

    if not skip_export and schema is not None and schema.is_file():
        out_json = out_dir / "publications" / "vertical_slice.json"
        try:
            _export_slice(
                schema=schema,
                package_path=result.package_path,
                out_json=out_json,
                implementation_id=str(impl_id),
            )
            lines.append(f"export-slice={out_json}")
        except Exception as exc:  # noqa: BLE001
            all_diags.append(
                Diagnostic(
                    code="EXPORT:ERROR",
                    severity=Severity.ERROR,
                    message_ru=f"export-slice failed: {exc}",
                    remediation="Проверьте moex-publication и package YAML.",
                )
            )

    md, _js = write_report(
        report,
        title=f"Import {result.src_system} → {result.slug}",
        diagnostics=all_diags,
        extras={
            "package": str(result.package_path),
            "io_skipped": result.io_skipped,
        },
    )
    lines.append(f"report={md}")
    n_err = sum(1 for d in all_diags if d.severity is Severity.ERROR)
    n_warn = sum(1 for d in all_diags if d.severity is Severity.WARNING)
    n_info = sum(1 for d in all_diags if d.severity is Severity.INFO)
    lines.append(f"SXI+ASSESS: error={n_err} warning={n_warn} info={n_info}")

    # Recompute exit: errors → 1; io skip → 3; else 0
    code = 1 if n_err else (3 if result.io_skipped else 0)
    # Surface errors fully; warnings only as a short sample (full list in report).
    errors = [d for d in all_diags if d.severity is Severity.ERROR]
    warnings = [d for d in all_diags if d.severity is Severity.WARNING]
    for d in errors[:50]:
        lines.append(str(d))
    if len(errors) > 50:
        lines.append(f"... and {len(errors) - 50} more errors (see report)")
    if warnings:
        lines.append(f"(first {min(5, len(warnings))} of {len(warnings)} warnings)")
        for d in warnings[:5]:
            lines.append(str(d))
        if len(warnings) > 5:
            lines.append(f"... see {md} for full warning list")
    return code, "\n".join(lines) + "\n"
