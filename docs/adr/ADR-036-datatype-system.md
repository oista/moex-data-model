---
status: Accepted
version: "0.1"
normative: false
supersedes: []
superseded_by: []
---

# ADR-036: Типовая система DataType и NativeTypeBinding

**Date:** 2026-10-05  
**Status:** Accepted  
**Normative parent:** [MODELING_ARCHITECTURE.md](../architecture/MODELING_ARCHITECTURE.md)  
**Related:** [ADR-034](ADR-034-lightweight-conceptual-property.md), [ADR-035](ADR-035-value-domains.md)

## Context

`LogicalDataTypeEnum` — плоский enum без параметров (precision/scale/length) и без
привязки к нативным типам диалектов.

## Decision

- Модуль `moex-datatypes.yaml`: `DataType` (`close_mappings: rdfs:Datatype`),
  `NativeTypeBinding`, позже `ValueDomain` / `PermissibleValue`.
- Enum'ы семейств — в `moex-types.yaml` (`TypeFamilyEnum`, `TimezonePolicyEnum`,
  `LossinessEnum`). Слот политики TZ у DataType — `datatype_timezone_policy`
  (не переиспользовать строковый `timezone_policy` атрибута).
- Стартовый набор: значения `LogicalDataTypeEnum` + `float`, `duration`, `array`;
  у каждого — `xsd_datatype` / `linkml_type`.
- `LogicalDataTypeEnum` остаётся на переходном этапе (deprecated `logical_type`);
  судьба после удаления deprecated-слотов — open question (оставить как projection
  или удалить).
- Коллекции `data_types` / `native_type_bindings` на `ModelPackage`; корпоративный
  реестр — enterprise-пакет (имя/путь — open: рядом с КМД или отдельный SpecImpl).
- DataType / NativeTypeBinding допустимы только в корпоративном реестре типов.
