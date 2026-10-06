"""Dry-run: which instances fail once JsonschemaValidationPlugin(closed=True) is on.

Does not change production code. Outputs JSON to stdout / --out.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import yaml
from linkml.validator import Validator
from linkml.validator.plugins import JsonschemaValidationPlugin

ROOT = Path(__file__).resolve().parents[2]
SCHEMA = ROOT / "model-assets/specifications/moex-dams/0.1/schemas/moex-dams.yaml"

# Targets currently reached by validate-*.ps1 + related solution models/examples.
TARGETS: list[tuple[str, str, str]] = [
    (
        "validate-examples",
        "model-assets/specifications/moex-dams/0.1/examples/client-contract-binding.yaml",
        "DataModelBinding",
    ),
    (
        "validate-examples",
        "model-assets/specifications/moex-dams/0.1/examples/client-data-flow.yaml",
        "DataFlow",
    ),
    (
        "validate-schemas",
        "model-assets/implementations/solutions/mdm/mdm-solution-model.yaml",
        "ModelPackage",
    ),
    (
        "validate-requirements",
        "model-assets/specifications/moex-dams/0.1/requirements/it-solution-requirements.yaml",
        "RequirementCatalog",
    ),
    # Same path as provider / ingest tests (not all in check_all today).
    (
        "related-example",
        "model-assets/specifications/moex-dams/0.1/examples/ontology/valid-model-package.yaml",
        "ModelPackage",
    ),
    (
        "related-example",
        "model-assets/specifications/moex-dams/0.1/requirements/examples/it-solution-model.example.yaml",
        "ModelPackage",
    ),
    (
        "related-solution",
        "model-assets/implementations/solutions/crm/crm-solution-model.yaml",
        "ModelPackage",
    ),
    (
        "related-solution",
        "model-assets/implementations/solutions/esed/esed-solution-model.yaml",
        "ModelPackage",
    ),
    (
        "related-solution",
        "model-assets/implementations/solutions/ucd/ucd-solution-model.yaml",
        "ModelPackage",
    ),
    (
        "related-catalog",
        "model-assets/specifications/moex-dams/0.1/requirements/conceptual-model-requirements.yaml",
        "RequirementCatalog",
    ),
]


def _errors(report) -> list[str]:
    out = []
    for r in report.results:
        sev = str(getattr(r, "severity", r))
        if "ERROR" not in sev.upper():
            continue
        msg = getattr(r, "message", None) or str(r)
        out.append(str(msg)[:500])
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=None)
    args = ap.parse_args()

    plug = [JsonschemaValidationPlugin(closed=True)]
    vacuous = Validator(SCHEMA)
    real = Validator(SCHEMA, plug)

    rows = []
    for group, rel, target in TARGETS:
        path = ROOT / rel
        if not path.is_file():
            rows.append(
                {
                    "group": group,
                    "path": rel,
                    "target": target,
                    "exists": False,
                }
            )
            continue
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        vac = _errors(vacuous.validate(data, target_class=target))
        err = _errors(real.validate(data, target_class=target))
        rows.append(
            {
                "group": group,
                "path": rel,
                "target": target,
                "exists": True,
                "vacuous_error_count": len(vac),
                "plugin_error_count": len(err),
                "newly_invalid": len(vac) == 0 and len(err) > 0,
                "still_ok": len(err) == 0,
                "errors_sample": err[:8],
            }
        )
        status = "OK" if not err else f"FAIL({len(err)})"
        flag = " NEWLY-INVALID" if (not vac and err) else ""
        print(f"{status:10} {group:22} {target:20} {rel}{flag}")

    payload = {
        "schema": str(SCHEMA.relative_to(ROOT)),
        "plugin": "JsonschemaValidationPlugin(closed=True)",
        "rows": rows,
        "newly_invalid": [r for r in rows if r.get("newly_invalid")],
        "ok": [r for r in rows if r.get("still_ok")],
    }
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        print(f"wrote {args.out}")
    return 0 if not payload["newly_invalid"] else 2


if __name__ == "__main__":
    sys.exit(main())
