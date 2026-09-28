import { describe, expect, it } from "vitest";
import { applyMutationOptimistic } from "./yamlMutate";

const SAMPLE = `element_id: dams:model/trading/1.0.0
name: trading_solution_model
logical_entities:
  - element_id: dams:logical/trading/Client
    name: TradingClient
    title: Client
    attributes:
      - element_id: dams:logical/trading/Client/clientId
        name: clientId
        logical_type: identifier
        required: true
physical_objects:
  - element_id: dams:physical/trading/client-topic
    name: client_changed_topic
    object_kind: topic
    physical_fields:
      - element_id: dams:physical/trading/client-topic/client_id
        name: client_id
        native_type: string
        required: true
`;

describe("applyMutationOptimistic", () => {
  it("updates logical entity title", () => {
    const out = applyMutationOptimistic(SAMPLE, {
      op: "update_logical_entity",
      element_id: "dams:logical/trading/Client",
      patch: { title: "Client Renamed" },
    });
    expect(out).toContain("Client Renamed");
    expect(out).toContain("dams:logical/trading/Client");
  });

  it("adds physical object and field", () => {
    const withObj = applyMutationOptimistic(SAMPLE, {
      op: "add_physical_object",
      physical_object: {
        element_id: "dams:physical/trading/orders",
        name: "orders_table",
        object_kind: "table",
      },
    });
    expect(withObj).toContain("dams:physical/trading/orders");
    const withField = applyMutationOptimistic(withObj, {
      op: "add_physical_field",
      owner_element_id: "dams:physical/trading/orders",
      physical_field: {
        element_id: "dams:physical/trading/orders/id",
        name: "id",
        native_type: "uuid",
      },
    });
    expect(withField).toContain("dams:physical/trading/orders/id");
    expect(withField).toContain("native_type: uuid");
  });

  it("deletes physical field", () => {
    const out = applyMutationOptimistic(SAMPLE, {
      op: "delete_physical_field",
      element_id: "dams:physical/trading/client-topic/client_id",
    });
    expect(out).not.toContain("dams:physical/trading/client-topic/client_id");
  });
});
