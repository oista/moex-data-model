"""One-off inventory builder for conceptual-property-inventory.md (run from repo root)."""
from __future__ import annotations

import re
import subprocess
from collections import defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]

SYMBOLS = [
    "logical_type",
    "LogicalDataTypeEnum",
    "format_pattern",
    "value_set_ref",
    "unit_code",
    "currency_attribute_ref",
    "timezone_policy",
    "temporal_semantics",
    "default_value",
    "derived_expression",
    "identity_rule",
    "business_key_kind",
    "key_attribute_refs",
    "definition_source_ref",
    "definition_rationale",
    "scoped_definitions",
    "genesis_kind",
    "external_class_refs",
    "conceptual_alignment_status",
    "alignment_rationale",
    "isolation_rationale",
    "business_importance",
    "HasBusinessClassification",
    "HasGovernanceClassification",
    "HasPolicyBindings",
]

GLOBS = [
    "!generated/**",
    "!tmp/**",
    "!node_modules/**",
    "!.git/**",
    "!.cursor/plans/**",
    "!docs/migration/_conceptual_property_inventory_data.json",
    "!docs/migration/conceptual-property-inventory.md",
    "!docs/migration/_build_conceptual_property_inventory.py",
]

USAGE_TYPES = {
    "schema definition",
    "model data",
    "validator",
    "projection",
    "viewer",
    "web form",
    "api mutate",
    "ingest/mapper",
    "test",
    "docs",
    "transformation",
    "other",
}


def classify_path(path: str) -> str:
    p = path.replace("\\", "/")
    if p.startswith("model-assets/specifications/moex-dams/0.1/schemas/"):
        return "schema definition"
    if p.startswith("model-assets/"):
        return "model data"
    if p.startswith("packages/specification-dams/"):
        if "/tests/" in p:
            return "test"
        if "/projection/" in p:
            return "projection"
        if "/rules/" in p or "validate" in p:
            return "validator"
        if "/application/" in p:
            return "transformation"
        return "transformation"
    if p.startswith("packages/standard-linkml/"):
        if "/tests/" in p:
            return "test"
        if "/ingest/" in p or "solution_xlsx" in p:
            return "ingest/mapper"
        return "ingest/mapper"
    if p.startswith("packages/ontology-catalog/"):
        return "transformation"
    if p.startswith("packages/drawdb-adapter/"):
        if "/tests/" in p:
            return "test"
        return "ingest/mapper"
    if p.startswith("apps/api/"):
        if "/tests/" in p:
            return "test"
        return "api mutate"
    if p.startswith("apps/viewer/"):
        if "/tests/" in p:
            return "test"
        return "viewer"
    if p.startswith("apps/web/"):
        if "/tests/" in p or ".test." in p:
            return "test"
        return "web form"
    if p.startswith("docs/"):
        return "docs"
    if "/tests/" in p or p.endswith("_test.py") or "test_" in Path(p).name:
        return "test"
    return "other"


def symbols_in_line(text: str) -> list[str]:
    found = []
    for s in SYMBOLS:
        if re.search(r"\b" + re.escape(s) + r"\b", text):
            found.append(s)
    return found


def run_rg() -> list[str]:
    args = ["rg", "-n", "--no-heading"]
    for g in GLOBS:
        args.extend(["--glob", g])
    pattern = "|".join(re.escape(s) for s in SYMBOLS)
    args.extend(["-e", pattern, str(REPO)])
    proc = subprocess.run(
        args,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        cwd=str(REPO),
    )
    return [l for l in proc.stdout.splitlines() if l.strip()]


def parse_line(line: str) -> tuple[str, int, str] | None:
    # path may contain drive letter with colon on Windows
    m = re.match(r"^(.+?):(\d+):(.+)$", line)
    if not m:
        return None
    path, num, content = m.group(1), int(m.group(2)), m.group(3)
    if path.startswith(str(REPO)):
        path = str(Path(path).relative_to(REPO)).replace("\\", "/")
    return path, num, content


