import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { render, screen, waitFor } from "@testing-library/react";
import { MemoryRouter } from "react-router-dom";
import { afterEach, describe, expect, it, vi } from "vitest";

vi.mock("@monaco-editor/react", () => ({
  default: (props: { value?: string }) => (
    <textarea data-testid="monaco" defaultValue={props.value} readOnly />
  ),
}));

import { EditorPage } from "./EditorPage";

describe("EditorPage", () => {
  afterEach(() => {
    vi.restoreAllMocks();
  });

  it("loads published body when no draft", async () => {
    const fetchMock = vi.fn(async (url: string, init?: RequestInit) => {
      if (url === "/api/workspaces" && init?.method === "POST") {
        return {
          ok: true,
          status: 200,
          json: async () => ({
            id: "ws-workbench",
            name: "Workbench",
            members: [],
          }),
        };
      }
      if (url.includes("/documents/trading") && init?.method !== "PUT") {
        return {
          ok: false,
          status: 404,
          statusText: "Not Found",
          text: async () => "missing",
        };
      }
      if (url === "/api/implementations/trading/body") {
        return {
          ok: true,
          status: 200,
          json: async () => ({
            content: "element_id: dams:model/trading/1.0.0\n",
            content_digest: "sha256:abc",
            path: "trading.yaml",
          }),
        };
      }
      return {
        ok: false,
        status: 500,
        statusText: "err",
        text: async () => "unexpected",
      };
    });
    vi.stubGlobal("fetch", fetchMock);

    const qc = new QueryClient({
      defaultOptions: { queries: { retry: false }, mutations: { retry: false } },
    });
    render(
      <QueryClientProvider client={qc}>
        <MemoryRouter>
          <EditorPage />
        </MemoryRouter>
      </QueryClientProvider>,
    );

    await waitFor(() => {
      expect(screen.getByTestId("monaco")).toBeTruthy();
    });
    expect(screen.getByText(/loaded: published/i)).toBeTruthy();
  });
});
