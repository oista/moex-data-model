import { render, screen } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { afterEach, describe, expect, it, vi } from "vitest";
import { DiagramPage } from "./DiagramPage";

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

  it("renders diagram chrome and iframe", async () => {
    render(
      <MemoryRouter initialEntries={["/models/trading/diagram"]}>
        <DiagramPage />
      </MemoryRouter>,
    );
    expect(await screen.findByRole("heading", { name: /Diagram/i })).toBeTruthy();
    expect(screen.getByTitle("drawDB")).toBeTruthy();
    expect(screen.getByRole("button", { name: /Submit for review/i })).toBeTruthy();
  });
});
