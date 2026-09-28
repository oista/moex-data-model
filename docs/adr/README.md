---
status: Proposed
version: "0.1"
normative: false
supersedes: []
superseded_by: MODELING_ARCHITECTURE.md
---

# ADR index (001–012)

**Status:** Proposed drafts  
**Date:** 2026-09-28  
**Normative parent:** [MODELING_ARCHITECTURE.md](../architecture/MODELING_ARCHITECTURE.md) (Proposed 0.2)

Список решений из [linkml_architecture.md](../architecture/linkml_architecture.md) § «Ключевые решения». Это **проекты ADR**, не Accepted: при расхождении побеждает нормативный документ ядра.

Viewer-решения живут отдельно: [viewer-decisions.md](../architecture/viewer-decisions.md).

| ADR | Title | Scope today |
|---|---|---|
| [ADR-001](ADR-001-linkml-yaml-canonical.md) | LinkML YAML — канон для DAMS / LinkML toolchain | действует на текущем срезе |
| [ADR-002](ADR-002-git-published-source.md) | Git — источник опубликованных версий | действует |
| [ADR-003](ADR-003-postgres-operational.md) | PostgreSQL — операционное хранилище и поисковая проекция | Workbench, ещё нет кода |
| [ADR-004](ADR-004-modular-monolith.md) | Модульный монолит | действует (packages + apps/cli) |
| [ADR-005](ADR-005-drawdb-isolated.md) | drawDB — изолированное self-hosted приложение | Workbench, ещё нет кода |
| [ADR-006](ADR-006-dbml-projection.md) | DBML — проекция, не source of truth | действует как принцип |
| [ADR-007](ADR-007-pydantic-dto-not-validator.md) | Pydantic — API DTO, не единственный validator | действует |
| [ADR-008](ADR-008-linkml-map-provider.md) | LinkML Map за provider interface | Workbench / mappings, ещё нет кода |
| [ADR-009](ADR-009-schema-automator-draft-only.md) | schema-automator только draft import | действует (ingest не использует) |
| [ADR-010](ADR-010-owl-not-primary-validation.md) | OWL не основной validation | действует (каталог read-only) |
| [ADR-011](ADR-011-reproducible-artifacts.md) | Generated artifacts воспроизводимы | Stage 0: `requirements-linkml.txt` + `compare-golden` (contracts/JSON Schema); полный matrix — этап 6 |
| [ADR-012](ADR-012-semantic-diff-review.md) | Публикация через semantic diff и review | Workbench; CLI `semantic-diff` есть; API/UI/PR attach — нет |

## Как принимать

1. Ревью по [CHECKLIST.md](../architecture/CHECKLIST.md), если правка затрагивает ядро.
2. Сменить `status: Proposed` → `Accepted` только после явного решения.
3. Не дублировать инварианты §14 MODELING_ARCHITECTURE — ADR ссылается на них.
