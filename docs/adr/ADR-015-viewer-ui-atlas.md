---
status: Proposed
version: "0.1"
normative: false
supersedes: []
superseded_by: MODELING_ARCHITECTURE.md
---

# ADR-015: MOEX Publication Viewer — UI/UX Design Standard (MOEX Atlas)

**Date:** 2026-09-28  
**Status:** Proposed 0.1  
**Normative parent:** [MODELING_ARCHITECTURE.md](../architecture/MODELING_ARCHITECTURE.md)  
**Related:** [viewer-decisions.md](../architecture/viewer-decisions.md), [viewer-atlas design principles](../design/viewer-atlas/README.md), [ADR-016](ADR-016-publication-section-kinds-and-profiles.md), [ADR-019](ADR-019-publication-contract-inheritance.md)

**Назначение:** дизайн-стандарт и ТЗ на переработку интерфейса статического MOEX Publication Viewer.  
**Целевой артефакт:** один автономный `apps/viewer/dist/index.html`.  
**Область изменений:** визуальный слой, шаблоны, клиентское поведение и UX. Модель публикации, modeling kernel и DAMS не изменяются без отдельного архитектурного решения.

## Context

Текущий Viewer корректно реализует IA (дерево → активный объект, publication modules, deep links, search), но выглядит как сгенерированный документ: слабая иерархия поверхностей, синий accent вместо бренда MOEX, монолитные CSS/JS, CSS/JS рядом с HTML вместо одного автономного файла.

Нужен единый визуальный язык **MOEX Atlas**: корпоративный explorer моделей (не marketing site), графически близкий к ERP B2B Design Kit (поверхности, плотность, sidebar/table/card), с MOEX Red и ограничениями статической публикации.

## Decision

### 1. Цель продукта

Viewer остаётся лёгким статическим представлением formal model assets:

- нормативные спецификации MOEX DAMS;
- реализации моделей;
- LinkML classes, slots, enums, schema-файлы;
- онтологии и термины FIBO;
- таблицы, иерархии, связи, исходный код;
- будущие публикации через `publish.yaml`.

Он **не** становится отдельной информационной системой.

### 2. Неизменяемые ограничения

- Финальный результат сборки — один автономный HTML.
- Нет backend, БД и обязательного web-hosting.
- Pipeline `publish.yaml → publication model → HTML` сохраняется.
- Новый модуль подключается декларативно, без правки shell.
- HTML и DBML не источники истины.
- UI без логики, специфичной только для DAMS или FIBO.
- Deep links сохраняются.
- Исходные данные публикации не меняются ради оформления.
- Нет обязательных CDN; шрифты, иконки, CSS и JS встраиваются при сборке.

### 3. Дизайн-направление: MOEX Atlas

**Характер**

- Современный корпоративный интерфейс редактора документации/модели.
- Светлый, нейтральный, информационно плотный.
- MOEX Red (`#d71920`) — только бренд, active, focus и критические действия.
- Структура через поверхности, интервалы и тонкие границы.
- Тени только у dialogs / popovers / dropdowns.
- Функциональные одноцветные иконки (Lucide, SVG).
- Без эмодзи, glass, градиентных кнопок и декоративных изображений.

