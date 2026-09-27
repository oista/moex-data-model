---
status: Proposed
version: "0.1"
normative: false
supersedes: []
superseded_by: MODELING_ARCHITECTURE.md
---

# ADR-008: LinkML Map скрывается за provider interface

**Date:** 2026-09-28  
**Status:** Proposed  
**Normative parent:** [MODELING_ARCHITECTURE.md](../architecture/MODELING_ARCHITECTURE.md) §10  
**Workbench detail:** [linkml_architecture.md](../architecture/linkml_architecture.md) «Mapping Engine»

## Context

`linkml-map` нужен для импорта внешних структур, миграций DAMS и профилей, но API нестабилен, SQL backend покрывает подмножество, expressions опасны без sandbox. Прямые импорты в application handlers привяжут домен к конкретной версии пакета.

На срезе §13 mapping engine **не реализован**. Есть kernel `StandardMapping` (provenance, semantic loss) и пакет `semantic-mappings` (SSSOM/SKOS), это другой контур, чем `linkml-map`.

## Decision

Когда появится transformation pipeline:

- Прикладной код зависит от **`MappingProvider`** (port), не от `linkml-map` напрямую.
- Transformation specs живут в Git; production transformer — Python `ObjectTransformer`; SQL backend — только после отдельного conformance-теста.
- Unrestricted evaluation выражений **запрещён** по умолчанию (allowlist + isolation).
- Mapping обязан фиксировать preserved/lost semantics, round-trip, authoritative source, provenance.

`linkml-map` — optional controlled dependency, pinned в lockfile.

## Consequences

- Можно сменить или урезать `linkml-map` без правки kernel classes.
- Не путать DAMS-класс `Mapping` (conceptual/logical/physical внутри решения) с cross-standard `StandardMapping` / SSSOM.

## Alternatives

| Alternative | Почему нет |
|---|---|
| Прямой `import linkml_map` в handlers | vendor lock, нестабильный API |
| SQL transformer как default | неполное подмножество |
| Ad-hoc Python scripts | нет provenance и review |

## Related

- ADR-009, ADR-011, ADR-012
- packages/semantic-mappings — не замена этому ADR
