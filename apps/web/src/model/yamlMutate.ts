import type { DocumentMutation } from "../api/types";
import { parseDraftYaml, serializeDraftYaml } from "./draft";

export class YamlMutateError extends Error {
  constructor(message: string) {
    super(message);
    this.name = "YamlMutateError";
  }
}

function asRecord(v: unknown): Record<string, unknown> | null {
  return v !== null && typeof v === "object" && !Array.isArray(v)
    ? (v as Record<string, unknown>)
    : null;
}

function ensureSeq(
  data: Record<string, unknown>,
  key: string,
): Record<string, unknown>[] {
  const cur = data[key];
  if (!Array.isArray(cur)) {
    data[key] = [];
  }
  return data[key] as Record<string, unknown>[];
}

function collectIds(data: Record<string, unknown>): Set<string> {
  const ids = new Set<string>();
  const root = data.element_id;
  if (root) ids.add(String(root));
  for (const key of [
    "logical_entities",
    "data_carriers",
    "access_points",
    "data_containers",
    "execution_assets",
    "mappings",
    "relationships",
    "conceptual_entities",
  ]) {
    const items = data[key];
    if (!Array.isArray(items)) continue;
    for (const item of items) {
      const row = asRecord(item);
      if (!row) continue;
      if (row.element_id) ids.add(String(row.element_id));
      for (const nestedKey of ["attributes"]) {
        const nested = row[nestedKey];
        if (!Array.isArray(nested)) continue;
        for (const n of nested) {
          const nr = asRecord(n);
          if (nr?.element_id) ids.add(String(nr.element_id));
        }
      }
    }
  }
  const structures = data.data_structures;
  if (Array.isArray(structures)) {
    for (const item of structures) {
      const row = asRecord(item);
      if (row?.element_id) ids.add(String(row.element_id));
    }
  }
  return ids;
}

function findLogicalEntity(
  data: Record<string, unknown>,
  elementId: string,
): { idx: number; row: Record<string, unknown> } {
  const entities = data.logical_entities;
  if (!Array.isArray(entities)) {
    throw new YamlMutateError("logical_entities missing");
  }
  for (let i = 0; i < entities.length; i++) {
    const row = asRecord(entities[i]);
    if (row && String(row.element_id) === elementId) {
      return { idx: i, row };
    }
  }
  throw new YamlMutateError(`logical entity not found: ${elementId}`);
}

function findLogicalAttribute(
  data: Record<string, unknown>,
  elementId: string,
): {
  owner: Record<string, unknown>;
  idx: number;
  row: Record<string, unknown>;
} {
  const entities = data.logical_entities;
  if (!Array.isArray(entities)) {
    throw new YamlMutateError("logical_entities missing");
  }
  for (const ent of entities) {
    const owner = asRecord(ent);
    if (!owner) continue;
    const attrs = owner.attributes;
    if (!Array.isArray(attrs)) continue;
    for (let i = 0; i < attrs.length; i++) {
      const row = asRecord(attrs[i]);
      if (row && String(row.element_id) === elementId) {
        return { owner, idx: i, row };
      }
    }
  }
  throw new YamlMutateError(`logical attribute not found: ${elementId}`);
}

function findTopLevel(
  data: Record<string, unknown>,
  key: string,
  elementId: string,
  label: string,
): { idx: number; row: Record<string, unknown> } {
  const items = data[key];
  if (!Array.isArray(items)) {
    throw new YamlMutateError(`${key} missing`);
  }
  for (let i = 0; i < items.length; i++) {
    const row = asRecord(items[i]);
    if (row && String(row.element_id) === elementId) {
      return { idx: i, row };
    }
  }
  throw new YamlMutateError(`${label} not found: ${elementId}`);
}

const TECH_COLLECTIONS = [
  "data_carriers",
  "access_points",
  "data_containers",
  "execution_assets",
] as const;

const LEGACY_KIND: Record<string, string> = {
  table: "relational_table",
  view: "relational_view",
  topic: "stream_topic",
  queue: "stream_queue",
  api: "interface",
  endpoint: "operation",
};

