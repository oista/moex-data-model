import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import {
  cleanup,
  fireEvent,
  render,
  screen,
  waitFor,
} from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import { RelationshipForms } from "./RelationshipForms";
import { MappingForms } from "./MappingForms";

const SAMPLE = `
logical_entities:
  - element_id: dams:logical/trading/Client
    name: TradingClient
    attributes:
      - element_id: dams:logical/trading/Client/clientId
        name: clientId
physical_objects:
  - element_id: dams:physical/trading/topic
    physical_fields:
      - element_id: dams:physical/trading/topic/id
mappings:
  - element_id: dams:mapping/trading/client-id
    name: map_client_id
    description: existing
    source_refs:
      - dams:logical/trading/Client/clientId
    target_refs:
      - dams:physical/trading/topic/id
    mapping_type: field_mapping
    mapping_cardinality: one_to_one
`;

function mockDoc(content: string) {
  return {
    ok: true,
    status: 200,
    json: async () => ({
      workspace_id: "ws-workbench",
      doc_key: "trading",
      content,
      base_digest: "sha256:x",
      updated_by: "dev",
    }),
  };
}

describe("RelationshipForms", () => {
  afterEach(() => {
    cleanup();
    vi.restoreAllMocks();
  });

  it("adds a relationship via mutation", async () => {
    const onDocument = vi.fn();
    const fetchMock = vi.fn().mockResolvedValue(mockDoc(SAMPLE));
    vi.stubGlobal("fetch", fetchMock);

    const qc = new QueryClient({
      defaultOptions: { mutations: { retry: false } },
    });
    render(
      <QueryClientProvider client={qc}>
        <RelationshipForms
          workspaceId="ws-workbench"
          implementationId="moex:implementation:trading:1.0.0"
          idNamespace="trading"
          content={SAMPLE}
          onDocument={onDocument}
        />
      </QueryClientProvider>,
    );

    fireEvent.click(screen.getByRole("button", { name: /^add relationship$/i }));

    await waitFor(() => expect(onDocument).toHaveBeenCalled());
    const body = JSON.parse(fetchMock.mock.calls[0][1].body as string);
    expect(body.op).toBe("add_relationship");
    expect(body.relationship.source_entity_ref).toBe(
      "dams:logical/trading/Client",
    );
  });
});

describe("MappingForms", () => {
  afterEach(() => {
    cleanup();
    vi.restoreAllMocks();
  });

  it("lists mappings and deletes selected", async () => {
    const onDocument = vi.fn();
    const fetchMock = vi.fn().mockResolvedValue(mockDoc(SAMPLE));
    vi.stubGlobal("fetch", fetchMock);
    vi.spyOn(window, "confirm").mockReturnValue(true);

    const qc = new QueryClient({
      defaultOptions: { mutations: { retry: false } },
    });
    render(
      <QueryClientProvider client={qc}>
        <MappingForms
          workspaceId="ws-workbench"
          implementationId="moex:implementation:trading:1.0.0"
          idNamespace="trading"
          content={SAMPLE}
          onDocument={onDocument}
        />
      </QueryClientProvider>,
    );

    expect(screen.getByTestId("mapping-list").textContent).toContain(
      "dams:mapping/trading/client-id",
    );
    fireEvent.click(screen.getByTestId("delete-mapping"));

    await waitFor(() => expect(onDocument).toHaveBeenCalled());
    const body = JSON.parse(fetchMock.mock.calls[0][1].body as string);
    expect(body).toMatchObject({
      op: "delete_mapping",
      element_id: "dams:mapping/trading/client-id",
    });
  });
});
