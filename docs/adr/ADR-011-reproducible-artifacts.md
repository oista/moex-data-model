---
status: Proposed
version: "0.1"
normative: false
supersedes: []
superseded_by: MODELING_ARCHITECTURE.md
---

# ADR-011: Generated artifacts должны быть воспроизводимыми

**Date:** 2026-09-28  
**Status:** Proposed  
**Normative parent:** [MODELING_ARCHITECTURE.md](../architecture/MODELING_ARCHITECTURE.md) §11, invariants 6 и 8

## Context

Генераторы LinkML иногда пишут timestamps и зависят от версии toolchain. Без pin и digest нельзя доказать, что bundle соответствует Git revision. Ручные правки `generated/` разъедутся с каноном.

## Decision

Каждый derived artifact сопровождается **manifest**: model id/version/revision, generator name, generator version (из lockfile), configuration digest, artifact digest (`sha256:…`).

- Повторная генерация с тем же source revision и pinned toolchain — побайтово идентична **или** отличается только явно разрешёнными полями.
- `generated/` не редактируется вручную.
- Недетерминированные поля (timestamps) отключаются или нормализуются.
- Lockfile фиксирует LinkML ecosystem; обновление toolchain — отдельный PR с объяснением golden diff.

На текущем срезе: `SpecificationImplementation.content_digest` и envelope `revision` от digest; publication JSON пересобирается `moex-model publish`. Полный generator matrix (JSON Schema, OWL, …) — ещё Workbench этап 6.

## Consequences

- CI later: generate + compare golden.
- Viewer `dist/` gitignored — воспроизводится командой сборки.
- Digest mismatch — ошибка публикации, не warning.

## Alternatives

| Alternative | Почему нет |
|---|---|
| Коммит generated без digest | нельзя проверить drift |
| Ручной golden forever | ломается при апдейте LinkML без процесса |
| Timestamps в артефактах | ломает byte-identity |

## Related

- ADR-001, ADR-002
- IMPLEMENTATION_PLAN artifact manifest
