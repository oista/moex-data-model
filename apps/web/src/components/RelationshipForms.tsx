import { useMutation } from "@tanstack/react-query";
import yaml from "js-yaml";
import { useEffect, useMemo, useState, type FormEvent } from "react";
import { api } from "../api/client";
import type { DocumentMutation, WorkspaceDocument } from "../api/types";

type RelSummary = {
  element_id: string;
  name: string;
  title: string;
  description: string;
  source_entity_ref: string;
  target_entity_ref: string;
};

type Props = {
  workspaceId: string;
  content: string;
  onDocument: (doc: WorkspaceDocument) => void;
  onBeforeMutate?: () => Promise<void>;
  onOptimisticOp?: (op: DocumentMutation) => void;
  onOptimisticRollback?: () => void;
  disabled?: boolean;
  focusElementId?: string | null;
};

function parseRelationships(content: string): {
  relationships: RelSummary[];
  entityIds: string[];
  error: string | null;
} {
  if (!content.trim()) {
    return { relationships: [], entityIds: [], error: null };
  }
  try {
    const data = yaml.load(content) as {
      logical_entities?: Array<{ element_id?: string }>;
      relationships?: Array<{
        element_id?: string;
        name?: string;
        title?: string;
        description?: string;
        source_entity_ref?: string;
        target_entity_ref?: string;
      }>;
    } | null;
    const entityIds = (data?.logical_entities ?? [])
      .filter((e) => e?.element_id)
      .map((e) => String(e.element_id));
    const relationships = (data?.relationships ?? [])
      .filter((r) => r?.element_id)
      .map((r) => ({
        element_id: String(r.element_id),
        name: String(r.name || ""),
        title: String(r.title || ""),
        description: String(r.description || ""),
        source_entity_ref: String(r.source_entity_ref || ""),
        target_entity_ref: String(r.target_entity_ref || ""),
      }));
    return { relationships, entityIds, error: null };
  } catch (err) {
    return {
      relationships: [],
      entityIds: [],
      error: err instanceof Error ? err.message : "Invalid YAML",
    };
  }
}