def section_for_path(path: str) -> str:
    p = path.replace("\\", "/")
    if p.startswith("model-assets/specifications/moex-dams/0.1/schemas/"):
        return "1. Schemas"
    if p.startswith("model-assets/specifications/moex-dams/0.1/requirements/"):
        return "2. Requirements"
    if p.startswith("model-assets/"):
        return "3. Examples and solution models"
    if p.startswith("packages/"):
        return "4. Code packages"
    if p.startswith("apps/"):
        return "5. Apps"
    if "/tests/" in p or "test_" in Path(p).name:
        return "6. Tests"
    if p.startswith("docs/"):
        return "8. Documentation"
    return "7. Other"


def compress_lines(nums: list[int]) -> str:
    if not nums:
        return ""
    nums = sorted(set(nums))
    ranges: list[str] = []
    start = prev = nums[0]
    for n in nums[1:]:
        if n == prev + 1:
            prev = n
            continue
        ranges.append(f"{start}" if start == prev else f"{start}-{prev}")
        start = prev = n
    ranges.append(f"{start}" if start == prev else f"{start}-{prev}")
    if len(ranges) <= 12:
        return ", ".join(ranges)
    head = ", ".join(ranges[:10])
    return f"{head}, … (+{len(ranges) - 10} more; last {nums[-1]})"


def main() -> None:
    lines = run_rg()
    by_symbol: dict[str, list[tuple[str, int, str, str]]] = defaultdict(list)
    by_section_file: dict[str, dict[str, dict]] = defaultdict(lambda: defaultdict(lambda: {"lines": [], "types": set(), "keys": set()}))

    for line in lines:
        parsed = parse_line(line)
        if not parsed:
            continue
        path, linenum, content = parsed
        ut = classify_path(path)
        sec = section_for_path(path)
        syms = symbols_in_line(content)
        for s in syms:
            by_symbol[s].append((path, linenum, ut, content.strip()[:100]))
        entry = by_section_file[sec][path]
        entry["lines"].append(linenum)
        entry["types"].add(ut)
        entry["keys"].update(syms)

    print("TOTAL", len(lines))
    print("FILES", len({parse_line(l)[0] for l in lines if parse_line(l)}))
    for s in SYMBOLS:
        print(f"{s}: {len(by_symbol[s])}")

    # key_attribute_refs analysis
    print("\n=== ConceptualEntity key_attribute_refs (model data) ===")
    for path, num, ut, content in by_symbol.get("key_attribute_refs", []):
        if "conceptual" not in path.lower() and "moex-enterprise" not in path and "moex-hierarchy" not in path:
            if not path.startswith("model-assets/implementations/enterprise"):
                continue
        if ut != "model data" and ut != "schema definition":
            continue
        if "key_attribute_refs" in content and ":" in content:
            print(f"  {path}:{num}  {content[:120]}")

    # Write JSON for agent
    out = REPO / "docs" / "migration" / "_conceptual_property_inventory_data.json"
    import json

    unique_files = len({parse_line(l)[0] for l in lines if parse_line(l)})
    payload = {
        "total_lines": len(lines),
        "unique_files": unique_files,
        "by_symbol_counts": {s: len(by_symbol[s]) for s in SYMBOLS},
        "by_symbol": {
            s: [{"path": p, "line": n, "type": t, "snippet": sn} for p, n, t, sn in rows]
            for s, rows in by_symbol.items()
        },
        "by_section_file": {
            sec: {
                path: {
                    "lines": sorted(set(v["lines"])),
                    "types": sorted(v["types"]),
                    "keys": sorted(v["keys"]),
                }
                for path, v in files.items()
            }
            for sec, files in by_section_file.items()
        },
    }
    out.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nWrote {out}")
    md_path = REPO / "docs" / "migration" / "conceptual-property-inventory.md"
    md_path.write_text(render_markdown(payload, by_symbol, by_section_file), encoding="utf-8")
    print(f"Wrote {md_path}")


