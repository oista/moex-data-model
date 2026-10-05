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
  - element_id: dams:logical/mdm/ENTERPRISE
    name: ENTERPRISE
    attributes:
      - element_id: dams:logical/mdm/ENTERPRISE/ENTERPRISE_ID
        name: clientId
data_carriers:
  - element_id: dams:physical/mdm/topic
    asset_kind: stream_topic
    physical_fields:
      - element_id: dams:physical/mdm/topic/id
        carrier_ref: dams:physical/mdm/topic
mappings:
  - element_id: dams:mapping/mdm/map_ENTERPRISE_ENTERPRISE_ID
    name: map_client_id
    description: existing
    source_refs:
      - dams:logical/mdm/ENTERPRISE/ENTERPRISE_ID
    target_refs:
      - dams:physical/mdm/topic/id
    mapping_type: field_mapping
    mapping_cardinality: one_to_one
`;

function mockDoc(content: string) {
  return {
    ok: true,
    status: 200,
    json: async () => ({
      workspace_id: "ws-workbench",
      doc_key: "mdm",
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
          implementationId="moex:implementation:mdm:0.1.0"
          idNamespace="mdm"
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
      "dams:logical/mdm/ENTERPRISE",
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
          implementationId="moex:implementation:mdm:0.1.0"
          idNamespace="mdm"
          content={SAMPLE}
          onDocument={onDocument}
        />
      </QueryClientProvider>,
    );

    expect(screen.getByTestId("mapping-list").textContent).toContain(
      "dams:mapping/mdm/map_ENTERPRISE_ENTERPRISE_ID",
    );
    fireEvent.click(screen.getByTestId("delete-mapping"));

    await waitFor(() => expect(onDocument).toHaveBeenCalled());
    const body = JSON.parse(fetchMock.mock.calls[0][1].body as string);
    expect(body).toMatchObject({
      op: "delete_mapping",
      element_id: "dams:mapping/mdm/map_ENTERPRISE_ENTERPRISE_ID",
    });
  });
});
