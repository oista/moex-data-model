import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import {
  cleanup,
  fireEvent,
  render,
  screen,
  waitFor,
  within,
} from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import { EntityForms } from "./EntityForms";

const SAMPLE = `
logical_entities:
  - element_id: dams:logical/trading/Client
    name: TradingClient
    title: Client
    description: A client
    attributes:
      - element_id: dams:logical/trading/Client/clientId
        name: clientId
        logical_type: identifier
        required: true
`;

describe("EntityForms", () => {
  afterEach(() => {
    cleanup();
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
    fireEvent.click(screen.getAllByRole("button", { name: /^add entity$/i })[0]);

    await waitFor(() => {
      expect(onDocument).toHaveBeenCalled();
    });
    expect(fetchMock).toHaveBeenCalledWith(
      "/api/workspaces/ws-workbench/documents/trading/mutations",
      expect.objectContaining({ method: "POST" }),
    );
  });

  it("updates and deletes selected entity", async () => {
    const onDocument = vi.fn();
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      status: 200,
      json: async () => ({
        workspace_id: "ws-workbench",
        doc_key: "trading",
        content: SAMPLE,
        base_digest: "sha256:y",
        updated_by: "dev",
      }),
    });
    vi.stubGlobal("fetch", fetchMock);
    vi.spyOn(window, "confirm").mockReturnValue(true);

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

    const editForm = screen.getByTestId("edit-entity-form");
    fireEvent.change(within(editForm).getByDisplayValue("TradingClient"), {
      target: { value: "TradingClient2" },
    });
    fireEvent.click(within(editForm).getByRole("button", { name: /save entity/i }));

    await waitFor(() => expect(onDocument).toHaveBeenCalled());
    const updateCall = fetchMock.mock.calls.find(
      (c) =>
        typeof c[0] === "string" &&
        c[0].includes("/mutations") &&
        c[1]?.body &&
        String(c[1].body).includes("update_logical_entity"),
    );
    expect(updateCall).toBeTruthy();
    expect(JSON.parse(String(updateCall![1]!.body))).toMatchObject({
      op: "update_logical_entity",
      element_id: "dams:logical/trading/Client",
      patch: { name: "TradingClient2" },
    });

    onDocument.mockClear();
    fireEvent.click(screen.getByTestId("delete-entity"));
    await waitFor(() => expect(onDocument).toHaveBeenCalled());
    const deleteCall = fetchMock.mock.calls.find(
      (c) =>
        c[1]?.body && String(c[1].body).includes("delete_logical_entity"),
    );
    expect(JSON.parse(String(deleteCall![1]!.body))).toMatchObject({
      op: "delete_logical_entity",
      element_id: "dams:logical/trading/Client",
    });
  });

  it("shows YAML parse error", () => {
    const qc = new QueryClient({
      defaultOptions: { mutations: { retry: false } },
    });
    render(
      <QueryClientProvider client={qc}>
        <EntityForms
          workspaceId="ws-workbench"
          content={"logical_entities: [\n  - broken"}
          onDocument={vi.fn()}
        />
      </QueryClientProvider>,
    );
    expect(screen.getByTestId("yaml-parse-error")).toBeTruthy();
  });

  it("calls onBeforeMutate before POST", async () => {
    const onBeforeMutate = vi.fn().mockResolvedValue(undefined);
    const onDocument = vi.fn();
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: true,
        status: 200,
        json: async () => ({
          workspace_id: "ws-workbench",
          doc_key: "trading",
          content: SAMPLE,
          base_digest: "sha256:z",
          updated_by: "dev",
        }),
      }),
    );

    const qc = new QueryClient({
      defaultOptions: { mutations: { retry: false } },
    });
    render(
      <QueryClientProvider client={qc}>
        <EntityForms
          workspaceId="ws-workbench"
          content={SAMPLE}
          onDocument={onDocument}
          onBeforeMutate={onBeforeMutate}
        />
      </QueryClientProvider>,
    );

    fireEvent.click(screen.getAllByRole("button", { name: /^add entity$/i })[0]);
    await waitFor(() => expect(onBeforeMutate).toHaveBeenCalled());
    await waitFor(() => expect(onDocument).toHaveBeenCalled());
  });

  it("applies optimistic op before fetch resolves", async () => {
    const onDocument = vi.fn();
    const onOptimisticOp = vi.fn();
    let resolveFetch: (v: unknown) => void = () => {};
    const fetchMock = vi.fn(
      () =>
        new Promise((resolve) => {
          resolveFetch = resolve;
        }),
    );
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
          onOptimisticOp={onOptimisticOp}
        />
      </QueryClientProvider>,
    );

    const form = screen.getByTestId("edit-entity-form");
    fireEvent.change(within(form).getByDisplayValue("Client"), {
      target: { value: "Client Optimistic" },
    });
    fireEvent.click(within(form).getByRole("button", { name: /^save entity$/i }));

    await waitFor(() => expect(onOptimisticOp).toHaveBeenCalled());
    expect(onDocument).not.toHaveBeenCalled();
    expect(onOptimisticOp.mock.calls[0][0]).toMatchObject({
      op: "update_logical_entity",
      element_id: "dams:logical/trading/Client",
      patch: { title: "Client Optimistic" },
    });

    resolveFetch({
      ok: true,
      status: 200,
      json: async () => ({
        workspace_id: "ws-workbench",
        doc_key: "trading",
        content: SAMPLE.replace("title: Client", "title: Client Optimistic"),
        base_digest: "sha256:x",
        updated_by: "dev",
      }),
    });
    await waitFor(() => expect(onDocument).toHaveBeenCalled());
  });
});