def render_markdown(
    payload: dict,
    by_symbol: dict[str, list[tuple[str, int, str, str]]],
    by_section_file: dict,
) -> str:
    lines: list[str] = []
    w = lines.append

    w("# ConceptualProperty migration: LogicalAttribute slot inventory")
    w("")
    w(
        "Инвентаризация слотов `LogicalAttribute` / связанных полей сущностей "
        "для миграции на `ConceptualProperty` (корпоративный уровень) и переноса "
        "domain-семантики с solution-bound атрибутов."
    )
    w("")
    w("**Target class (planned):** `ConceptualProperty` — в схемах и данных **отсутствует** (grep 0 hits вне служебных скриптов инвентаризации).")
    w("")
    w("**Patterns:** см. таблицу слотов в Summary; плюс mixin-ссылки на `LogicalAttribute`.")
    w("")
    w("**Excluded:** `generated/**`, `tmp/**`, `node_modules/**`, `.git/**`, `.cursor/plans/**`.")
    w("")
    w(
        f"**Source:** live `rg` via `docs/migration/_build_conceptual_property_inventory.py`. "
        f"Raw line hits: {payload['total_lines']}; unique files: {payload.get('unique_files', '—')}."
    )
    w("")
    w("---")
    w("")
    w("## Summary: key slots / classes")
    w("")
    w("| Concept | Location | Notes |")
    w("|---|---|---|")
    w(
        "| `LogicalAttribute` property slots | "
        "`model-assets/specifications/moex-dams/0.1/schemas/moex-core.yaml:124-154`, slot defs `:437-493` | "
        "`logical_type`, `value_set_ref`, `format_pattern`, `default_value`, `derived_expression`, "
        "Wave-2: `unit_code`, `currency_attribute_ref`, `timezone_policy`, `temporal_semantics` |"
    )
    w(
        "| `LogicalAttribute` mixins | `moex-core.yaml:126-130` | "
        "`HasOwnership`, `HasGovernanceClassification`, `HasPolicyBindings`, `HasDefinition` "
        "(**not** `HasBusinessClassification`) |"
    )
    w(
        "| `LogicalEntity` identity / alignment | `moex-core.yaml:110-116`, slot defs `:460-473` | "
        "`key_attribute_refs`, `identity_rule`, `business_key_kind`, "
        "`conceptual_alignment_status`, `alignment_rationale`, `isolation_rationale` |"
    )
    w(
        "| `ConceptualEntity` CMD slots | `moex-core.yaml:81-87`, slot defs `:370-402` | "
        "`key_attribute_refs` (shared slot, range `uriorcurie`), `genesis_kind`, `external_class_refs` |"
    )
    w(
        "| `HasDefinition` | `moex-governance.yaml:105-111`, slot defs `:209-219` | "
        "`definition_source_ref`, `definition_rationale`, `scoped_definitions` |"
    )
    w(
        "| `HasBusinessClassification` | `moex-governance.yaml:60-66`, `:178` | "
        "`entity_type`, `data_class`, `business_importance` (entity-level; не на LogicalAttribute) |"
    )
    w(
        "| `LogicalDataTypeEnum` | `moex-types.yaml:243+` | "
        "Range of `logical_type`; `identifier` описан как tech key, не замена `identity_rule` |"
    )
    w("")
    w("### Counts by inventory category")
    w("")
    w("| Category | Files | Line hits |")
    w("|---|---:|---:|")

    cat_order = [
        ("1. Schemas", "schema definition"),
        ("2. Requirements", "model data"),
        ("3. Examples and solution models", "model data"),
        ("4. Code packages", "transformation"),
        ("5. Apps", "api mutate"),
        ("6. Tests", "test"),
        ("8. Documentation", "docs"),
    ]
    # aggregate from by_section_file
    sec_stats: dict[str, dict] = {}
    for sec, files in by_section_file.items():
        hits = sum(len(v["lines"]) for v in files.values())
        sec_stats[sec] = {"files": len(files), "hits": hits}
    total_files = sum(s["files"] for s in sec_stats.values())
    total_hits = sum(s["hits"] for s in sec_stats.values())
    for sec in sorted(sec_stats.keys(), key=lambda x: x):
        s = sec_stats[sec]
        w(f"| {sec} | {s['files']} | {s['hits']} |")
    w(f"| **Total (non-generated)** | **{total_files}** | **{total_hits}** |")
    w("")
    w("### Counts by symbol (line hits; a line may match multiple symbols)")
    w("")
    w("| Symbol | Hits | Primary carrier |")
    w("|---|---:|---|")
    carriers = {
        "logical_type": "LogicalAttribute",
        "LogicalDataTypeEnum": "schema enum",
        "format_pattern": "LogicalAttribute",
        "value_set_ref": "LogicalAttribute",
        "unit_code": "LogicalAttribute (Wave 2)",
        "currency_attribute_ref": "LogicalAttribute (Wave 2)",
        "timezone_policy": "LogicalAttribute (Wave 2)",
        "temporal_semantics": "LogicalAttribute (Wave 2)",
        "default_value": "LogicalAttribute",
        "derived_expression": "LogicalAttribute",
        "identity_rule": "LogicalEntity",
        "business_key_kind": "LogicalEntity",
        "key_attribute_refs": "ConceptualEntity + LogicalEntity",
        "definition_source_ref": "HasDefinition (all mixins)",
        "definition_rationale": "HasDefinition",
        "scoped_definitions": "HasDefinition",
        "genesis_kind": "ConceptualEntity",
        "external_class_refs": "ConceptualEntity",
        "conceptual_alignment_status": "LogicalEntity",
        "alignment_rationale": "LogicalEntity",
        "isolation_rationale": "LogicalEntity",
        "business_importance": "HasBusinessClassification",
        "HasBusinessClassification": "mixin class",
        "HasGovernanceClassification": "mixin on LogicalAttribute",
        "HasPolicyBindings": "mixin on LogicalAttribute",
    }
    for s in SYMBOLS:
        w(f"| `{s}` | {len(by_symbol[s])} | {carriers.get(s, '—')} |")
    w("")
    w("---")
    w("")
    w("## Per-symbol usage inventory")
    w("")

    for sym in SYMBOLS:
        rows = by_symbol[sym]
        w(f"### `{sym}` ({len(rows)} hits)")
        w("")
        if not rows:
            w("*No matches outside excluded paths.*")
            w("")
            continue
        # group by section
        by_sec: dict[str, list] = defaultdict(list)
        for path, num, ut, snip in rows:
            if "_build_conceptual_property" in path or "_conceptual_property_inventory" in path:
                continue
            by_sec[section_for_path(path)].append((path, num, ut, snip))
        if not by_sec:
            w("*Only tooling matches (excluded from table).*")
            w("")
            continue
        w("| File | Line(s) | Usage type | Context |")
        w("|---|---|---|---|")
        for sec in sorted(by_sec.keys()):
            file_rows: dict[str, list] = defaultdict(list)
            for path, num, ut, snip in by_sec[sec]:
                file_rows[path].append((num, ut, snip))
            for path in sorted(file_rows.keys()):
                nums = [n for n, _, _ in file_rows[path]]
                uts = sorted({u for _, u, _ in file_rows[path]})
                snips = file_rows[path][0][2].replace("|", "\\|")
                w(
                    f"| `{path}` | {compress_lines(nums)} | {', '.join(uts)} | {snips[:80]} |"
                )
        w("")

    w("---")
    w("")
    w("## Special findings")
    w("")
    w("### ConceptualEntity.`key_attribute_refs` — real data vs schema")
    w("")
    w("| Finding | Detail |")
    w("|---|---|")
    w(
        "| Enterprise conceptual model | "
        "`model-assets/implementations/enterprise/moex-enterprise-conceptual-model/0.1/enterprise-conceptual-model.yaml` "
        "— **нет** ни одного заполненного `key_attribute_refs` на `ConceptualEntity` (только `genesis_kind` / `external_class_refs`). |"
    )
    w(
        "| Hierarchy spec dump | "
        "`moex-dams-full.yaml:1488-1489` — мета-запись слота (`name: key_attribute_refs`), не бизнес-данные. |"
    )
    w(
        "| LogicalEntity (solution models) | "
        "Все фактические значения `key_attribute_refs` — списки `dams:logical/{solution}/...` "
        "(см. crm/esed/mdm/ucd solution YAML, example `it-solution-model.example.yaml`). |"
    )
    w(
        "| Validator | "
        "`packages/specification-dams/src/moex_dams/rules/structural.py` — проверяет, что refs ∈ attributes entity. |"
    )
    w(
        "| Semantic diff | "
        "`key_attribute_refs` в `_SKIP_KEYS` (`diff.py:42`) — изменения ключей не классифицируются отдельно (остаются в graph edges). |"
    )
    w("")
    w("### LogicalAttribute governance mixins (ADR-023)")
    w("")
    w("| Mixin | On LogicalAttribute | In code / rules |")
    w("|---|---|---|")
    w("| `HasBusinessClassification` | **No** (only ConceptualEntity, LogicalEntity) | `formal_checks`, cascade — entity-level `business_importance` |")
    w("| `HasGovernanceClassification` | **Yes** (`moex-core.yaml:128`) | `cascade.py`, `formal_checks.py`, projections inherit display |")
    w("| `HasPolicyBindings` | **Yes** (`moex-core.yaml:129`) | `cascade.py`, policy full-replace semantics ADR-023 |")
    w("")
    w("### `packages/specification-dams`: ChangeCategory & deprecated")
    w("")
    w("| Location | Relevance to this migration |")
    w("|---|---|")
    w(
        "| `application/diff.py` | Property deltas on `logical_type`, `identity_rule`, etc. → "
        "`ChangeCategory.BREAKING` (`DAMS-DIFF-PROP`) unless doc/gov-only; "
        "`key_attribute_refs` skipped in scalar diff. |"
    )
    w(
        "| `application/ontology_report.py` | Structural add/remove → BREAKING / NON_BREAKING. |"
    )
    w(
        "| `tests/test_semantic_diff.py`, `test_ontology_report.py` | Fixture coverage for categories; "
        "no slot-specific deprecation map. |"
    )
    w(
        "| `deprecated` | Only requirement lifecycle fixture (`tests/fixtures/requirements/status-showcase.yaml`); "
        "**no** deprecated markers for LogicalAttribute slots in specification-dams. |"
    )
    w(
        "| `packages/linkml-tooling/tests/test_dams_slice_migrations.py` | Slice preview lists "
        "`logical_type` / `LogicalAttribute.logical_type` as **lost_semantics** when slicing — "
        "relevant if ConceptualProperty extraction uses DAMS slice. |"
    )
    w("")
    w("---")
    w("")
    w("## Preliminary ConceptualProperty candidates (no objects created)")
    w("")
    w("Criteria applied to current **solution** `LogicalAttribute` rows and **enterprise** `ConceptualEntity` metadata.")
    w("")
    # candidates appended by analyze_candidates() at runtime
    return "\n".join(lines)


