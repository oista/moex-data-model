# MOEX Publication Viewer — UI/UX Design Standard and Implementation Guide
**Статус:** Proposed 0.1  
**Назначение:** дизайн-стандарт и техническое задание на переработку интерфейса статического MOEX Publication Viewer  
**Целевой артефакт:** один автономный `apps/viewer/dist/index.html`  
**Область изменений:** визуальный слой, шаблоны, клиентское поведение и UX; модель публикации, modeling kernel и DAMS не изменяются без отдельного архитектурного решения
## 1. Цель
MOEX Publication Viewer должен стать лёгким, современным и единообразным интерфейсом для просмотра формальных модельных активов:

- нормативных спецификаций MOEX DAMS;
- конкретных реализаций моделей;
- LinkML-классов, slots, enums и schema-файлов;
- онтологий и терминов FIBO;
- таблиц, иерархий, связей и исходного кода;
- будущих публикаций, подключаемых через `publish.yaml`.

Переработка не должна превращать Viewer в отдельную информационную систему. Он остаётся производным статическим представлением модели публикации, формируемым в виде одного автономного HTML-файла.
## 2. Неизменяемые ограничения
Следующие ограничения являются обязательными:

- Финальный результат сборки — один автономный HTML.
- Viewer не требует backend, базы данных и web-hosting.
- Существующий pipeline `publish.yaml → publication model → HTML` сохраняется.
- Новый модуль должен подключаться декларативно, без изменения shell-интерфейса.
- HTML и DBML не становятся источниками истины.
- UI не должен содержать логику, специфичную только для DAMS или FIBO.
- Deep links должны сохраняться.
- Исходные данные публикации не должны изменяться ради оформления.
- В итоговом HTML не должно быть обязательных CDN-зависимостей.
- Все шрифты, иконки, стили и JavaScript встраиваются при сборке.
## 3. Оценка текущего решения
Текущая информационная архитектура в целом корректна:

- слева расположено иерархическое дерево публикаций и объектов;
- сверху находятся поиск и глобальные действия;
- справа отображается активная карточка;
- публикации организованы независимо;
- поддерживаются DAMS, implementation-модель и FIBO;
- пользователь может переходить к исходным schema-файлам.

Основные проблемы находятся не в концепции, а в качестве представления:

- слабая визуальная иерархия между фоном, панелью и карточками;
- дерево трудно быстро сканировать;
- типы объектов обозначены недостаточно системно;
- toolbar перегружен равноценными текстовыми кнопками;
- длинные IRI и технические идентификаторы нарушают композицию;
- карточки используют свободное пространство неравномерно;
- отсутствует полноценное представление атрибутов, связей и зависимостей;
- недостаточно проработаны keyboard navigation и responsive behavior;
- UI выглядит как результат генерации документа, а не как законченный инструмент просмотра.
## 4. Дизайн-направление
Рабочее название визуальной концепции — **MOEX Atlas**.
### 4.1. Характер
- Современный корпоративный интерфейс.
- Визуальный язык редактора документации и модели, а не маркетингового сайта.
- Светлый, нейтральный, информационно плотный, но не перегруженный.
- MOEX Red используется только для бренда, активного состояния, фокуса и критически важных действий.
- Структура создаётся главным образом поверхностями, интервалами и тонкими границами.
- Тени применяются только для плавающих элементов: dialogs, popovers, dropdowns.
- Иконки функциональные и одноцветные.
- Декоративные изображения, эмодзи, стеклянные панели и градиентные кнопки не используются.
### 4.2. UX-принципы
1. **Сначала объект, затем его источник.** Пользователь видит смысл модели, а не структуру YAML.
2. **Прогрессивное раскрытие.** Обзор показывает основное; детали открываются tabs, accordions и related panels.
3. **Единый shell.** DAMS, FIBO, implementation и будущие публикации используют одинаковые правила навигации.
4. **Контекст не теряется.** Sidebar, breadcrumbs и активная публикация всегда показывают положение пользователя.
5. **Один экран — одна основная задача.** Просмотр класса, файла или термина не смешивается с глобальным каталогом.
6. **Технические значения доступны, но не доминируют.** IRI, paths и identifiers сокращаются визуально и копируются полностью.
7. **Keyboard first.** Дерево, поиск, tabs и действия доступны без мыши.
8. **Responsive — через перестройку, а не уменьшение.** Sidebar становится drawer, таблицы — scroll container, definition lists — одной колонкой.
## 5. Каркас приложения
```text
┌─────────────────────────────────────────────────────────────────────────────┐
│ MOEX MODEL EXPLORER │ Search models, classes, terms…  ⌘K │ ◐ │ ⋯          │
├─────────────────────┬───────────────────────────────────────────────────────┤
│                     │ MOEX DAMS / Integration / DataFlow                   │
│  Publications       │                                                       │
│                     │ DataFlow                                  Class       │
│  ● MOEX DAMS   0.1  │ Поток данных между системами и объектами модели       │
│    Trading     1.0  │                                                       │
│  ● FIBO       2026  │ [Overview] [Attributes 12] [Relations 4] [Source]     │
│                     │                                                       │
│  Filter tree…       │ ┌───────────────────────────────────────────────────┐ │
│                     │ │ Definition                                        │ │
│  ▾ Classes      40  │ │ ...                                               │ │
│    ▾ Integration    │ └───────────────────────────────────────────────────┘ │
│      C DataFlow     │                                                       │
│      C Binding      │ ┌──────────────────────┐ ┌──────────────────────────┐ │
│    ▸ Governance     │ │ Identity             │ │ Relationships            │ │
│    ▸ Analytics      │ │ ID, package, source  │ │ refers to / referred by │ │
│                     │ └──────────────────────┘ └──────────────────────────┘ │
│  ─────────────────  │                                                       │
│  Ontology Catalog   │                                                       │
└─────────────────────┴───────────────────────────────────────────────────────┘
```
### 5.1. Основные зоны
| Зона | Размер | Назначение |
|---|---:|---|
| Sidebar | 288 px; регулируется от 240 до 420 px | Публикации, разделы, классы, файлы и иерархия объектов |
| Topbar | 56 px | Поиск, команды текущего представления, тема |
| Content viewport | Остаток окна | Активная страница публикации |
| Content container | До 1180 px | Карточки, таблицы, код и диаграммы |
| Reading column | До 76ch | Определения и Markdown-документация |

