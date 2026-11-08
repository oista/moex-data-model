# Репозиторий моделей

Здесь лежит опубликованная модель. Программы её не содержат: они читают рабочую копию этого репозитория.

Кто чем владеет (ADR-058 D7):

- Ветки и запросы на слияние по `model-assets/implementations/`, `external-selections/`, `transformations/`, `external-scopes/`, `catalog-snapshots/` приходят из веб-приложения и от людей. Опись `model-assets/implementations/manifest.yaml` и фиксация `manifest.lock` живут здесь же.
- `model-assets/specifications/`, `model-assets/standards/`, `model-assets/external-sources/`, `generated/` и `packages/ontology/publications/` приходят только запросом на слияние spec-sync из репозитория программ. Вручную их не правят.

Основная ветка `main` закрыта от прямого push. Обновление схем не обгоняет образ программ: сначала на сервер ставят образ с теми же контрактами, потом сливают spec-sync. Иначе служебный интерфейс откажется работать, потому что схема копии и контракты образа разойдутся.

Первое наполнение и spec-sync описаны в репозитории программ, страница «Модели в локальном GitLab».

Файл `.gitlab-ci.yml` запускает проверки только если в проекте задана переменная `MOEX_MODELS_CI=1`. Без неё pipeline пустой. Образ job — `moex-data-model-api`, его runner должен уже иметь у себя.
