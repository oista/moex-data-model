import { useMutation } from "@tanstack/react-query";
import yaml from "js-yaml";
import { useMemo, useState, type FormEvent } from "react";
import { api } from "../api/client";
import type { WorkspaceDocument } from "../api/types";

type EntitySummary = {
  element_id: string;
  name: string;
  attribute_count: number;
};

function parseEntities(content: string): EntitySummary[] {
  try {
    const data = yaml.load(content) as {
      logical_entities?: Array<{
        element_id?: string;
        name?: string;
        attributes?: unknown[];
      }>;
    } | null;
    const list = data?.logical_entities ?? [];
    return list
      .filter((e) => e?.element_id)
      .map((e) => ({
        element_id: String(e.element_id),
        name: String(e.name || ""),
        attribute_count: Array.isArray(e.attributes) ? e.attributes.length : 0,
      }));
  } catch {
    return [];
  }
}

type Props = {
  workspaceId: string;
  content: string;
  onDocument: (doc: WorkspaceDocument) => void;
};

export function EntityForms({ workspaceId, content, onDocument }: Props) {
  const entities = useMemo(() => parseEntities(content), [content]);
  const [entityId, setEntityId] = useState("dams:logical/trading/NewEntity");
  const [entityName, setEntityName] = useState("NewEntity");
  const [entityTitle, setEntityTitle] = useState("");
  const [ownerId, setOwnerId] = useState("");
  const [attrId, setAttrId] = useState("");
  const [attrName, setAttrName] = useState("");
  const [attrType, setAttrType] = useState("string");

  const mutate = useMutation({
    mutationFn: api.mutateDocument.bind(null, workspaceId),
    onSuccess: onDocument,
  });

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
    const owner = ownerId || entities[0]?.element_id;
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

  return (
    <div className="forms-panel">
      <h2>Logical entities</h2>
      <ul className="entity-list" data-testid="entity-list">
        {entities.map((ent) => (
          <li key={ent.element_id}>
            <code>{ent.element_id}</code> · {ent.name} · {ent.attribute_count}{" "}
            attrs
          </li>
        ))}
        {entities.length === 0 && <li className="lede">No entities parsed</li>}
      </ul>

      <form className="form-block" onSubmit={onAddEntity}>
        <h3>Add LogicalEntity</h3>
        <label>
          element_id
          <input
            type="text"
            value={entityId}
            onChange={(e) => setEntityId(e.target.value)}
            required
          />
        </label>
        <label>
          name
          <input
            type="text"
            value={entityName}
            onChange={(e) => setEntityName(e.target.value)}
            required
          />
        </label>
        <label>
          title
          <input
            type="text"
            value={entityTitle}
            onChange={(e) => setEntityTitle(e.target.value)}
          />
        </label>
        <button className="primary" type="submit" disabled={mutate.isPending}>
          Add entity
        </button>
      </form>

      <form className="form-block" onSubmit={onAddAttribute}>
        <h3>Add LogicalAttribute</h3>
        <label>
          owner
          <select
            value={ownerId || entities[0]?.element_id || ""}
            onChange={(e) => setOwnerId(e.target.value)}
            required
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
          />
        </label>
        <label>
          name
          <input
            type="text"
            value={attrName}
            onChange={(e) => setAttrName(e.target.value)}
            required
          />
        </label>
        <label>
          logical_type
          <input
            type="text"
            value={attrType}
            onChange={(e) => setAttrType(e.target.value)}
            required
          />
        </label>
        <button className="primary" type="submit" disabled={mutate.isPending}>
          Add attribute
        </button>
      </form>

      {mutate.isError && (
        <p className="error">{(mutate.error as Error).message}</p>
      )}
    </div>
  );
}