Sidebar и topbar закрепляются. Основная область содержит единственный основной вертикальный scroll. Дерево может прокручиваться независимо, но вложенных вертикальных scroll areas внутри карточек следует избегать.
## 6. Информационная архитектура
### 6.1. Первый уровень
Sidebar начинается с перечня публикаций:

- MOEX DAMS;
- Trading solution;
- FIBO;
- будущие спецификации и реализации;
- Other publications.

Публикация отображается компактной строкой с типом, названием и версией. Текущая публикация выделяется фоном и индикатором MOEX Red.
### 6.2. Второй уровень
После выбора публикации показываются группы:

- Overview;
- Classes;
- Slots или Attributes;
- Enumerations;
- Specification files;
- Implementations;
- Glossary;
- Class hierarchy;
- Relationships;
- Diagrams;
- другие sections из publication model.

Shell не должен содержать фиксированный список разделов. Их порядок и видимость приходят из нормализованной publication model.
### 6.3. Третий уровень
Внутри группы отображаются:

- packages;
- классы;
- атрибуты;
- enum;
- термины;
- schema-файлы;
- реализации;
- диаграммы.

Каждый элемент имеет стабильный идентификатор, тип, label, route и optional count.
## 7. Моки экранов
### 7.1. Overview публикации
```text
MOEX DAMS                                                     Specification 0.1
Reference specification корпоративной модели данных MOEX

┌──────────────────────┬──────────────────────┬──────────────────────┐
│ 40 Classes           │ 126 Slots            │ 9 Enumerations       │
│ 7 packages           │ 8 schema files       │ LinkML               │
└──────────────────────┴──────────────────────┴──────────────────────┘

Structure
┌────────────────────────────────────────────────────────────────────┐
│ Core                         14 classes                             │
│ Концептуальные, логические и физические элементы модели            │
├────────────────────────────────────────────────────────────────────┤
│ Governance                    8 classes                             │
│ Владение, lifecycle, классификация и provenance                    │
├────────────────────────────────────────────────────────────────────┤
│ Integration                   2 classes                             │
│ DataFlow, DataFlowEntityBinding                                    │
└────────────────────────────────────────────────────────────────────┘

Specification files
moex-core.yaml              14 classes · 42 slots
moex-governance.yaml         8 classes · 17 slots
moex-integration.yaml        2 classes · 11 slots

Documentation
[README content]
```

Верхняя часть overview должна отвечать на вопросы:

- Что это за публикация?
- Какую роль она играет?
- Какой у неё стандарт и версия?
- Что в неё входит?
- Куда перейти дальше?

README располагается после структурированного обзора, а не заменяет его.
### 7.2. Карточка класса
```text
DataFlow
Поток данных между системами и объектами корпоративной модели

Class · Integration                              moex-integration.yaml

Overview    Attributes 8    Relations 3    Usage 5    Source

Definition
Описывает направленную передачу данных между источником и получателем,
связанную с интеграцией и элементами логической модели.

Identity
Qualified name       dams:DataFlow                         [Copy]
Package              Integration
Parent               ModelElement                          [Open]
Source               moex-integration.yaml                 [Open]

Attributes
┌──────────────────────┬──────────────┬──────────┬──────────┬─────────────┐
│ Attribute            │ Type         │ Required │ Multiple │ Description │
├──────────────────────┼──────────────┼──────────┼──────────┼─────────────┤
│ id                   │ URI          │ Yes      │ No       │ ...         │
│ source_system_ref    │ RegistryRef  │ Yes      │ No       │ ...         │
│ bindings             │ Binding      │ No       │ Yes      │ ...         │
└──────────────────────┴──────────────┴──────────┴──────────┴─────────────┘
```

Информация группируется по пользовательским задачам, а не по порядку ключей в YAML.
### 7.3. Термин FIBO
```text
cash settlement method                           метод денежного расчёта

FIBO class · DER · OWL 2                             Open source ↗

Definition
Strategy for calculating or otherwise establishing a reference
final price for the contract.

Русское определение
Способ определения итоговой справочной цены контракта.

Identity
IRI          spec.edmcouncil.org/…/CashSettlementMethod      [Copy]
Local name   CashSettlementMethod
Domain       DER

Taxonomy
Credit derivatives
└── Credit default swaps
    └── Cash settlement method

Related terms
Credit default swap · Settlement · Reference price
```