**Графический референс:** [ERP B2B Design Kit](https://www.figma.com/community/file/1220373386573896297/erp-b2b-design-kit) — см. [docs/design/viewer-atlas/reference/](../design/viewer-atlas/reference/). Берём плотность, white cards, sidebar/table language; **не** копируем Shop Floor IA и синий accent.

**UX-принципы** — см. [docs/design/viewer-atlas/README.md](../design/viewer-atlas/README.md).

### 4. Каркас приложения

| Зона | Размер | Назначение |
|---|---:|---|
| Sidebar | 288 px (240–420) | Публикации, разделы, иерархия |
| Topbar | 56 px | Поиск, команды, тема |
| Content viewport | Остаток | Активная страница |
| Content container | ≤ 1180 px | Карточки, таблицы, код |
| Reading column | ≤ 76ch | Определения и Markdown |

Sidebar и topbar закреплены. Один основной vertical scroll в content; дерево скроллится отдельно.

Бренд в UI: **Data Specification Player**.

### 5. Информационная архитектура

1. Перечень публикаций (тип, название, версия; active — фон + MOEX Red rail).
2. Группы из publication model (Overview, Classes, Slots, Enums, files, …) — **не** hardcoded в shell.
3. Объекты с стабильным id, type, label, route, optional count.

### 6. Ключевые экраны

Нормативные wireframes (текстовые): Publication Overview (KPI + structure + files + README), Class card (tabs Overview/Attributes/Relations/Usage/Source), FIBO term (middle-ellipsis IRI), Schema file (Overview + Source), Command palette (`Ctrl/Cmd+K`), compact drawer &lt; 900 px.

Полные mocks и component CSS живут в исходниках Viewer после внедрения; этот ADR фиксирует контракт, не дублирует полный stylesheet.

### 7. Дизайн-токены (нормативные)

Светлая / тёмная тема через CSS variables. Канон после внедрения: `apps/viewer/static/css/10-tokens.css`.

Ключевые значения light:

- `--app-bg: #f5f6f8`; `--surface-1: #ffffff`; `--surface-2: #fafbfc`; `--surface-3: #f0f2f5`
- `--text-primary: #17191d`; `--text-secondary: #545c68`; `--text-tertiary: #7d8794`
- `--brand: #d71920`; `--brand-soft: #fcebed`; `--link: #315da8`; `--focus: #d71920`
- spacing 4 px scale; `--radius-sm/md/lg: 6/8/12px`; motion 120–260 ms

Шрифты: **MOEX UI** = Inter Variable (embedded WOFF2); code = JetBrains Mono 400/500 embedded. Fallback: Segoe UI / Arial; Cascadia / Consolas.

### 8. Компоненты и DOM-контракт

Обязательные компоненты: Content Card, Tree Row, Badge, Definition List, Tabs, Data Table, Code Viewer, Search Dialog, Empty/Error states.

Стабильные attributes: `data-ui`, `data-renderer`, `data-tree-node`, `data-node-id`, `data-node-type`, `data-depth`, `data-item-id`, `data-item-type`, ARIA (`aria-current`, `aria-expanded`, `aria-selected`).

Shell не содержит DAMS/FIBO conditionals. Renderer обрабатывает только нормализованную секцию.

### 9. JavaScript modules

Разделение: `state`, `navigation`, `tree`, `search`, `theme`, `clipboard`, `tables`, `dialogs`, `accessibility`. Не смешивать в одном `DOMContentLoaded`-монолите без модульных границ (concat при build допустим).

### 10. Responsive, a11y, print

Breakpoints: 1199 / 899 / 599. &lt; 900 px — sidebar drawer. WCAG AA, focus visible, touch ≥ 44 px, `prefers-reduced-motion`. Print скрывает sidebar/topbar/search.

### 11. Исходная структура (целевая)

```text
apps/viewer/
├── templates/          # shell, sidebar, topbar, content, components/
├── static/css/         # 00-reset … 80-print
├── static/js/          # state, navigation, tree, search, …
├── static/icons/       # Lucide SVG
├── static/fonts/       # WOFF2 sources for embed
└── src/.../build.py    # inline assets → dist/index.html
```

### 12. Запреты

- React/Vue/Svelte только ради оформления.
- Менять `publish.yaml` / publication model ради visual details.
- CDN в итоговом HTML; base64 PNG для UI-icons.
- Отдельные HTML-страницы; rendered HTML как source of truth.
- DAMS/FIBO branching в shell.

**UI display preferences** (theme, density, palette, section visibility, glossary chrome) live in `apps/viewer/config/display.yaml` (product defaults) and reader overlay in `localStorage` (`moex-viewer-prefs`), with graceful fallback when storage is unavailable (`file://`). They must not be authored in `publish.yaml`.

### 13. Definition of Done

- Один автономный HTML; все существующие публикации.
- Новый модуль через `publish.yaml` без правки shell.
- Keyboard: tree, search, tabs, deep links.
- Light/dark эквивалентны функционально.
- 375 px без обрезания; reading column ≤ 76ch; wide tables — horizontal scroll.
- Fonts/icons embedded; неизвестный renderer не валит Viewer; print читаем.

## Consequences

- UI presentation governed by this ADR; pipeline decisions remain in [viewer-decisions.md](../architecture/viewer-decisions.md).
- Build must inline CSS/JS/fonts (сегодня копируются sibling files — это drift, закрывается реализацией Atlas).
- Visual regression / baseline fixtures живут рядом с Viewer tests.

## Alternatives

| Alternative | Почему нет |
|---|---|
| Оставить синий GitHub-like accent | не соответствует бренду MOEX |
| React SPA / Vite | нарушает single-file / no-hosting constraint |
| Копировать Shop Floor IA из Figma | Viewer — model explorer, не MES |
| CDN fonts/icons | нарушает автономность артефакта |

## Related

- ADR-011 (reproducible artifacts)
- [docs/design/viewer-atlas/](../design/viewer-atlas/)
