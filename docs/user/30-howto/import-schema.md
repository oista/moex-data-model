---
id: import-schema
sources:
  - docs/adr/ADR-009-schema-automator-draft-only.md
  - apps/cli/src/moex_model_cli/commands/import_.py
  - apps/cli/src/moex_model_cli/gates/publish_gate.py
  - packages/linkml-tooling/src/moex_linkml_tooling/import_engine.py
  - packages/modeling-kernel/src/moex_modeling/import_draft/public.py
draft: true
---

# Черновой импорт схемы

Чужую схему можно снять в черновик командой `moex-model import` (ADR-009). На вход годятся JSON Schema, SQL, CSV и RDF. Черновик сам в модель не публикуется. Его дописывают: идентификаторы, описания, связи. В состав репозитория он попадает уже как YAML, который правят руками, и только после обычной проверки.

Команде нужны три аргумента и дополнительный пакет. Если пакета `moex-linkml-tooling[automator]` нет, команда останавливается и пишет, чего не хватает.

```text
moex-model import --source-type json_schema --source путь\к\файлу.json --out generated/imports --root .
```

`--source-type` — одно из `json_schema`, `sql`, `csv`, `rdf`. Каталог `--out` задаёте сами. Обычное место — `generated/imports`. Внутри появляется каталог задания со статусом `generated-draft`: исходный файл и то, что программа из него вывела. Шаг `publish-gate` общей проверки путь под `generated/imports` не принимает. Черновик оттуда в публикацию не уходит.

Та же команда с флагами `--workbook`, `--profile` и `--out` читает словарь сущностей и собирает [модельный пакет](glossary:model-package). Это другой вход. К черновику чужой схемы он не относится, и программа schema-automator там не используется.

Где прочитать решение: [ADR-009](docs/adr/ADR-009-schema-automator-draft-only.md).
