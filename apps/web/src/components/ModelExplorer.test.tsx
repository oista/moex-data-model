import { cleanup, fireEvent, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import { ModelExplorer } from "./ModelExplorer";

const SAMPLE = `
conceptual_entities:
  - element_id: dams:concept/Client
    name: Client
domain_contexts:
  - element_id: dams:context/trading
    name: TradingContext
logical_entities:
  - element_id: dams:logical/trading/Client
    name: TradingClient
    attributes:
      - element_id: dams:logical/trading/Client/clientId
        name: clientId
relationships:
  - element_id: dams:rel/trading/X
    name: x
physical_objects:
  - element_id: dams:physical/trading/topic
    name: topic
    physical_fields:
      - element_id: dams:physical/trading/topic/id
        name: id
mappings:
  - element_id: dams:mapping/trading/m
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
      screen.getByTestId("explorer-node-dams:logical/trading/Client/clientId"),
    );
    expect(onSelect).toHaveBeenCalledWith({
      elementId: "dams:logical/trading/Client/clientId",
      kind: "logical_attribute",
      tab: "entities",
    });
  });
});
