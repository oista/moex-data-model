import Editor from "@monaco-editor/react";
import { useMutation } from "@tanstack/react-query";
import { useState } from "react";
import { Link, useParams } from "react-router-dom";
import { api, setLastJobId } from "../api/client";
import type { Job, Publication, SemanticDiffReport } from "../api/types";
import {
  ModelFormsPanel,
  type FormsTab,
} from "../components/ModelFormsPanel";
import {
  ModelExplorer,
  type ExplorerSelect,
} from "../components/ModelExplorer";
import { ArtifactsPanel } from "../components/ArtifactsPanel";
import { StatusBadge } from "../components/StatusBadge";
import { useImplementation } from "../model/useImplementation";
import { useModelDraft } from "../model/useModelDraft";

const WS_ID = "ws-workbench";

function categoryBadgeClass(category: string): string {
  if (category === "breaking") return "badge bad";
  if (
    category === "backward_compatible" ||
    category === "non_breaking"
  ) {
    return "badge ok";
  }
  return "badge neutral";
}

export function EditorPage() {
  const { slug = "" } = useParams();
  const { asset, editable, isLoading: implLoading, error: implError } =
    useImplementation(slug);
  const draft = useModelDraft(WS_ID, asset?.id);
  const [job, setJob] = useState<Job | null>(null);
  const [publication, setPublication] = useState<Publication | null>(null);
  const [diff, setDiff] = useState<SemanticDiffReport | null>(null);
  const [formsTab, setFormsTab] = useState<FormsTab>("entities");
  const [focusElementId, setFocusElementId] = useState<string | null>(null);
  const [saveError, setSaveError] = useState<string | null>(null);

  const save = useMutation({
    mutationFn: () => draft.putNow(),
    onError: (err) => setSaveError((err as Error).message),
    onSuccess: () => setSaveError(null),
  });

  const reloadPublished = useMutation({
    mutationFn: async () => {
      if (!asset) return null;
      if (draft.dirty && !window.confirm("Discard unsaved changes?")) {
        return null;
      }
      return api.implementationBody(asset.id);
    },
    onSuccess: (body) => {
      if (!body) return;
      draft.discardToPublished(body.content, body.content_digest);
    },
  });

  const validate = useMutation({
    mutationFn: async () => {
      if (!asset) throw new Error("implementation not resolved");
      await draft.putNow();
      const result = await api.createJob(
        {
          kind: "validate",
          workspace_id: WS_ID,
          implementation_id: asset.id,
          source: "draft",
        },
        `validate-draft-${Date.now()}`,
      );
      setLastJobId(result.id);
      return api.getJob(result.id);
    },
    onSuccess: setJob,
  });

  const compile = useMutation({
    mutationFn: async () => {
      if (!asset) throw new Error("implementation not resolved");
      const result = await api.createJob(
        {
          kind: "compile",
          workspace_id: WS_ID,
          implementation_id: asset.id,
          source: "published",
        },
        `compile-${Date.now()}`,
      );
      setLastJobId(result.id);
      return api.getJob(result.id);
    },
    onSuccess: setJob,
  });

  const reviewChanges = useMutation({
    mutationFn: async () => {
      if (!asset) throw new Error("implementation not resolved");
      await draft.putNow();
      return api.previewSemanticDiff(WS_ID, asset.id);
    },
    onSuccess: setDiff,
  });

  const publish = useMutation({
    mutationFn: async () => {
      if (!asset) throw new Error("implementation not resolved");
      await draft.putNow();
      return api.createPublication(
        {
          workspace_id: WS_ID,
          implementation_id: asset.id,
          title: `Workbench publish ${asset.slug} draft`,
          base_ref: "HEAD",
        },
        `publish-${Date.now()}`,
      );
    },
    onSuccess: setPublication,
  });

  const formsBusy =
    save.isPending ||
    validate.isPending ||
    reviewChanges.isPending ||
    publish.isPending;

  const formsDisabled = formsBusy || Boolean(draft.parseError);

  if (implLoading) {
    return (
      <section>
        <h1>Model editor</h1>
        <p className="lede">Loading…</p>
      </section>
    );
  }

  if (implError || !asset) {
    return (
      <section>
        <h1>Model editor</h1>
        <p className="error">{implError?.message || `Unknown model “${slug}”`}</p>
        <Link to="/models">Back</Link>
      </section>
    );
  }

  if (!editable) {
    return (
      <section>
        <h1>{asset.title}</h1>
        <p className="lede">
          Not editable in Workbench (requires LinkML DAMS data model).
        </p>
        <Link to={`/models/${asset.slug}`}>Back to model</Link>
      </section>
    );
  }

  return (
    <section>
      <h1>Model editor — {asset.title}</h1>
      <p className="lede">
        Edit workspace draft YAML, validate/compile via jobs, review semantic
        diff, or publish a GitHub review from the draft.
      </p>
      <div className="actions">
        <button
          type="button"
          className="primary"
          onClick={() => save.mutate()}
          disabled={draft.loading || save.isPending || !draft.dirty}
        >
          Save draft
        </button>
        <button
          type="button"
          onClick={() => reloadPublished.mutate()}
          disabled={draft.loading || reloadPublished.isPending}
        >
          Reload published
        </button>
        <button
          type="button"
          onClick={() => validate.mutate()}
          disabled={draft.loading || validate.isPending || !draft.content}
        >
          Validate draft
        </button>
        <button
          type="button"
          onClick={() => compile.mutate()}
          disabled={draft.loading || compile.isPending}
          data-testid="compile-job"
        >
          Compile
        </button>
        <button
          type="button"
          onClick={() => reviewChanges.mutate()}
          disabled={draft.loading || reviewChanges.isPending || !draft.content}
          data-testid="review-changes"
        >
          Review changes
        </button>
        <button
          type="button"
          onClick={() => publish.mutate()}
          disabled={draft.loading || publish.isPending || !draft.content}
        >
          Publish draft
        </button>
        <Link to={`/models/${asset.slug}`}>Back to model</Link>
        <Link to={`/models/${asset.slug}/diagram?profile=logical`}>
          Open diagram
        </Link>
        {draft.sourceLabel && (
          <span className="badge neutral">loaded: {draft.sourceLabel}</span>
        )}
        {draft.dirty && <span className="badge neutral">unsaved</span>}
      </div>

      {draft.loadError && <p className="error">{draft.loadError}</p>}
      {draft.parseError && (
        <p className="error" data-testid="draft-parse-error">
          YAML parse error — forms disabled until YAML is valid:{" "}
          {draft.parseError}
        </p>
      )}
      {(save.isError || saveError) && (
        <p className="error">
          {saveError || (save.error as Error).message}
        </p>
      )}
      {validate.isError && (
        <p className="error">{(validate.error as Error).message}</p>
      )}
      {compile.isError && (
        <p className="error">{(compile.error as Error).message}</p>
      )}
      {reviewChanges.isError && (
        <p className="error">{(reviewChanges.error as Error).message}</p>
      )}
      {publish.isError && (
        <p className="error">{(publish.error as Error).message}</p>
      )}

      {job && (
        <div className="panel">
          <div className="row">
            <strong>Job</strong>
            <code>{job.id}</code>
            <StatusBadge status={job.status} />
          </div>
          <p>{job.result_summary}</p>
        </div>
      )}

      {job?.kind === "compile" && job.status === "succeeded" && (
        <ArtifactsPanel jobId={job.id} />
      )}

      {diff && (
        <div className="panel" data-testid="semantic-diff-result">
          <div className="row">
            <strong>Semantic diff</strong>
            <span className="badge neutral">
              {diff.base_label} → {diff.target_label}
            </span>
            {diff.has_breaking ? (
              <span className="badge bad">breaking</span>
            ) : (
              <span className="badge ok">no breaking</span>
            )}
          </div>
          <p className="lede" style={{ marginBottom: "0.5rem" }}>
            {diff.changes.length === 0
              ? "No semantic changes versus published."
              : Object.entries(diff.counts)
                  .filter(([, n]) => n > 0)
                  .map(([cat, n]) => `${cat}: ${n}`)
                  .join(" · ")}
          </p>
          {diff.changes.length > 0 && (
            <ul className="diff-list">
              {diff.changes.map((change, idx) => (
                <li key={`${change.change_code}-${change.subject_ref}-${idx}`}>
                  <span className={categoryBadgeClass(change.category)}>
                    {change.category}
                  </span>{" "}
                  <code>{change.change_code}</code>{" "}
                  {change.subject_ref && (
                    <code className="diff-subject">{change.subject_ref}</code>
                  )}
                  <div>{change.message}</div>
                </li>
              ))}
            </ul>
          )}
        </div>
      )}

      {publication && (
        <div className="panel" data-testid="publication-result">
          <div className="row">
            <strong>Publication</strong>
            <code>{publication.id}</code>
            <StatusBadge status={publication.status} />
          </div>
          <p className="lede" style={{ marginBottom: "0.35rem" }}>
            Branch <code>{publication.branch_name}</code> · commit{" "}
            <code>{publication.commit_sha.slice(0, 12)}</code>
          </p>
          <p>
            Review:{" "}
            <a href={publication.review_url}>{publication.review_url}</a>
          </p>
        </div>
      )}

      <div className="editor-layout">
        {!draft.loading && (
          <div className="editor-sidebar">
            <ModelExplorer
              content={draft.content}
              selectedId={focusElementId}
              onSelect={(sel: ExplorerSelect) => {
                setFocusElementId(sel.elementId);
                if (sel.tab) setFormsTab(sel.tab);
              }}
            />
            <ModelFormsPanel
              workspaceId={WS_ID}
              implementationId={asset.id}
              idNamespace={asset.slug}
              content={draft.content}
              onDocument={draft.replaceFromServer}
              onBeforeMutate={draft.ensureSaved}
              onOptimisticOp={draft.applyLocalOp}
              onOptimisticRollback={draft.rollbackOptimistic}
              disabled={formsDisabled}
              activeTab={formsTab}
              onTabChange={setFormsTab}
              focusElementId={focusElementId}
            />
          </div>
        )}
        <div className="editor-main">
          {draft.loading ? (
            <p>Loading draft…</p>
          ) : (
            <Editor
              height="70vh"
              defaultLanguage="yaml"
              value={draft.content}
              onChange={(v) => draft.setContentFromMonaco(v ?? "")}
              options={{
                minimap: { enabled: false },
                fontSize: 13,
                wordWrap: "on",
              }}
            />
          )}
        </div>
      </div>
    </section>
  );
}
