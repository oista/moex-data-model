import { afterEach, describe, expect, it, vi } from "vitest";
import { api, setActor } from "./client";

describe("api artifacts", () => {
  afterEach(() => {
    vi.restoreAllMocks();
    localStorage.clear();
  });

  it("lists job artifacts with actor header", async () => {
    setActor("art-user");
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      status: 200,
      json: async () => [
        {
          id: "art:1",
          job_id: "job-1",
          kind: "pydantic-contracts",
          path_or_uri: "generated/contracts",
          content_digest: "sha256:x",
        },
      ],
    });
    vi.stubGlobal("fetch", fetchMock);

    const items = await api.listJobArtifacts("job-1");
    expect(items).toHaveLength(1);
    expect(fetchMock).toHaveBeenCalledWith(
      "/api/jobs/job-1/artifacts",
      expect.objectContaining({
        headers: expect.any(Headers),
      }),
    );
    const headers = fetchMock.mock.calls[0][1].headers as Headers;
    expect(headers.get("X-Moex-Actor")).toBe("art-user");
  });

  it("fetches artifact content as text", async () => {
    setActor("art-user");
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      status: 200,
      text: async () => "hello artifact",
    });
    vi.stubGlobal("fetch", fetchMock);

    const text = await api.getArtifactContent("job-1", "art:1");
    expect(text).toBe("hello artifact");
    expect(fetchMock).toHaveBeenCalledWith(
      "/api/jobs/job-1/artifacts/art:1/content",
      expect.any(Object),
    );
  });
});
