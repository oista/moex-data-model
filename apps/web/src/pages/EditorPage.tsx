import Editor from "@monaco-editor/react";
import { useMutation } from "@tanstack/react-query";
import { useCallback, useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api, setLastJobId } from "../api/client";
import type {
  Job,
  Publication,
  SemanticDiffReport,
  WorkspaceDocument,
} from "../api/types";
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

const WS_ID = "ws-workbench";
const IMPL = "moex:implementation:trading:1.0.0";

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
  const [value, setValue] = useState("");
  const [baseDigest, setBaseDigest] = useState("");
  const [dirty, setDirty] = useState(false);
  const [sourceLabel, setSourceLabel] = useState<"draft" | "published" | "">("");
  const [loadError, setLoadError] = useState<string | null>(null);
  const [job, setJob] = useState<Job | null>(null);
  const [publication, setPublication] = useState<Publication | null>(null);
  const [diff, setDiff] = useState<SemanticDiffReport | null>(null);
  const [loading, setLoading] = useState(true);
  const [formsTab, setFormsTab] = useState<FormsTab>("entities");
  const [focusElementId, setFocusElementId] = useState<string | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    setLoadError(null);
    try {
      await api.createWorkspace({ id: WS_ID, name: "Workbench" });
      try {
        const draft = await api.getDocument(WS_ID);
        setValue(draft.content);
        setBaseDigest(draft.base_digest);
        setSourceLabel("draft");
      } catch {
        const published = await api.tradingBody();
        setValue(published.content);
        setBaseDigest(published.content_digest);
        setSourceLabel("published");
      }
      setDirty(false);
    } catch (err) {
      setLoadError((err as Error).message);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void load();
  }, [load]);

  const save = useMutation({
    mutationFn: () =>
      api.putDocument(WS_ID, { content: value, base_digest: baseDigest }),
    onSuccess: (doc) => {
      setBaseDigest(doc.base_digest);
      setSourceLabel("draft");
      setDirty(false);
    },
  });

  const reloadPublished = useMutation({
    mutationFn: async () => {
      if (dirty && !window.confirm("Discard unsaved changes?")) {
        return null;
      }
      return api.tradingBody();
    },
    onSuccess: (body) => {
      if (!body) return;
      setValue(body.content);
      setBaseDigest(body.content_digest);
      setSourceLabel("published");
      setDirty(false);
    },
  });

  const validate = useMutation({
    mutationFn: async () => {
      await api.putDocument(WS_ID, { content: value, base_digest: baseDigest });
      setDirty(false);
      setSourceLabel("draft");
      const result = await api.createJob(
        {
          kind: "validate",
          workspace_id: WS_ID,
          implementation_id: IMPL,
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
      const result = await api.createJob(
        {
          kind: "compile",
          workspace_id: WS_ID,
          implementation_id: IMPL,
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
      await api.putDocument(WS_ID, { content: value, base_digest: baseDigest });
      setDirty(false);
      setSourceLabel("draft");
      return api.previewSemanticDiff(WS_ID);
    },
    onSuccess: setDiff,
  });

  const publish = useMutation({
    mutationFn: async () => {
      await api.putDocument(WS_ID, { content: value, base_digest: baseDigest });
      setDirty(false);
      setSourceLabel("draft");
      return api.createPublication(
        {
          workspace_id: WS_ID,
          implementation_id: IMPL,
          title: "Workbench publish trading draft",
          base_ref: "HEAD",
        },
        `publish-${Date.now()}`,
      );
    },
    onSuccess: setPublication,
  });

  function onMutatedDocument(doc: WorkspaceDocument) {
    setValue(doc.content);
    setBaseDigest(doc.base_digest);
    setSourceLabel("draft");
    setDirty(false);
  }

  const ensureSaved = useCallback(async () => {
    if (!dirty) return;
    const doc = await api.putDocument(WS_ID, {
      content: value,
      base_digest: baseDigest,
    });
    setBaseDigest(doc.base_digest);
    setSourceLabel("draft");
    setDirty(false);
  }, [dirty, value, baseDigest]);

  const formsBusy =
    loading ||
    save.isPending ||
    validate.isPending ||
    compile.isPending ||
    reviewChanges.isPending ||
    publish.isPending;

  return (
    <section>
      <h1>Edit trading YAML</h1>
      <p className="lede">
        Monaco draft in workspace <code>{WS_ID}</code>. Git published file is
        not overwritten. Forms apply controlled mutations to the draft.
      </p>

      <div className="row">
        <button
          type="button"
          className="primary"
          onClick={() => save.mutate()}
          disabled={loading || save.isPending || !value}
        >
          Save draft
        </button>
        <button
          type="button"
          onClick={() => reloadPublished.mutate()}
          disabled={loading || reloadPublished.isPending}
        >
          Reload published
        </button>
        <button
          type="button"
          onClick={() => validate.mutate()}
          disabled={loading || validate.isPending || !value}
        >
          Validate draft
        </button>
        <button
          type="button"
          onClick={() => compile.mutate()}
          disabled={loading || compile.isPending}
          data-testid="compile-job"
        >
          Compile
        </button>
        <button
          type="button"
          onClick={() => reviewChanges.mutate()}
          disabled={loading || reviewChanges.isPending || !value}
          data-testid="review-changes"
        >
          Review changes
        </button>
        <button
          type="button"
          onClick={() => publish.mutate()}
          disabled={loading || publish.isPending || !value}
        >
          Publish draft
        </button>
        <Link to="/models/trading">Back to model</Link>
        {sourceLabel && (
          <span className="badge neutral">loaded: {sourceLabel}</span>
        )}
        {dirty && <span className="badge neutral">unsaved</span>}
      </div>

      {loadError && <p className="error">{loadError}</p>}
      {save.isError && (
        <p className="error">{(save.error as Error).message}</p>
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
        {!loading && (
          <div className="editor-sidebar">
            <ModelExplorer
              content={value}
              selectedId={focusElementId}
              onSelect={(sel: ExplorerSelect) => {
                setFocusElementId(sel.elementId);
                if (sel.tab) setFormsTab(sel.tab);
              }}
            />
            <ModelFormsPanel
              workspaceId={WS_ID}
              content={value}
              onDocument={onMutatedDocument}
              onBeforeMutate={ensureSaved}
              disabled={formsBusy}
              activeTab={formsTab}
              onTabChange={setFormsTab}
              focusElementId={focusElementId}
            />
          </div>
        )}
        <div className="editor-frame">
          {loading ? (
            <p>Loading…</p>
          ) : (
            <Editor
              height="60vh"
              defaultLanguage="yaml"
              theme="vs-light"
              value={value}
              onChange={(next) => {
                setValue(next ?? "");
                setDirty(true);
              }}
              options={{
                minimap: { enabled: false },
                fontSize: 13,
                wordWrap: "on",
                scrollBeyondLastLine: false,
              }}
            />
          )}
        </div>
      </div>
    </section>
  );
}
