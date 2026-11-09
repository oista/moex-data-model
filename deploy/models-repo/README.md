# Репозиторий моделей

Здесь лежит опубликованная модель. Программы её не содержат: они читают рабочую копию этого репозитория.

Кто чем владеет (ADR-058 D7):

- Ветки и запросы на слияние по `model-assets/implementations/`, `external-selections/`, `transformations/`, `external-scopes/`, `catalog-snapshots/` приходят из веб-приложения и от людей. Опись `model-assets/implementations/manifest.yaml` и фиксация `manifest.lock` живут здесь же. Владелец — группа `@moex/data-architects`.
- `model-assets/specifications/`, `model-assets/standards/`, `model-assets/external-sources/`, `generated/` и `packages/ontology/publications/` приходят только запросом на слияние spec-sync из репозитория программ. Вручную их не правят. Владелец — группа `@moex/spec-sync`. Ей же принадлежат файлы корня `CODEOWNERS` и `.gitlab-ci.yml`.

Файл `CODEOWNERS` в GitLab Community Edition только показывает владельцев в запросе на слияние. Обязательное подтверждение владельцем кода (Code Owner approval) есть лишь в платной редакции. Поэтому владение держится на ролях: группа `@moex/data-architects` приглашена в проект как Maintainer, и сливать в `main` может только Maintainer.

Основная ветка `main` закрыта от прямого push. Обновление схем не обгоняет образ программ: сначала на сервер ставят образ с теми же контрактами, потом сливают spec-sync. Иначе служебный интерфейс откажется работать, потому что схема копии и контракты образа разойдутся.

Первое наполнение и spec-sync описаны в репозитории программ, страница «Модели в локальном GitLab».

Файл `.gitlab-ci.yml` запускает проверки только если в проекте задана переменная `MOEX_MODELS_CI=1`. Без неё pipeline пустой. Образ job — `moex-data-model-api`, его runner должен уже иметь у себя.

Stage 1. Pipeline на запросе на слияние гоняет `models-check`, `ci-validate` (бюджет soft-диагностик в `.moex/warning-baseline.yaml`), `publications-fresh`, блокирующий `semantic-diff` с меткой `approved-breaking` от Maintainer, `matrix-check`, отчёты JUnit/Code Quality и комментарий `mr-summary`. Для API нужен `MOEX_CI_TOKEN`. Сканер секретов и `fmt --check` пока с `allow_failure`.

Приёмка после выката образа и spec-sync:

1. MR с нарушением спецификации (удалён обязательный slot у crm/esed/mdm/ucd) — pipeline красный, Merge закрыт.
2. MR с новым soft-диагностиком вне baseline — красный, в комментарии виден отпечаток.
3. MR с breaking без метки — красный; с меткой от Developer — красный; с меткой от Maintainer на текущем HEAD — зелёный.
