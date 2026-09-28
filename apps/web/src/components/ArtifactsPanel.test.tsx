import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import {
  cleanup,
  fireEvent,
  render,
  screen,
  waitFor,
} from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import { ArtifactsPanel } from "./ArtifactsPanel";

describe("ArtifactsPanel", () => {
  afterEach(() => {
    cleanup();
    vi.restoreAllMocks();
  });

  it("lists artifacts and previews content", async () => {
    const fetchMock = vi.fn(async (url: string) => {
      if (String(url).endsWith("/artifacts")) {
        return {
          ok: true,
          status: 200,
          json: async () => [
            {
              id: "art:1",
              job_id: "job-1",
              kind: "pydantic-contracts",
              path_or_uri: "generated/contracts/moex-dams/0.1",
              content_digest: "sha256:abc",
            },
          ],
        };
      }
      if (String(url).includes("/content")) {
        return {
          ok: true,
          status: 200,
          text: async () => "# directory listing\n__init__.py\n",
        };
      }
      return { ok: false, status: 404, text: async () => "no" };
    });
    vi.stubGlobal("fetch", fetchMock);

    const qc = new QueryClient({
      defaultOptions: { mutations: { retry: false } },
    });
    render(
      <QueryClientProvider client={qc}>
        <ArtifactsPanel jobId="job-1" />
      </QueryClientProvider>,
    );

    await waitFor(() =>
      expect(screen.getByTestId("artifact-list").textContent).toContain(
        "pydantic-contracts",
      ),
    );

    fireEvent.click(screen.getByTestId("preview-artifact-art:1"));
    await waitFor(() =>
      expect(screen.getByTestId("artifact-preview").textContent).toContain(
        "__init__.py",
      ),
    );
  });
});
