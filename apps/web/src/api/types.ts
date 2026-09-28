export type Health = { status: string };

export type Implementation = {
  id: string;
  slug: string;
  title: string;
  implementation_path: string;
};

export type Conformance = {
  implementation_id: string;
  overall_result: string;
  is_conformant: boolean;
  diagnostic_count: number;
};

export type WorkspaceMember = { user_id: string; role: string };

export type Workspace = {
  id: string;
  name: string;
  members: WorkspaceMember[];
};

export type Job = {
  id: string;
  workspace_id: string;
  kind: string;
  status: string;
  implementation_id: string;
  result_summary: string;
  finished_at: string | null;
};

export type ModelIndexRebuild = {
  index_id: string;
  implementation_id: string;
  revision: string;
  element_count: number;
};

export type ElementHit = {
  element_id: string;
  element_kind: string;
  name: string;
  layer: string;
  implementation_id: string;
};

export type ImplementationBody = {
  content: string;
  content_digest: string;
  path: string;
};

export type WorkspaceDocument = {
  workspace_id: string;
  doc_key: string;
  content: string;
  base_digest: string;
  updated_by: string;
};

export type DocumentMutation =
  | {
      op: "add_logical_entity";
      entity: {
        element_id: string;
        name: string;
        title?: string;
        description?: string;
      };
    }
  | {
      op: "add_logical_attribute";
      owner_element_id: string;
      attribute: {
        element_id: string;
        name: string;
        logical_type: string;
        title?: string;
        description?: string;
        required?: boolean;
      };
    };

export type Publication = {
  id: string;
  workspace_id: string;
  implementation_id: string;
  branch_name: string;
  base_revision: string;
  commit_sha: string;
  review_url: string;
  review_id: string;
  status: string;
};
