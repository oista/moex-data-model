import { useMutation } from "@tanstack/react-query";
import yaml from "js-yaml";
import { useEffect, useMemo, useState, type FormEvent } from "react";
import { api } from "../api/client";
import type { DocumentMutation, WorkspaceDocument } from "../api/types";

type FieldSummary = {
  element_id: string;
  name: string;
  native_type: string;
  required: boolean;
};

type ObjectSummary = {
  element_id: string;
  name: string;
  title: string;
  description: string;
  object_kind: string;
  fields: FieldSummary[];
};

function parsePhysical(content: string): {
  objects: ObjectSummary[];
  error: string | null;
} {
  if (!content.trim()) {
    return { objects: [], error: null };
  }
  try {
    const data = yaml.load(content) as {
      physical_objects?: Array<{
        element_id?: string;
        name?: string;
        title?: string;
        description?: string;
        object_kind?: string;
        physical_fields?: Array<{
          element_id?: string;
          name?: string;
          native_type?: string;
          required?: boolean;
        }>;
      }>;
    } | null;
    const objects = (data?.physical_objects ?? [])
      .filter((o) => o?.element_id)
      .map((o) => ({
        element_id: String(o.element_id),
        name: String(o.name || ""),
        title: String(o.title || ""),
        description: String(o.description || ""),
        object_kind: String(o.object_kind || "table"),
        fields: (Array.isArray(o.physical_fields) ? o.physical_fields : [])
          .filter((f) => f?.element_id)
          .map((f) => ({
            element_id: String(f.element_id),
            name: String(f.name || ""),
            native_type: String(f.native_type || "string"),
            required: Boolean(f.required),
          })),
      }));
    return { objects, error: null };
  } catch (err) {
    return {
      objects: [],
      error: err instanceof Error ? err.message : "Invalid YAML",
    };
  }
}

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

