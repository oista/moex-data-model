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
