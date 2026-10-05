import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import { ModelExplorer } from "./ModelExplorer";

const SAMPLE = `
conceptual_entities:
  - element_id: dams:concept/ENTERPRISE
    name: ENTERPRISE
domain_contexts:
  - element_id: dams:context/mdm
    name: TradingContext
logical_entities:
  - element_id: dams:logical/mdm/ENTERPRISE
    name: ENTERPRISE
    attributes:
      - element_id: dams:logical/mdm/ENTERPRISE/ENTERPRISE_ID
        name: clientId
relationships:
  - element_id: dams:rel/mdm/X
    name: x
physical_objects:
  - element_id: dams:physical/mdm/topic
    name: topic
    physical_fields:
      - element_id: dams:physical/mdm/topic/id
        name: id
mappings:
  - element_id: dams:mapping/mdm/m
    name: m
`;

describe("ModelExplorer", () => {
  afterEach(() => {
    cleanup();
  });

  it("renders groups and selects logical attribute into entities tab", () => {
    const onSelect = vi.fn();
    render(<ModelExplorer content={SAMPLE} onSelect={onSelect} />);

    expect(screen.getByTestId("model-explorer").textContent).toContain(
      "Logical entities",
    );
    expect(screen.getByTestId("model-explorer").textContent).toContain(
      "Mappings",
    );

    fireEvent.click(
      screen.getByTestId("explorer-node-dams:logical/mdm/ENTERPRISE/ENTERPRISE_ID"),
    );
    expect(onSelect).toHaveBeenCalledWith({
      elementId: "dams:logical/mdm/ENTERPRISE/ENTERPRISE_ID",
      kind: "logical_attribute",
      tab: "entities",
    });
  });
});
