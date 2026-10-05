import { afterEach, describe, expect, it, vi } from "vitest";
import { api, setActor } from "./client";

describe("createPublication", () => {
  afterEach(() => {
    vi.restoreAllMocks();
    localStorage.clear();
  });

  it("posts with Idempotency-Key and actor", async () => {
    setActor("pub-user");
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      status: 200,
      json: async () => ({
        id: "pub:1",
        workspace_id: "ws-workbench",
        implementation_id: "moex:implementation:trading:1.0.0",
        branch_name: "workbench/publish-1",
        base_revision: "abc",
        commit_sha: "def4567890ab",
        review_url: "local://review/workbench/publish-1",
        review_id: "x",
        status: "submitted",
      }),
    });
    vi.stubGlobal("fetch", fetchMock);

    const pub = await api.createPublication(
      {
        workspace_id: "ws-workbench",
        implementation_id: "moex:implementation:trading:1.0.0",
      },
      "idem-1",
    );
    expect(pub.status).toBe("submitted");
    const headers = fetchMock.mock.calls[0][1].headers as Headers;
    expect(headers.get("X-Moex-Actor")).toBe("pub-user");
    expect(headers.get("Idempotency-Key")).toBe("idem-1");
  });
});
