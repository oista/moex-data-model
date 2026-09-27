---
status: Accepted
version: "0.1"
normative: false
supersedes: []
superseded_by: MODELING_ARCHITECTURE.md
---

# Architecture review checklist

Обязателен для любого PR, который меняет `docs/architecture/*` или `docs/architecture/modeling-kernel.yaml`.

Машинные проверки: `make architecture-check`.  
Этот чеклист покрывает смысловые инварианты, которые regex/SchemaView не ловят.

## Перед merge

- [ ] Новый или изменённый класс/слот/enum в `modeling-kernel.yaml` не специфичен для одного standard family (`LinkML*`, `OpenAPI*`, `OWL*`, …). `make architecture-check` зелёный.
- [ ] Каждый `Protocol`/интерфейс, работающий с телом модели, различает **specification body** (schema) и **implementation body** (instance) — не один `TypeVar`/`TBody` на оба метода. Fitness: [`tests/architecture/test_public_apis.py`](../../tests/architecture/test_public_apis.py).
- [ ] Каждая новая relation (`RelationKind`) имеет однозначное определение «откуда → куда» и не дублирует смысл существующей (`conforms_to` ≠ `implements`).
- [ ] Инварианты §14 [MODELING_ARCHITECTURE.md](MODELING_ARCHITECTURE.md) не нарушены; если нужны исключения — обновлён сам §14.
- [ ] Диаграммы hexagon/flow отражают направление `application → ports → adapters`, а не наоборот.
- [ ] Ровно один документ в `docs/architecture/` с `normative: true` во frontmatter.
- [ ] `root_type` / spec root в нормативном тексте согласован с `tree_root` в `model-assets/specifications/moex-dams/0.1/schemas/moex-dams.yaml` (сейчас `MOEXModelRepository`).
- [ ] DAMS / OpenAPI Profile и т.п. описаны как **instances** reference specification, не как subclasses kernel.
- [ ] Typed bodies остаются в provider schemas; kernel хранит только envelope + `body_ref`.
- [ ] Нет живых ссылок на retired `model_src/` вне [`docs/migration/`](../migration/) (`tests/architecture/test_no_model_src.py`).

Спецификация protocol-теста: [provider-protocol-test-spec.md](provider-protocol-test-spec.md).
