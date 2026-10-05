import { describe, expect, it } from "vitest";
import { applyMutationOptimistic } from "./yamlMutate";

const SAMPLE = `element_id: dams:model/mdm/0.1.0
name: mdm_solution_model
logical_entities:
  - element_id: dams:logical/mdm/Client
    name: TradingClient
    title: Client
    attributes:
      - element_id: dams:logical/mdm/Client/clientId
        name: clientId
        logical_type: identifier
        required: true
data_carriers:
  - element_id: dams:physical/mdm/client-topic
    name: client_changed_topic
    asset_kind: stream_topic
    physical_fields:
      - element_id: dams:physical/mdm/client-topic/client_id
        name: client_id
        native_type: string
        required: true
        carrier_ref: dams:physical/mdm/client-topic
`;

describe("applyMutationOptimistic", () => {
  it("updates logical entity title", () => {
    const out = applyMutationOptimistic(SAMPLE, {
      op: "update_logical_entity",
      element_id: "dams:logical/mdm/Client",
      patch: { title: "Client Renamed" },
    });
    expect(out).toContain("Client Renamed");
    expect(out).toContain("dams:logical/mdm/Client");
  });

  it("adds data carrier and field", () => {
    const withObj = applyMutationOptimistic(SAMPLE, {
      op: "add_physical_object",
      physical_object: {
        element_id: "dams:physical/mdm/orders",
        name: "orders_table",
        asset_kind: "relational_table",
      },
    });
    expect(withObj).toContain("dams:physical/mdm/orders");
    expect(withObj).toContain("data_carriers:");
    expect(withObj).toContain("asset_kind: relational_table");
    const withField = applyMutationOptimistic(withObj, {
      op: "add_physical_field",
      owner_element_id: "dams:physical/mdm/orders",
      physical_field: {
        element_id: "dams:physical/mdm/orders/id",
        name: "id",
        native_type: "uuid",
      },
    });
    expect(withField).toContain("dams:physical/mdm/orders/id");
    expect(withField).toContain("native_type: uuid");
    expect(withField).toContain("carrier_ref:");
  });

  it("deletes physical field", () => {
    const out = applyMutationOptimistic(SAMPLE, {
      op: "delete_physical_field",
      element_id: "dams:physical/mdm/client-topic/client_id",
    });
    expect(out).not.toContain("dams:physical/mdm/client-topic/client_id");
  });
});
