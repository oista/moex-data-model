import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import { EntityForms } from "./EntityForms";

const SAMPLE = `
logical_entities:
  - element_id: dams:logical/trading/Client
    name: TradingClient
    attributes: []
`;

describe("EntityForms", () => {
  afterEach(() => {
    vi.restoreAllMocks();
  });

  it("lists entities and applies mutation", async () => {
    const onDocument = vi.fn();
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      status: 200,
      json: async () => ({
        workspace_id: "ws-workbench",
        doc_key: "trading",
        content: `${SAMPLE}
  - element_id: dams:logical/trading/OrderBook
    name: OrderBook
    attributes: []
`,
        base_digest: "sha256:x",
        updated_by: "dev",
      }),
    });
    vi.stubGlobal("fetch", fetchMock);

    const qc = new QueryClient({
      defaultOptions: { mutations: { retry: false } },
    });
    render(
      <QueryClientProvider client={qc}>
        <EntityForms
          workspaceId="ws-workbench"
          content={SAMPLE}
          onDocument={onDocument}
        />
      </QueryClientProvider>,
    );

    expect(screen.getByTestId("entity-list").textContent).toContain(
      "dams:logical/trading/Client",
    );

    fireEvent.change(screen.getByDisplayValue("dams:logical/trading/NewEntity"), {
      target: { value: "dams:logical/trading/OrderBook" },
    });
    fireEvent.change(screen.getByDisplayValue("NewEntity"), {
      target: { value: "OrderBook" },
    });
    fireEvent.click(screen.getByRole("button", { name: /add entity/i }));

    await waitFor(() => {
      expect(onDocument).toHaveBeenCalled();
    });
    expect(fetchMock).toHaveBeenCalledWith(
      "/api/workspaces/ws-workbench/documents/trading/mutations",
      expect.objectContaining({ method: "POST" }),
    );
  });
});
