import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen, waitFor } from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { afterEach, describe, expect, it, vi } from "vitest";
import { DiagramPage } from "./DiagramPage";
import { api } from "../api/client";

vi.mock("../api/client", () => ({
  api: {
    listImplementations: vi.fn().mockResolvedValue([
      {
        id: "moex:implementation:mdm:0.1.0",
        slug: "mdm",
        title: "MDM data model",
        version: "1.0.0",
        implementation_path: "p",
        implementation_kind: "linkml",
        implementation_profile: "dams-data-model",
        workbench_editable: true,
      },
    ]),
    createWorkspace: vi.fn().mockResolvedValue({ id: "ws-workbench" }),
    getDocument: vi.fn().mockResolvedValue({
      content: "name: x",
      base_digest: "sha256:1",
    }),
    openDiagram: vi.fn().mockResolvedValue({
      session_id: "sess-1",
      workspace_id: "ws-workbench",
      profile: "logical",
      dbml: "Table Demo {}",
    }),
    submitDiagram: vi.fn(),
    applyDiagram: vi.fn(),
  },
}));

function renderAt(path: string) {
  const qc = new QueryClient({
    defaultOptions: { queries: { retry: false }, mutations: { retry: false } },
  });
  return render(
    <QueryClientProvider client={qc}>
      <MemoryRouter initialEntries={[path]}>
        <Routes>
          <Route path="models/:slug/diagram" element={<DiagramPage />} />
        </Routes>
      </MemoryRouter>
    </QueryClientProvider>,
  );
}

describe("DiagramPage", () => {
  afterEach(() => {
    vi.clearAllMocks();
  });

  it("renders diagram chrome, profile toggle, and iframe", async () => {
    renderAt("/models/mdm/diagram");
    expect(await screen.findByRole("heading", { name: /Diagram/i })).toBeTruthy();
    expect(screen.getByTitle("drawDB")).toBeTruthy();
    expect(screen.getByRole("button", { name: /Submit for review/i })).toBeTruthy();
    expect(screen.getByTestId("profile-toggle")).toBeTruthy();
    expect(screen.getByTestId("profile-logical")).toBeTruthy();
    expect(screen.getByTestId("profile-physical")).toBeTruthy();
  });

  it("opens session with physical profile from query", async () => {
    vi.mocked(api.openDiagram).mockResolvedValueOnce({
      session_id: "sess-phys",
      workspace_id: "ws-workbench",
      profile: "physical",
      dbml: "Table Phys {}",
    });
    renderAt("/models/mdm/diagram?profile=physical");
    await waitFor(() => {
      expect(api.openDiagram).toHaveBeenCalledWith(
        "ws-workbench",
        "moex:implementation:mdm:0.1.0",
        "physical",
      );
    });
    expect(screen.getByText(/profile: physical/i)).toBeTruthy();
  });
});
