---
id: build-viewer
sources:
  - Makefile
  - apps/viewer/README.md
  - apps/viewer/src/moex_publication_viewer/cli.py
  - docs/adr/ADR-057-user-documentation.md
draft: true
---

# Собрать просмотр

[Публикация](glossary:publication) модели и этот текст собираются разными командами. Обе читают исходники и пишут HTML. Готовый HTML руками не правят: правят исходник и собирают снова.

Просмотр модели собирает `make viewer`. Команда ставит `apps/viewer` и вызывает `moex-publication-viewer build`. Открыть результат локально: `make viewer-serve`, адрес на порту 8765. В общую проверку эта сборка не входит. Её запускают, когда нужно посмотреть модель.

Этот текст собирает `make user-docs`. Команда пишет `docs/user/index.html` (ADR-057). Файл открывают в браузере, отдельный сервер не нужен. Общая проверка сверяет его со свежей сборкой шагом `user-docs`, то же делает `make user-docs-check`. Если менялись страницы в `docs/user/`, в том же изменении коммитят и собранный `docs/user/index.html`. Иначе проверка не сойдётся.

Где прочитать решение: [ADR-057](docs/adr/ADR-057-user-documentation.md).