Длинный IRI отображается сокращённо через middle ellipsis, но полное значение сохраняется в `title`, copy action и accessible name.
### 7.4. Файл спецификации
```text
moex-analytics.yaml                                  YAML · 0.1.0

schemas/moex-analytics.yaml                           [Copy path] [Raw]

Overview    Definitions    Dependencies    Source

Dependencies
Imports  5                                       Imported by  1

← linkml:types      ← moex-core        ← moex-governance
← moex-types        ← moex-registries
→ moex-dams

Definitions
2 classes · 0 enums · 11 slots

Source
┌────┬───────────────────────────────────────────────────────────────┐
│  1 │ id: https://data.moex.com/dams/analytics/v0.1                │
│  2 │ name: moex_analytics                                        │
│  3 │ version: 0.1.0                                              │
│  4 │ imports:                                                    │
│  5 │   - linkml:types                                            │
└────┴───────────────────────────────────────────────────────────────┘
```

Для schema-файла обязательны два режима:

- **Overview** — интерпретированная структура;
- **Source** — исходный YAML, JSON или CSV.
### 7.5. Глобальный поиск
По `Ctrl/Cmd + K` открывается command palette:

```text
┌──────────────────────────────────────────────────────────────────┐
│ Search classes, attributes, terms and files…                     │
├──────────────────────────────────────────────────────────────────┤
│ CLASSES                                                          │
│ C  DataFlow                                      MOEX DAMS       │
│ C  DataFlowEntityBinding                         MOEX DAMS       │
│                                                                  │
│ FIBO TERMS                                                       │
│ C  cash settlement method                       DER             │
│ C  cash flow                                    FND             │
│                                                                  │
│ FILES                                                            │
│ F  moex-integration.yaml                        Specification    │
└──────────────────────────────────────────────────────────────────┘
```

Требования:

- результаты группируются по типам;
- поддерживаются title, alias, translated label, description, identifier и source path;
- совпавшая часть подсвечивается;
- `Up/Down` перемещают выбор;
- `Enter` открывает результат;
- `Escape` закрывает dialog и возвращает focus;
- до прокрутки показывается 8–10 результатов;
- индекс полностью встроен в HTML.
### 7.6. Компактный режим
```text
┌─────────────────────────────────────────────────────────────┐
│ ☰  MOEX Explorer      Search…                        ◐  ⋯   │
├─────────────────────────────────────────────────────────────┤
│ MOEX DAMS / Integration / DataFlow                           │
│                                                             │
│ DataFlow                                            Class    │
│ [Overview] [Attributes] [Relations] [Source]                 │
│                                                             │
│ Definition                                                  │
│ ...                                                         │
└─────────────────────────────────────────────────────────────┘
```

При ширине меньше 900 px sidebar превращается в modal drawer шириной `min(88vw, 360px)`. Tabs прокручиваются горизонтально, а таблицы получают отдельный horizontal scroll container.
## 8. Дизайн-токены
### 8.1. Светлая тема
```css
:root,
[data-theme="light"] {
  --app-bg: #f5f6f8;
  --surface-1: #ffffff;
  --surface-2: #fafbfc;
  --surface-3: #f0f2f5;

  --text-primary: #17191d;
  --text-secondary: #545c68;
  --text-tertiary: #7d8794;
  --text-disabled: #a8afb9;
  --text-inverse: #ffffff;

  --border-subtle: rgba(18, 24, 33, 0.08);
  --border-default: rgba(18, 24, 33, 0.13);
  --border-strong: rgba(18, 24, 33, 0.22);

  --brand: #d71920;
  --brand-hover: #b91118;
  --brand-active: #950d13;
  --brand-soft: #fcebed;

  --link: #315da8;
  --focus: #d71920;

  --success: #147d52;
  --warning: #9b6300;
  --danger: #bd1e2d;
  --info: #315da8;

  --code-bg: #f7f8fa;
  --code-gutter: #eceff3;
  --selection-bg: #fcebed;

  --shadow-float:
    0 1px 2px rgba(18, 24, 33, 0.05),
    0 8px 24px rgba(18, 24, 33, 0.06);
}
```
### 8.2. Тёмная тема
```css
[data-theme="dark"] {
  --app-bg: #101216;
  --surface-1: #171a20;
  --surface-2: #1c2027;
  --surface-3: #242a33;

  --text-primary: #f1f3f5;
  --text-secondary: #b4bbc5;
  --text-tertiary: #858f9d;
  --text-disabled: #606875;
  --text-inverse: #121418;

  --border-subtle: rgba(255, 255, 255, 0.07);
  --border-default: rgba(255, 255, 255, 0.12);
  --border-strong: rgba(255, 255, 255, 0.20);

  --brand: #ff5a61;
  --brand-hover: #ff7379;
  --brand-active: #e54750;
  --brand-soft: rgba(255, 90, 97, 0.13);

  --link: #8eb4f0;
  --focus: #ff6b72;

  --success: #56b98b;
  --warning: #e2ae55;
  --danger: #ff747e;
  --info: #8eb4f0;

  --code-bg: #12151a;
  --code-gutter: #1b1f26;
  --selection-bg: rgba(255, 90, 97, 0.12);

  --shadow-float:
    0 1px 2px rgba(0, 0, 0, 0.3),
    0 12px 36px rgba(0, 0, 0, 0.24);
}
```
### 8.3. Пространственная шкала
```css
:root {
  --space-1: 4px;
  --space-2: 8px;
  --space-3: 12px;
  --space-4: 16px;
  --space-5: 20px;
  --space-6: 24px;
  --space-8: 32px;
  --space-10: 40px;
  --space-12: 48px;
}
```

Рекомендуемые значения:

- Sidebar item: `6px 8px`.
- Module row: `10px 12px`.
- Toolbar gap: `8px`.
- Card padding: `24px`, в крупных detail-карточках `28px`.
- Расстояние между карточками: `16px`.
- Content gutter: `32px`.
- Mobile content gutter: `16px`.
- Tree indentation: `16px` на уровень.
### 8.4. Radius и motion
```css
:root {
  --radius-sm: 6px;
  --radius-md: 8px;
  --radius-lg: 12px;
  --radius-full: 999px;

  --duration-fast: 120ms;
  --duration-default: 180ms;
  --duration-slow: 260ms;
  --ease-standard: cubic-bezier(0.2, 0, 0, 1);
}
```

