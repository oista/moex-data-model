"""validate command — calls specification-dams assess_implementation."""

from __future__ import annotations

from moex_dams.application.assess import assess_implementation
from moex_model_cli.bootstrap import SlicePaths
from moex_model_cli.presenters import format_validate_json, format_validate_text


def run_validate(
    paths: SlicePaths,
    *,
    as_json: bool = False,
    implementation_id: str | None = None,
) -> tuple[int, str]:
    result = assess_implementation(
        schema_path=paths.schema,
        implementation_path=paths.implementation,
        implementation_id=implementation_id,
    )
    text = format_validate_json(result) if as_json else format_validate_text(result)
    return (0 if result.report.is_conformant else 1, text)
