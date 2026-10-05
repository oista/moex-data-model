import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import {
  cleanup,
  fireEvent,
  render,
  screen,
  waitFor,
} from "@testing-library/react";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { afterEach, describe, expect, it, vi } from "vitest";

vi.mock("@monaco-editor/react", () => ({
  default: (props: {
    value?: string;
    onChange?: (v: string | undefined) => void;
  }) => (
    <textarea
      data-testid="monaco"
      value={props.value}
      onChange={(e) => props.onChange?.(e.target.value)}
    />
  ),
}));

import { EditorPage } from "./EditorPage";

const PUBLISHED = `element_id: dams:model/trading/1.0.0
logical_entities:
  - element_id: dams:logical/trading/Client
    name: TradingClient
    attributes: []
`;

describe("EditorPage", () => {
  afterEach(() => {
    cleanup();
    vi.restoreAllMocks();
  });

  it("loads published body when no draft", async () => {
    const fetchMock = vi.fn(async (url: string, init?: RequestInit) => {
      if (url === "/api/implementations" && (!init || !init.method || init.method === "GET")) {
        return {
          ok: true,
          status: 200,
          json: async () => ([
            {
              id: "moex:implementation:trading:1.0.0",
              slug: "trading",
              title: "Trading platform",
              version: "1.0.0",
              implementation_path: "p",
              implementation_kind: "linkml",
              implementation_profile: "dams-data-model",
              workbench_editable: true,
            },
          ]),
        };
      }
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
      if (
        url.includes("/documents/moex%3Aimplementation%3Atrading%3A1.0.0") &&
        !url.includes("/mutations") &&
        init?.method !== "PUT"
      ) {
        return {
          ok: false,
          status: 404,
          statusText: "Not Found",
          text: async () => "missing",
        };
      }
      if (url === "/api/implementations/moex%3Aimplementation%3Atrading%3A1.0.0/body") {
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
        <MemoryRouter initialEntries={["/models/trading/edit"]}>
          <Routes>
            <Route path="models/:slug/edit" element={<EditorPage />} />
          </Routes>
        </MemoryRouter>
      </QueryClientProvider>,
    );

    await waitFor(() => {
      expect(screen.getByTestId("monaco")).toBeTruthy();
    });
    expect(screen.getByText(/loaded: published/i)).toBeTruthy();
  });

  it("PUTs dirty Monaco content before mutation", async () => {
    const fetchMock = vi.fn(async (url: string, init?: RequestInit) => {
      if (url === "/api/implementations" && (!init || !init.method || init.method === "GET")) {
        return {
          ok: true,
          status: 200,
          json: async () => ([
            {
              id: "moex:implementation:trading:1.0.0",
              slug: "trading",
              title: "Trading platform",
              version: "1.0.0",
              implementation_path: "p",
              implementation_kind: "linkml",
              implementation_profile: "dams-data-model",
              workbench_editable: true,
            },
          ]),
        };
      }
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
      if (
        url.includes("/documents/moex%3Aimplementation%3Atrading%3A1.0.0") &&
        !url.includes("/mutations") &&
        init?.method !== "PUT"
      ) {
        return {
          ok: false,
          status: 404,
          statusText: "Not Found",
          text: async () => "missing",
        };
      }
      if (url === "/api/implementations/moex%3Aimplementation%3Atrading%3A1.0.0/body") {
        return {
          ok: true,
          status: 200,
          json: async () => ({
            content: PUBLISHED,
            content_digest: "sha256:pub",
            path: "trading.yaml",
          }),
        };
      }
      if (url.includes("/documents/moex%3Aimplementation%3Atrading%3A1.0.0") && init?.method === "PUT") {
        const body = JSON.parse(String(init.body));
        return {
          ok: true,
          status: 200,
          json: async () => ({
            workspace_id: "ws-workbench",
            doc_key: "trading",
            content: body.content,
            base_digest: "sha256:saved",
            updated_by: "dev",
          }),
        };
      }
      if (url.includes("/mutations") && init?.method === "POST") {
        return {
          ok: true,
          status: 200,
          json: async () => ({
            workspace_id: "ws-workbench",
            doc_key: "trading",
            content: `${PUBLISHED}\n  - element_id: dams:logical/trading/Order\n    name: Order\n`,
            base_digest: "sha256:mut",
            updated_by: "dev",
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
        <MemoryRouter initialEntries={["/models/trading/edit"]}>
          <Routes>
            <Route path="models/:slug/edit" element={<EditorPage />} />
          </Routes>
        </MemoryRouter>
      </QueryClientProvider>,
    );

    await waitFor(() => expect(screen.getAllByTestId("monaco").length).toBeGreaterThan(0));

    const monaco = screen.getAllByTestId("monaco")[0];
    fireEvent.change(monaco, {
      target: { value: `${PUBLISHED}\n# dirty edit\n` },
    });
    expect(screen.getByText(/unsaved/i)).toBeTruthy();

    fireEvent.click(screen.getAllByRole("button", { name: /^add entity$/i })[0]);

    await waitFor(() => {
      const put = fetchMock.mock.calls.find(
        (c) => c[1]?.method === "PUT" && String(c[0]).includes("/documents/moex%3Aimplementation%3Atrading%3A1.0.0"),
      );
      expect(put).toBeTruthy();
      expect(String(put![1]!.body)).toContain("dirty edit");
    });

    await waitFor(() => {
      const mut = fetchMock.mock.calls.find(
        (c) => c[1]?.method === "POST" && String(c[0]).includes("/mutations"),
      );
      expect(mut).toBeTruthy();
    });
  });

  it("saves draft then previews semantic diff", async () => {
    const fetchMock = vi.fn(async (url: string, init?: RequestInit) => {
      if (url === "/api/implementations" && (!init || !init.method || init.method === "GET")) {
        return {
          ok: true,
          status: 200,
          json: async () => ([
            {
              id: "moex:implementation:trading:1.0.0",
              slug: "trading",
              title: "Trading platform",
              version: "1.0.0",
              implementation_path: "p",
              implementation_kind: "linkml",
              implementation_profile: "dams-data-model",
              workbench_editable: true,
            },
          ]),
        };
      }
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
      if (
        url.includes("/documents/moex%3Aimplementation%3Atrading%3A1.0.0") &&
        !url.includes("/mutations") &&
        !url.includes("/semantic-diff") &&
        (!init?.method || init.method === "GET")
      ) {
        return {
          ok: false,
          status: 404,
          statusText: "Not Found",
          text: async () => "missing",
        };
      }
      if (url === "/api/implementations/moex%3Aimplementation%3Atrading%3A1.0.0/body") {
        return {
          ok: true,
          status: 200,
          json: async () => ({
            content: PUBLISHED,
            content_digest: "sha256:pub",
            path: "trading.yaml",
          }),
        };
      }
      if (url.includes("/documents/moex%3Aimplementation%3Atrading%3A1.0.0") && init?.method === "PUT") {
        const body = JSON.parse(String(init.body));
        return {
          ok: true,
          status: 200,
          json: async () => ({
            workspace_id: "ws-workbench",
            doc_key: "trading",
            content: body.content,
            base_digest: "sha256:saved",
            updated_by: "dev",
          }),
        };
      }
      if (url.includes("/semantic-diff") && init?.method === "POST") {
        return {
          ok: true,
          status: 200,
          json: async () => ({
            id: "semantic-diff:published:draft",
            base_label: "published",
            target_label: "draft:ws-workbench",
            changes: [
              {
                change_code: "DAMS-DIFF-REMOVE",
                category: "breaking",
                subject_ref: "dams:logical/trading/Client/fullName",
                message: "Removed attribute",
                path: "logical_attribute",
              },
            ],
            has_breaking: true,
            counts: {
              breaking: 1,
              backward_compatible: 0,
              governance: 0,
              operational: 0,
              non_breaking: 0,
            },
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
        <MemoryRouter initialEntries={["/models/trading/edit"]}>
          <Routes>
            <Route path="models/:slug/edit" element={<EditorPage />} />
          </Routes>
        </MemoryRouter>
      </QueryClientProvider>,
    );

    await waitFor(() => expect(screen.getByTestId("monaco")).toBeTruthy());
    fireEvent.click(screen.getByTestId("review-changes"));

    await waitFor(() => {
      expect(screen.getByTestId("semantic-diff-result")).toBeTruthy();
    });
    expect(screen.getByText(/breaking: 1/i)).toBeTruthy();
    expect(screen.getByText(/DAMS-DIFF-REMOVE/)).toBeTruthy();

    const put = fetchMock.mock.calls.find(
      (c) => c[1]?.method === "PUT" && String(c[0]).includes("/documents/moex%3Aimplementation%3Atrading%3A1.0.0"),
    );
    expect(put).toBeTruthy();
    const diffCall = fetchMock.mock.calls.find(
      (c) =>
        c[1]?.method === "POST" && String(c[0]).includes("/semantic-diff"),
    );
    expect(diffCall).toBeTruthy();
  });
});
