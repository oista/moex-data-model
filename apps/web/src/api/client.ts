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
  rebuildIndex: () =>
    request<import("./types").ModelIndexRebuild>("/model-index/rebuild", {
      method: "POST",
    }),
  searchIndex: (q: string) =>
    request<import("./types").ElementHit[]>(
      `/model-index/search?q=${encodeURIComponent(q)}`,
    ),
};
