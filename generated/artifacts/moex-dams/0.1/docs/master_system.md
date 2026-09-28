---
search:
  boost: 5.0
---

# Slot: master_system 

<div data-search-exclude markdown="1">



URI: [dams:master_system](https://data.moex.com/dams/master_system)
<!-- no inheritance hierarchy -->





## Applicable Classes

| Name | Description | Modifies Slot |
| --- | --- | --- |
| [RegistryEntry](RegistryEntry.md) | Локальная ссылочная проекция записи внешней мастер-системы; не является масте... |  no  |
| [ITSystem](ITSystem.md) | ИТ-система; мастер данных — EAM |  no  |
| [ITSolution](ITSolution.md) | ИТ-решение, объединяющее одну или несколько ИТ-систем; мастер данных — EAM |  no  |
| [ITPlatform](ITPlatform.md) | ИТ-платформа; мастер данных — EAM |  no  |
| [BusinessDomain](BusinessDomain.md) | Бизнес-домен или предметная область; мастер определяется архитектурным govern... |  no  |
| [GlossaryTerm](GlossaryTerm.md) | Термин корпоративного бизнес-глоссария |  no  |
| [OrganizationUnit](OrganizationUnit.md) | Организационное подразделение |  no  |
| [Role](Role.md) | Управляемая роль владельца, стюарда, потребителя или согласующего |  no  |
| [DataClassificationTerm](DataClassificationTerm.md) | Специальная категория чувствительности или регулирования, например ПДн или ин... |  no  |
| [Policy](Policy.md) | Политика доступа, хранения, качества или архитектурный инвариант |  no  |
| [BusinessProcess](BusinessProcess.md) | Ссылка на бизнес-процесс или его шаг в BPMN-репозитории |  no  |
| [DataContractReference](DataContractReference.md) | Ссылка на дата-контракт в корпоративном дата-каталоге |  no  |
| [IntegrationReference](IntegrationReference.md) | Ссылка на интеграцию в Clinkr |  no  |






## Properties

### Type and Range

| Property | Value |
| --- | --- |
| Range | [String](String.md) |
| Domain Of | [RegistryEntry](RegistryEntry.md) |

### Cardinality and Requirements

| Property | Value |
| --- | --- |
| Required | Yes |










## Identifier and Mapping Information





### Schema Source


* from schema: https://data.moex.com/dams/v0.1




## Mappings

| Mapping Type | Mapped Value |
| ---  | ---  |
| self | dams:master_system |
| native | dams:master_system |




## LinkML Source

<details>
```yaml
name: master_system
from_schema: https://data.moex.com/dams/v0.1
rank: 1000
domain_of:
- RegistryEntry
range: string
required: true

```
</details></div>
