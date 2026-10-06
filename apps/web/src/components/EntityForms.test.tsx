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
  - element_id: dams:logical/mdm/ENTERPRISE
    name: ENTERPRISE
    title: Legal entity
    description: A legal entity
    attributes:
      - element_id: dams:logical/mdm/ENTERPRISE/ENTERPRISE_ID
        name: enterpriseId
        data_type_ref: dams:datatype/identifier
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
        doc_key: "mdm",
        content: `${SAMPLE}
  - element_id: dams:logical/mdm/OrderBook
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
          implementationId="moex:implementation:mdm:0.1.0"
          idNamespace="mdm"
          content={SAMPLE}
          onDocument={onDocument}
        />
      </QueryClientProvider>,
    );

    expect(screen.getByTestId("entity-list").textContent).toContain(
      "dams:logical/mdm/ENTERPRISE",
    );

    fireEvent.change(screen.getByDisplayValue("dams:logical/mdm/NewEntity"), {
      target: { value: "dams:logical/mdm/OrderBook" },
    });
    fireEvent.change(screen.getByDisplayValue("NewEntity"), {
      target: { value: "OrderBook" },
    });
    fireEvent.click(screen.getAllByRole("button", { name: /^add entity$/i })[0]);

    await waitFor(() => {
      expect(onDocument).toHaveBeenCalled();
    });
    expect(fetchMock).toHaveBeenCalledWith(
      "/api/workspaces/ws-workbench/documents/moex%3Aimplementation%3Amdm%3A0.1.0/mutations",
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
        doc_key: "mdm",
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
          implementationId="moex:implementation:mdm:0.1.0"
          idNamespace="mdm"
          content={SAMPLE}
          onDocument={onDocument}
        />
      </QueryClientProvider>,
    );

    const editForm = screen.getByTestId("edit-entity-form");
    fireEvent.change(within(editForm).getByDisplayValue("ENTERPRISE"), {
      target: { value: "ENTERPRISE2" },
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
      element_id: "dams:logical/mdm/ENTERPRISE",
      patch: { name: "ENTERPRISE2" },
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
      element_id: "dams:logical/mdm/ENTERPRISE",
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
          implementationId="moex:implementation:mdm:0.1.0"
          idNamespace="mdm"
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
          doc_key: "mdm",
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
          implementationId="moex:implementation:mdm:0.1.0"
          idNamespace="mdm"
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
          implementationId="moex:implementation:mdm:0.1.0"
          idNamespace="mdm"
          content={SAMPLE}
          onDocument={onDocument}
          onOptimisticOp={onOptimisticOp}
        />
      </QueryClientProvider>,
    );

    const form = screen.getByTestId("edit-entity-form");
    fireEvent.change(within(form).getByDisplayValue("Legal entity"), {
      target: { value: "ENTERPRISE Optimistic" },
    });
    fireEvent.click(within(form).getByRole("button", { name: /^save entity$/i }));

    await waitFor(() => expect(onOptimisticOp).toHaveBeenCalled());
    expect(onDocument).not.toHaveBeenCalled();
    expect(onOptimisticOp.mock.calls[0][0]).toMatchObject({
      op: "update_logical_entity",
      element_id: "dams:logical/mdm/ENTERPRISE",
      patch: { title: "ENTERPRISE Optimistic" },
    });

    resolveFetch({
      ok: true,
      status: 200,
      json: async () => ({
        workspace_id: "ws-workbench",
        doc_key: "mdm",
        content: SAMPLE.replace("title: Legal entity", "title: ENTERPRISE Optimistic"),
        base_digest: "sha256:x",
        updated_by: "dev",
      }),
    });
    await waitFor(() => expect(onDocument).toHaveBeenCalled());
  });
});
