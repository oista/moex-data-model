import { EntityForms } from "./EntityForms";
import { MappingForms } from "./MappingForms";
import { PhysicalForms } from "./PhysicalForms";
import { RelationshipForms } from "./RelationshipForms";
import type { DocumentMutation, WorkspaceDocument } from "../api/types";

export type FormsTab =
  | "entities"
  | "relationships"
  | "mappings"
  | "physical";

type Props = {
  workspaceId: string;
  content: string;
  onDocument: (doc: WorkspaceDocument) => void;
  onBeforeMutate?: () => Promise<void>;
  onOptimisticOp?: (op: DocumentMutation) => void;
  onOptimisticRollback?: () => void;
  disabled?: boolean;
  activeTab: FormsTab;
  onTabChange: (tab: FormsTab) => void;
  focusElementId?: string | null;
};

export function ModelFormsPanel({
  workspaceId,
  content,
  onDocument,
  onBeforeMutate,
  onOptimisticOp,
  onOptimisticRollback,
  disabled = false,
  activeTab,
  onTabChange,
  focusElementId = null,
}: Props) {
  const formProps = {
    workspaceId,
    content,
    onDocument,
    onBeforeMutate,
    onOptimisticOp,
    onOptimisticRollback,
    disabled,
    focusElementId,
  };

  return (
    <div className="model-forms-panel" data-testid="model-forms-panel">
      <div className="form-tabs" role="tablist" data-testid="form-tabs">
        {(
          [
            ["entities", "Entities"],
            ["relationships", "Relationships"],
            ["mappings", "Mappings"],
            ["physical", "Physical"],
          ] as const
        ).map(([id, label]) => (
          <button
            key={id}
            type="button"
            role="tab"
            aria-selected={activeTab === id}
            className={activeTab === id ? "form-tab active" : "form-tab"}
            data-testid={`form-tab-${id}`}
            onClick={() => onTabChange(id)}
            disabled={disabled}
          >
            {label}
          </button>
        ))}
      </div>
      {activeTab === "entities" && <EntityForms {...formProps} />}
      {activeTab === "relationships" && <RelationshipForms {...formProps} />}
      {activeTab === "mappings" && <MappingForms {...formProps} />}
      {activeTab === "physical" && <PhysicalForms {...formProps} />}
    </div>
  );
}
