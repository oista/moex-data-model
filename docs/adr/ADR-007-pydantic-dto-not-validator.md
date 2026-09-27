---
status: Proposed
version: "0.1"
normative: false
supersedes: []
superseded_by: MODELING_ARCHITECTURE.md
---

# ADR-007: Pydantic — API DTO, но не единственный validator

**Date:** 2026-09-28  
**Status:** Proposed  
**Normative parent:** [MODELING_ARCHITECTURE.md](../architecture/MODELING_ARCHITECTURE.md) §5

## Context

`gen-pydantic` удобен для FastAPI и форм. Kernel уже использует frozen Pydantic для envelopes. Если считать generated Pydantic единственным валидатором, часть LinkML constructs и MOEX rules выпадет. Параллельно `gen-python` dataclasses как второй runtime semantics разъедется с Pydantic.

## Decision

- **Канонический validator экземпляров LinkML** — `linkml-validate` / `linkml.validator` (на срезе: `LinkMLStandardProvider.validate_standard`).
- **MOEX/DAMS semantic rules** — отдельный слой (`specification-dams`), не «ещё один Pydantic model».
- **Kernel envelopes** — рукописный frozen Pydantic, совпадающий с `modeling-kernel.yaml` по смыслу, без подмены provider bodies.
- **`gen-pydantic`** — API DTO, формы, request/response Workbench, когда появится generate pipeline.
- **`gen-python`** — conformance/runtime там, где нужен `linkml-runtime`, не второй источник истины.
- Browser: JSON Schema / AJV — предварительная проверка, не канон.

## Consequences

- Нельзя пропускать публикацию, если Pydantic прошёл, а `linkml-validate` или DAMS rules нет.
- Kernel `StandardProvider` разделяет `TSpecBody` и `TImplBody` (не dict[str, Any] как универсальная модель).

## Alternatives

| Alternative | Почему нет |
|---|---|
| Только Pydantic | дыры относительно LinkML metamodel |
| Только dataclasses | хуже для API |
| `type + dict` bodies | запрещено MODELING_ARCHITECTURE §4 |

## Related

- ADR-001, ADR-010
- IMPLEMENTATION_PLAN «Решение по Python-моделям»
