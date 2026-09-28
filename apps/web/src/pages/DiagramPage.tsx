import { useCallback, useEffect, useRef, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { api } from "../api/client";
import type {
  DiagramSubmitResult,
  SemanticDiffReport,
} from "../api/types";

const WS_ID = "ws-workbench";

function drawdbUrl(): string {
  return import.meta.env.VITE_DRAWDB_URL || "http://localhost:5174";
}

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

export function DiagramPage() {
  const [params, setParams] = useSearchParams();
  const profile =
    params.get("profile") === "physical" ? "physical" : "logical";
  const iframeRef = useRef<HTMLIFrameElement>(null);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [dbml, setDbml] = useState("");
  const [bridgeReady, setBridgeReady] = useState(false);
  const [submitResult, setSubmitResult] = useState<DiagramSubmitResult | null>(
    null,
  );
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [applied, setApplied] = useState(false);

  const setProfile = (next: "logical" | "physical") => {
    const nextParams = new URLSearchParams(params);
    nextParams.set("profile", next);
    setParams(nextParams, { replace: true });
  };

  const openSession = useCallback(async () => {
    setError(null);
    setBusy(true);
    setSubmitResult(null);
    setApplied(false);
    try {
      await api.createWorkspace({ id: WS_ID, name: "Workbench" });
      try {
        await api.getDocument(WS_ID);
      } catch {
        const published = await api.tradingBody();
        await api.putDocument(WS_ID, {
          content: published.content,
          base_digest: published.content_digest,
        });
      }
      const session = await api.openDiagram(WS_ID, profile);
      setSessionId(session.session_id);
      setDbml(session.dbml);
      if (iframeRef.current?.contentWindow && bridgeReady) {
        iframeRef.current.contentWindow.postMessage(
          { type: "moex:import-dbml", dbml: session.dbml },
          "*",
        );
      }
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setBusy(false);
    }
  }, [profile, bridgeReady]);

  useEffect(() => {
    void openSession();
  }, [openSession]);

  useEffect(() => {
    function onMessage(event: MessageEvent) {
      const data = event.data;
      if (!data || typeof data !== "object") return;
      if (data.type === "moex:ready") {
        setBridgeReady(true);
        if (dbml && iframeRef.current?.contentWindow) {
          iframeRef.current.contentWindow.postMessage(
            { type: "moex:import-dbml", dbml },
            "*",
          );
        }
      } else if (data.type === "moex:export-dbml" && typeof data.dbml === "string") {
        setDbml(data.dbml);
      }
    }
    window.addEventListener("message", onMessage);
    return () => window.removeEventListener("message", onMessage);
  }, [dbml]);

  const requestExport = () => {
    iframeRef.current?.contentWindow?.postMessage(
      { type: "moex:request-export" },
      "*",
    );
  };

  const pushImport = () => {
    iframeRef.current?.contentWindow?.postMessage(
      { type: "moex:import-dbml", dbml },
      "*",
    );
  };

  const onSubmit = async () => {
    if (!sessionId) return;
    setBusy(true);
    setError(null);
    setApplied(false);
    try {
      requestExport();
      // Allow bridge to reply; fall back to current dbml state
      await new Promise((r) => setTimeout(r, 50));
      const result = await api.submitDiagram(WS_ID, sessionId, dbml);
      setSubmitResult(result);
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setBusy(false);
    }
  };

  const onApply = async () => {
    if (!sessionId) return;
    setBusy(true);
    setError(null);
    try {
      await api.applyDiagram(WS_ID, sessionId);
      setApplied(true);
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setBusy(false);
    }
  };

  const diff: SemanticDiffReport | null = submitResult?.semantic_diff ?? null;

  return (
    <div className="diagram-page">
      <header className="page-header">
        <h1>Diagram</h1>
        <div
          className="row"
          role="group"
          aria-label="Projection profile"
          data-testid="profile-toggle"
        >
          <button
            type="button"
            className={profile === "logical" ? "primary" : undefined}
            aria-pressed={profile === "logical"}
            data-testid="profile-logical"
            onClick={() => setProfile("logical")}
            disabled={busy}
          >
            Logical
          </button>
          <button
            type="button"
            className={profile === "physical" ? "primary" : undefined}
            aria-pressed={profile === "physical"}
            data-testid="profile-physical"
            onClick={() => setProfile("physical")}
            disabled={busy}
          >
            Physical
          </button>
          <span className="badge neutral">profile: {profile}</span>
        </div>
        <div className="actions">
          <button type="button" onClick={() => void openSession()} disabled={busy}>
            Reload projection
          </button>
          <button type="button" onClick={pushImport} disabled={!dbml}>
            Push DBML to editor
          </button>
          <button type="button" onClick={requestExport}>
            Pull DBML from editor
          </button>
          <button type="button" onClick={() => void onSubmit()} disabled={busy || !sessionId}>
            Submit for review
          </button>
          <button
            type="button"
            onClick={() => void onApply()}
            disabled={
              busy ||
              !sessionId ||
              !submitResult ||
              (submitResult.rejected?.length ?? 0) > 0
            }
          >
            Confirm apply
          </button>
          <Link to="/models/trading/edit?reload=1">Open editor</Link>
        </div>
      </header>
      {error && <p className="error">{error}</p>}
      {applied && (
        <p className="ok" data-testid="diagram-applied">
          Applied to workspace draft.{" "}
          <Link to="/models/trading/edit?reload=1">Open editor</Link> to review
          the updated YAML.
        </p>
      )}
      {submitResult && (submitResult.rejected?.length ?? 0) > 0 && (
        <div className="panel" data-testid="diagram-rejected">
          <strong>Rejected operations</strong>
          <ul>
            {submitResult.rejected.map((r, i) => (
              <li key={i}>
                <span className="badge bad">{r.code}</span> {r.message}
                {r.path ? (
                  <>
                    {" "}
                    <code>{r.path}</code>
                  </>
                ) : null}
              </li>
            ))}
          </ul>
        </div>
      )}
      <div className="diagram-layout">
        <iframe
          ref={iframeRef}
          title="drawDB"
          src={drawdbUrl()}
          className="diagram-iframe"
        />
        <aside className="diagram-side">
          <h2>DBML</h2>
          <textarea
            value={dbml}
            onChange={(e) => setDbml(e.target.value)}
            rows={12}
            spellCheck={false}
          />
          {submitResult && (
            <>
              <h2>Submit</h2>
              <p>
                ops={submitResult.op_count} rejected=
                {submitResult.rejected.length}
              </p>
              {submitResult.rejected.length > 0 && (
                <ul data-testid="rejected-list">
                  {submitResult.rejected.map((r, i) => (
                    <li key={i}>
                      <span className="badge bad">{r.code}</span> {r.message}
                    </li>
                  ))}
                </ul>
              )}
            </>
          )}
          {diff && (
            <>
              <h2>Semantic diff</h2>
              <p>
                {diff.has_breaking ? (
                  <span className="badge bad">breaking</span>
                ) : (
                  <span className="badge ok">no breaking</span>
                )}{" "}
                {diff.changes.length} change(s)
              </p>
              <ul>
                {diff.changes.map((c, i) => (
                  <li key={i}>
                    <span className={categoryBadgeClass(c.category)}>
                      {c.category}
                    </span>{" "}
                    {c.message}
                  </li>
                ))}
              </ul>
            </>
          )}
        </aside>
      </div>
    </div>
  );
}