def analyze_candidates() -> str:
    """Load solution YAMLs and emit candidate tables."""
    import yaml

    solutions = [
        REPO / "model-assets/implementations/solutions/crm/crm-solution-model.yaml",
        REPO / "model-assets/implementations/solutions/esed/esed-solution-model.yaml",
        REPO / "model-assets/implementations/solutions/mdm/mdm-solution-model.yaml",
        REPO / "model-assets/implementations/solutions/ucd/ucd-solution-model.yaml",
    ]
    attrs_by_sig: dict[tuple[str, str], set[str]] = defaultdict(set)
    identifying: list[tuple[str, str, str]] = []
    governance_high: list[tuple[str, str]] = []

    for path in solutions:
        if not path.exists():
            continue
        sol = path.parent.name
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        for ent in data.get("logical_entities") or []:
            keys = set(ent.get("key_attribute_refs") or [])
            imp = str(ent.get("business_importance") or "")
            if imp.lower() in ("high", "critical"):
                governance_high.append((sol, ent.get("element_id", "")))
            for attr in ent.get("attributes") or []:
                aid = attr.get("element_id", "")
                name = attr.get("name", "")
                ltype = str(attr.get("logical_type", ""))
                if aid in keys:
                    identifying.append((sol, aid, name))
                attrs_by_sig[(name.lower(), ltype)].add(sol)

    cross = [(sig, sorted(sols)) for sig, sols in attrs_by_sig.items() if len(sols) >= 2]
    cross.sort(key=lambda x: (-len(x[1]), x[0][0]))

    ent_path = (
        REPO
        / "model-assets/implementations/enterprise/moex-enterprise-conceptual-model/0.1/enterprise-conceptual-model.yaml"
    )
    external_entities: list[tuple[str, str]] = []
    if ent_path.exists():
        data = yaml.safe_load(ent_path.read_text(encoding="utf-8"))
        for ce in data.get("conceptual_entities") or []:
            if str(ce.get("genesis_kind")) == "external":
                refs = ce.get("external_class_refs") or []
                targets = ", ".join(
                    str(r.get("target_ref") or r.get("external_class_ref_id") or "") for r in refs[:2]
                )
                external_entities.append((ce.get("element_id", ""), targets))

    lines = []
    lines.append("### identifying (from `LogicalEntity.key_attribute_refs`)")
    lines.append("")
    lines.append("| Solution | Attribute id | Name |")
    lines.append("|---|---|---|")
    for sol, aid, name in sorted(identifying):
        lines.append(f"| {sol} | `{aid}` | {name} |")
    lines.append("")
    lines.append(f"*Total identifying attribute refs: {len(identifying)}.*")
    lines.append("")
    lines.append("### externally_aligned (entity-level; property TBD)")
    lines.append("")
    lines.append("| ConceptualEntity | External target(s) | Note |")
    lines.append("|---|---|---|")
    for eid, tgts in external_entities:
        lines.append(f"| `{eid}` | {tgts or '—'} | Candidate **entity** anchor; attributes not lifted yet |")
    lines.append("")
    lines.append("### cross_solution (same `name` + `logical_type` in 2+ solutions)")
    lines.append("")
    lines.append("| Name | logical_type | Solutions |")
    lines.append("|---|---|---|")
    for (name, ltype), sols in cross[:40]:
        lines.append(f"| {name} | {ltype} | {', '.join(sols)} |")
    if len(cross) > 40:
        lines.append(f"| … | … | *+{len(cross) - 40} more signatures* |")
    lines.append("")
    lines.append(f"*Total cross-solution signatures: {len(cross)}.*")
    lines.append("")
    lines.append("### critical_data")
    lines.append("")
    lines.append("N/A — нет отдельного слота `critical_data` / regulatory flag на атрибутах; "
                 "использовать `governance_classification` / policies (out of scope v1 inventory).")
    lines.append("")
    lines.append("### regulatory")
    lines.append("")
    lines.append("N/A — явных regulatory markers на LogicalAttribute не найдено (grep `regulatory` в связке с attrs — 0).")
    lines.append("")
    lines.append("### governance_anchor (entity `business_importance` high/critical)")
    lines.append("")
    lines.append("| Solution | LogicalEntity |")
    lines.append("|---|---|")
    if governance_high:
        for sol, eid in sorted(governance_high):
            lines.append(f"| {sol} | `{eid}` |")
    else:
        lines.append("| — | *Нет записей: во всех solution YAML (`crm`/`esed`/`mdm`/`ucd`) `business_importance: medium`.* |")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## Notes")
    lines.append("")
    lines.append("- `definition_source_ref` доминирует по hit-count из‑за validation/remediation текстов в `*/publications/vertical_slice.json` (не model slots).")
    lines.append("- Wave-2 soft slots (`unit_code`, `currency_attribute_ref`, `timezone_policy`, `temporal_semantics`) почти не заполнены в solution data; правила — `formal_checks.py` (ATR warnings).")
    lines.append("- Existing transform `model-assets/transformations/dams-logical-attribute-rename-type.yaml` переименовывает `logical_type` → `attribute_type` (slice experiment); учитывать при проектировании `ConceptualProperty`.")
    lines.append("- Hotspots для миграции: `moex-core.yaml` slot defs, `formal_checks.py`, ER projections (`dbml.py`, `mermaid_er.py`, `er_scene.py`), `standard-linkml/ingest/mapper.py`, `apps/web` `EntityForms.tsx`, `definitions.py` / ADR-025 cascade.")
    lines.append("")
    return "\n".join(lines)


if __name__ == "__main__":
    main()
    # append candidates to md
    md_path = REPO / "docs" / "migration" / "conceptual-property-inventory.md"
    if md_path.exists():
        text = md_path.read_text(encoding="utf-8")
        if "## Preliminary ConceptualProperty candidates" in text:
            head = text.split("## Preliminary ConceptualProperty candidates")[0]
            md_path.write_text(head + "## Preliminary ConceptualProperty candidates (no objects created)\n\n"
                               + analyze_candidates(), encoding="utf-8")