export function RelationshipForms({
  workspaceId,
  content,
  onDocument,
  onBeforeMutate,
  onOptimisticOp,
  onOptimisticRollback,
  disabled = false,
  focusElementId = null,
}: Props) {
  const { relationships, entityIds, error: parseError } = useMemo(
    () => parseRelationships(content),
    [content],
  );
  const [selectedId, setSelectedId] = useState("");
  const selected =
    relationships.find((r) => r.element_id === selectedId) ??
    relationships[0] ??
    null;

  useEffect(() => {
    if (focusElementId) {
      setSelectedId(focusElementId);
    }
  }, [focusElementId]);

  useEffect(() => {
    if (selected && selected.element_id !== selectedId) {
      setSelectedId(selected.element_id);
    }
  }, [selected, selectedId]);

  const [editName, setEditName] = useState("");
  const [editTitle, setEditTitle] = useState("");
  const [editDescription, setEditDescription] = useState("");
  const [editSource, setEditSource] = useState("");
  const [editTarget, setEditTarget] = useState("");

  useEffect(() => {
    if (!selected) {
      setEditName("");
      setEditTitle("");
      setEditDescription("");
      setEditSource("");
      setEditTarget("");
      return;
    }
    setEditName(selected.name);
    setEditTitle(selected.title);
    setEditDescription(selected.description);
    setEditSource(selected.source_entity_ref);
    setEditTarget(selected.target_entity_ref);
  }, [
    selected?.element_id,
    selected?.name,
    selected?.title,
    selected?.description,
    selected?.source_entity_ref,
    selected?.target_entity_ref,
  ]); // eslint-disable-line react-hooks/exhaustive-deps

  const [newId, setNewId] = useState("dams:rel/trading/NewRel");
  const [newName, setNewName] = useState("new_rel");
  const [newDescription, setNewDescription] = useState("New relationship");
  const [newSource, setNewSource] = useState("");
  const [newTarget, setNewTarget] = useState("");

  const mutate = useMutation({
    mutationFn: async (body: DocumentMutation) => {
      if (onBeforeMutate) await onBeforeMutate();
      onOptimisticOp?.(body);
      return api.mutateDocument(workspaceId, body);
    },
    onSuccess: onDocument,
    onError: () => onOptimisticRollback?.(),
  });

  const busy = disabled || mutate.isPending;
  const defaultEntity = entityIds[0] || "";

  function onAdd(e: FormEvent) {
    e.preventDefault();
    mutate.mutate({
      op: "add_relationship",
      relationship: {
        element_id: newId.trim(),
        name: newName.trim(),
        description: newDescription.trim(),
        source_entity_ref: (newSource || defaultEntity).trim(),
        target_entity_ref: (newTarget || defaultEntity).trim(),
      },
    });
  }

  function onSave(e: FormEvent) {
    e.preventDefault();
    if (!selected) return;
    mutate.mutate({
      op: "update_relationship",
      element_id: selected.element_id,
      patch: {
        name: editName.trim(),
        title: editTitle.trim(),
        description: editDescription,
        source_entity_ref: editSource.trim(),
        target_entity_ref: editTarget.trim(),
      },
    });
  }

  function onDelete() {
    if (!selected) return;
    if (!window.confirm(`Delete relationship ${selected.element_id}?`)) return;
    mutate.mutate({
      op: "delete_relationship",
      element_id: selected.element_id,
    });
    setSelectedId("");
  }

  return (
    <div className="forms-panel" data-testid="relationship-forms">
      <h2>Relationships</h2>
      {parseError && (
        <p className="error" data-testid="yaml-parse-error">
          YAML parse error: {parseError}
        </p>
      )}
      <ul className="entity-list" data-testid="relationship-list">
        {relationships.map((rel) => (
          <li key={rel.element_id}>
            <button
              type="button"
              className={
                selected?.element_id === rel.element_id
                  ? "entity-select active"
                  : "entity-select"
              }
              onClick={() => setSelectedId(rel.element_id)}
              disabled={busy}
            >
              <code>{rel.element_id}</code> · {rel.name}
            </button>
          </li>
        ))}
        {!parseError && relationships.length === 0 && (
          <li className="lede">No relationships</li>
        )}
      </ul>

      {selected && (
        <form
          className="form-block"
          onSubmit={onSave}
          data-testid="edit-relationship-form"
        >
          <h3>Edit relationship</h3>
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
            source_entity_ref
            <select
              value={editSource}
              onChange={(e) => setEditSource(e.target.value)}
              disabled={busy}
            >
              {entityIds.map((id) => (
                <option key={id} value={id}>
                  {id}
                </option>
              ))}
              {editSource && !entityIds.includes(editSource) && (
                <option value={editSource}>{editSource}</option>
              )}
            </select>
          </label>
          <label>
            target_entity_ref
            <select
              value={editTarget}
              onChange={(e) => setEditTarget(e.target.value)}
              disabled={busy}
            >
              {entityIds.map((id) => (
                <option key={id} value={id}>
                  {id}
                </option>
              ))}
              {editTarget && !entityIds.includes(editTarget) && (
                <option value={editTarget}>{editTarget}</option>
              )}
            </select>
          </label>
          <div className="row">
            <button className="primary" type="submit" disabled={busy}>
              Save relationship
            </button>
            <button
              type="button"
              onClick={onDelete}
              disabled={busy}
              data-testid="delete-relationship"
            >
              Delete
            </button>
          </div>
        </form>
      )}

      <form className="form-block" onSubmit={onAdd} data-testid="add-relationship-form">
        <h3>Add relationship</h3>
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
          source_entity_ref
          <select
            value={newSource || defaultEntity}
            onChange={(e) => setNewSource(e.target.value)}
            disabled={busy || entityIds.length === 0}
          >
            {entityIds.map((id) => (
              <option key={id} value={id}>
                {id}
              </option>
            ))}
          </select>
        </label>
        <label>
          target_entity_ref
          <select
            value={newTarget || defaultEntity}
            onChange={(e) => setNewTarget(e.target.value)}
            disabled={busy || entityIds.length === 0}
          >
            {entityIds.map((id) => (
              <option key={id} value={id}>
                {id}
              </option>
            ))}
          </select>
        </label>
        <button className="primary" type="submit" disabled={busy || !defaultEntity}>
          Add relationship
        </button>
      </form>

      {mutate.isError && (
        <p className="error">{(mutate.error as Error).message}</p>
      )}
    </div>
  );
}
