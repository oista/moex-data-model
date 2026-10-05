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

На текущем срезе: `SpecificationImplementation.content_digest` и envelope `revision` от digest; publication JSON пересобирается `moex-model publish` (с fail-closed `publish_gate`). **CI `compare-golden`** сверяет regenerable contracts, `moex-dams.schema.json`, OWL, SHACL, `moex-dams.dbml` (не colored sample), Mermaid, gen-python, gen-doc, gen-rdf, **ontology-profile** (`ontology-profile.json` / Stage 8) и release-bundle index (`moex-dams-bundle.json`) с pinned `requirements-linkml.txt`. OWL/SHACL/RDF digests используют ground triples (без blank nodes); RDF additionally strips volatile `generation_date`; Python strips `# Generation date:` comments. **gen-doc** хранит в git только `docs/index.md` + `docs/README.md` (`git_policy: index_subset`); полный tree проверяется regen→digest в `compare-golden`, не on-disk digest в publish_gate. Ещё вне golden: полный drawDB editor import (bridge smoke — Playwright), colored DBML sample, optional pySHACL / `linkml-owl` (`make ontology-check`, ADR-030).

## Consequences

- CI: generate + compare golden for contracts (Stage 0).
- Viewer `dist/` gitignored — воспроизводится командой сборки.
- Digest mismatch — ошибка публикации / `compare-golden`, не warning.

## Alternatives

| Alternative | Почему нет |
|---|---|
| Коммит generated без digest | нельзя проверить drift |
| Ручной golden forever | ломается при апдейте LinkML без процесса |
| Timestamps в артефактах | ломает byte-identity |

## Related

- ADR-001, ADR-002
- IMPLEMENTATION_PLAN artifact manifest
