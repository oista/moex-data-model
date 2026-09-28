# Viewer client modules (MOEX Atlas)

Canonical application script today: [`../viewer.js`](../viewer.js).

Target split (ADR-015), concatenated by `moex_publication_viewer.assets.assemble_js` when files exist:

| File | Responsibility |
|---|---|
| `state.js` | View state and subscriptions |
| `navigation.js` | Hash routing, deep links |
| `tree.js` | Expand/collapse, keyboard |
| `search.js` | Index filter, command palette |
| `theme.js` | Light/dark |
| `clipboard.js` | Copy link / IRI / path |
| `tables.js` | Sort, columns, overflow |
| `dialogs.js` | Focus trap, Escape |
| `accessibility.js` | Announcements, focus after nav |
| `app.js` | Bootstrap |

Until the split lands, `assemble_js()` falls back to `static/viewer.js` (which already includes Atlas search dialog, drawer, tree filter, and status announcements).
