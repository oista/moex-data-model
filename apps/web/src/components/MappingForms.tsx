import { useMutation } from "@tanstack/react-query";
import yaml from "js-yaml";
import { useEffect, useMemo, useState, type FormEvent } from "react";
import { api } from "../api/client";
import type { DocumentMutation, WorkspaceDocument } from "../api/types";

type MapSummary = {
  element_id: string;
  name: string;
  title: string;
  description: string;
  source_refs: string[];
  target_refs: string[];
  mapping_type: string;
  mapping_cardinality: string;
};

type Props = {
  workspaceId: string;
  implementationId: string;
  idNamespace: string;
  content: string;
  onDocument: (doc: WorkspaceDocument) => void;
  onBeforeMutate?: () => Promise<void>;
  onOptimisticOp?: (op: DocumentMutation) => void;
  onOptimisticRollback?: () => void;
  disabled?: boolean;
  focusElementId?: string | null;
};

function collectRefOptions(content: string): string[] {
  try {
    const data = yaml.load(content) as {
      logical_entities?: Array<{
        element_id?: string;
        attributes?: Array<{ element_id?: string }>;
      }>;
      data_carriers?: Array<{
        element_id?: string;
        physical_fields?: Array<{ element_id?: string }>;
      }>;
      access_points?: Array<{ element_id?: string }>;
      data_containers?: Array<{ element_id?: string }>;
      execution_assets?: Array<{ element_id?: string }>;
    } | null;
    const ids: string[] = [];
    for (const ent of data?.logical_entities ?? []) {
      if (ent?.element_id) ids.push(String(ent.element_id));
      for (const a of ent?.attributes ?? []) {
        if (a?.element_id) ids.push(String(a.element_id));
      }
    }
    for (const key of [
      "data_carriers",
      "access_points",
      "data_containers",
      "execution_assets",
    ] as const) {
      for (const obj of data?.[key] ?? []) {
        if (obj?.element_id) ids.push(String(obj.element_id));
        const fields = (obj as { physical_fields?: Array<{ element_id?: string }> })
          .physical_fields;
        for (const f of fields ?? []) {
          if (f?.element_id) ids.push(String(f.element_id));
        }
      }
    }
    return ids;
  } catch {
    return [];
  }
}

function parseMappings(content: string): {
  mappings: MapSummary[];
  refOptions: string[];
  error: string | null;
} {
  if (!content.trim()) {
    return { mappings: [], refOptions: [], error: null };
  }
  try {
    const data = yaml.load(content) as {
      mappings?: Array<{
        element_id?: string;
        name?: string;
        title?: string;
        description?: string;
        source_refs?: string[];
        target_refs?: string[];
        mapping_type?: string;
        mapping_cardinality?: string;
      }>;
    } | null;
    const mappings = (data?.mappings ?? [])
      .filter((m) => m?.element_id)
      .map((m) => ({
        element_id: String(m.element_id),
        name: String(m.name || ""),
        title: String(m.title || ""),
        description: String(m.description || ""),
        source_refs: Array.isArray(m.source_refs)
          ? m.source_refs.map(String)
          : [],
        target_refs: Array.isArray(m.target_refs)
          ? m.target_refs.map(String)
          : [],
        mapping_type: String(m.mapping_type || "field_mapping"),
        mapping_cardinality: String(m.mapping_cardinality || "one_to_one"),
      }));
    return {
      mappings,
      refOptions: collectRefOptions(content),
      error: null,
    };
  } catch (err) {
    return {
      mappings: [],
      refOptions: [],
      error: err instanceof Error ? err.message : "Invalid YAML",
    };
  }
}

function refsToText(refs: string[]): string {
  return refs.join(", ");
}

function textToRefs(text: string): string[] {
  return text
    .split(/[,\n]+/)
    .map((s) => s.trim())
    .filter(Boolean);
}

