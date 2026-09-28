import { afterEach, describe, expect, it, vi } from "vitest";
import { api, setActor } from "./client";

describe("previewSemanticDiff", () => {
  afterEach(() => {
    vi.restoreAllMocks();
    localStorage.clear();
  });

  it("posts workspace semantic-diff with actor", async () => {
    setActor("diff-user");
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      status: 200,
      json: async () => ({
        id: "semantic-diff:published:draft",
        base_label: "published",
        target_label: "draft:ws-workbench",
        changes: [],
        has_breaking: false,
        counts: { breaking: 0, backward_compatible: 0 },
      }),
    });
    vi.stubGlobal("fetch", fetchMock);

    const report = await api.previewSemanticDiff("ws-workbench");
    expect(report.has_breaking).toBe(false);
    expect(fetchMock).toHaveBeenCalledWith(
      "/api/workspaces/ws-workbench/semantic-diff",
      expect.objectContaining({ method: "POST" }),
    );
    const headers = fetchMock.mock.calls[0][1].headers as Headers;
    expect(headers.get("X-Moex-Actor")).toBe("diff-user");
  });
});