Анимация применяется только к `opacity`, `transform`, цвету, border и box-shadow. Раскрытие дерева может анимироваться только при отсутствии проблем с производительностью; для больших деревьев предпочтительно мгновенное изменение с коротким fade содержимого.
## 9. Типографика
### 9.1. Основной шрифт
Рекомендуемый шрифт — **Inter Variable** с поддержкой кириллицы. Он должен быть встроен в HTML как WOFF2 data URI во время сборки.

```css
@font-face {
  font-family: "MOEX UI";
  src: url("data:font/woff2;base64,...") format("woff2");
  font-weight: 100 900;
  font-style: normal;
  font-display: swap;
}
```

Fallback:

```css
font-family:
  "MOEX UI",
  "Segoe UI",
  Arial,
  sans-serif;
```

Для исходного кода:

```css
font-family:
  "JetBrains Mono",
  "Cascadia Code",
  "SFMono-Regular",
  Consolas,
  monospace;
```

JetBrains Mono рекомендуется встроить в двух начертаниях: 400 и 500.
### 9.2. Размеры
```css
:root {
  --font-2xs: 11px;
  --font-xs: 12px;
  --font-sm: 13px;
  --font-ui: 14px;
  --font-body: 15px;
  --font-lead: 16px;
  --font-h3: 18px;
  --font-h2: 22px;
  --font-h1: 28px;

  --line-compact: 1.25;
  --line-ui: 1.4;
  --line-body: 1.6;
}
```

| Элемент | Размер | Вес |
|---|---:|---:|
| Название продукта | 15 px | 650 |
| Sidebar item | 13–14 px | 400 |
| Активный sidebar item | 13–14 px | 600 |
| Badge | 11–12 px | 500 |
| Breadcrumb | 12 px | 400 |
| Body | 15 px | 400 |
| Lead definition | 16 px | 400 |
| Card heading | 16–18 px | 600 |
| Page title | 26–28 px | 650 |
| Code | 13 px | 400 |

Не следует использовать `font-weight: 700–800` повсеместно. Основной набор весов: 400, 500, 600 и 650.
## 10. Компоненты
### 10.1. Content Card
```css
.content-card {
  padding: var(--space-6);
  background: var(--surface-1);
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-lg);
  box-shadow: 0 1px 2px rgba(18, 24, 33, 0.025);
}

.content-card + .content-card {
  margin-top: var(--space-4);
}
```

Карточка не должна иметь:

- толстую цветную полосу сбоку;
- декоративный градиент;
- глубокую постоянную тень;
- радиус более 16 px;
- несколько вложенных карточек без необходимости.

Для `Identity`, `Relationships`, `Taxonomy` применяются definition lists или двухколоночная сетка внутри общей карточки.
### 10.2. Tree Row
```html
<button class="tree-row" style="--tree-level: 2">
  <span class="tree-toggle" aria-hidden="true"></span>
  <span class="type-icon type-icon--class">C</span>
  <span class="tree-label">DataFlow</span>
  <span class="tree-count">8</span>
</button>
```

```css
.tree-row {
  position: relative;
  width: 100%;
  min-height: 30px;
  display: grid;
  grid-template-columns: 16px 20px minmax(0, 1fr) auto;
  align-items: center;
  gap: 6px;

  padding:
    4px
    8px
    4px
    calc(8px + var(--tree-level) * 16px);

  color: var(--text-secondary);
  background: transparent;
  border: 0;
  border-radius: 7px;
  text-align: left;
}

.tree-row:hover {
  color: var(--text-primary);
  background: var(--surface-3);
}

.tree-row[aria-current="page"] {
  color: var(--text-primary);
  background: var(--selection-bg);
  font-weight: 600;
}

.tree-row[aria-current="page"]::before {
  content: "";
  position: absolute;
  inset-block: 6px;
  left: 0;
  width: 2px;
  border-radius: 2px;
  background: var(--brand);
}

.tree-label {
  min-width: 0;
  overflow: hidden;
  white-space: nowrap;
  text-overflow: ellipsis;
}
```

Требования:

- Стрелка вправо означает свёрнутое состояние.
- Стрелка вниз означает раскрытое состояние.
- У листа слот chevron остаётся пустым.
- Счётчик располагается справа.
- Hover визуально слабее active.
- Полное длинное имя доступно через tooltip или `title`.
- `Left` сворачивает ветку.
- `Right` раскрывает ветку.
- `Up/Down` перемещают focus.
- `Home/End` переходят к первому или последнему видимому узлу.
- Активный объект прокручивается в видимую область.
- Состояние раскрытия сохраняется при переходах.
### 10.3. Badges
```css
.badge {
  display: inline-flex;
  align-items: center;
  min-height: 22px;
  padding: 2px 8px;
  border: 1px solid var(--border-subtle);
  border-radius: var(--radius-full);
  color: var(--text-secondary);
  background: var(--surface-2);
  font-size: var(--font-xs);
  font-weight: 500;
  line-height: 1;
}

.badge--brand {
  color: var(--brand-active);
  background: var(--brand-soft);
  border-color: transparent;
}
```

