import { afterEach, describe, expect, it, vi } from "vitest";
import { api, getActor, setActor } from "./client";

describe("api client", () => {
  afterEach(() => {
    vi.restoreAllMocks();
    localStorage.clear();
  });

  it("persists actor and sends X-Moex-Actor", async () => {
    setActor("alice");
    expect(getActor()).toBe("alice");

    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      status: 200,
      json: async () => [{ id: "x", slug: "trading", title: "T", version: "1.0.0", implementation_path: "p", implementation_kind: "linkml", implementation_profile: "dams-data-model", workbench_editable: true }],
    });
    vi.stubGlobal("fetch", fetchMock);

    const rows = await api.listImplementations();
    expect(rows[0].slug).toBe("trading");
    expect(fetchMock).toHaveBeenCalledWith(
      "/api/implementations",
      expect.objectContaining({
        headers: expect.any(Headers),
      }),
    );
    const headers = fetchMock.mock.calls[0][1].headers as Headers;
    expect(headers.get("X-Moex-Actor")).toBe("alice");
  });
});
