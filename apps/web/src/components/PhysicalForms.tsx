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
  asset_kind: string;
  collection: string;
  fields: FieldSummary[];
};

const ASSET_KIND_OPTIONS: Record<string, string[]> = {
  data_carriers: [
    "relational_table",
    "relational_view",
    "stream_topic",
    "stream_queue",
    "file",
    "dataset",
    "message_type",
    "in_memory",
    "api_resource",
    "other",
  ],
  access_points: ["interface", "operation", "channel"],
  data_containers: ["database", "schema", "bucket", "broker", "directory", "cluster"],
  execution_assets: ["pipeline", "job"],
};

const LEGACY_KIND: Record<string, string> = {
  table: "relational_table",
  view: "relational_view",
  topic: "stream_topic",
  queue: "stream_queue",
  message: "message_type",
  payload: "message_type",
  api: "interface",
  endpoint: "operation",
};

function normalizeKind(raw: unknown): string {
  const k = String(raw || "relational_table").trim() || "relational_table";
  return LEGACY_KIND[k] || k;
}

type TechItem = {
  element_id?: string;
  name?: string;
  title?: string;
  description?: string;
  asset_kind?: string;
  object_kind?: string;
  physical_fields?: Array<{
    element_id?: string;
    name?: string;
    native_type?: string;
    required?: boolean;
  }>;
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
      data_carriers?: TechItem[];
      access_points?: TechItem[];
      data_containers?: TechItem[];
      execution_assets?: TechItem[];
    } | null;
    const objects: ObjectSummary[] = [];
    for (const [collection, items] of [
      ["data_carriers", data?.data_carriers],
      ["access_points", data?.access_points],
      ["data_containers", data?.data_containers],
      ["execution_assets", data?.execution_assets],
    ] as const) {
      for (const o of items ?? []) {
        if (!o?.element_id) continue;
        objects.push({
          element_id: String(o.element_id),
          name: String(o.name || ""),
          title: String(o.title || ""),
          description: String(o.description || ""),
          asset_kind: normalizeKind(o.asset_kind || o.object_kind),
          collection,
          fields: (Array.isArray(o.physical_fields) ? o.physical_fields : [])
            .filter((f) => f?.element_id)
            .map((f) => ({
              element_id: String(f.element_id),
              name: String(f.name || ""),
              native_type: String(f.native_type || "string"),
              required: Boolean(f.required),
            })),
        });
      }
    }
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
  const [editKind, setEditKind] = useState("relational_table");
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
      setEditKind("relational_table");
      setEditFieldId(null);
      return;
    }
    setEditName(selected.name);
    setEditTitle(selected.title);
    setEditDescription(selected.description);
    setEditKind(selected.asset_kind);
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
    selected?.asset_kind,
    selected?.fields,
    pendingFieldFocus,
  ]); // eslint-disable-line react-hooks/exhaustive-deps

  const [objId, setObjId] = useState(`dams:physical/${idNamespace}/new-object`);
  const [objName, setObjName] = useState("new_object");
  const [objTitle, setObjTitle] = useState("");
  const [objCollection, setObjCollection] = useState("data_carriers");
  const [objKind, setObjKind] = useState("relational_table");
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
        asset_kind: objKind.trim() || "relational_table",
        collection: objCollection,
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
        asset_kind: editKind.trim() || "relational_table",
      },
    });
  }

  function onDeleteObject() {
    if (!selected) return;
    if (!window.confirm(`Delete technical asset ${selected.element_id}?`)) {
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
      <h2>Technical assets</h2>
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
              <code>{obj.element_id}</code> · {obj.name} · {obj.asset_kind} ·{" "}
              {obj.fields.length} fields
            </button>
          </li>
        ))}
        {!parseError && objects.length === 0 && (
          <li className="lede">No technical assets parsed</li>
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
            asset_kind
            <select
              value={editKind}
              onChange={(e) => setEditKind(e.target.value)}
              disabled={busy}
            >
              {(ASSET_KIND_OPTIONS[selected.collection] || ASSET_KIND_OPTIONS.data_carriers).map(
                (k) => (
                  <option key={k} value={k}>
                    {k}
                  </option>
                ),
              )}
            </select>
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
        <h3>Add TechnicalAsset</h3>
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
          subclass
          <select
            value={objCollection}
            onChange={(e) => {
              const next = e.target.value;
              setObjCollection(next);
              const kinds = ASSET_KIND_OPTIONS[next] || ASSET_KIND_OPTIONS.data_carriers;
              setObjKind(kinds[0]);
            }}
            disabled={busy}
          >
            <option value="data_carriers">DataCarrier</option>
            <option value="access_points">AccessPoint</option>
            <option value="data_containers">DataContainer</option>
            <option value="execution_assets">ExecutionAsset</option>
          </select>
        </label>
        <label>
          asset_kind
          <select
            value={objKind}
            onChange={(e) => setObjKind(e.target.value)}
            disabled={busy}
          >
            {(ASSET_KIND_OPTIONS[objCollection] || ASSET_KIND_OPTIONS.data_carriers).map(
              (k) => (
                <option key={k} value={k}>
                  {k}
                </option>
              ),
            )}
          </select>
        </label>
        <button className="primary" type="submit" disabled={busy}>
          Add asset
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
