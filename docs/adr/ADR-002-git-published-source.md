---
status: Proposed
version: "0.1"
normative: false
supersedes: []
superseded_by: MODELING_ARCHITECTURE.md
---

# ADR-002: Git — источник опубликованных версий

**Date:** 2026-09-28  
**Status:** Proposed  
**Normative parent:** [MODELING_ARCHITECTURE.md](../architecture/MODELING_ARCHITECTURE.md) §11

## Context

Нужны неизменяемые версии model assets, review и воспроизводимые артефакты. Workbench также хочет drafts, search, jobs, audit — это плохо кладётся только в Git.

## Decision

**Опубликованный** model asset идентифицируется **Git revision** (commit SHA / tag). Версия модели, specification и implementation pin'ятся на immutable revision.

PostgreSQL, object storage и search index — operational / derived projections. Они **не** подменяют Git как реестр опубликованных спецификаций.

Git hosting (GitHub и др.) скрыт за `GitProvider`; прикладной код не зависит от vendor DTO.

## Consequences

- Публикация = merge/tag в Git + воспроизводимый bundle (ADR-011).
- CLI/срез сегодня читает файлы рабочего дерева; identity уже завязана на digest/revision envelope, не на хостинг.
- Workspace/draft появятся в PostgreSQL (ADR-003), канон после merge — снова Git.

## Alternatives

| Alternative | Почему нет |
|---|---|
| PostgreSQL как master опубликованных моделей | теряется review/PR, сложно доказать immutability |
| Object storage как канон | нет естественного review workflow |
| Только файлы без Git | нет стабильной revision для conformance |

## Related

- ADR-003, ADR-011, ADR-012
- Invariant 8 MODELING_ARCHITECTURE (artifact provenance → implementation revision)