const KIND_COLLECTION: Record<string, string> = {
  relational_table: "data_carriers",
  relational_view: "data_carriers",
  file: "data_carriers",
  dataset: "data_carriers",
  stream_topic: "data_carriers",
  stream_queue: "data_carriers",
  in_memory: "data_carriers",
  api_resource: "data_carriers",
  other: "data_carriers",
  interface: "access_points",
  operation: "access_points",
  channel: "access_points",
  database: "data_containers",
  schema: "data_containers",
  bucket: "data_containers",
  broker: "data_containers",
  directory: "data_containers",
  cluster: "data_containers",
  pipeline: "execution_assets",
  job: "execution_assets",
};

function normalizeAssetKind(raw: unknown): string {
  const k = String(raw || "relational_table").trim() || "relational_table";
  return LEGACY_KIND[k] || k;
}

function findTechnicalAsset(
  data: Record<string, unknown>,
  elementId: string,
): { collection: string; idx: number; row: Record<string, unknown> } {
  for (const key of TECH_COLLECTIONS) {
    const items = data[key];
    if (!Array.isArray(items)) continue;
    for (let i = 0; i < items.length; i++) {
      const row = asRecord(items[i]);
      if (row && String(row.element_id) === elementId) {
        return { collection: key, idx: i, row };
      }
    }
  }
  throw new YamlMutateError(`technical asset not found: ${elementId}`);
}

function findDataCarrier(
  data: Record<string, unknown>,
  elementId: string,
): { idx: number; row: Record<string, unknown> } {
  const found = findTechnicalAsset(data, elementId);
  return { idx: found.idx, row: found.row };
}

function findSchemaNode(
  data: Record<string, unknown>,
  nodeRef: string,
): {
  structure: Record<string, unknown>;
  idx: number;
  row: Record<string, unknown>;
} {
  const hash = nodeRef.indexOf("#");
  if (hash < 0) {
    throw new YamlMutateError(
      `schema node ref must be structure_id#local_key, got: ${nodeRef}`,
    );
  }
  const sid = nodeRef.slice(0, hash);
  const localKey = nodeRef.slice(hash + 1);
  const structures = data.data_structures;
  if (!Array.isArray(structures)) {
    throw new YamlMutateError("data_structures missing");
  }
  for (const st of structures) {
    const structure = asRecord(st);
    if (!structure || String(structure.element_id) !== sid) continue;
    const nodes = structure.nodes;
    if (!Array.isArray(nodes)) continue;
    for (let i = 0; i < nodes.length; i++) {
      const row = asRecord(nodes[i]);
      if (row && String(row.local_key) === localKey) {
        return { structure, idx: i, row };
      }
    }
  }
  throw new YamlMutateError(`schema node not found: ${nodeRef}`);
}

function slugLocalKey(text: string): string {
  const s = text.trim().toLowerCase();
  let out = "";
  for (const ch of s) {
    if (/[a-z0-9_.-]/.test(ch)) out += ch;
    else out += "_";
  }
  return out.replace(/^[_.-]+|[_.-]+$/g, "") || "_";
}

function ensureStructureForCarrier(
  data: Record<string, unknown>,
  carrier: Record<string, unknown>,
): Record<string, unknown> {
  const sid = String(carrier.structure_ref || "").trim();
  const structures = ensureSeq(data, "data_structures");
  if (sid) {
    for (const st of structures) {
      const row = asRecord(st);
      if (row && String(row.element_id) === sid) {
        if (!Array.isArray(row.nodes)) row.nodes = [];
        return row;
      }
    }
  }
  const name = String(carrier.name || "structure");
  const eid = String(carrier.element_id || "");
  const parts = eid.split("/");
  const slug = parts.length >= 3 ? parts[1] : "unknown";
  const structureId = `dams:structure/${slug}/${name}`;
  const row: Record<string, unknown> = {
    element_id: structureId,
    name,
    title: carrier.title || name,
    description: `Structure for ${name}`,
    lifecycle_status: carrier.lifecycle_status || "draft",
    schema_format: "relational",
    structure_version: "1.0.0",
    root_local_key: "root",
    nodes: [
      { local_key: "root", node_kind: "object", children: [] as string[] },
    ],
  };
  structures.push(row);
  carrier.structure_ref = structureId;
  return row;
}