На одной строке рекомендуется не более трёх badges.
### 10.4. Definition List
```css
.definition-list {
  display: grid;
  grid-template-columns: minmax(140px, 220px) minmax(0, 1fr);
  column-gap: var(--space-6);
  row-gap: var(--space-3);
}

.definition-list dt {
  color: var(--text-tertiary);
  font-size: var(--font-sm);
}

.definition-list dd {
  min-width: 0;
  color: var(--text-primary);
}
```

На мобильном definition list переключается в одну колонку.
### 10.5. Tabs
Tabs применяются для разных представлений одного объекта:

- Overview;
- Attributes;
- Relations;
- Usage;
- Dependencies;
- Source.

Tabs не используются как глобальная навигация между публикациями.

```css
.tabs {
  display: flex;
  gap: var(--space-1);
  overflow-x: auto;
  border-bottom: 1px solid var(--border-subtle);
}

.tab {
  min-height: 40px;
  padding: 0 var(--space-3);
  color: var(--text-secondary);
  white-space: nowrap;
  border-bottom: 2px solid transparent;
}

.tab[aria-selected="true"] {
  color: var(--text-primary);
  border-bottom-color: var(--brand);
  font-weight: 600;
}
```
### 10.6. Data Table
```css
.data-table-shell {
  position: relative;
  overflow: auto;
  border: 1px solid var(--border-subtle);
  border-radius: 10px;
  background: var(--surface-1);
}

.data-table {
  width: 100%;
  border-collapse: collapse;
}

.data-table th {
  position: sticky;
  top: 0;
  z-index: 1;
  height: 40px;
  padding: 0 12px;
  color: var(--text-secondary);
  background: var(--surface-2);
  border-bottom: 1px solid var(--border-default);
  font-size: var(--font-xs);
  font-weight: 600;
  text-align: left;
}

.data-table td {
  min-height: 44px;
  padding: 10px 12px;
  border-bottom: 1px solid var(--border-subtle);
  font-size: var(--font-sm);
  vertical-align: top;
}

.data-table tbody tr:hover {
  background: var(--surface-2);
}
```

Возможности:

- сортировка колонок;
- скрытие колонок;
- закрепление первой колонки;
- горизонтальная прокрутка;
- команда `Columns`;
- фильтрация по tags;
- popover полного значения;
- copy action для identifier и IRI;
- sticky header.
### 10.7. Code Viewer
```css
.code-view {
  overflow: auto;
  max-height: min(68vh, 860px);
  background: var(--code-bg);
  border: 1px solid var(--border-subtle);
  border-radius: 10px;
  font: 400 13px/1.65 var(--font-code);
  tab-size: 2;
}

.code-line {
  display: grid;
  grid-template-columns: 52px minmax(max-content, 1fr);
}

.code-line-number {
  padding-right: 12px;
  color: var(--text-tertiary);
  background: var(--code-gutter);
  text-align: right;
  user-select: none;
}

.code-line-content {
  padding-left: 16px;
  white-space: pre;
}
```

Code viewer поддерживает:

- line numbers;
- copy all;
- copy selected line;
- wrap/no-wrap;
- переход к строке по deep link;
- highlight выбранной строки;
- подсветку YAML, JSON, CSV, Markdown и Turtle без обязательной внешней библиотеки.
## 11. Пиктограммы
Использовать SVG-пиктограммы Lucide, встроенные в HTML во время генерации.

| Объект | Иконка |
|---|---|
| Specification | `book-open` |
| Implementation | `box` |
| Class | `braces` или типовая метка `C` |
| Attribute/slot | `list-tree` |
| Enumeration | `list` |
| File | `file-code-2` |
| Package | `package` |
| Ontology | `network` |
| Glossary | `book-a` |
| Relationship | `git-branch` |
| Data flow | `workflow` |
| Source | `code-2` |
| Search | `search` |
| Copy | `copy` |
| External link | `external-link` |
| Theme | `sun` / `moon` |
| Sidebar | `panel-left-open` / `panel-left-close` |
| Overflow menu | `ellipsis` |
| Fit graph | `maximize` |
| Filter | `list-filter` |

```css
.icon {
  width: 16px;
  height: 16px;
  stroke-width: 1.75;
  flex: none;
}

.icon-button .icon {
  width: 18px;
  height: 18px;
}
```

Иконки не помещаются в декоративные цветные круги. Icon-only button обязательно имеет `aria-label` и tooltip.
## 12. Верхняя панель
Новая иерархия действий:

```text
[Search models, classes, terms…                    ⌘K] [Expand all] [⋯] [◐]
```

Меню `⋯` содержит:

- Collapse all;
- Copy link;
- Copy identifier;
- Open source;
- Print;
- About publication.

`Expand all` и `Collapse all` могут быть одной контекстной командой.

```css
.topbar {
  height: 56px;
  display: flex;
  align-items: center;
  gap: var(--space-2);
  padding: 0 var(--space-5);
  background: color-mix(in srgb, var(--surface-1) 92%, transparent);
  border-bottom: 1px solid var(--border-subtle);
  backdrop-filter: blur(12px);
}

.search-trigger {
  max-width: 620px;
  flex: 1;
  height: 36px;
}
```

На мобильном поиск представлен icon button или компактным полем; вторичные действия переносятся в overflow menu.
## 13. Изображения и диаграммы
Для Viewer полезными изображениями являются визуализации самой модели, а не фотографии или декоративные иллюстрации.

Необходимые типы:

- Dependency graph schema-файлов.
- Class hierarchy.
- Relationship graph.
- DataFlow topology.
- Мини-карта структуры публикации.
- ER-проекция через drawDB.
- Semantic diff.

Контракт renderer:

```yaml
section:
  id: class-hierarchy
  title: Class hierarchy
  renderer: graph
  options:
    graph_kind: class-hierarchy
    direction: top-down
    interactive: true
```

