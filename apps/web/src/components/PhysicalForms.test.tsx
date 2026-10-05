import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import {
  cleanup,
  fireEvent,
  render,
  screen,
  waitFor,
} from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import { PhysicalForms } from "./PhysicalForms";

const SAMPLE = `
physical_objects:
  - element_id: dams:physical/mdm/client-topic
    name: client_changed_topic
    title: Client topic
    object_kind: topic
    physical_fields:
      - element_id: dams:physical/mdm/client-topic/client_id
        name: client_id
        native_type: string
        required: true
`;

describe("PhysicalForms", () => {
  afterEach(() => {
    cleanup();
    vi.restoreAllMocks();
  });

  it("lists physical objects and mutates", async () => {
    const onDocument = vi.fn();
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      status: 200,
      json: async () => ({
        workspace_id: "ws-workbench",
        doc_key: "mdm",
        content: SAMPLE,
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
        <PhysicalForms
          workspaceId="ws-workbench"
          implementationId="moex:implementation:mdm:0.1.0"
          idNamespace="mdm"
          content={SAMPLE}
          onDocument={onDocument}
        />
      </QueryClientProvider>,
    );

    expect(screen.getByTestId("physical-object-list").textContent).toContain(
      "dams:physical/mdm/client-topic",
    );

    fireEvent.change(
      screen.getByDisplayValue("dams:physical/mdm/new-object"),
      { target: { value: "dams:physical/mdm/orders" } },
    );
    fireEvent.change(screen.getByDisplayValue("new_object"), {
      target: { value: "orders" },
    });
    fireEvent.click(screen.getByRole("button", { name: /^add object$/i }));

    await waitFor(() => expect(onDocument).toHaveBeenCalled());
    expect(fetchMock).toHaveBeenCalledWith(
      "/api/workspaces/ws-workbench/documents/moex%3Aimplementation%3Amdm%3A0.1.0/mutations",
      expect.objectContaining({ method: "POST" }),
    );
  });
});
