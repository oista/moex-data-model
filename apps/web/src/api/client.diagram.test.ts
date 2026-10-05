import { afterEach, describe, expect, it, vi } from "vitest";
import { api, setActor } from "./client";

describe("diagram API client", () => {
  afterEach(() => {
    vi.restoreAllMocks();
    localStorage.clear();
  });

  it("opens and submits diagram", async () => {
    setActor("diagram-user");
    const fetchMock = vi
      .fn()
      .mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => ({
          session_id: "s1",
          workspace_id: "ws-workbench",
          profile: "logical",
          dbml: "Table T {}",
        }),
      })
      .mockResolvedValueOnce({
        ok: true,
        status: 200,
        json: async () => ({
          session_id: "s1",
          rejected: [],
          op_count: 1,
          semantic_diff: {
            id: "d1",
            base_label: "a",
            target_label: "b",
            changes: [],
            has_breaking: false,
            counts: {},
          },
        }),
      });
    vi.stubGlobal("fetch", fetchMock);

    const opened = await api.openDiagram("ws-workbench", "moex:implementation:mdm:0.1.0", "logical");
    expect(opened.session_id).toBe("s1");
    expect(fetchMock.mock.calls[0][0]).toBe(
      "/api/workspaces/ws-workbench/diagrams",
    );

    const submitted = await api.submitDiagram("ws-workbench", "s1", "Table T {}");
    expect(submitted.op_count).toBe(1);
    expect(fetchMock.mock.calls[1][0]).toBe(
      "/api/workspaces/ws-workbench/diagrams/s1/submit",
    );
  });
});
