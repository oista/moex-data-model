---
id: gitlab-models
sources:
  - docs/adr/ADR-058-airgap-image-deploy.md
  - docs/adr/ADR-002-git-published-source.md
  - docs/adr/ADR-012-semantic-diff-review.md
  - deploy/models-repo/paths.yaml
  - scripts/export_models_repo.py
  - docker-compose.yml
  - .env.example
  - docker/models-sync.sh
  - deploy/models-repo/.gitlab-ci.yml
  - apps/api/src/moex_model_api/app.py
  - deploy/models-repo/CODEOWNERS
  - deploy/models-repo/README.md
  - model-assets/implementations/manifest.yaml
draft: true
---

# Модели в локальном GitLab

[Репозиторий моделей](glossary:models-repo) — отдельный проект локального GitLab. Туда публикуют модель, и оттуда рабочий сервер забирает рабочую копию. Программы едут своим архивом, как на странице «Развернуть на рабочем сервере». Эта страница — как завести проект, как сервер его читает и как правка попадает обратно.

Зачем отдельно. Опубликованная модель остаётся ревизией Git (ADR-002). Если положить файлы модели в образ программ, правка модели потребует новой сборки программ. [Защищённая ветка](glossary:protected-branch) `main` не даёт записать правку мимо просмотра: служебный интерфейс открывает ветку и [запрос на слияние](glossary:merge-request), а в `main` напрямую не коммитит. Разбор изменения перед слиянием записан в [ADR-012](docs/adr/ADR-012-semantic-diff-review.md). Прямой push в `main` закрыт. Слияние ждёт зелёный pipeline: `models-check`, [проверка реализаций](glossary:ci-validate) с бюджетом soft-диагностик, свежесть публикаций и `matrix-check`. Job `semantic-diff` блокирует [ломающие изменения](glossary:breaking-change), пока Maintainer не поставит метку `approved-breaking`.

Где лежит. Список путей и файлы корня — `deploy/models-repo/`. Команды — `scripts/export_models_repo.py`. На сервере копия монтируется томом `models`, шаг `models-sync` в `docker-compose.yml` забирает ревизию. Секреты — в `.env` рядом с compose, образец в `.env.example`.

На рабочем сервере app-srv GitLab стоит на той же машине и слушает `http://192.168.10.140:8929`. Проект моделей — `root/moex-models`, ветка `main`. Своего сертификата нет, поэтому `MOEX_GITLAB_CA_BUNDLE` оставляют пустым. Контейнерам нельзя указывать `localhost`: для контейнера это он сам, а не GitLab на хосте. Из контейнеров служебного интерфейса и шага синхронизации открывается адрес сервера `192.168.10.140:8929`; тот же порт отвечает и на мосту Docker `172.17.0.1`. В `.env` на app-srv оба адреса, `MOEX_GITLAB_URL` и `MOEX_MODELS_GIT_URL`, указывают на адрес сервера. Режим `MOEX_AUTH_MODE` там пока `dev`. Переход на `trusted-header` и файл `auth/htpasswd` — отдельное решение.

Что сейчас работает. Команды выделения и [синхронизации схем](glossary:spec-sync) есть. Образы и compose умеют читать GitLab, если в `.env` заданы адрес и токены. Сам проект в GitLab этим репозиторием не создаётся: его заводит человек по шагам ниже.

Шаблон проверок запроса на слияние лежит в `deploy/models-repo/.gitlab-ci.yml` и копируется в корень репозитория моделей вместе с остальными файлами корня. Он ничего не запускает, пока в проекте не задана переменная `MOEX_MODELS_CI=1`. Job берёт образ `moex-data-model-api`. Политика загрузки образа записана внутри `image`: GitLab 19 не принимает её рядом с именем образа. На app-srv работает один runner этого проекта. Это контейнер с сокетом Docker того же хоста: job запускается в Docker, теги job не нужны, образы берутся только уже загруженные (`if-not-present`), в том числе служебный образ, которым runner забирает репозиторий. Его версия совпадает с бинарником runner. Переменная проекта `MODEL_TAG` называет тег на хосте и перекрывает значение из шаблона. Сейчас это `0.1.7-ce81851`. Проверка `models-check` на `main` зелёная. Job `validate` гоняет `moex-model ci-validate` по описи и сравнивает soft-диагностики с `.moex/warning-baseline.yaml`: новое предупреждение и рост счётчика блокируют, уменьшение разрешено. Job `semantic-diff` берёт полную историю (`GIT_DEPTH: 0`) и через `breaking-gate` требует метку `approved-breaking` от Maintainer. Отчёты JUnit и Code Quality кладутся в artifacts; job `mr-summary` обновляет один комментарий в запросе. Сканер секретов (`gitleaks`) и `moex-model fmt --check` пока с `allow_failure`, пока на runner нет образа gitleaks и пока YAML не переформатирован отдельным запросом. Запрос из интерфейса несёт файл модели, обновлённую фиксацию `manifest.lock`, при наличии у решения — пересобранный `publications/vertical_slice.json`, и, когда правка меняет [действующую ответственность](glossary:effective-governance), пересобранный `generated/governance/effective-governance-view-2026-10-12.yaml`. Отдельный `lock update` для такой правки не нужен. Если файл модели меняли руками и сверка фиксации красная, на ветке запроса выполняют `moex-model lock update --root .` и добавляют `manifest.lock` в ту же ветку. В репозитории программ и в копии GitLab фиксация по crm, esed, mdm и ucd уже совпадает, владельцы записаны. Команда `python -m moex_model_cli.gates.publish_gate` в шаблон не входит: на выделенном дереве ей не хватает `scripts/build_release_bundle.py`, этот файл остаётся в репозитории программ.