export function MappingForms({
  workspaceId,
  implementationId,
  idNamespace,
  content,
  onDocument,
  onBeforeMutate,
  onOptimisticOp,
  onOptimisticRollback,
  disabled = false,
  focusElementId = null,
}: Props) {
  const { mappings, refOptions, error: parseError } = useMemo(
    () => parseMappings(content),
    [content],
  );
  const [selectedId, setSelectedId] = useState("");
  const selected =
    mappings.find((m) => m.element_id === selectedId) ?? mappings[0] ?? null;

  useEffect(() => {
    if (focusElementId) setSelectedId(focusElementId);
  }, [focusElementId]);

  useEffect(() => {
    if (selected && selected.element_id !== selectedId) {
      setSelectedId(selected.element_id);
    }
  }, [selected, selectedId]);

  const [editName, setEditName] = useState("");
  const [editTitle, setEditTitle] = useState("");
  const [editDescription, setEditDescription] = useState("");
  const [editSources, setEditSources] = useState("");
  const [editTargets, setEditTargets] = useState("");
  const [editType, setEditType] = useState("field_mapping");
  const [editCard, setEditCard] = useState("one_to_one");

  useEffect(() => {
    if (!selected) {
      setEditName("");
      setEditTitle("");
      setEditDescription("");
      setEditSources("");
      setEditTargets("");
      return;
    }
    setEditName(selected.name);
    setEditTitle(selected.title);
    setEditDescription(selected.description);
    setEditSources(refsToText(selected.source_refs));
    setEditTargets(refsToText(selected.target_refs));
    setEditType(selected.mapping_type);
    setEditCard(selected.mapping_cardinality);
  }, [
    selected?.element_id,
    selected?.name,
    selected?.title,
    selected?.description,
    selected?.mapping_type,
    selected?.mapping_cardinality,
    selected?.source_refs,
    selected?.target_refs,
  ]); // eslint-disable-line react-hooks/exhaustive-deps

  const [newId, setNewId] = useState(`dams:mapping/${idNamespace}/new`);
  const [newName, setNewName] = useState("map_new");
  const [newDescription, setNewDescription] = useState("New mapping");
  const [newSources, setNewSources] = useState("");
  const [newTargets, setNewTargets] = useState("");
  const [newType, setNewType] = useState("field_mapping");
  const [newCard, setNewCard] = useState("one_to_one");

  const mutate = useMutation({
    mutationFn: async (body: DocumentMutation) => {
      if (onBeforeMutate) await onBeforeMutate();
      onOptimisticOp?.(body);
      return api.mutateDocument(workspaceId, implementationId, body);
    },
    onSuccess: onDocument,
    onError: () => onOptimisticRollback?.(),
  });

  const busy = disabled || mutate.isPending;
  const defaultRef = refOptions[0] || "";

  function onAdd(e: FormEvent) {
    e.preventDefault();
    const sources = textToRefs(newSources);
    const targets = textToRefs(newTargets);
    mutate.mutate({
      op: "add_mapping",
      mapping: {
        element_id: newId.trim(),
        name: newName.trim(),
        description: newDescription.trim(),
        source_refs: sources.length ? sources : [defaultRef],
        target_refs: targets.length ? targets : [defaultRef],
        mapping_type: newType.trim() || "field_mapping",
        mapping_cardinality: newCard.trim() || "one_to_one",
      },
    });
  }

  function onSave(e: FormEvent) {
    e.preventDefault();
    if (!selected) return;
    mutate.mutate({
      op: "update_mapping",
      element_id: selected.element_id,
      patch: {
        name: editName.trim(),
        title: editTitle.trim(),
        description: editDescription,
        source_refs: textToRefs(editSources),
        target_refs: textToRefs(editTargets),
        mapping_type: editType.trim(),
        mapping_cardinality: editCard.trim(),
      },
    });
  }

  function onDelete() {
    if (!selected) return;
    if (!window.confirm(`Delete mapping ${selected.element_id}?`)) return;
    mutate.mutate({
      op: "delete_mapping",
      element_id: selected.element_id,
    });
    setSelectedId("");
  }

  return (
    <div className="forms-panel" data-testid="mapping-forms">
      <h2>Mappings</h2>
      {parseError && (
        <p className="error" data-testid="yaml-parse-error">
          YAML parse error: {parseError}
        </p>
      )}
      <ul className="entity-list" data-testid="mapping-list">
        {mappings.map((m) => (
          <li key={m.element_id}>
            <button
              type="button"
              className={
                selected?.element_id === m.element_id
                  ? "entity-select active"
                  : "entity-select"
              }
              onClick={() => setSelectedId(m.element_id)}
              disabled={busy}
            >
              <code>{m.element_id}</code> · {m.name}
            </button>
          </li>
        ))}
        {!parseError && mappings.length === 0 && (
          <li className="lede">No mappings</li>
        )}
      </ul>

      {selected && (
        <form
          className="form-block"
          onSubmit={onSave}
          data-testid="edit-mapping-form"
        >
          <h3>Edit mapping</h3>
          <p className="lede">
            <code>{selected.element_id}</code>
          </p>
          <label>
            name
            <input
              type="text"
              value={editName}
              onChange={(e) => setEditName(e.target.value)}
              required
              disabled={busy}
            />
          </label>
          <label>
            title
            <input
              type="text"
              value={editTitle}
              onChange={(e) => setEditTitle(e.target.value)}
              disabled={busy}
            />
          </label>
          <label>
            description
            <textarea
              value={editDescription}
              onChange={(e) => setEditDescription(e.target.value)}
              disabled={busy}
              rows={2}
            />
          </label>
          <label>
            source_refs (comma-separated)
            <input
              type="text"
              value={editSources}
              onChange={(e) => setEditSources(e.target.value)}
              required
              disabled={busy}
              list="mapping-ref-options"
            />
          </label>
          <label>
            target_refs (comma-separated)
            <input
              type="text"
              value={editTargets}
              onChange={(e) => setEditTargets(e.target.value)}
              required
              disabled={busy}
              list="mapping-ref-options"
            />
          </label>
          <label>
            mapping_type
            <input
              type="text"
              value={editType}
              onChange={(e) => setEditType(e.target.value)}
              required
              disabled={busy}
            />
          </label>
          <label>
            mapping_cardinality
            <input
              type="text"
              value={editCard}
              onChange={(e) => setEditCard(e.target.value)}
              required
              disabled={busy}
            />
          </label>
          <div className="row">
            <button className="primary" type="submit" disabled={busy}>
              Save mapping
            </button>
            <button
              type="button"
              onClick={onDelete}
              disabled={busy}
              data-testid="delete-mapping"
            >
              Delete
            </button>
          </div>
        </form>
      )}

      <form className="form-block" onSubmit={onAdd} data-testid="add-mapping-form">
        <h3>Add mapping</h3>
        <label>
          element_id
          <input
            type="text"
            value={newId}
            onChange={(e) => setNewId(e.target.value)}
            required
            disabled={busy}
          />
        </label>
        <label>
          name
          <input
            type="text"
            value={newName}
            onChange={(e) => setNewName(e.target.value)}
            required
            disabled={busy}
          />
        </label>
        <label>
          description
          <input
            type="text"
            value={newDescription}
            onChange={(e) => setNewDescription(e.target.value)}
            required
            disabled={busy}
          />
        </label>
        <label>
          source_refs
          <input
            type="text"
            value={newSources}
            onChange={(e) => setNewSources(e.target.value)}
            placeholder={defaultRef}
            disabled={busy}
            list="mapping-ref-options"
          />
        </label>
        <label>
          target_refs
          <input
            type="text"
            value={newTargets}
            onChange={(e) => setNewTargets(e.target.value)}
            placeholder={defaultRef}
            disabled={busy}
            list="mapping-ref-options"
          />
        </label>
        <label>
          mapping_type
          <input
            type="text"
            value={newType}
            onChange={(e) => setNewType(e.target.value)}
            required
            disabled={busy}
          />
        </label>
        <label>
          mapping_cardinality
          <input
            type="text"
            value={newCard}
            onChange={(e) => setNewCard(e.target.value)}
            required
            disabled={busy}
          />
        </label>
        <button className="primary" type="submit" disabled={busy || !defaultRef}>
          Add mapping
        </button>
      </form>

      <datalist id="mapping-ref-options">
        {refOptions.map((id) => (
          <option key={id} value={id} />
        ))}
      </datalist>

      {mutate.isError && (
        <p className="error">{(mutate.error as Error).message}</p>
      )}
    </div>
  );
}
