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
import { hasPromoteControl, TransformPage } from "./TransformPage";

describe("TransformPage", () => {
  afterEach(() => {
    cleanup();
    vi.restoreAllMocks();
  });

  it("runs preview and shows lost semantics + diagnostics without promote", async () => {
    const fetchMock = vi.fn(async (url: string, init?: RequestInit) => {
      if (
        url.includes("/transforms") &&
        !url.includes("/run") &&
        (!init || !init.method || init.method === "GET")
      ) {
        return {
          ok: true,
          status: 200,
          json: async () => ({
            specs: [
              {
                rel_path: "dams-logical-entity-rename-kind.yaml",
                spec_id: "moex:transform:dams-logical-entity-rename-kind:0.1",
                source_schema_revision: "dams-0.1-slice",
                target_schema_revision: "dams-0.1-next-slice",
                transformation_kind: "partial",
                description: "rename entity_type",
              },
            ],
            samples: [
              {
                rel_path: "samples/dams_logical_entity_sample.json",
                name: "dams_logical_entity_sample.json",
              },
            ],
            warnings: [],
          }),
        };
      }
      if (url.includes("/transforms/run") && init?.method === "POST") {
        return {
          ok: true,
          status: 200,
          json: async () => ({
            mode: "preview",
            backend: "object",
            spec: {
              spec_id: "moex:transform:dams-logical-entity-rename-kind:0.1",
              source_schema_revision: "dams-0.1-slice",
              target_schema_revision: "dams-0.1-next-slice",
              transformation_kind: "partial",
              description: "rename entity_type",
              allow_unrestricted_eval: false,
            },
            preserved_semantics: ["LogicalEntity.name"],
            lost_semantics: ["LogicalEntity.entity_type"],
            diagnostics: [
              {
                diagnostic_code: "MAP-INFO-001",
                severity: "info",
                diagnostic_message: "ok",
                subject_ref: null,
              },
            ],
            preview_payload: {
              name: "TradeOrder",
              logical_entity_kind: "core",
            },
            output: null,
            round_trip_ok: null,
          }),
        };
      }
      return {
        ok: false,
        status: 404,
        statusText: "Not Found",
        text: async () => "missing",
        json: async () => ({}),
      };
    });
    vi.stubGlobal("fetch", fetchMock);

    const qc = new QueryClient({
      defaultOptions: { queries: { retry: false } },
    });
    render(
      <QueryClientProvider client={qc}>
        <MemoryRouter initialEntries={["/workspaces/ws-1/transform"]}>
          <Routes>
            <Route
              path="/workspaces/:workspaceId/transform"
              element={<TransformPage />}
            />
          </Routes>
        </MemoryRouter>
      </QueryClientProvider>,
    );

    await waitFor(() => {
      expect(screen.getByTestId("transform-spec")).toBeTruthy();
    });

    await waitFor(() => {
      expect(
        (screen.getByTestId("transform-spec") as HTMLSelectElement).value,
      ).toBe("dams-logical-entity-rename-kind.yaml");
    });

    fireEvent.submit(screen.getByTestId("transform-form"));

    await waitFor(() => {
      expect(screen.getByTestId("transform-result")).toBeTruthy();
    });

    expect(screen.getByTestId("transform-lost").textContent).toContain(
      "LogicalEntity.entity_type",
    );
    expect(screen.getByTestId("transform-diagnostics").textContent).toContain(
      "MAP-INFO-001",
    );
    expect(screen.getByTestId("transform-payload").textContent).toContain(
      "logical_entity_kind",
    );
    expect(screen.queryByTestId("auto-promote")).toBeNull();
    expect(hasPromoteControl()).toBe(false);
  });
});