Допустимые `graph_kind`:

- `class-hierarchy`;
- `dependencies`;
- `relationships`;
- `data-flow`;
- `implementation-map`;
- `semantic-diff`.

Визуальный стиль:

- нейтральный canvas;
- узлы используют `surface-1`;
- активный узел использует MOEX Red;
- родительский или основной узел использует `text-primary`;
- внешние объекты имеют пунктирную границу;
- связи имеют толщину 1–1.5 px;
- подписи имеют размер 12–13 px;
- zoom controls находятся справа снизу;
- доступны `Fit`, `100%` и `Fullscreen`;
- SVG является предпочтительным форматом экспорта;
- узлы не должны иметь постоянные глубокие тени.
## 14. DOM-контракт
CSS и JavaScript должны опираться на стабильные `data-*` attributes и ARIA, а не на случайную вложенность `div`.

```html
<body
  data-viewer-version="2"
  data-theme="light"
  data-density="comfortable">

<aside data-ui="sidebar">
<nav data-ui="publication-tree">

<button
  data-tree-node
  data-node-id="dams:DataFlow"
  data-node-type="class"
  data-depth="3"
  aria-expanded="false">

<main data-ui="content">
<article
  data-publication-item
  data-item-id="dams:DataFlow"
  data-item-type="class">

<section data-renderer="definition">
<section data-renderer="properties-table">
<section data-renderer="source-code">
```

Обязательные attributes:

| Attribute | Назначение |
|---|---|
| `data-ui` | Стабильная часть shell или component |
| `data-renderer` | Тип renderer секции |
| `data-node-id` | Стабильный идентификатор tree node |
| `data-node-type` | Тип объекта |
| `data-depth` | Уровень дерева |
| `data-item-id` | Идентификатор активного объекта |
| `data-item-type` | Тип активного объекта |
| `aria-current` | Активная ссылка или node |
| `aria-expanded` | Состояние ветки |
| `aria-selected` | Активный tab |
## 15. Исходная структура проекта
Ограничение «один HTML» относится к выходному артефакту, а не к организации исходников.

```text
apps/viewer/src/moex_publication_viewer/
├── templates/
│   ├── shell.html.j2
│   ├── sidebar.html.j2
│   ├── topbar.html.j2
│   ├── content.html.j2
│   └── components/
│       ├── tree.html.j2
│       ├── card.html.j2
│       ├── definition-list.html.j2
│       ├── tabs.html.j2
│       ├── table.html.j2
│       ├── code.html.j2
│       ├── glossary.html.j2
│       ├── graph.html.j2
│       ├── search-dialog.html.j2
│       └── states.html.j2
├── static/
│   ├── css/
│   │   ├── 00-reset.css
│   │   ├── 10-tokens.css
│   │   ├── 20-base.css
│   │   ├── 30-layout.css
│   │   ├── 40-components.css
│   │   ├── 50-renderers.css
│   │   ├── 60-utilities.css
│   │   ├── 70-responsive.css
│   │   └── 80-print.css
│   ├── js/
│   │   ├── state.js
│   │   ├── navigation.js
│   │   ├── tree.js
│   │   ├── search.js
│   │   ├── theme.js
│   │   ├── clipboard.js
│   │   ├── tables.js
│   │   ├── dialogs.js
│   │   └── accessibility.js
│   ├── icons/
│   └── fonts/
└── build/
    ├── inline_assets.py
    └── assemble_html.py
```

Сборщик объединяет шаблоны, CSS, JavaScript, fonts, icons, publication data и search index в один `dist/index.html`.
## 16. JavaScript-модули
### 16.1. Состояние
```javascript
const state = {
  activePublicationId: null,
  activeItemId: null,
  expandedNodeIds: new Set(),
  searchQuery: "",
  theme: "system",
  sidebarOpen: true,
  density: "comfortable"
};
```

Для автономного файла состояние хранится в памяти. Если позже понадобится сохранение настроек, это должно быть отдельным решением с graceful fallback.
### 16.2. Ответственность модулей
| Модуль | Ответственность |
|---|---|
| `state.js` | Единое view state и подписки |
| `navigation.js` | Hash routing, history, deep links |
| `tree.js` | Expand/collapse, focus и keyboard navigation |
| `search.js` | Index, ranking и command palette |
| `theme.js` | System/light/dark theme |
| `clipboard.js` | Copy link, IRI, path, identifier |
| `tables.js` | Sort, filters, columns и overflow |
| `dialogs.js` | Open/close, focus trap, Escape |
| `accessibility.js` | Announcements и focus management |

Нельзя смешивать tree, theme, search и routing в одном обработчике `DOMContentLoaded`.
## 17. Renderer architecture
Каждый тип `PublicationSection` обрабатывается независимым renderer:

- `markdown-doc`;
- `entity-detail`;
- `properties-table`;
- `enum-table`;
- `glossary`;
- `schema-source`;
- `dependency-list`;
- `hierarchy`;
- `relationship-graph`;
- `data-flow`;
- `raw-json`;
- `raw-yaml`;
- `raw-csv`.

Renderer получает только нормализованную секцию и render context:

```python
class SectionRenderer(Protocol):
    renderer_type: str

    def render(
        self,
        section: PublicationSection,
        context: RenderContext,
    ) -> str:
        ...
```

Renderer не должен:

