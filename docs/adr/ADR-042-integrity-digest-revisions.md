---
status: Accepted
version: "0.1"
normative: false
supersedes: []
superseded_by: MODELING_ARCHITECTURE.md
---

# ADR-042: integrity_digest and model revisions for non-demo models

**Date:** 2026-10-05  
**Status:** Accepted  
**Normative parent:** [MODELING_ARCHITECTURE.md](../architecture/MODELING_ARCHITECTURE.md)  
**Related:** [ADR-031](ADR-031-technical-asset-registry.md) (digest note), [ADR-012](ADR-012-semantic-diff-review.md)

## Context

`DataModelBinding.integrity_digest` фиксирует неизменяемый срез контрактной ревизии. При миграции физического объекта к TechnicalAsset (фаза 1) digest пересчитывался только в `--demo`. Для не-demo моделей неизменяемость ревизии требует **новой** ревизии с baseline, а не in-place пересчёта.

## Decision

### Правило ревизии

При изменении содержимого не-demo модели, которое влияет на `DataModelBinding`:

1. Создаётся **новая** запись/ревизия binding (`model_revision` обновляется).
2. У новой ревизии заполняется `compatibility_baseline_ref` на предыдущую ревизию (или на предшествующий binding id).
3. `integrity_digest` **пересчитывается** для новой ревизии (канонический JSON без полей `integrity_digest` и `generated_at`).
4. Предыдущая ревизия не мутируется.

Для fixtures / examples / `--demo` допустим in-place пересчёт digest без новой ревизии (как в ADR-031).

### Канонический digest

```
sha256: hex(SHA-256( UTF-8( json.dumps(binding_without_digest_and_generated_at, sort_keys=True) ) ))
```

### CLI

`moex-model digest --root . [--model <element_id|path>] [--write]`

- без `--write` — проверка расхождений (exit 1 при mismatch);
- с `--write` — запись вычисленного digest (только demo/examples по умолчанию; для не-demo требуется явный `--allow-non-demo-write` и наличие baseline-правила в процессе ревью).

### Gate

`publish-gate` и Stage 0 checks вызывают проверку digest: любое расхождение у найденных binding-инстансов — ошибка.

## Open question (фаза 1)

Модели решений MDM / CRM / ESED / UCD, затронутые миграцией фазы 1, **не содержат** экземпляров `DataModelBinding` / `model_revision` / `integrity_digest`. Создавать ревизии «с нуля» в рамках хвостов фазы 1 **нельзя** (нет baseline данных).

Открытый вопрос: когда и кем заводятся первые contract bindings для solution models? До появления bindings digest-gate для них — no-op (нечего проверять). Единственный текущий инстанс — `model-assets/specifications/moex-dams/0.1/examples/client-contract-binding.yaml`.

## Consequences

- Не-demo: digest меняется только вместе с новой ревизией + `compatibility_baseline_ref`.
- Demo/examples: `moex-model digest --write` допустим.
- CI ловит рассинхрон digest ↔ содержимое binding.

## Alternatives

| Alternative | Почему нет |
|---|---|
| Пересчитывать digest in-place у не-demo | ломает неизменяемость ревизии |
| Хранить digest у ModelPackage | другой уровень (пакет ≠ контрактный срез) |
| Придумать revision ids для MDM в фазе 1 | нет исходных bindings; inventing запрещён ТЗ |
