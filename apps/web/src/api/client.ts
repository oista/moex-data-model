const ACTOR_KEY = "moex.actor";
const LAST_JOB_KEY = "moex.lastJob";

export function getActor(): string {
  return localStorage.getItem(ACTOR_KEY) || "dev";
}

export function setActor(actor: string): void {
  localStorage.setItem(ACTOR_KEY, actor.trim() || "dev");
}

export function getLastJobId(): string | null {
  return localStorage.getItem(LAST_JOB_KEY);
}

export function setLastJobId(jobId: string): void {
  localStorage.setItem(LAST_JOB_KEY, jobId);
}

async function request<T>(
  path: string,
  init: RequestInit = {},
): Promise<T> {
  const headers = new Headers(init.headers);
  headers.set("X-Moex-Actor", getActor());
  if (init.body && !headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }
  const res = await fetch(`/api${path}`, { ...init, headers });
  if (!res.ok) {
    const detail = await res.text();
    throw new Error(`${res.status} ${res.statusText}: ${detail}`);
  }
  if (res.status === 204) {
    return undefined as T;
  }
  return (await res.json()) as T;
}

export const api = {
  health: () => request<{ status: string }>("/health"),
  listImplementations: () =>
    request<import("./types").Implementation[]>("/implementations"),
  tradingConformance: () =>
    request<import("./types").Conformance>(
      "/implementations/trading/conformance",
    ),
  tradingBody: () =>
    request<import("./types").ImplementationBody>(
      "/implementations/trading/body",
    ),
  listWorkspaces: () =>
    request<import("./types").Workspace[]>("/workspaces"),
  createWorkspace: (body: { id?: string; name: string }) =>
    request<import("./types").Workspace>("/workspaces", {
      method: "POST",
      body: JSON.stringify(body),
    }),
  getWorkspace: (id: string) =>
    request<import("./types").Workspace>(`/workspaces/${id}`),
  getDocument: (workspaceId: string) =>
    request<import("./types").WorkspaceDocument>(
      `/workspaces/${workspaceId}/documents/trading`,
    ),
  putDocument: (
    workspaceId: string,
    body: { content: string; base_digest?: string },
  ) =>
    request<import("./types").WorkspaceDocument>(
      `/workspaces/${workspaceId}/documents/trading`,
      {
        method: "PUT",
        body: JSON.stringify(body),
      },
    ),
  mutateDocument: (
    workspaceId: string,
    body: import("./types").DocumentMutation,
  ) =>
    request<import("./types").WorkspaceDocument>(
      `/workspaces/${workspaceId}/documents/trading/mutations`,
      {
        method: "POST",
        body: JSON.stringify(body),
      },
    ),
  createPublication: (
    body: {
      workspace_id: string;
      implementation_id?: string;
      title?: string;
      base_ref?: string;
    },
    idempotencyKey?: string,
  ) => {
    const headers: Record<string, string> = {};
    if (idempotencyKey) {
      headers["Idempotency-Key"] = idempotencyKey;
    }
    return request<import("./types").Publication>("/publications", {
      method: "POST",
      headers,
      body: JSON.stringify(body),
    });
  },
  previewSemanticDiff: (workspaceId: string) =>
    request<import("./types").SemanticDiffReport>(
      `/workspaces/${workspaceId}/semantic-diff`,
      { method: "POST" },
    ),
  getPublication: (id: string) =>
    request<import("./types").Publication>(`/publications/${id}`),
  createJob: (
    body: {
      kind: "validate" | "compile";
      workspace_id: string;
      implementation_id: string;
      source?: "published" | "draft";
    },
    idempotencyKey?: string,
  ) => {
    const headers: Record<string, string> = {};
    if (idempotencyKey) {
      headers["Idempotency-Key"] = idempotencyKey;
    }
    return request<import("./types").Job>("/jobs", {
      method: "POST",
      headers,
      body: JSON.stringify(body),
    });
  },
  getJob: (id: string) => request<import("./types").Job>(`/jobs/${id}`),
  listJobArtifacts: (jobId: string) =>
    request<import("./types").JobArtifact[]>(`/jobs/${jobId}/artifacts`),
  getArtifactContent: async (jobId: string, artifactId: string) => {
    const headers = new Headers();
    headers.set("X-Moex-Actor", getActor());
    const res = await fetch(
      `/api/jobs/${jobId}/artifacts/${artifactId}/content`,
      { headers },
    );
    if (!res.ok) {
      const detail = await res.text();
      throw new Error(`${res.status} ${res.statusText}: ${detail}`);
    }
    return res.text();
  },
  rebuildIndex: () =>
    request<import("./types").ModelIndexRebuild>("/model-index/rebuild", {
      method: "POST",
    }),
  searchIndex: (q: string) =>
    request<import("./types").ElementHit[]>(
      `/model-index/search?q=${encodeURIComponent(q)}`,
    ),
  openDiagram: (
    workspaceId: string,
    profile: "logical" | "physical" = "logical",
  ) =>
    request<import("./types").DiagramSession>(
      `/workspaces/${workspaceId}/diagrams`,
      {
        method: "POST",
        body: JSON.stringify({ profile }),
      },
    ),
  getDiagram: (workspaceId: string, sessionId: string) =>
    request<import("./types").DiagramSession>(
      `/workspaces/${workspaceId}/diagrams/${sessionId}`,
    ),
  submitDiagram: (workspaceId: string, sessionId: string, dbml: string) =>
    request<import("./types").DiagramSubmitResult>(
      `/workspaces/${workspaceId}/diagrams/${sessionId}/submit`,
      {
        method: "POST",
        body: JSON.stringify({ dbml }),
      },
    ),
  applyDiagram: (workspaceId: string, sessionId: string) =>
    request<import("./types").DiagramApplyResult>(
      `/workspaces/${workspaceId}/diagrams/${sessionId}/apply`,
      { method: "POST" },
    ),
  putDiagramLayout: (
    workspaceId: string,
    sessionId: string,
    body: { nodes: Record<string, { x: number; y: number }>; model_revision?: string },
  ) =>
    request<{
      diagram_id: string;
      workspace_id: string;
      profile: string;
      model_revision: string;
      nodes: Record<string, { x: number; y: number }>;
    }>(`/workspaces/${workspaceId}/diagrams/${sessionId}/layout`, {
      method: "PUT",
      body: JSON.stringify(body),
    }),
};
