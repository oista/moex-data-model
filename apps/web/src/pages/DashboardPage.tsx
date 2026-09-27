import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import { api, getActor, getLastJobId } from "../api/client";
import { StatusBadge } from "../components/StatusBadge";

export function DashboardPage() {
  const health = useQuery({ queryKey: ["health"], queryFn: api.health });
  const lastJobId = getLastJobId();
  const lastJob = useQuery({
    queryKey: ["job", lastJobId],
    queryFn: () => api.getJob(lastJobId!),
    enabled: Boolean(lastJobId),
  });

  return (
    <section>
      <h1>Dashboard</h1>
      <p className="lede">
        Operational shell over the modeling API. Actor: {getActor()}.
      </p>

      <div className="panel">
        <div className="row">
          <strong>API health</strong>
          {health.isLoading && <span className="badge neutral">loading</span>}
          {health.data && <StatusBadge status={health.data.status} />}
          {health.isError && (
            <span className="error">
              unreachable — start API on :8000 and use Vite proxy
            </span>
          )}
        </div>
      </div>

      <div className="panel">
        <div className="row">
          <strong>Last job</strong>
          {!lastJobId && <span className="badge neutral">none yet</span>}
          {lastJob.data && (
            <>
              <StatusBadge status={lastJob.data.status} />
              <code>{lastJob.data.id}</code>
              <span>{lastJob.data.result_summary}</span>
            </>
          )}
        </div>
      </div>

      <div className="row">
        <Link to="/models">Open models</Link>
        <Link to="/workspaces">Workspaces</Link>
        <Link to="/models/trading/validate">Validate trading</Link>
      </div>
    </section>
  );
}