function applyPatch(
  row: Record<string, unknown>,
  patch: Record<string, unknown>,
  allowed: Set<string>,
): void {
  for (const [k, v] of Object.entries(patch)) {
    if (!allowed.has(k) || v === undefined) continue;
    row[k] = v;
  }
}

function mutateData(
  data: Record<string, unknown>,
  payload: DocumentMutation,
): void {
  const ids = () => collectIds(data);

  switch (payload.op) {
    case "add_logical_entity": {
      const entity = payload.entity;
      const eid = String(entity.element_id || "").trim();
      const name = String(entity.name || "").trim();
      if (!eid || !name) throw new YamlMutateError("element_id and name are required");
      if (ids().has(eid)) throw new YamlMutateError(`duplicate element_id: ${eid}`);
      const seq = ensureSeq(data, "logical_entities");
      seq.push({
        element_id: eid,
        name,
        title: entity.title || name,
        description:
          entity.description || `Logical entity ${name} (workbench draft).`,
        lifecycle_status: "draft",
        attributes: [],
      });
      break;
    }
    case "add_logical_attribute": {
      const attr = payload.attribute;
      const ownerId = String(payload.owner_element_id || "").trim();
      const eid = String(attr.element_id || "").trim();
      const name = String(attr.name || "").trim();
      const dataTypeRef = String(attr.data_type_ref || "").trim();
      const valueDomainRef = String(attr.value_domain_ref || "").trim();
      if (!ownerId || !eid || !name || !(dataTypeRef || valueDomainRef)) {
        throw new YamlMutateError(
          "owner_element_id, element_id, name, and data_type_ref or value_domain_ref are required",
        );
      }
      if (ids().has(eid)) throw new YamlMutateError(`duplicate element_id: ${eid}`);
      const { row: owner } = findLogicalEntity(data, ownerId);
      if (!Array.isArray(owner.attributes)) owner.attributes = [];
      const row: Record<string, unknown> = {
        element_id: eid,
        name,
        title: attr.title || name,
        description:
          attr.description || `Logical attribute ${name} (workbench draft).`,
        lifecycle_status: "draft",
        owner_entity_ref: ownerId,
        required: Boolean(attr.required),
        multivalued: false,
      };
      if (dataTypeRef) row.data_type_ref = dataTypeRef;
      if (valueDomainRef) row.value_domain_ref = valueDomainRef;
      (owner.attributes as Record<string, unknown>[]).push(row);
      break;
    }
    case "update_logical_entity": {
      const { row } = findLogicalEntity(data, payload.element_id);
      applyPatch(
        row,
        payload.patch as Record<string, unknown>,
        new Set([
          "name",
          "title",
          "description",
          "lifecycle_status",
          "context_ref",
          "solution_data_role",
        ]),
      );
      break;
    }
    case "delete_logical_entity": {
      const { idx } = findLogicalEntity(data, payload.element_id);
      (data.logical_entities as unknown[]).splice(idx, 1);
      break;
    }
    case "update_logical_attribute": {
      const { row } = findLogicalAttribute(data, payload.element_id);
      applyPatch(
        row,
        payload.patch as Record<string, unknown>,
        new Set([
          "name",
          "title",
          "description",
          "data_type_ref",
          "value_domain_ref",
          "required",
          "multivalued",
          "lifecycle_status",
        ]),
      );
      break;
    }
    case "delete_logical_attribute": {
      const { owner, idx } = findLogicalAttribute(data, payload.element_id);
      (owner.attributes as unknown[]).splice(idx, 1);
      break;
    }
    case "add_relationship": {
      const rel = payload.relationship;
      const eid = String(rel.element_id || "").trim();
      const name = String(rel.name || "").trim();
      if (!eid || !name) throw new YamlMutateError("element_id and name are required");
      if (ids().has(eid)) throw new YamlMutateError(`duplicate element_id: ${eid}`);
      ensureSeq(data, "relationships").push({
        element_id: eid,
        name,
        title: rel.title || name,
        description: rel.description,
        lifecycle_status: rel.lifecycle_status || "draft",
        source_entity_ref: rel.source_entity_ref,
        target_entity_ref: rel.target_entity_ref,
      });
      break;
    }
    case "update_relationship": {
      const { row } = findTopLevel(
        data,
        "relationships",
        payload.element_id,
        "relationship",
      );
      applyPatch(
        row,
        payload.patch as Record<string, unknown>,
        new Set([
          "name",
          "title",
          "description",
          "lifecycle_status",
          "source_entity_ref",
          "target_entity_ref",
          "source_role",
          "target_role",
          "source_min_cardinality",
          "source_max_cardinality",
          "target_min_cardinality",
          "target_max_cardinality",
          "identifying",
          "associative",
        ]),
      );
      break;
    }
    case "delete_relationship": {
      const { idx } = findTopLevel(
        data,
        "relationships",
        payload.element_id,
        "relationship",
      );
      (data.relationships as unknown[]).splice(idx, 1);
      break;
    }
    case "add_mapping": {
      const mapping = payload.mapping;
      const eid = String(mapping.element_id || "").trim();
      const name = String(mapping.name || "").trim();
      if (!eid || !name) throw new YamlMutateError("element_id and name are required");
      if (ids().has(eid)) throw new YamlMutateError(`duplicate element_id: ${eid}`);
      ensureSeq(data, "mappings").push({
        element_id: eid,
        name,
        title: mapping.title || name,
        description: mapping.description,
        lifecycle_status: mapping.lifecycle_status || "draft",
        source_refs: mapping.source_refs,
        target_refs: mapping.target_refs,
        mapping_type: mapping.mapping_type,
        mapping_cardinality: mapping.mapping_cardinality,
        ...(mapping.transformation_expression
          ? { transformation_expression: mapping.transformation_expression }
          : {}),
      });
      break;
    }
    case "update_mapping": {
      const { row } = findTopLevel(data, "mappings", payload.element_id, "mapping");
      applyPatch(
        row,
        payload.patch as Record<string, unknown>,
        new Set([
          "name",
          "title",
          "description",
          "lifecycle_status",
          "source_refs",
          "target_refs",
          "mapping_type",
          "mapping_cardinality",
          "transformation_expression",
        ]),
      );
      break;
    }
    case "delete_mapping": {
      const { idx } = findTopLevel(data, "mappings", payload.element_id, "mapping");
      (data.mappings as unknown[]).splice(idx, 1);
      break;
    }
    case "add_physical_object": {
      const obj = payload.physical_object;
      const eid = String(obj.element_id || "").trim();
      const name = String(obj.name || "").trim();
      if (!eid || !name) throw new YamlMutateError("element_id and name are required");
      if (ids().has(eid)) throw new YamlMutateError(`duplicate element_id: ${eid}`);
      const assetKind = normalizeAssetKind(obj.asset_kind || obj.object_kind);
      const collection =
        String(obj.collection || KIND_COLLECTION[assetKind] || "data_carriers");
      const row: Record<string, unknown> = {
        element_id: eid,
        name,
        title: obj.title || name,
        description:
          obj.description || `Technical asset ${name} (workbench draft).`,
        lifecycle_status: obj.lifecycle_status || "draft",
        asset_kind: assetKind,
        ...(obj.logical_entity_ref
          ? { logical_entity_ref: obj.logical_entity_ref }
          : {}),
        ...(obj.qualified_name ? { qualified_name: obj.qualified_name } : {}),
        ...(obj.technology ? { technology: obj.technology } : {}),
        ...(obj.asset_namespace ? { asset_namespace: obj.asset_namespace } : {}),
        ...(obj.structure_ref ? { structure_ref: obj.structure_ref } : {}),
        ...(obj.parent_ref ? { parent_ref: obj.parent_ref } : {}),
      };
      ensureSeq(data, collection).push(row);
      break;
    }
    case "update_physical_object": {
      const { row } = findDataCarrier(data, payload.element_id);
      const patch = { ...(payload.patch as Record<string, unknown>) };
      if (patch.object_kind != null && patch.asset_kind == null) {
        patch.asset_kind = normalizeAssetKind(patch.object_kind);
        delete patch.object_kind;
      } else if (patch.asset_kind != null) {
        patch.asset_kind = normalizeAssetKind(patch.asset_kind);
        delete patch.object_kind;
      }
      applyPatch(
        row,
        patch,
        new Set([
          "name",
          "title",
          "description",
          "lifecycle_status",
          "asset_kind",
          "logical_entity_ref",
          "qualified_name",
          "technology",
          "system_ref",
          "direction",
          "asset_namespace",
          "structure_ref",
          "parent_ref",
        ]),
      );
      break;
    }
    case "delete_physical_object": {
      const found = findTechnicalAsset(data, payload.element_id);
      (data[found.collection] as unknown[]).splice(found.idx, 1);
      break;
    }
    case "add_schema_node": {
      const node = payload.schema_node;
      const ownerId = String(payload.owner_element_id || "").trim();
      const name = String(node.name || node.native_name || "").trim();
      const nativeType = String(node.native_type || "").trim();
      if (!ownerId || !name || !nativeType) {
        throw new YamlMutateError(
          "owner_element_id, name, and native_type are required",
        );
      }
      const { row: carrier } = findDataCarrier(data, ownerId);
      const structure = ensureStructureForCarrier(data, carrier);
      const nodes = structure.nodes as Record<string, unknown>[];
      let localKey = String(node.local_key || slugLocalKey(name)).trim();
      const used = new Set(
        nodes.map((n) => String(n.local_key || "")).filter(Boolean),
      );
      if (used.has(localKey)) {
        let n = 2;
        while (used.has(`${localKey}-${n}`)) n += 1;
        localKey = `${localKey}-${n}`;
      }
      nodes.push({
        local_key: localKey,
        node_kind: "scalar",
        native_name: node.native_name || name,
        native_type: nativeType,
        required: Boolean(node.required),
        ...(node.description ? { description: node.description } : {}),
      });
      const root = nodes.find((n) => String(n.local_key) === "root");
      if (root) {
        if (!Array.isArray(root.children)) root.children = [];
        (root.children as string[]).push(localKey);
      }
      break;
    }
    case "update_schema_node": {
      const { row } = findSchemaNode(data, payload.element_id);
      applyPatch(
        row,
        payload.patch as Record<string, unknown>,
        new Set([
          "native_name",
          "native_type",
          "required",
          "description",
          "nullable",
        ]),
      );
      break;
    }
    case "delete_schema_node": {
      const { structure, idx, row } = findSchemaNode(data, payload.element_id);
      const localKey = String(row.local_key);
      (structure.nodes as unknown[]).splice(idx, 1);
      for (const n of structure.nodes as Record<string, unknown>[]) {
        const children = n.children;
        if (Array.isArray(children)) {
          n.children = children.filter((c) => c !== localKey);
        }
      }
      break;
    }
    default: {
      const _exhaustive: never = payload;
      throw new YamlMutateError(
        `unsupported op: ${(_exhaustive as DocumentMutation).op}`,
      );
    }
  }
}

/** Client-side mirror of server yaml_mutate.apply_mutation for optimistic Monaco updates. */
export function applyMutationOptimistic(
  text: string,
  payload: DocumentMutation,
): string {
  const parsed = parseDraftYaml(text);
  if (parsed.error) {
    throw new YamlMutateError(parsed.error);
  }
  if (!parsed.data) {
    throw new YamlMutateError("root YAML must be a mapping");
  }
  const data = structuredClone(parsed.data);
  mutateData(data, payload);
  return serializeDraftYaml(data);
}