export function PhysicalForms({
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
  const { objects, error: parseError } = useMemo(
    () => parsePhysical(content),
    [content],
  );
  const [selectedId, setSelectedId] = useState("");
  const selected =
    objects.find((o) => o.element_id === selectedId) ?? objects[0] ?? null;

  const [editName, setEditName] = useState("");
  const [editTitle, setEditTitle] = useState("");
  const [editDescription, setEditDescription] = useState("");
  const [editKind, setEditKind] = useState("table");
  const [editFieldId, setEditFieldId] = useState<string | null>(null);
  const [editFieldName, setEditFieldName] = useState("");
  const [editFieldType, setEditFieldType] = useState("string");
  const [editFieldRequired, setEditFieldRequired] = useState(false);
  const [pendingFieldFocus, setPendingFieldFocus] = useState<string | null>(
    null,
  );

  useEffect(() => {
    if (!focusElementId) return;
    const asObj = objects.find((o) => o.element_id === focusElementId);
    if (asObj) {
      setSelectedId(asObj.element_id);
      setPendingFieldFocus(null);
      return;
    }
    for (const obj of objects) {
      const field = obj.fields.find((f) => f.element_id === focusElementId);
      if (field) {
        setSelectedId(obj.element_id);
        setPendingFieldFocus(field.element_id);
        return;
      }
    }
  }, [focusElementId, objects]);

  useEffect(() => {
    if (selected && selected.element_id !== selectedId) {
      setSelectedId(selected.element_id);
    }
  }, [selected, selectedId]);

  useEffect(() => {
    if (!selected) {
      setEditName("");
      setEditTitle("");
      setEditDescription("");
      setEditKind("table");
      setEditFieldId(null);
      return;
    }
    setEditName(selected.name);
    setEditTitle(selected.title);
    setEditDescription(selected.description);
    setEditKind(selected.object_kind);
    if (pendingFieldFocus) {
      const field = selected.fields.find(
        (f) => f.element_id === pendingFieldFocus,
      );
      if (field) {
        setEditFieldId(field.element_id);
        setEditFieldName(field.name);
        setEditFieldType(field.native_type);
        setEditFieldRequired(field.required);
        setPendingFieldFocus(null);
        return;
      }
    }
    if (editFieldId) {
      const field = selected.fields.find((f) => f.element_id === editFieldId);
      if (field) {
        setEditFieldName(field.name);
        setEditFieldType(field.native_type);
        setEditFieldRequired(field.required);
        return;
      }
      setEditFieldId(null);
    }
  }, [
    selected?.element_id,
    selected?.name,
    selected?.title,
    selected?.description,
    selected?.object_kind,
    selected?.fields,
    pendingFieldFocus,
  ]); // eslint-disable-line react-hooks/exhaustive-deps

  const [objId, setObjId] = useState(`dams:physical/${idNamespace}/new-object`);
  const [objName, setObjName] = useState("new_object");
  const [objTitle, setObjTitle] = useState("");
  const [objKind, setObjKind] = useState("table");
  const [ownerId, setOwnerId] = useState("");
  const [fieldId, setFieldId] = useState("");
  const [fieldName, setFieldName] = useState("");
  const [fieldType, setFieldType] = useState("string");

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

  function onAddObject(e: FormEvent) {
    e.preventDefault();
    mutate.mutate({
      op: "add_physical_object",
      physical_object: {
        element_id: objId.trim(),
        name: objName.trim(),
        title: objTitle.trim() || undefined,
        object_kind: objKind.trim() || "table",
      },
    });
  }

  function onAddField(e: FormEvent) {
    e.preventDefault();
    const owner = ownerId || selected?.element_id || objects[0]?.element_id;
    if (!owner) return;
    mutate.mutate({
      op: "add_physical_field",
      owner_element_id: owner,
      physical_field: {
        element_id: fieldId.trim(),
        name: fieldName.trim(),
        native_type: fieldType.trim() || "string",
      },
    });
  }

  function onSaveObject(e: FormEvent) {
    e.preventDefault();
    if (!selected) return;
    mutate.mutate({
      op: "update_physical_object",
      element_id: selected.element_id,
      patch: {
        name: editName.trim(),
        title: editTitle.trim(),
        description: editDescription,
        object_kind: editKind.trim() || "table",
      },
    });
  }

  function onDeleteObject() {
    if (!selected) return;
    if (!window.confirm(`Delete physical object ${selected.element_id}?`)) {
      return;
    }
    mutate.mutate({
      op: "delete_physical_object",
      element_id: selected.element_id,
    });
    setSelectedId("");
  }

  function onSaveField(e: FormEvent) {
    e.preventDefault();
    if (!editFieldId) return;
    mutate.mutate({
      op: "update_physical_field",
      element_id: editFieldId,
      patch: {
        name: editFieldName.trim(),
        native_type: editFieldType.trim() || "string",
        required: editFieldRequired,
      },
    });
  }

  function onDeleteField(elementId: string) {
    if (!window.confirm(`Delete physical field ${elementId}?`)) return;
    mutate.mutate({
      op: "delete_physical_field",
      element_id: elementId,
    });
    if (editFieldId === elementId) setEditFieldId(null);
  }

  function selectField(field: FieldSummary) {
    setEditFieldId(field.element_id);
    setEditFieldName(field.name);
    setEditFieldType(field.native_type);
    setEditFieldRequired(field.required);
  }

  return (
    <div className="forms-panel" data-testid="physical-forms">
      <h2>Physical objects</h2>
      {parseError && (
        <p className="error" data-testid="yaml-parse-error">
          YAML parse error: {parseError}
        </p>
      )}
      <ul className="entity-list" data-testid="physical-object-list">
        {objects.map((obj) => (
          <li key={obj.element_id}>
            <button
              type="button"
              className={
                selected?.element_id === obj.element_id
                  ? "entity-select active"
                  : "entity-select"
              }
              onClick={() => setSelectedId(obj.element_id)}
              disabled={busy}
            >
              <code>{obj.element_id}</code> · {obj.name} · {obj.object_kind} ·{" "}
              {obj.fields.length} fields
            </button>
          </li>
        ))}
        {!parseError && objects.length === 0 && (
          <li className="lede">No physical objects parsed</li>
        )}
      </ul>

      {selected && (
        <form
          className="form-block"
          onSubmit={onSaveObject}
          data-testid="edit-physical-object-form"
        >
          <h3>Edit physical object</h3>
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
            object_kind
            <input
              type="text"
              value={editKind}
              onChange={(e) => setEditKind(e.target.value)}
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
              Save object
            </button>
            <button
              type="button"
              onClick={onDeleteObject}
              disabled={busy}
              data-testid="delete-physical-object"
            >
              Delete object
            </button>
          </div>
        </form>
      )}

      {selected && (
        <div className="form-block" data-testid="physical-field-panel">
          <h3>Physical fields</h3>
          <ul className="entity-list">
            {selected.fields.map((field) => (
              <li key={field.element_id}>
                <button
                  type="button"
                  className={
                    editFieldId === field.element_id
                      ? "entity-select active"
                      : "entity-select"
                  }
                  onClick={() => selectField(field)}
                  disabled={busy}
                >
                  <code>{field.element_id}</code> · {field.name}
                </button>
                <button
                  type="button"
                  onClick={() => onDeleteField(field.element_id)}
                  disabled={busy}
                >
                  Delete
                </button>
              </li>
            ))}
            {selected.fields.length === 0 && (
              <li className="lede">No fields</li>
            )}
          </ul>
          {editFieldId && (
            <form onSubmit={onSaveField} data-testid="edit-physical-field-form">
              <label>
                name
                <input
                  type="text"
                  value={editFieldName}
                  onChange={(e) => setEditFieldName(e.target.value)}
                  required
                  disabled={busy}
                />
              </label>
              <label>
                native_type
                <input
                  type="text"
                  value={editFieldType}
                  onChange={(e) => setEditFieldType(e.target.value)}
                  required
                  disabled={busy}
                />
              </label>
              <label className="row">
                <input
                  type="checkbox"
                  checked={editFieldRequired}
                  onChange={(e) => setEditFieldRequired(e.target.checked)}
                  disabled={busy}
                />
                required
              </label>
              <button className="primary" type="submit" disabled={busy}>
                Save field
              </button>
            </form>
          )}
        </div>
      )}

      <form className="form-block" onSubmit={onAddObject}>
        <h3>Add PhysicalObject</h3>
        <label>
          element_id
          <input
            type="text"
            value={objId}
            onChange={(e) => setObjId(e.target.value)}
            required
            disabled={busy}
          />
        </label>
        <label>
          name
          <input
            type="text"
            value={objName}
            onChange={(e) => setObjName(e.target.value)}
            required
            disabled={busy}
          />
        </label>
        <label>
          title
          <input
            type="text"
            value={objTitle}
            onChange={(e) => setObjTitle(e.target.value)}
            disabled={busy}
          />
        </label>
        <label>
          object_kind
          <input
            type="text"
            value={objKind}
            onChange={(e) => setObjKind(e.target.value)}
            disabled={busy}
          />
        </label>
        <button className="primary" type="submit" disabled={busy}>
          Add object
        </button>
      </form>

      <form className="form-block" onSubmit={onAddField}>
        <h3>Add PhysicalField</h3>
        <label>
          owner
          <select
            value={
              ownerId || selected?.element_id || objects[0]?.element_id || ""
            }
            onChange={(e) => setOwnerId(e.target.value)}
            required
            disabled={busy}
          >
            {objects.map((obj) => (
              <option key={obj.element_id} value={obj.element_id}>
                {obj.element_id}
              </option>
            ))}
          </select>
        </label>
        <label>
          element_id
          <input
            type="text"
            value={fieldId}
            onChange={(e) => setFieldId(e.target.value)}
            required
            disabled={busy}
          />
        </label>
        <label>
          name
          <input
            type="text"
            value={fieldName}
            onChange={(e) => setFieldName(e.target.value)}
            required
            disabled={busy}
          />
        </label>
        <label>
          native_type
          <input
            type="text"
            value={fieldType}
            onChange={(e) => setFieldType(e.target.value)}
            required
            disabled={busy}
          />
        </label>
        <button className="primary" type="submit" disabled={busy}>
          Add field
        </button>
      </form>

      {mutate.isError && (
        <p className="error">{(mutate.error as Error).message}</p>
      )}
    </div>
  );
}
