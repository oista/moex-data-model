# MOEX Atlas — принципы формирования UI

**Статус:** Proposed 0.1  
**Нормативный ADR:** [ADR-015](../../adr/ADR-015-viewer-ui-atlas.md)  
**Визуальный референс:** [reference/](reference/) (ERP B2B Design Kit, CC BY 4.0)

Publication Viewer — производный статический HTML. Принципы ниже управляют **представлением**, не моделью данных.

## 1. Объект раньше источника

Пользователь сначала видит смысл модели (класс, термин, файл как актив), а не структуру YAML. Исходник доступен через Source / Open path, но не доминирует на Overview.

## 2. Progressive disclosure

Overview даёт определение, identity и ключевые связи. Детали — tabs, accordions, related panels. Не вываливать все attributes и IRI на первый экран.

## 3. Единый shell

DAMS, FIBO, implementation и будущие публикации используют одни правила навигации. Список разделов приходит из publication model, не из hardcoded shell.

## 4. Контекст не теряется

Sidebar, breadcrumbs и активная публикация всегда показывают положение пользователя. Выбор листа не сворачивает ветку дерева.

## 5. Один экран — одна основная задача

Просмотр класса, файла или термина не смешивается с глобальным каталогом. Глобальный поиск — command palette, не второй сайдбар.

## 6. Технические значения доступны, но не доминируют

IRI, paths и identifiers сокращаются (middle ellipsis), полное значение — в `title`, copy action и accessible name.

## 7. Keyboard first

Дерево, поиск, tabs и основные действия доступны без мыши (`Up/Down/Left/Right/Home/End`, `Enter`, `Escape`, `Ctrl/Cmd+K`, `/`).

## 8. Responsive через перестройку

&lt; 900 px: sidebar → drawer, tabs → horizontal scroll, definition lists → одна колонка. Не уменьшать шрифты до нечитаемости.

## Графический маппинг Figma → Atlas

| Берём из ERP B2B Design Kit | Не берём / заменяем |
|---|---|
| Светлый app-bg, белые surface-карточки | Синий primary → **MOEX Red** |
| Sidebar + topbar + content density | Shop Floor / Inventory IA |
| Плотные tree-rows и KPI-strip | Цветные декоративные machine cards |
| Sticky-header таблицы, тонкие borders | Глубокие постоянные тени |
| Минимальные float-shadows у dialogs | Glass / gradients / emoji |

Скриншоты и captions: [reference/README.md](reference/README.md).

## Пространство и иерархия

- Иерархия поверхностей: `app-bg` → `surface-1` (панели/карточки) → `surface-2/3` (hover, table header).
- Active tree: soft brand background + 2 px MOEX Red rail.
- Карточки: padding 24 px, gap 16 px, radius ≤ 12 px, без цветной полосы сбоку.
- Reading column Markdown ≤ 76ch.

## Именование в UI

- Продукт: **MOEX Model Explorer**
- Концепция: **MOEX Atlas**
- Артефакт сборки: `apps/viewer/dist/index.html`
