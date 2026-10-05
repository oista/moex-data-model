import yaml from "js-yaml";
import { useMemo, useState } from "react";
import type { FormsTab } from "./ModelFormsPanel";

export type ExplorerKind =
  | "conceptual"
  | "domain"
  | "logical_entity"
  | "logical_attribute"
  | "relationship"
  | "physical_object"
  | "physical_field"
  | "mapping";

export type ExplorerSelect = {
  elementId: string;
  kind: ExplorerKind;
  tab: FormsTab | null;
};

type TreeNode = {
  id: string;
  label: string;
  kind: ExplorerKind;
  tab: FormsTab | null;
  children?: TreeNode[];
};

type Group = {
  id: string;
  title: string;
  nodes: TreeNode[];
};

function parseTree(content: string): { groups: Group[]; error: string | null } {
  if (!content.trim()) {
    return { groups: [], error: null };
  }
  try {
    const data = yaml.load(content) as Record<string, unknown> | null;
    if (!data || typeof data !== "object") {
      return { groups: [], error: null };
    }

    const groups: Group[] = [];

    const conceptual = Array.isArray(data.conceptual_entities)
      ? data.conceptual_entities
      : [];
    if (conceptual.length) {
      groups.push({
        id: "conceptual",
        title: "Conceptual",
        nodes: conceptual
          .filter((e): e is Record<string, unknown> => !!e && typeof e === "object")
          .filter((e) => e.element_id)
          .map((e) => ({
            id: String(e.element_id),
            label: String(e.name || e.element_id),
            kind: "conceptual" as const,
            tab: null,
          })),
      });
    }

    const contexts = Array.isArray(data.domain_contexts)
      ? data.domain_contexts
      : [];
    if (contexts.length) {
      groups.push({
        id: "domains",
        title: "Domain contexts",
        nodes: contexts
          .filter((e): e is Record<string, unknown> => !!e && typeof e === "object")
          .filter((e) => e.element_id)
          .map((e) => ({
            id: String(e.element_id),
            label: String(e.name || e.element_id),
            kind: "domain" as const,
            tab: null,
          })),
      });
    }

    const logical = Array.isArray(data.logical_entities)
      ? data.logical_entities
      : [];
    if (logical.length) {
      groups.push({
        id: "logical",
        title: "Logical entities",
        nodes: logical
          .filter((e): e is Record<string, unknown> => !!e && typeof e === "object")
          .filter((e) => e.element_id)
          .map((e) => {
            const attrs = Array.isArray(e.attributes) ? e.attributes : [];
            return {
              id: String(e.element_id),
              label: String(e.name || e.element_id),
              kind: "logical_entity" as const,
              tab: "entities" as FormsTab,
              children: attrs
                .filter(
                  (a): a is Record<string, unknown> =>
                    !!a && typeof a === "object",
                )
                .filter((a) => a.element_id)
                .map((a) => ({
                  id: String(a.element_id),
                  label: String(a.name || a.element_id),
                  kind: "logical_attribute" as const,
                  tab: "entities" as FormsTab,
                })),
            };
          }),
      });
    }

    const relationships = Array.isArray(data.relationships)
      ? data.relationships
      : [];
    if (relationships.length) {
      groups.push({
        id: "relationships",
        title: "Relationships",
        nodes: relationships
          .filter((e): e is Record<string, unknown> => !!e && typeof e === "object")
          .filter((e) => e.element_id)
          .map((e) => ({
            id: String(e.element_id),
            label: String(e.name || e.element_id),
            kind: "relationship" as const,
            tab: "relationships" as FormsTab,
          })),
      });
    }

    const carriers = Array.isArray(data.data_carriers) ? data.data_carriers : [];
    const accessPoints = Array.isArray(data.access_points) ? data.access_points : [];
    const containers = Array.isArray(data.data_containers)
      ? data.data_containers
      : [];
    const execution = Array.isArray(data.execution_assets)
      ? data.execution_assets
      : [];
    const technical = [
      ...carriers.map((e) => ({ ...(e as object), _collection: "data_carriers" })),
      ...accessPoints.map((e) => ({
        ...(e as object),
        _collection: "access_points",
      })),
      ...containers.map((e) => ({
        ...(e as object),
        _collection: "data_containers",
      })),
      ...execution.map((e) => ({
        ...(e as object),
        _collection: "execution_assets",
      })),
    ];
    if (technical.length) {
      // Group by subclass, then nest children under parent_ref when present
      const byId = new Map<string, Record<string, unknown>>();
      for (const e of technical) {
        const rec = e as Record<string, unknown>;
        if (rec.element_id) byId.set(String(rec.element_id), rec);
      }
      const roots: Record<string, unknown>[] = [];
      const childrenOf = new Map<string, Record<string, unknown>[]>();
      for (const e of technical) {
        const rec = e as Record<string, unknown>;
        if (!rec.element_id) continue;
        const parent = rec.parent_ref ? String(rec.parent_ref) : "";
        if (parent && byId.has(parent)) {
          const list = childrenOf.get(parent) || [];
          list.push(rec);
          childrenOf.set(parent, list);
        } else {
          roots.push(rec);
        }
      }
      const toNode = (e: Record<string, unknown>): TreeNode => {
        const fields = Array.isArray(e.physical_fields) ? e.physical_fields : [];
        const nested = childrenOf.get(String(e.element_id)) || [];
        return {
          id: String(e.element_id),
          label: `${String(e.name || e.element_id)} (${String(e.asset_kind || e._collection)})`,
          kind: "physical_object" as const,
          tab: "physical" as FormsTab,
          children: [
            ...nested.map(toNode),
            ...fields
              .filter(
                (f): f is Record<string, unknown> =>
                  !!f && typeof f === "object",
              )
              .filter((f) => f.element_id)
              .map((f) => ({
                id: String(f.element_id),
                label: String(f.name || f.element_id),
                kind: "physical_field" as const,
                tab: "physical" as FormsTab,
              })),
          ],
        };
      };
      groups.push({
        id: "technical",
        title: "Technical assets",
        nodes: roots.map(toNode),
      });
    }

    const mappings = Array.isArray(data.mappings) ? data.mappings : [];
    if (mappings.length) {
      groups.push({
        id: "mappings",
        title: "Mappings",
        nodes: mappings
          .filter((e): e is Record<string, unknown> => !!e && typeof e === "object")
          .filter((e) => e.element_id)
          .map((e) => ({
            id: String(e.element_id),
            label: String(e.name || e.element_id),
            kind: "mapping" as const,
            tab: "mappings" as FormsTab,
          })),
      });
    }

    return { groups, error: null };
  } catch (err) {
    return {
      groups: [],
      error: err instanceof Error ? err.message : "Invalid YAML",
    };
  }
}

