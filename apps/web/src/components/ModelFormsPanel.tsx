import { EntityForms } from "./EntityForms";
import { MappingForms } from "./MappingForms";
import { RelationshipForms } from "./RelationshipForms";
import type { WorkspaceDocument } from "../api/types";

export type FormsTab = "entities" | "relationships" | "mappings";

type Props = {
  workspaceId: string;
  content: string;
  onDocument: (doc: WorkspaceDocument) => void;
  onBeforeMutate?: () => Promise<void>;
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
  disabled = false,
  activeTab,
  onTabChange,
  focusElementId = null,
}: Props) {
  return (
    <div className="model-forms-panel" data-testid="model-forms-panel">
      <div className="form-tabs" role="tablist" data-testid="form-tabs">
        {(
          [
            ["entities", "Entities"],
            ["relationships", "Relationships"],
            ["mappings", "Mappings"],
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
      {activeTab === "entities" && (
        <EntityForms
          workspaceId={workspaceId}
          content={content}
          onDocument={onDocument}
          onBeforeMutate={onBeforeMutate}
          disabled={disabled}
          focusElementId={focusElementId}
        />
      )}
      {activeTab === "relationships" && (
        <RelationshipForms
          workspaceId={workspaceId}
          content={content}
          onDocument={onDocument}
          onBeforeMutate={onBeforeMutate}
          disabled={disabled}
          focusElementId={focusElementId}
        />
      )}
      {activeTab === "mappings" && (
        <MappingForms
          workspaceId={workspaceId}
          content={content}
          onDocument={onDocument}
          onBeforeMutate={onBeforeMutate}
          disabled={disabled}
          focusElementId={focusElementId}
        />
      )}
    </div>
  );
}
