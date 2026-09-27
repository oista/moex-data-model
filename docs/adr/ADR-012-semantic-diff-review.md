---
status: Proposed
version: "0.1"
normative: false
supersedes: []
superseded_by: MODELING_ARCHITECTURE.md
---

# ADR-012: Все изменения публикуются через semantic diff и review

**Date:** 2026-09-28  
**Status:** Proposed  
**Normative parent:** [MODELING_ARCHITECTURE.md](../architecture/MODELING_ARCHITECTURE.md) — нет отдельной секции под review workflow; §11 (источники истины) смежный  
**Workbench:** [linkml_architecture.md](../architecture/linkml_architecture.md) Git Publishing Service

## Context

Текстовый Git diff по YAML плохо показывает breaking vs compatible (удаление slot, смена URI, optional→required). Публикация в обход review (прямой push generated, apply DBML без patch) ломает ADR-001/006/011.

## Decision

Путь публикации Workbench:

1. workspace от Git revision  
2. правки канона (YAML или patch из проекции)  
3. validation pipeline (LinkML + DAMS + policy)  
4. **semantic diff** (классификация: backward-compatible / breaking / governance / operational)  
5. review (PR)  
6. merge → immutable revision → artifacts  

Прямая запись в published branch без diff/review не допускается. Breaking changes требуют migration note / approval (IMPLEMENTATION_PLAN этап 10).

На текущем срезе: `moex-model validate` / `assess` даёт `ConformanceReport`; **semantic diff и PR automation ещё нет** — это следующий Workbench кусок, не закрытый CLI.

## Consequences

- drawDB/import не публикуют сами (ADR-006, ADR-009).
- Нужен стабильный diagnostic code (уже есть в kernel `Diagnostic`).
- GitProvider.create_review — первая реализация может быть GitHub, без GitHub DTO в domain.

## Alternatives

| Alternative | Почему нет |
|---|---|
| Только textual diff | не классифицирует breaking |
| Автоmerge при зелёном validate | нет governance/approval |
| Публикация из UI без Git | ломает ADR-002 |

## Related

- ADR-002, ADR-006, ADR-009, ADR-011
- ConformanceReport / `moex-model validate` как предок шага 3
