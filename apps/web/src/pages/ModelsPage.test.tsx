import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen, waitFor } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { afterEach, describe, expect, it, vi } from "vitest";
import { ModelsPage } from "./ModelsPage";

describe("ModelsPage", () => {
  afterEach(() => {
    vi.restoreAllMocks();
  });

  it("renders implementation from API", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: true,
        status: 200,
        json: async () => [
          {
            id: "moex:implementation:mdm:0.1.0",
            slug: "mdm",
            version: "1.0.0",
            implementation_kind: "linkml",
            implementation_profile: "dams-data-model",
            workbench_editable: true,
            title: "MDM data model",
            implementation_path: "model-assets/.../mdm-solution-model.yaml",
          },
        ],
      }),
    );

    const qc = new QueryClient({
      defaultOptions: { queries: { retry: false } },
    });
    render(
      <QueryClientProvider client={qc}>
        <MemoryRouter>
          <ModelsPage />
        </MemoryRouter>
      </QueryClientProvider>,
    );

    await waitFor(() => {
      expect(screen.getByText("MDM data model")).toBeTruthy();
    });
  });
});
