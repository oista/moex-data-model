"""Verify four solution packages against expected entity sets from xlsx/ERD."""

from __future__ import annotations

import sys
from pathlib import Path

import yaml

sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parents[1]
EXPECTED = {
    "mdm": {
        "ENTERPRISE",
        "PERSON",
        "PERSON_CEO",
        "PERSON_REPRESENTATIVE",
    },
    "ucd": {
        "ORGANIZATION",
        "ORGANIZATION_TYPE",
        "PERSON",
        "EMPOYEE",  # source typo preserved
        "POSITION",
        "AUTHORIZATION",
        "AGREEMENT",
    },
    "crm": {"CUSTOMER", "CONTACT", "LEAD"},
    "esed": {
        "instance",
        "document",
        "file",
        "file_binary",
        "attorney_check_info",
        "common_state",
        "common_type",
        "division",
        "employee",
        "organization",
        "organization_employee",
        "universal_item",
    },
}


def main() -> int:
    ok = True
    for slug, expected in EXPECTED.items():
        path = (
            ROOT
            / "model-assets"
            / "implementations"
            / "solutions"
            / slug
            / f"{slug}-solution-model.yaml"
        )
        impl = (
            ROOT
            / "model-assets"
            / "implementations"
            / "solutions"
            / slug
            / "implementation.yaml"
        )
        pub = (
            ROOT
            / "model-assets"
            / "implementations"
            / "solutions"
            / slug
            / "publish.yaml"
        )
        slice_json = (
            ROOT
            / "model-assets"
            / "implementations"
            / "solutions"
            / slug
            / "publications"
            / "vertical_slice.json"
        )
        for required in (path, impl, pub, slice_json):
            if not required.is_file():
                print(f"FAIL {slug}: missing {required.relative_to(ROOT)}")
                ok = False
        if not path.is_file():
            continue
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        names = {e["name"] for e in data.get("logical_entities") or []}
        missing = sorted(expected - names)
        extra = sorted(names - expected)
        n_attr = sum(len(e.get("attributes") or []) for e in data["logical_entities"])
        n_phys = len(data.get("physical_objects") or [])
        n_map = len(data.get("mappings") or [])
        n_rel = len(data.get("relationships") or [])
        status = "OK" if not missing and not extra else "FAIL"
        if missing or extra:
            ok = False
        print(
            f"{status} {slug}: entities={len(names)} attrs={n_attr} "
            f"phys={n_phys} maps={n_map} rels={n_rel}"
        )
        if missing:
            print(f"  missing: {missing}")
        if extra:
            print(f"  extra: {extra}")
        # Envelope checks
        env = yaml.safe_load(impl.read_text(encoding="utf-8"))
        assert env.get("implementation_profile") == "dams-data-model"
        assert env.get("dams_model_level") == "solution"
        assert "file:///" not in str(env.get("source", {}))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
