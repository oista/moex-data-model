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
import {
  hasAutoPromoteControl,
  ImportWizardPage,
} from "./ImportWizardPage";

describe("ImportWizardPage", () => {
  afterEach(() => {
    cleanup();
    vi.restoreAllMocks();
  });

  it("runs import and opens generated-draft without promote", async () => {
    const fetchMock = vi.fn(async (url: string, init?: RequestInit) => {
      if (url === "/api/implementations") {
        return {
          ok: true,
          status: 200,
          json: async () => [
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
          ],
        };
      }
      if (url.includes("/imports") && init?.method === "POST") {
        return {
          ok: true,
          status: 200,
          json: async () => ({
            id: "job:import1",
            workspace_id: "ws-1",
            kind: "import_draft",
            status: "succeeded",
            implementation_id: "moex:import:draft",
            result_summary: "import_draft status=generated-draft diagnostics=1",
            finished_at: "2026-09-28T00:00:00Z",
          }),
        };
      }
      if (url.endsWith("/jobs/job:import1/artifacts")) {
        return {
          ok: true,
          status: 200,
          json: async () => [
            {
              id: "art:diag",
              job_id: "job:import1",
              kind: "import-diagnostics",
              path_or_uri: "generated/imports/x/diagnostics.json",
              content_digest: "sha256:a",
            },
            {
              id: "art:schema",
              job_id: "job:import1",
              kind: "import-inferred-schema",
              path_or_uri: "generated/imports/x/inferred-schema.yaml",
              content_digest: "sha256:b",
            },
            {
              id: "art:enrich",
              job_id: "job:import1",
              kind: "import-enrich-checklist",
              path_or_uri: "generated/imports/x/enrich-checklist.json",
              content_digest: "sha256:c",
            },
          ],
        };
      }
      if (url.includes("/artifacts/art:diag/content")) {
        return {
          ok: true,
          status: 200,
          text: async () =>
            JSON.stringify([
              {
                diagnostic_code: "IMPORT-UNCERTAIN-001",
                severity: "warning",
                diagnostic_message: "refine ranges",
              },
            ]),
        };
      }
      if (url.includes("/artifacts/art:schema/content")) {
        return {
          ok: true,
          status: 200,
          text: async () => "name: MiniPerson\nclasses: {}\n",
        };
      }
      if (url.includes("/artifacts/art:enrich/content")) {
        return {
          ok: true,
          status: 200,
          text: async () =>
            JSON.stringify([
              {
                code: "IMPORT-ENRICH-DESC",
                severity: "warning",
                path: "classes.Person",
                message: "class Person is missing a description",
                field: "description",
              },
              {
                code: "IMPORT-ENRICH-RANGE",
                severity: "warning",
                path: "classes.Person.slots.name",
                message: "weak range",
                field: "range",
              },
            ]),
        };
      }
      if (
        url.includes("/documents/moex%3Aimplementation%3Atrading%3A1.0.0") &&
        init?.method === "PUT"
      ) {
        const body = JSON.parse(String(init.body || "{}")) as {
          content: string;
        };
        expect(body.content).toContain("generated-draft");
        expect(body.content).toContain("MiniPerson");
        return {
          ok: true,
          status: 200,
          json: async () => ({
            workspace_id: "ws-1",
            doc_key: "moex:implementation:trading:1.0.0",
            content: body.content,
            base_digest: "sha256:x",
            updated_by: "dev",
          }),
        };
      }
      return { ok: false, status: 404, text: async () => "missing" };
    });
    vi.stubGlobal("fetch", fetchMock);

    const qc = new QueryClient({
      defaultOptions: { queries: { retry: false }, mutations: { retry: false } },
    });
    render(
      <QueryClientProvider client={qc}>
        <MemoryRouter initialEntries={["/workspaces/ws-1/import"]}>
          <Routes>
            <Route
              path="/workspaces/:workspaceId/import"
              element={<ImportWizardPage />}
            />
          </Routes>
        </MemoryRouter>
      </QueryClientProvider>,
    );

    expect(screen.getByTestId("draft-banner")).toBeTruthy();
    expect(screen.queryByTestId("auto-promote")).toBeNull();
    expect(screen.queryByRole("button", { name: /publish as modelpackage/i })).toBeNull();
    expect(hasAutoPromoteControl([])).toBe(false);

    const file = new File(['{"type":"object"}'], "mini.json", {
      type: "application/json",
    });
    const input = screen.getByTestId("import-file") as HTMLInputElement;
    fireEvent.change(input, { target: { files: [file] } });
    fireEvent.click(screen.getByTestId("run-import"));

    await waitFor(() =>
      expect(screen.getByTestId("inferred-preview").textContent).toContain(
        "MiniPerson",
      ),
    );
    expect(screen.getByTestId("import-diagnostics").textContent).toContain(
      "IMPORT-UNCERTAIN-001",
    );
    expect(screen.getByTestId("enrich-checklist").textContent).toContain(
      "IMPORT-ENRICH-DESC",
    );
    expect(screen.getByTestId("enrich-checklist").textContent).toContain(
      "IMPORT-ENRICH-RANGE",
    );
    expect(screen.getByTestId("enrich-monaco-link")).toBeTruthy();

    fireEvent.click(screen.getByTestId("open-as-draft"));
    await waitFor(() =>
      expect(screen.getByTestId("draft-opened")).toBeTruthy(),
    );
  });
});
