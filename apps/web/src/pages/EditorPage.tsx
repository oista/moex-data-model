import Editor from "@monaco-editor/react";
import { useMutation } from "@tanstack/react-query";
import { useCallback, useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api, setLastJobId } from "../api/client";
import type { Job, WorkspaceDocument } from "../api/types";
import { EntityForms } from "../components/EntityForms";
import { StatusBadge } from "../components/StatusBadge";

const WS_ID = "ws-workbench";
const IMPL = "moex:implementation:trading:1.0.0";

export function EditorPage() {
  const [value, setValue] = useState("");
  const [baseDigest, setBaseDigest] = useState("");
  const [dirty, setDirty] = useState(false);
  const [sourceLabel, setSourceLabel] = useState<"draft" | "published" | "">("");
  const [loadError, setLoadError] = useState<string | null>(null);
  const [job, setJob] = useState<Job | null>(null);
  const [loading, setLoading] = useState(true);

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

  function onMutatedDocument(doc: WorkspaceDocument) {
    setValue(doc.content);
    setBaseDigest(doc.base_digest);
    setSourceLabel("draft");
    setDirty(false);
  }

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

      <div className="editor-layout">
        {!loading && (
          <EntityForms
            workspaceId={WS_ID}
            content={value}
            onDocument={onMutatedDocument}
          />
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
