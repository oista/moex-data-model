import { useMutation } from "@tanstack/react-query";
import yaml from "js-yaml";
import { useEffect, useMemo, useState, type FormEvent } from "react";
import { api } from "../api/client";
import type { DocumentMutation, WorkspaceDocument } from "../api/types";

type AttrSummary = {
  element_id: string;
  name: string;
  title: string;
  logical_type: string;
  required: boolean;
};

type EntitySummary = {
  element_id: string;
  name: string;
  title: string;
  description: string;
  attributes: AttrSummary[];
};

type ParseResult = {
  entities: EntitySummary[];
  error: string | null;
};

function parseEntities(content: string): ParseResult {
  if (!content.trim()) {
    return { entities: [], error: null };
  }
  try {
    const data = yaml.load(content) as {
      logical_entities?: Array<{
        element_id?: string;
        name?: string;
        title?: string;
        description?: string;
        attributes?: Array<{
          element_id?: string;
          name?: string;
          title?: string;
          logical_type?: string;
          required?: boolean;
        }>;
      }>;
    } | null;
    const list = data?.logical_entities ?? [];
    const entities = list
      .filter((e) => e?.element_id)
      .map((e) => ({
        element_id: String(e.element_id),
        name: String(e.name || ""),
        title: String(e.title || ""),
        description: String(e.description || ""),
        attributes: (Array.isArray(e.attributes) ? e.attributes : [])
          .filter((a) => a?.element_id)
          .map((a) => ({
            element_id: String(a.element_id),
            name: String(a.name || ""),
            title: String(a.title || ""),
            logical_type: String(a.logical_type || "string"),
            required: Boolean(a.required),
          })),
      }));
    return { entities, error: null };
  } catch (err) {
    return {
      entities: [],
      error: err instanceof Error ? err.message : "Invalid YAML",
    };
  }
}

type Props = {
  workspaceId: string;
  content: string;
  onDocument: (doc: WorkspaceDocument) => void;
  onBeforeMutate?: () => Promise<void>;
  disabled?: boolean;
};