Для комментария в запросе и проверки метки задают переменную проекта `MOEX_CI_TOKEN` (project access token, роль Developer, scope `api`, masked). Без неё `mr-summary` и `breaking-gate` не достучатся до API.

## Проект

Имя проекта — `moex-models` в нужной группе. Основная ветка — `main`. В настройках ветки: прямой push никому (`Allowed to push: No one`), слияние — только Maintainer. Пункт `Pipelines must succeed` включён. Runner есть, `MOEX_MODELS_CI=1` задана, `models-check` на `main` зелёный. Запрос с испорченной фиксацией остаётся красным, и слить его нельзя. Файл `CODEOWNERS` из `deploy/models-repo/` называет две группы [владельцев кода](glossary:code-owners). Пути моделей принадлежат `@moex/data-architects`, она же записана владельцем каждого документа в `manifest.yaml`. Пути схем и файлы корня `CODEOWNERS` и `.gitlab-ci.yml` принадлежат `@moex/spec-sync`, которая открывает синхронизацию схем. Эти пути вручную не правят. На app-srv стоит GitLab Community Edition. В нём `CODEOWNERS` только показывает владельцев в запросе: обязательное подтверждение владельцем кода (Code Owner approval) и запрет автору утверждать свой запрос есть лишь в платной редакции. Поэтому владение держится на ролях. Группу `@moex/data-architects` приглашают в проект как Maintainer, `@moex/spec-sync` — как Developer, и слить запрос в `main` может только Maintainer.

## Два токена

[Токен развёртывания](glossary:deploy-token) создают на этом проекте, область `read_repository`. Имя и секрет попадают в `MOEX_MODELS_DEPLOY_USER` и `MOEX_MODELS_DEPLOY_TOKEN`. Ими пользуется только шаг синхронизации.

Второй токен — project access token, роль Developer, область `api`. Он попадает в `MOEX_GITLAB_TOKEN`. Им служебный интерфейс создаёт ветку, коммит и запрос на слияние. В защищённую `main` Developer записать не может. Срок ставят заранее и меняют токен до истечения. Оба значения лежат в `.env` на сервере, права файла `600`. В образ и в пакет для контура они не входят.

## Значения на сервере

`MOEX_GIT_PROVIDER=gitlab`. `MOEX_GITLAB_URL` — адрес локального GitLab, как его видит контейнер, не `localhost` контейнера. `MOEX_GITLAB_PROJECT` — `группа/moex-models` или числовой id. `MOEX_GITLAB_BASE=main`. `MOEX_MODELS_GIT_URL` — `https://…/moex-models.git`. `MOEX_MODELS_GIT_REF=main`. `MOEX_MODELS_SYNC_INTERVAL` — секунды между заборами, по умолчанию 60. Сборка просмотра начинается только после того, как закончилась предыдущая, даже если она длилась дольше интервала. `MOEX_AUTH_MODE=trusted-header`. Порт 8000 наружу не публикуют: интерфейс открыт только через nginx веб-приложения.

Если сертификат GitLab внутренний, файл CA кладут в `./certs/gitlab-ca.pem` и пишут `MOEX_GITLAB_CA_BUNDLE=/certs/gitlab-ca.pem`. Каталог `certs` смонтирован в контейнеры интерфейса и синхронизации. Для публичного сертификата переменную оставляют пустой.

## Первая установка

