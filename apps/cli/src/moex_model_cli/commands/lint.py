"""lint — LinkML lint + DAMS structural/reference rules."""

from __future__ import annotations

from moex_dams.rules.references import check_references
from moex_dams.rules.structural import check_structural
from moex_modeling import DiagnosticSeverity
from moex_model_cli.bootstrap import SlicePaths
from moex_standard_linkml.provider import LinkMLStandardProvider
from moex_modeling import ImplementationRef, SpecificationRef


def run_lint(paths: SlicePaths) -> tuple[int, str]:
    provider = LinkMLStandardProvider(default_schema_path=paths.schema)
    spec_ref = SpecificationRef(
        specification_id="moex:spec:dams",
        specification_version="0.1.0",
        specification_revision="0.1.0",
    )
    impl_ref = ImplementationRef(
        implementation_id="lint",
        implementation_revision="workdir",
    )
    provider.load_specification_body(spec_ref, path=str(paths.schema))
    body = provider.load_implementation_body(
        impl_ref, path=str(paths.implementation)
    )
    diags = (
        list(provider.validate_standard(body))
        + list(check_structural(body))
        + list(check_references(body))
    )
    lines = [f"{d.severity.value}\t{d.diagnostic_code}\t{d.diagnostic_message}" for d in diags]
    errors = [
        d
        for d in diags
        if d.severity in (DiagnosticSeverity.ERROR, DiagnosticSeverity.FATAL)
    ]
    header = f"lint diagnostics={len(diags)} errors={len(errors)}\n"
    return (1 if errors else 0, header + ("\n".join(lines) + ("\n" if lines else "")))
