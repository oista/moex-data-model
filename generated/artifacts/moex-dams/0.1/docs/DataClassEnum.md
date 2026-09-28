---
search:
  boost: 2.0
---


# Enum: DataClassEnum 




_Класс данных для наследования модельной спецификацией дата-контракта; не совпадает с entity_type._



<div data-search-exclude markdown="1">

URI: [dams:DataClassEnum](https://data.moex.com/dams/DataClassEnum)

## Permissible Values
| Value | Meaning | Description |
| --- | --- | --- |
| reference_data | None | Нормативно-справочная информация (НСИ) |
| master_data | None | Мастер-данные |
| transactional_data | None | Транзакционные данные |
| analytical_data | None | Аналитические или производные наборы данных |
| metadata | None | Метаданные |




## Slots

| Name | Description |
| ---  | --- |
| [data_class](data_class.md) |  |










## Identifier and Mapping Information





### Schema Source


* from schema: https://data.moex.com/dams/v0.1






## LinkML Source

<details>
```yaml
name: DataClassEnum
description: Класс данных для наследования модельной спецификацией дата-контракта;
  не совпадает с entity_type.
from_schema: https://data.moex.com/dams/v0.1
rank: 1000
permissible_values:
  reference_data:
    text: reference_data
    description: Нормативно-справочная информация (НСИ).
  master_data:
    text: master_data
    description: Мастер-данные.
  transactional_data:
    text: transactional_data
    description: Транзакционные данные.
  analytical_data:
    text: analytical_data
    description: Аналитические или производные наборы данных.
  metadata:
    text: metadata
    description: Метаданные.

```
</details>

</div>