export function EntityForms({
  workspaceId,
  content,
  onDocument,
  onBeforeMutate,
  disabled = false,
}: Props) {
  const { entities, error: parseError } = useMemo(
    () => parseEntities(content),
    [content],
  );
  const [selectedId, setSelectedId] = useState<string>("");
  const selected =
    entities.find((e) => e.element_id === selectedId) ?? entities[0] ?? null;

  useEffect(() => {
    if (selected && selected.element_id !== selectedId) {
      setSelectedId(selected.element_id);
    }
  }, [selected, selectedId]);

  const [editName, setEditName] = useState("");
  const [editTitle, setEditTitle] = useState("");
  const [editDescription, setEditDescription] = useState("");
  const [editAttrId, setEditAttrId] = useState<string | null>(null);
  const [editAttrName, setEditAttrName] = useState("");
  const [editAttrType, setEditAttrType] = useState("string");
  const [editAttrRequired, setEditAttrRequired] = useState(false);

  useEffect(() => {
    if (!selected) {
      setEditName("");
      setEditTitle("");
      setEditDescription("");
      setEditAttrId(null);
      return;
    }
    setEditName(selected.name);
    setEditTitle(selected.title);
    setEditDescription(selected.description);
    setEditAttrId(null);
  }, [selected?.element_id]); // eslint-disable-line react-hooks/exhaustive-deps

  const [entityId, setEntityId] = useState("dams:logical/trading/NewEntity");
  const [entityName, setEntityName] = useState("NewEntity");
  const [entityTitle, setEntityTitle] = useState("");
  const [ownerId, setOwnerId] = useState("");
  const [attrId, setAttrId] = useState("");
  const [attrName, setAttrName] = useState("");
  const [attrType, setAttrType] = useState("string");

  const mutate = useMutation({
    mutationFn: async (body: DocumentMutation) => {
      if (onBeforeMutate) {
        await onBeforeMutate();
      }
      return api.mutateDocument(workspaceId, body);
    },
    onSuccess: onDocument,
  });

  const busy = disabled || mutate.isPending;

  function onAddEntity(e: FormEvent) {
    e.preventDefault();
    mutate.mutate({
      op: "add_logical_entity",
      entity: {
        element_id: entityId.trim(),
        name: entityName.trim(),
        title: entityTitle.trim() || undefined,
      },
    });
  }

  function onAddAttribute(e: FormEvent) {
    e.preventDefault();
    const owner = ownerId || selected?.element_id || entities[0]?.element_id;
    if (!owner) return;
    mutate.mutate({
      op: "add_logical_attribute",
      owner_element_id: owner,
      attribute: {
        element_id: attrId.trim(),
        name: attrName.trim(),
        logical_type: attrType.trim() || "string",
      },
    });
  }

  function onSaveEntity(e: FormEvent) {
    e.preventDefault();
    if (!selected) return;
    mutate.mutate({
      op: "update_logical_entity",
      element_id: selected.element_id,
      patch: {
        name: editName.trim(),
        title: editTitle.trim(),
        description: editDescription,
      },
    });
  }

  function onDeleteEntity() {
    if (!selected) return;
    if (!window.confirm(`Delete entity ${selected.element_id}?`)) return;
    mutate.mutate({
      op: "delete_logical_entity",
      element_id: selected.element_id,
    });
    setSelectedId("");
  }

  function onSaveAttribute(e: FormEvent) {
    e.preventDefault();
    if (!editAttrId) return;
    mutate.mutate({
      op: "update_logical_attribute",
      element_id: editAttrId,
      patch: {
        name: editAttrName.trim(),
        logical_type: editAttrType.trim() || "string",
        required: editAttrRequired,
      },
    });
  }

  function onDeleteAttribute(elementId: string) {
    if (!window.confirm(`Delete attribute ${elementId}?`)) return;
    mutate.mutate({
      op: "delete_logical_attribute",
      element_id: elementId,
    });
    if (editAttrId === elementId) setEditAttrId(null);
  }

  function selectAttr(attr: AttrSummary) {
    setEditAttrId(attr.element_id);
    setEditAttrName(attr.name);
    setEditAttrType(attr.logical_type);
    setEditAttrRequired(attr.required);
  }

  return (
    <div className="forms-panel">
      <h2>Logical entities</h2>
      {parseError && (
        <p className="error" data-testid="yaml-parse-error">
          YAML parse error: {parseError}
        </p>
      )}
      <ul className="entity-list" data-testid="entity-list">
        {entities.map((ent) => (
          <li key={ent.element_id}>
            <button
              type="button"
              className={
                selected?.element_id === ent.element_id
                  ? "entity-select active"
                  : "entity-select"
              }
              onClick={() => setSelectedId(ent.element_id)}
              disabled={busy}
            >
              <code>{ent.element_id}</code> · {ent.name} ·{" "}
              {ent.attributes.length} attrs
            </button>
          </li>
        ))}
        {!parseError && entities.length === 0 && (
          <li className="lede">No entities parsed</li>
        )}
      </ul>

      {selected && (
        <form
          className="form-block"
          onSubmit={onSaveEntity}
          data-testid="edit-entity-form"
        >
          <h3>Edit entity</h3>
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
              rows={3}
            />
          </label>
          <div className="row">
            <button className="primary" type="submit" disabled={busy}>
              Save entity
            </button>
            <button
              type="button"
              onClick={onDeleteEntity}
              disabled={busy}
              data-testid="delete-entity"
            >
              Delete entity
            </button>
          </div>
        </form>
      )}

      {selected && (
        <div className="form-block" data-testid="attribute-panel">
          <h3>Attributes</h3>
          <ul className="entity-list">
            {selected.attributes.map((attr) => (
              <li key={attr.element_id}>
                <button
                  type="button"
                  className={
                    editAttrId === attr.element_id
                      ? "entity-select active"
                      : "entity-select"
                  }
                  onClick={() => selectAttr(attr)}
                  disabled={busy}
                >
                  <code>{attr.element_id}</code> · {attr.name}
                </button>
                <button
                  type="button"
                  onClick={() => onDeleteAttribute(attr.element_id)}
                  disabled={busy}
                  data-testid={`delete-attr-${attr.element_id}`}
                >
                  Delete
                </button>
              </li>
            ))}
            {selected.attributes.length === 0 && (
              <li className="lede">No attributes</li>
            )}
          </ul>
          {editAttrId && (
            <form onSubmit={onSaveAttribute} data-testid="edit-attr-form">
              <label>
                name
                <input
                  type="text"
                  value={editAttrName}
                  onChange={(e) => setEditAttrName(e.target.value)}
                  required
                  disabled={busy}
                />
              </label>
              <label>
                logical_type
                <input
                  type="text"
                  value={editAttrType}
                  onChange={(e) => setEditAttrType(e.target.value)}
                  required
                  disabled={busy}
                />
              </label>
              <label className="row">
                <input
                  type="checkbox"
                  checked={editAttrRequired}
                  onChange={(e) => setEditAttrRequired(e.target.checked)}
                  disabled={busy}
                />
                required
              </label>
              <button className="primary" type="submit" disabled={busy}>
                Save attribute
              </button>
            </form>
          )}
        </div>
      )}

      <form className="form-block" onSubmit={onAddEntity}>
        <h3>Add LogicalEntity</h3>
        <label>
          element_id
          <input
            type="text"
            value={entityId}
            onChange={(e) => setEntityId(e.target.value)}
            required
            disabled={busy}
          />
        </label>
        <label>
          name
          <input
            type="text"
            value={entityName}
            onChange={(e) => setEntityName(e.target.value)}
            required
            disabled={busy}
          />
        </label>
        <label>
          title
          <input
            type="text"
            value={entityTitle}
            onChange={(e) => setEntityTitle(e.target.value)}
            disabled={busy}
          />
        </label>
        <button className="primary" type="submit" disabled={busy}>
          Add entity
        </button>
      </form>

      <form className="form-block" onSubmit={onAddAttribute}>
        <h3>Add LogicalAttribute</h3>
        <label>
          owner
          <select
            value={ownerId || selected?.element_id || entities[0]?.element_id || ""}
            onChange={(e) => setOwnerId(e.target.value)}
            required
            disabled={busy}
          >
            {entities.map((ent) => (
              <option key={ent.element_id} value={ent.element_id}>
                {ent.element_id}
              </option>
            ))}
          </select>
        </label>
        <label>
          element_id
          <input
            type="text"
            value={attrId}
            onChange={(e) => setAttrId(e.target.value)}
            required
            disabled={busy}
          />
        </label>
        <label>
          name
          <input
            type="text"
            value={attrName}
            onChange={(e) => setAttrName(e.target.value)}
            required
            disabled={busy}
          />
        </label>
        <label>
          logical_type
          <input
            type="text"
            value={attrType}
            onChange={(e) => setAttrType(e.target.value)}
            required
            disabled={busy}
          />
        </label>
        <button className="primary" type="submit" disabled={busy}>
          Add attribute
        </button>
      </form>

      {mutate.isError && (
        <p className="error">{(mutate.error as Error).message}</p>
      )}
    </div>
  );
}
