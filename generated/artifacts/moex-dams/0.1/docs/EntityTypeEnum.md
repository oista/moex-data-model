---
search:
  boost: 2.0
---


# Enum: EntityTypeEnum 




_Роль логической сущности в модели решения._



<div data-search-exclude markdown="1">

URI: [dams:EntityTypeEnum](https://data.moex.com/dams/EntityTypeEnum)

## Permissible Values
| Value | Meaning | Description |
| --- | --- | --- |
| core | None | Базовая сущность, создаваемая и управляемая решением |
| derived | None | Производная сущность, вычисляемая или агрегируемая из других данных |
| reference | None | Справочная сущность или представление управляемого справочника |




## Slots

| Name | Description |
| ---  | --- |
| [entity_type](entity_type.md) |  |










## Identifier and Mapping Information





### Schema Source


* from schema: https://data.moex.com/dams/v0.1






## LinkML Source

<details>
```yaml
name: EntityTypeEnum
description: Роль логической сущности в модели решения.
from_schema: https://data.moex.com/dams/v0.1
rank: 1000
permissible_values:
  core:
    text: core
    description: Базовая сущность, создаваемая и управляемая решением.
  derived:
    text: derived
    description: Производная сущность, вычисляемая или агрегируемая из других данных.
  reference:
    text: reference
    description: Справочная сущность или представление управляемого справочника.

```
</details>

</div>