1. На машине с этим репозиторием и с `git filter-repo`: `python scripts/export_models_repo.py seed --dest <пустой каталог>`. В каталоге — история только по путям модели и файлы корня.
2. В каталоге: `git remote add origin <url проекта>` и `git push -u origin HEAD`.
3. Выдать два токена, как выше.
4. На машине с сетью и Docker собрать пакет программ: `make pack-full` или `make pack-contour` с `PARENT_TAG`.
5. Перенести архив на сервер и применить `apply-contour.sh` из архива. Сценарий создаёт `.env` из примера, если файла ещё нет. Секреты и адрес GitLab вписывают до запуска.
6. Создать пароль для входа через nginx. Каталога `auth/` в пакете для контура нет: рядом с `docker-compose.yml` заводят `auth/` и пишут файл `auth/htpasswd`:
   `printf 'user:%s\n' "$(openssl passwd -apr1)" >> auth/htpasswd`.
   В режиме `MOEX_AUTH_MODE=trusted-header` без этого файла контейнер веб-приложения не стартует.
7. Из каталога поставки: `docker compose -f docker-compose.yml -f docker/docker-compose.prod.yml up -d`. Первый файл — `docker-compose.yml`.
8. Проверить. `docker compose logs models-sync` показывает клон и собранный просмотр. `GET /api/health` отвечает. `GET /api/ready` без списка проблем. Страница `/viewer/` открывается.

## Обновление

Программы обновляют новым пакетом для контура, как на странице развёртывания. Модели обновляют слиянием запроса. Шаг синхронизации подхватывает `main` не позже чем через `MOEX_MODELS_SYNC_INTERVAL` секунд. Немедленно — `docker compose restart models-sync`.

Схемы и каталог `generated/` приходят только синхронизацией схем: `python scripts/export_models_repo.py spec-sync --models-clone <клон> --push`. Без `--push` ветка остаётся локальной. При смене схемы DAMS порядок такой. Сначала на сервер ставят образ, в котором те же контракты. Потом сливают запрос синхронизации. Если слить схемы раньше образа, `/ready` покажет расхождение контрактов, и интерфейс не готов.

## Откат

Программы. В `.env` ставят прежний `MODEL_TAG` и снова `docker compose -f docker-compose.yml -f docker/docker-compose.prod.yml up -d`. Старые образы остаются на диске, пока их не удалит уборка упаковки. Что применено, видно в `airgap-state.json` рядом с compose и в метках образа `moexmodel.full_version`, `moexmodel.git_sha`, `moexmodel.deps_fingerprint`.

Модели. Откат — обратный запрос на слияние в GitLab, не переписывание истории. Переписанный `main` останавливает быструю перемотку на сервере: шаг синхронизации делает только `merge --ff-only`. Если историю всё же переписали, один раз внутри контейнера `models-sync` выполняют `git fetch` и `git reset --hard FETCH_HEAD` в каталоге `/models`, либо удаляют том `models` и дают шагу клонировать заново.

## Если не поднимается

`ERROR: ... is not a git checkout and is not empty` — том `models` уже занят чужими файлами. Его очищают до первого клона.

`fetch` отвечает 401 или 403 — токен развёртывания неверный или срок вышел.

`merge --ff-only` отказывается — на сервере грязное дерево или в GitLab переписали историю. Грязное дерево шаг обычно сам возвращает к полученному коммиту после сборки просмотра. Переписанная история — случай отката выше.

Интерфейс отвечает 503 на обычные запросы — копия моделей ещё не совпала с контрактами образа: том пуст до первого клона или схема в копии и в образе разные. `/health` и `/ready` при этом открыты. Смотрят `/ready` и логи `models-sync`.

`/ready` перечисляет расхождения — схема в копии и контракты образа разные. Ставят подходящий образ или сливают синхронизацию схем, не наоборот.

Запрос на слияние не создаётся — у `MOEX_GITLAB_TOKEN` нет области `api` или роль выше, чем нужно для ветки; проект в `MOEX_GITLAB_PROJECT` указан не так; ветка `main` защищена, и это ожидаемо для прямого коммита, не для запроса.

Ошибка TLS — не задан `MOEX_GITLAB_CA_BUNDLE` или файла нет в `/certs`.

Сверка фиксации (`moex-model lock verify --root .`) краснеет, если файл модели поменяли руками и не обновили `manifest.lock`. Запрос из интерфейса несёт обновлённую фиксацию. Для ручной правки на ветке запроса выполняют `moex-model lock update --root .` и добавляют этот файл в ту же ветку.

## Что копировать

Копию моделей хранит резервная копия GitLab. Сессии служебного интерфейса лежат в томе `data` (файл SQLite). Каталог `certs` и `.env` копируют вместе с настройкой сервера, не вместе с образом.
