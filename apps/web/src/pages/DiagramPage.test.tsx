import { render, screen, waitFor } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { afterEach, describe, expect, it, vi } from "vitest";
import { DiagramPage } from "./DiagramPage";
import { api } from "../api/client";

vi.mock("../api/client", () => ({
  api: {
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

describe("DiagramPage", () => {
  afterEach(() => {
    vi.clearAllMocks();
  });

  it("renders diagram chrome, profile toggle, and iframe", async () => {
    render(
      <MemoryRouter initialEntries={["/models/trading/diagram"]}>
        <DiagramPage />
      </MemoryRouter>,
    );
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
    render(
      <MemoryRouter initialEntries={["/models/trading/diagram?profile=physical"]}>
        <DiagramPage />
      </MemoryRouter>,
    );
    await waitFor(() => {
      expect(api.openDiagram).toHaveBeenCalledWith("ws-workbench", "physical");
    });
    expect(screen.getByText(/profile: physical/i)).toBeTruthy();
  });
});
