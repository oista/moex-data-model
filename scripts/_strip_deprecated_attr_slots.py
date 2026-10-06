"""One-shot: strip deprecated LogicalAttribute keys after PR-5 schema removal."""

from __future__ import annotations

from pathlib import Path

REMOVED = ("logical_type", "format_pattern", "value_set_ref", "unit_code")
ROOTS = [
    Path("model-assets/implementations"),
    Path("model-assets/specifications/moex-dams/0.1/examples"),
    Path("model-assets/specifications/moex-dams/0.1/requirements/examples"),
]


def strip_attrs(data: object) -> int:
    n = 0
    if not isinstance(data, dict):
        return 0
    for ent in data.get("logical_entities") or []:
        if not isinstance(ent, dict):
            continue
        for attr in ent.get("attributes") or []:
            if not isinstance(attr, dict):
                continue
            for k in REMOVED:
                if k in attr:
                    del attr[k]
                    n += 1
    return n


def main() -> None:
    try:
        from ruamel.yaml import YAML

        yaml = YAML()
        yaml.preserve_quotes = True
        yaml.width = 4096
        engine = "ruamel"
    except Exception:
        import yaml as pyyaml

        yaml = pyyaml
        engine = "pyyaml"

    changed: list[str] = []
    total = 0
    for root in ROOTS:
        if not root.exists():
            continue
        for path in root.rglob("*.yaml"):
            text = path.read_text(encoding="utf-8")
            if "logical_entities" not in text:
                continue
            if engine == "ruamel":
                data = yaml.load(text)
            else:
                data = yaml.safe_load(text)
            n = strip_attrs(data)
            if not n:
                continue
            total += n
            if engine == "ruamel":
                with path.open("w", encoding="utf-8") as f:
                    yaml.dump(data, f)
            else:
                path.write_text(
                    yaml.safe_dump(data, allow_unicode=True, sort_keys=False),
                    encoding="utf-8",
                )
            changed.append(path.as_posix())
    print(f"files={len(changed)} keys_removed={total}")
    for p in changed:
        print(p)


if __name__ == "__main__":
    main()
