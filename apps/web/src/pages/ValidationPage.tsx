import { useMutation } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import { api, setLastJobId } from "../api/client";
import { StatusBadge } from "../components/StatusBadge";

const WS_ID = "ws-workbench";
const IMPL = "moex:implementation:trading:1.0.0";

export function ValidationPage() {
  const run = useMutation({
    mutationFn: async () => {
      await api.createWorkspace({ id: WS_ID, name: "Workbench" });
      const key = `validate-${IMPL}-${Date.now()}`;
      const job = await api.createJob(
        {
          kind: "validate",
          workspace_id: WS_ID,
          implementation_id: IMPL,
        },
        key,
      );
      setLastJobId(job.id);
      return api.getJob(job.id);
    },
  });

  return (
    <section>
      <h1>Validation report</h1>
      <p className="lede">
        Synchronous validate job for trading via <code>POST /jobs</code>.
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
        <Link to="/models/trading">Back to model</Link>
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