- управлять shell;
- формировать sidebar;
- изменять theme;
- реализовывать hash routing;
- читать `publish.yaml` напрямую;
- содержать DAMS- или FIBO-specific branching, если оно может быть выражено данными.
## 18. Responsive behavior
```css
@media (max-width: 1199px) {
  /* Уменьшенные content gutters и sidebar width. */
}

@media (max-width: 899px) {
  /* Sidebar drawer, full-width content, mobile topbar. */
}

@media (max-width: 599px) {
  /* One-column cards, compact header, scrollable tabs and tables. */
}
```

На ширине менее 900 px:

- sidebar становится drawer;
- появляется menu button;
- content занимает всю ширину;
- tabs допускают horizontal scroll;
- definition lists становятся одноколоночными;
- secondary actions переходят в overflow menu.

На ширине менее 600 px:

- card padding уменьшается до 16 px;
- page title уменьшается до 22–24 px;
- таблицы не преобразуются в нечитаемые узкие колонки, а прокручиваются;
- touch targets имеют минимум 44×44 px;
- breadcrumbs допускают middle truncation.
## 19. Accessibility
Обязательные требования:

- Использовать `header`, `aside`, `nav`, `main`, `article`, `section`, `table`, `dl`.
- На активной странице должен быть один `h1`.
- Заголовки идут в правильной иерархии.
- Tree использует подходящий ARIA pattern.
- Search dialog имеет `role="dialog"`, accessible name и focus trap.
- Icon-only buttons имеют `aria-label`.
- Body text соответствует контрасту WCAG AA.
- Focus indicator не удаляется.
- Touch target на мобильном имеет размер не менее 44 px.
- `prefers-reduced-motion` отключает необязательные переходы.
- После keyboard navigation focus перемещается на `h1` активной страницы.
- Динамические результаты поиска объявляются через `aria-live`.
- Copy action сообщает результат через доступный status region.
## 20. Print stylesheet
При печати:

- скрываются sidebar, topbar, search dialog и интерактивные controls;
- контент занимает всю ширину;
- URLs могут выводиться после внешних ссылок;
- карточки не разрываются без необходимости;
- code blocks допускают перенос или печать в landscape;
- цвета остаются различимыми в grayscale;
- tabs преобразуются в последовательные секции либо печатается только активный tab по явному правилу.

```css
@media print {
  [data-ui="sidebar"],
  [data-ui="topbar"],
  [data-ui="search-dialog"],
  .no-print {
    display: none !important;
  }

  [data-ui="content"] {
    width: 100%;
    max-width: none;
    overflow: visible;
  }

  .content-card {
    break-inside: avoid;
    box-shadow: none;
  }
}
```
## 21. Состояния интерфейса
### Loading
Для статического Viewer загрузка короткая, но при больших встроенных индексах допускается skeleton для content и состояния `Building search index…`.
### Empty
Empty state объясняет, почему данных нет:

- No attributes defined for this class.
- No parent found in the selected preview.
- No publications matched the filter.
### Error
Ошибки показывают:

- понятное сообщение;
- имя публикации или секции;
- возможное действие;
- раскрываемые технические details.

Raw traceback не отображается как основной пользовательский текст.
### Unsupported renderer
```text
This section uses an unsupported renderer: timeline-v2.
The publication data is available in raw JSON.
[Open raw data]
```

Viewer не должен падать целиком из-за одной неизвестной секции.
## 22. Инструкция для Cursor
Следующий текст можно сохранить как `.cursor/plans/viewer-redesign.md`.
### Цель
Переработать визуальную систему и UX статического Publication Viewer, сохранив:

- один автономный `apps/viewer/dist/index.html`;
- существующий pipeline `publish.yaml → publication model → HTML`;
- существующую семантику публикаций;
- deep links;
- поддержку MOEX DAMS, implementation-моделей, FIBO и остальных модулей;
- отсутствие backend и обязательного web-hosting.

Не менять modeling kernel, DAMS schemas, publication model и содержимое `publish.yaml`, если изменение не требуется для общего renderer contract.
### Этап 1. Зафиксировать baseline
1. Выполнить текущую сборку Viewer.
2. Сохранить baseline HTML как test fixture, не редактируя его.
3. Зафиксировать DOM snapshots ключевых представлений.
4. Проверить маршруты Overview, Class, Slot, Enum, Schema file, Implementation и FIBO term.
5. Зафиксировать Search, Expand/Collapse, Copy link, Theme и Deep link.
6. Не менять publication manifests и данные.
### Этап 2. Ввести токены
Создать `10-tokens.css`:

- light и dark surface tokens;
- уровни текста;
- MOEX Red brand tokens;
- semantic status colors;
- spacing 4 px;
- typography scale;
- radius scale;
- border и shadow tokens;
- motion duration/easing;
- sidebar и topbar dimensions.

Hardcoded colors и spacing в component CSS запрещаются.
### Этап 3. Разделить shell
Выделить шаблоны:

- `AppShell`;
- `Sidebar`;
- `Topbar`;
- `ContentViewport`;
- `MobileDrawer`;
- `SearchDialog`.

Финальный build продолжает содержать один HTML.
### Этап 4. Компонентная библиотека
Реализовать:

- `Button`;
- `IconButton`;
- `Badge`;
- `Breadcrumbs`;
- `Tree`;
- `TreeNode`;
- `Card`;
- `DefinitionList`;
- `Tabs`;
- `DataTable`;
- `CodeViewer`;
- `CopyField`;
- `SearchDialog`;
- `EmptyState`;
- `ErrorState`;
- `GraphToolbar`.

Компоненты реализовать через Jinja macros или equivalent template partials.
### Этап 5. Обновить renderers
Каждый `PublicationSection.renderer` реализовать отдельной функцией или шаблоном:

