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
    }
  | {
      op: "update_logical_entity";
      element_id: string;
      patch: {
        name?: string;
        title?: string;
        description?: string;
        lifecycle_status?: string;
        context_ref?: string;
        solution_data_role?: string;
      };
    }
  | {
      op: "delete_logical_entity";
      element_id: string;
    }
  | {
      op: "update_logical_attribute";
      element_id: string;
      patch: {
        name?: string;
        title?: string;
        description?: string;
        logical_type?: string;
        required?: boolean;
        multivalued?: boolean;
        lifecycle_status?: string;
      };
    }
  | {
      op: "delete_logical_attribute";
      element_id: string;
    }
  | {
      op: "add_relationship";
      relationship: {
        element_id: string;
        name: string;
        description: string;
        lifecycle_status?: string;
        source_entity_ref: string;
        target_entity_ref: string;
        title?: string;
      };
    }
  | {
      op: "update_relationship";
      element_id: string;
      patch: {
        name?: string;
        title?: string;
        description?: string;
        lifecycle_status?: string;
        source_entity_ref?: string;
        target_entity_ref?: string;
        source_role?: string;
        target_role?: string;
        source_min_cardinality?: number;
        source_max_cardinality?: number;
        target_min_cardinality?: number;
        target_max_cardinality?: number;
        identifying?: boolean;
        associative?: boolean;
      };
    }
  | {
      op: "delete_relationship";
      element_id: string;
    }
  | {
      op: "add_mapping";
      mapping: {
        element_id: string;
        name: string;
        description: string;
        lifecycle_status?: string;
        source_refs: string[];
        target_refs: string[];
        mapping_type: string;
        mapping_cardinality: string;
        title?: string;
        transformation_expression?: string;
      };
    }
  | {
      op: "update_mapping";
      element_id: string;
      patch: {
        name?: string;
        title?: string;
        description?: string;
        lifecycle_status?: string;
        source_refs?: string[];
        target_refs?: string[];
        mapping_type?: string;
        mapping_cardinality?: string;
        transformation_expression?: string;
      };
    }
  | {
      op: "delete_mapping";
      element_id: string;
    }
  | {
      op: "add_physical_object";
      physical_object: {
        element_id: string;
        name: string;
        title?: string;
        description?: string;
        lifecycle_status?: string;
        object_kind?: string;
        logical_entity_ref?: string;
        qualified_name?: string;
        technology?: string;
      };
    }
  | {
      op: "update_physical_object";
      element_id: string;
      patch: {
        name?: string;
        title?: string;
        description?: string;
        lifecycle_status?: string;
        object_kind?: string;
        logical_entity_ref?: string;
        qualified_name?: string;
        technology?: string;
        system_ref?: string;
        direction?: string;
      };
    }
  | {
      op: "delete_physical_object";
      element_id: string;
    }
  | {
      op: "add_physical_field";
      owner_element_id: string;
      physical_field: {
        element_id: string;
        name: string;
        native_type: string;
        description?: string;
        lifecycle_status?: string;
        native_name?: string;
        required?: boolean;
        nullable?: boolean;
        logical_attribute_ref?: string;
      };
    }
  | {
      op: "update_physical_field";
      element_id: string;
      patch: {
        name?: string;
        title?: string;
        description?: string;
        lifecycle_status?: string;
        native_name?: string;
        native_type?: string;
        required?: boolean;
        nullable?: boolean;
        logical_attribute_ref?: string;
        schema_path?: string;
      };
    }
  | {
      op: "delete_physical_field";
      element_id: string;
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

export type SemanticDiffChange = {
  change_code: string;
  category: string;
  subject_ref: string | null;
  message: string;
  path: string | null;
};

export type SemanticDiffReport = {
  id: string;
  base_label: string;
  target_label: string;
  changes: SemanticDiffChange[];
  has_breaking: boolean;
  counts: Record<string, number>;
};

export type JobArtifact = {
  id: string;
  job_id: string;
  kind: string;
  path_or_uri: string;
  content_digest: string;
};

export type DiagramSession = {
  session_id: string;
  workspace_id: string;
  profile: string;
  dbml: string;
};

export type DiagramRejected = {
  code: string;
  message: string;
  path: string | null;
};

export type DiagramSubmitResult = {
  session_id: string;
  rejected: DiagramRejected[];
  op_count: number;
  semantic_diff: SemanticDiffReport;
};

export type DiagramApplyResult = {
  workspace_id: string;
  doc_key: string;
  content: string;
  base_digest: string;
};

export type TransformSpecCatalogItem = {
  rel_path: string;
  spec_id: string;
  source_schema_revision: string;
  target_schema_revision: string;
  transformation_kind: string;
  description: string | null;
};

export type TransformSampleCatalogItem = {
  rel_path: string;
  name: string;
};

export type TransformCatalogWarning = {
  rel_path: string;
  message: string;
};

export type TransformCatalog = {
  specs: TransformSpecCatalogItem[];
  samples: TransformSampleCatalogItem[];
  warnings: TransformCatalogWarning[];
};

export type TransformDiagnostic = {
  diagnostic_code: string;
  severity: string;
  diagnostic_message: string;
  subject_ref: string | null;
};

export type TransformSpecMeta = {
  spec_id: string;
  source_schema_revision: string;
  target_schema_revision: string;
  transformation_kind: string;
  description: string | null;
  allow_unrestricted_eval: boolean;
};

export type TransformRunResult = {
  mode: "preview" | "sample" | string;
  backend: "object" | "sql" | string;
  spec: TransformSpecMeta;
  preserved_semantics: string[];
  lost_semantics: string[];
  diagnostics: TransformDiagnostic[];
  preview_payload: Record<string, unknown> | null;
  output: Record<string, unknown> | null;
  round_trip_ok: boolean | null;
};
