import { useMutation } from "@tanstack/react-query";
import { Link, useParams } from "react-router-dom";
import { api, setLastJobId } from "../api/client";
import { StatusBadge } from "../components/StatusBadge";
import { useImplementation } from "../model/useImplementation";

const WS_ID = "ws-workbench";

export function ValidationPage() {
  const { slug = "" } = useParams();
  const { asset, isLoading, error } = useImplementation(slug);

  const run = useMutation({
    mutationFn: async () => {
      if (!asset) throw new Error("implementation not resolved");
      await api.createWorkspace({ id: WS_ID, name: "Workbench" });
      const key = `validate-${asset.id}-${Date.now()}`;
      const job = await api.createJob(
        {
          kind: "validate",
          workspace_id: WS_ID,
          implementation_id: asset.id,
        },
        key,
      );
      setLastJobId(job.id);
      return api.getJob(job.id);
    },
  });

  if (isLoading) {
    return (
      <section>
        <h1>Validation report</h1>
        <p className="lede">Loading…</p>
      </section>
    );
  }

  if (error || !asset) {
    return (
      <section>
        <h1>Validation report</h1>
        <p className="error">{error?.message || `Unknown model “${slug}”`}</p>
        <Link to="/models">Back</Link>
      </section>
    );
  }

  return (
    <section>
      <h1>Validation report</h1>
      <p className="lede">
        Synchronous validate job for <code>{asset.slug}</code> via{" "}
        <code>POST /jobs</code>.
      </p>

      <div className="row">
        <button
          type="button"
          className="primary"
          onClick={() => run.mutate()}
          disabled={run.isPending}
        >
          Run validate
        </button>
        <Link to={`/models/${asset.slug}`}>Back to model</Link>
      </div>

      {run.isError && (
        <p className="error">{(run.error as Error).message}</p>
      )}

      {run.data && (
        <div className="panel">
          <div className="row">
            <strong>Job</strong>
            <code>{run.data.id}</code>
            <StatusBadge status={run.data.status} />
          </div>
          <p>
            <strong>Summary</strong>
            <br />
            {run.data.result_summary}
          </p>
          <p className="lede">
            Workspace <code>{run.data.workspace_id}</code> · finished{" "}
            {run.data.finished_at || "—"}
          </p>
        </div>
      )}
    </section>
  );
}
