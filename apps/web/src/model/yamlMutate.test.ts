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
        data_type_ref: dams:datatype/identifier
        required: true
data_carriers:
  - element_id: dams:physical/mdm/client-topic
    name: client_changed_topic
    asset_kind: stream_topic
    structure_ref: dams:structure/mdm/client_changed_topic
data_structures:
  - element_id: dams:structure/mdm/client_changed_topic
    name: client_changed_topic
    schema_format: relational
    root_local_key: root
    nodes:
      - local_key: root
        node_kind: object
        children:
          - client_id
      - local_key: client_id
        node_kind: scalar
        native_name: client_id
        native_type: string
        required: true
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

  it("adds data carrier and schema node", () => {
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
      op: "add_schema_node",
      owner_element_id: "dams:physical/mdm/orders",
      schema_node: {
        name: "id",
        native_type: "uuid",
      },
    });
    expect(withField).toContain("native_type: uuid");
    expect(withField).toContain("data_structures:");
    expect(withField).toContain("structure_ref:");
  });

  it("deletes schema node", () => {
    const out = applyMutationOptimistic(SAMPLE, {
      op: "delete_schema_node",
      element_id: "dams:structure/mdm/client_changed_topic#client_id",
    });
    expect(out).not.toContain("local_key: client_id");
  });
});