- `markdown-doc`;
- `entity-detail`;
- `properties-table`;
- `enum-table`;
- `glossary`;
- `schema-source`;
- `dependency-list`;
- `hierarchy`;
- `relationship-graph`;
- `data-flow`;
- `raw-json`.

Renderer не управляет shell, sidebar, theme или routing.
### Этап 6. Перестроить sidebar
1. Визуально отделить публикации от дерева активной публикации.
2. Добавить filter input для текущего дерева.
3. Сохранить постоянный слот для chevron.
4. Использовать отступ уровня 16 px.
5. Добавить type icons.
6. Активный узел обозначать фоном и красным индикатором.
7. Реализовать `Up/Down`, `Left/Right`, `Home/End`, `Enter`.
8. Не сворачивать ветки при выборе элемента.
9. Автоматически раскрывать путь активного элемента.
10. Поддержать изменение ширины sidebar в desktop mode.
### Этап 7. Реализовать новый поиск
1. Topbar search открывает modal command palette.
2. Индекс остаётся встроенным в HTML.
3. Результаты группируются в Publications, Classes, Attributes, Enumerations, Terms и Files.
4. Индексировать aliases, translated labels и identifiers.
5. Добавить keyboard navigation.
6. Сохранять query только в памяти.
7. По `Escape` возвращать focus на search trigger.
8. Добавить `Ctrl/Cmd + K` и `/` как shortcuts.
### Этап 8. Добавить responsive behavior
Breakpoints:

```css
@media (max-width: 1199px) { }
@media (max-width: 899px) { }
@media (max-width: 599px) { }
```

На экранах меньше 900 px:

- Sidebar становится drawer.
- Появляется menu button.
- Content занимает 100%.
- Tabs допускают horizontal scroll.
- Definition list становится одноколоночным.
- Таблицы прокручиваются горизонтально.
### Этап 9. Обеспечить доступность
- Semantic HTML.
- Один `h1` на активной странице.
- ARIA tree pattern.
- Focus trap в dialogs.
- Accessible names у icon buttons.
- WCAG AA contrast.
- Touch targets не менее 44 px.
- `prefers-reduced-motion`.
- Focus management после навигации.
- `aria-live` для результатов поиска и copy feedback.
### Этап 10. Добавить тесты
Проверить:

- создаётся один HTML;
- в HTML нет обязательных внешних ресурсов;
- internal links разрешаются;
- icon buttons имеют accessible name;
- активный tree path раскрыт;
- deep link открывает нужный объект;
- search находит DAMS class и FIBO term;
- light и dark tokens присутствуют;
- таблицы не расширяют viewport;
- на ширине 375 px контент не обрезается;
- print stylesheet скрывает sidebar и toolbar;
- desktop, tablet и mobile screenshots соответствуют golden baseline.
### Запреты
- Не добавлять React, Vue или Svelte только ради нового оформления.
- Не менять `publish.yaml` для визуальных деталей.
- Не хранить UI preferences в publication model. Допустимо: дефолты в `apps/viewer/config/display.yaml` и overlay читателя в `localStorage` (`moex-viewer-prefs`) с graceful fallback.
- Не использовать CDN в итоговом HTML.
- Не использовать base64 PNG для UI-icons.
- Не создавать отдельные HTML-страницы.
- Не делать rendered HTML источником истины.
- Не смешивать все JavaScript-функции в одном модуле.
- Не дублировать renderer markup в нескольких шаблонах.
- Не использовать DAMS/FIBO conditionals в shell.
## 23. Порядок pull requests
1. `viewer: capture UI baseline and behavior tests`
2. `viewer: introduce design tokens and embedded fonts`
3. `viewer: split shell templates and static sources`
4. `viewer: redesign sidebar and accessible tree`
5. `viewer: redesign page header cards and tabs`
6. `viewer: add reusable tables and code viewer`
7. `viewer: add command palette search`
8. `viewer: add responsive drawer and print styles`
9. `viewer: add graph renderer contract`
10. `viewer: accessibility and visual regression hardening`

Каждый PR должен сохранять работающую сборку единственного HTML.
## 24. Definition of Done
Редизайн считается завершённым, если:

- Финальный артефакт — один автономный HTML.
- Все существующие публикации отображаются.
- Новый модуль подключается через `publish.yaml` без изменения shell.
- UI shell не зависит от DAMS или FIBO.
- Каждый renderer тестируется отдельно.
- Поиск, дерево, tabs и deep links управляются с клавиатуры.
- Светлая и тёмная темы функционально эквивалентны.
- На ширине 375 px отсутствуют потерянный и обрезанный контент.
- На ширине 1440 px строки документации не растягиваются сверх 76ch.
- Wide tables имеют управляемый горизонтальный scroll.
- Исходники разделены на tokens, base, layout, components, renderers, responsive и print.
- Все шрифты и UI-icons встроены.
- Сборка воспроизводима.
- Неизвестный renderer не ломает Viewer целиком.
- Print mode создаёт читаемое представление активного объекта.
## 25. Что сохранить и изменить
### Сохранить
- Модель «дерево → активный объект».
- Publication-based организацию.
- Breadcrumbs.
- Ссылки на source.
- Глобальный поиск.
- Deep linking.
- Независимость Viewer от конкретного modeling standard.
- Генерацию одного HTML.
### Изменить
- Визуальную иерархию.
- Читаемость и keyboard behavior дерева.
- Плотность и структуру карточек.
- Представление контекстных действий.
- Search UX.
- Tables и code viewer.
- Responsive behavior.
- Системность CSS и шаблонов.
- Доступность.
- Поддержку диаграмм как независимых renderers.