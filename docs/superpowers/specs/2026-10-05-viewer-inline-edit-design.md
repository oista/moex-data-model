# Viewer: inline editing of description / title / aliases (serve mode)

Status: Draft for review  
Date: 2026-10-05  
Scope: `apps/viewer` (derived read model, [ADR-015](../../adr/ADR-015-viewer-ui-atlas.md))

## 1. Goal

Let a model owner edit `description`, `title` and `aliases` of an element
directly from the viewer UI and have the change written to the canonical
YAML/LinkML source in the working tree.

Non-goals (v1):

- Editing computed values (effective definition from the ADR-025 cascade,
  FIBO CSV rows, generated projections such as `dams_glossary.json`, SKOS).
- Editing identifiers (`id`, `name`) or ADR-025 cascade fields
  (`definition_source_ref`, `definition_rationale`, `scoped_definitions`).
- Author / timestamp stored in YAML. History is Git only.
- Any Git operation (stage, commit, push). The owner commits from the IDE.

## 2. Modes

- `dist/index.html` stays autonomous and read-only (`file://`). No change to
  `render_viewer` contract for this mode.
- New command `moex-viewer serve --root . [--port N]` serves the same page
  plus `/api/*` on `127.0.0.1` only.
- Client JS calls `GET /api/capabilities` on load. If unavailable, edit
  controls are not rendered.

## 3. Edit targets

At build time normalizers attach to each editable record:

```
edit_target = {
  file:      <path relative to --root>,
  yaml_path: <path inside the document, e.g. classes.Party.description>,
  field:     "description" | "title" | "aliases",
  base_hash: <hash of the current source value>
}
```

Rules:

- Emitted only by the YAML and LinkML normalizers, and only for fields that
  physically exist in the source file.
- Not emitted for CSV / JSON / Markdown sources, projections, or inherited
  (cascade) values. Those show a link to the source instead of an edit button.
- Stored on `PublicationItem` as a new optional field `edit_target` and
  forwarded by `html_renderer` next to `source_ref`.
- `name` / `id` are shown read-only.

## 4. Write path

- Add `ruamel.yaml` to `apps/viewer/pyproject.toml` (pinned, like the other
  dependencies). PyYAML stays for read-only parsing; it drops comments and
  formatting and must not be used for writes.
- New module `moex_publication_viewer/edits.py`:
  - resolve `file` against `--root`; reject paths outside the root, symlinks
    leaving the root, and anything but `.yaml` / `.yml`;
  - accept only targets that were issued by the last build (registry keyed
    by `(file, yaml_path, field)`); arbitrary paths are not accepted;
  - compare `base_hash` with the current value, otherwise return `409`;
  - update the single value with `ruamel.yaml` round-trip, write atomically
    (temp file + replace), keep a backup in memory for rollback;
  - `aliases`: replace the whole list; hash covers the whole list.
- After writing: rebuild the model (`compile_modules`), run `formal_checks`
  for the affected `moex_dams` package, return diagnostics. If the rebuild
  fails, restore the file and return `422` with errors.
- `title` validation: non-empty; not duplicating a sibling title inside the
  same package. A full rebuild is required because `title` feeds navigation,
  search index and ADR-025 `description == title` diagnostics.

## 5. API

| Method | Path | Purpose |
|---|---|---|
| GET | `/api/capabilities` | `{edit: true, token: <one-time>}` |
| POST | `/api/edit` | `{edit_target, new_value, token}` -> `{ok, diagnostics, item}` |

Errors: `403` bad token / origin, `404` unknown target, `409` hash
conflict, `422` validation or rebuild failure.

## 6. UI

- "Править" next to description, title and aliases in the item card.
  Description / title: text input. Aliases: one value per line.
- Read-only hint explains why a field cannot be edited (inherited,
  generated, source format).
- On success the page refreshes data from the rebuilt model without a full
  reload and shows diagnostics inline. On failure the field stays in edit
  mode with the error.
- Styles and scripts go into the Atlas layers (`static/js/`, `static/css/`),
  following ADR-015; `viewer.js` is not grown further.

## 7. Security

- Bind to `127.0.0.1`; refuse other hosts.
- One-time token issued with the served page and required on `POST`;
  check `Origin` / `Host` to block cross-site requests.
- Only build-issued `edit_target` values are writable (section 4).

## 8. Testing

- Round-trip: edit keeps comments, key order and indentation (byte diff
  limited to the changed value).
- `base_hash` conflict, path escape, wrong extension, unknown target.
- Rebuild failure triggers rollback; file content is restored.
- `title` duplicate / empty rejected; `aliases` list replace.
- UI: edit controls absent in `file://` build, present with serve
  capabilities (pattern of `tests/test_atlas_ui.py`).
- Existing `make viewer-check` stays green.

## 9. Risks / open points

- `edit_target` coverage grows per normalizer; v1 covers YAML and LinkML
  only. Other formats show source links.
- Hand-edited multi-line / folded YAML scalars: round-trip preserves style
  when possible; otherwise fall back to a literal block and report it.
- Concurrent edit in IDE and viewer is caught by `base_hash` (`409`), not
  merged.
