---
name: "moex-data-model: Publication requirements nav"
overview: "Добавить под DAMS «Требования» последний пункт «Публикация» по зеркалу «ИТ-решения»: список PublicationRequirement (entity-table) и исходник publication-requirements.yaml (source_file)."
todos:
  - id: flatten-helper
    content: Helper flatten profiles[].requirements → rows (id, name, description, profile, required) + YamlNormalizer select flattened_requirements
    status: completed
  - id: explorer-tree
    content: Добавить group Публикация (list section_ref + source_file) последним child у Требования; ИТ-решения не трогать
    status: completed
  - id: publish-yaml
    content: Секция publication-requirements entity-table в moex-dams publish.yaml
    status: completed
  - id: viewer-badges
    content: Badge/meta section_root для requirements-publication* в viewer.js
    status: completed
  - id: tests-docs
    content: Обновить normalizer/explorer tests + nav hierarchy design note
    status: completed
isProject: false
---

# moex-data-model: Publication requirements nav

## Цель

В explorer DAMS:

```text
Требования
├── ИТ-решения          ← без изменений
└── Публикация          ← новый
    ├── Требования публикации
    └── Спецификация
```

Источник: [`model-assets/specifications/moex-dams/0.1/publication-requirements.yaml`](model-assets/specifications/moex-dams/0.1/publication-requirements.yaml) (ADR-019). Новый renderer не вводить.

## Locked approach

Зеркало «ИТ-решения» через explorer в [`dams_explorer_roots.py`](apps/viewer/src/moex_publication_viewer/normalizers/dams_explorer_roots.py) + секция `entity-table` в [`publish.yaml`](model-assets/specifications/moex-dams/0.1/publish.yaml).

Несуществующие поля из наброска **не** добавлять:

- `parent_section` — нет в `ManifestSection`; вложенность только через explorer groups / `section_ref`
- `type: source-code` / `renderer: publication-requirements-table` — нет в `SectionType`; raw YAML уже рендерится как `source_file` (`data-renderer="source-code"`)
- `format: linkml-yaml` + `select: classes` — файл не LinkML; это `profiles[].requirements`

## Изменения

### 1. Flatten helper

В helpers / `dams_explorer_roots`: из YAML → плоский список записей:

| колонка | откуда |
|--------|--------|
| `id` | `requirement.id` |
| `name` | `title` (fallback `id`) |
| `description` | `description` / capability |
| `profile` | id профиля (`dams-logical-modeling` / `dams-logical-and-physical`) |
| `required` | `obligation` → `required` \| `recommended` |

Явный select для нормализатора: `flattened_requirements` (не `classes`).

### 2. Explorer tree

В `wrap_dams_explorer_roots`:

- `group:requirements-publication` — **последний** child у `group:requirements`
- `group:requirements-publication-list` — «Требования публикации»: `section_ref` → секция `publication-requirements`
- `group:requirements-publication-spec` — «Спецификация»: один `source_file` на `publication-requirements.yaml` (как min-spec / example)

Обновить `member_ids` / `structure_why` у корня «Требования». **ИТ-решения не трогать.**

### 3. `publish.yaml`

```yaml
- id: publication-requirements
  title: Требования публикации
  description: PublicationRequirement из publication-requirements.yaml (ADR-019)
  type: entity-table
  kind: source
  source:
    format: yaml
    path: publication-requirements.yaml
    select: flattened_requirements
  columns: [id, name, description, profile, required]
  filterable: [profile, required]
  sort: { by: id, order: asc }
  default_collapsed: true
```

`kind: source` — из закрытого ADR-016 enum (документация контракта публикации эталона).

### 4. YamlNormalizer

В [`yaml_normalizer.py`](apps/viewer/src/moex_publication_viewer/normalizers/yaml_normalizer.py): при `select: flattened_requirements` — flatten `profiles[].requirements` → list[dict], затем `records_to_items`. Иначе прежняя `select_path`.

### 5. Viewer UI

В [`viewer.js`](apps/viewer/static/viewer.js): badge/meta для новых `section_root` (`requirements-publication`, `requirements-publication-list`, `requirements-publication-spec`) по аналогии с IT-solutions (count / files). Открытие list → существующий entity-table path через `section_ref`.

### 6. Tests + docs

- Обновить [`test_normalizers.py`](apps/viewer/tests/test_normalizers.py) / [`test_dams_explorer_roots.py`](apps/viewer/tests/test_dams_explorer_roots.py): children корня Требования = `{it-solutions, publication}`; состав Публикация; flatten rows
- Короткий unit на YamlNormalizer + `flattened_requirements`
- Строка в [`2026-09-28-viewer-nav-hierarchy-design.md`](docs/superpowers/specs/2026-09-28-viewer-nav-hierarchy-design.md) под Target UX

## Проверка

`make viewer-check` (или точечные pytest по listed tests).
