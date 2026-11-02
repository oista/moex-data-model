---
id: change-and-check
sources:
  - scripts/check_all.py
  - Makefile
  - scripts/compare_golden.py
  - scripts/generate_contracts.py
  - docs/adr/ADR-011-reproducible-artifacts.md
  - docs/adr/ADR-047-repository-manifest-and-lock.md
draft: true
---

# Изменить модель и проверить

Модель правят в YAML и прогоняют одной общей командой. Так в коммит не попадает файл, который уже не сходится с остальным репозиторием.

Из корня: `python scripts/check_all.py`. То же делает `make check`. Один шаг запускают так: `python scripts/check_all.py --only compare-golden`. Имена шагов совпадают с целями Makefile. Пока шаг не прошёл, следующие не запускаются. Чтобы увидеть все сбои за один проход, добавляют `--keep-going`.

Шаг `compare-golden` сверяет каталог `generated/` со свежей сборкой. Это [производные файлы](glossary:derived-artifact): их снова получают из YAML (ADR-011). Если шаг упал, схема и эталон разъехались. Соберите заново то, о чём он пишет: `make generate-contracts`, `make generate-artifacts` и `make generate-bundle`. Затем повторите `python scripts/check_all.py --only compare-golden`. Каталог `generated/` руками не правят. Если схему менять не собирались, верните правку схемы и оставьте эталон как был.

Если менялся состав документов или сам документ из [описи состава](glossary:repository-manifest), устаревает [фиксация состава](glossary:repository-lock). Её переписывает только `moex-model lock update --root .`. Команда `moex-model lock verify --root .` (цель `make lock-verify`) файл не переписывает, она только сверяет (ADR-047). Оба шага входят в общую проверку: `check-manifest` и `lock-verify`.

Где прочитать решение: [ADR-011](docs/adr/ADR-011-reproducible-artifacts.md), [ADR-047](docs/adr/ADR-047-repository-manifest-and-lock.md).