type Props = {
  content: string;
  selectedId?: string | null;
  onSelect: (sel: ExplorerSelect) => void;
};

function TreeItem({
  node,
  selectedId,
  onSelect,
  depth,
}: {
  node: TreeNode;
  selectedId?: string | null;
  onSelect: (sel: ExplorerSelect) => void;
  depth: number;
}) {
  const [open, setOpen] = useState(depth < 1);
  const hasChildren = !!node.children?.length;
  const active = selectedId === node.id;

  return (
    <li>
      <div className="explorer-row" style={{ paddingLeft: `${depth * 0.75}rem` }}>
        {hasChildren ? (
          <button
            type="button"
            className="explorer-toggle"
            aria-expanded={open}
            onClick={() => setOpen((v) => !v)}
          >
            {open ? "▾" : "▸"}
          </button>
        ) : (
          <span className="explorer-toggle spacer" />
        )}
        <button
          type="button"
          className={active ? "explorer-node active" : "explorer-node"}
          data-testid={`explorer-node-${node.id}`}
          onClick={() =>
            onSelect({
              elementId: node.id,
              kind: node.kind,
              tab: node.tab,
            })
          }
        >
          {node.label}
        </button>
      </div>
      {hasChildren && open && (
        <ul className="explorer-children">
          {node.children!.map((child) => (
            <TreeItem
              key={child.id}
              node={child}
              selectedId={selectedId}
              onSelect={onSelect}
              depth={depth + 1}
            />
          ))}
        </ul>
      )}
    </li>
  );
}

export function ModelExplorer({ content, selectedId, onSelect }: Props) {
  const { groups, error } = useMemo(() => parseTree(content), [content]);

  return (
    <div className="model-explorer" data-testid="model-explorer">
      <h2>Model explorer</h2>
      {error && (
        <p className="error" data-testid="explorer-parse-error">
          YAML parse error: {error}
        </p>
      )}
      {!error && groups.length === 0 && (
        <p className="lede">No model elements</p>
      )}
      {groups.map((group) => (
        <div key={group.id} className="explorer-group">
          <h3>{group.title}</h3>
          <ul className="explorer-tree">
            {group.nodes.map((node) => (
              <TreeItem
                key={node.id}
                node={node}
                selectedId={selectedId}
                onSelect={onSelect}
                depth={0}
              />
            ))}
          </ul>
        </div>
      ))}
    </div>
  );
}
