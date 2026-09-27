import { useMutation, useQuery } from "@tanstack/react-query";
import { useState, type FormEvent } from "react";
import { Link, useParams } from "react-router-dom";
import { api } from "../api/client";
import { StatusBadge } from "../components/StatusBadge";

export function ModelDetailPage() {
  const { slug = "trading" } = useParams();
  const [q, setQ] = useState("Client");
  const [hits, setHits] = useState<
    Awaited<ReturnType<typeof api.searchIndex>> | null
  >(null);

  const conformance = useQuery({
    queryKey: ["conformance", slug],
    queryFn: api.tradingConformance,
    enabled: slug === "trading",
  });

  const rebuild = useMutation({
    mutationFn: api.rebuildIndex,
    onSuccess: async () => {
      setHits(await api.searchIndex(q));
    },
  });

  async function onSearch(e: FormEvent) {
    e.preventDefault();
    setHits(await api.searchIndex(q));
  }

  if (slug !== "trading") {
    return (
      <section>
        <h1>Unknown model</h1>
        <p className="lede">Only trading is wired in this MVP.</p>
        <Link to="/models">Back</Link>
      </section>
    );
  }

  return (
    <section>
      <h1>Trading platform</h1>
      <p className="lede">Conformance and searchable model index.</p>

      <div className="panel">
        <div className="row">
          <strong>Conformance</strong>
          {conformance.isLoading && <span className="badge neutral">…</span>}
          {conformance.data && (
            <>
              <StatusBadge status={conformance.data.overall_result} />
              <span>{conformance.data.diagnostic_count} diagnostics</span>
            </>
          )}
          {conformance.isError && (
            <span className="error">{(conformance.error as Error).message}</span>
          )}
        </div>
        <div className="row">
          <Link to="/models/trading/edit">Edit YAML</Link>
          <Link to="/models/trading/validate">Run validation job</Link>
        </div>
      </div>

      <div className="panel">
        <div className="row">
          <button
            type="button"
            className="primary"
            onClick={() => rebuild.mutate()}
            disabled={rebuild.isPending}
          >
            Rebuild index
          </button>
          {rebuild.data && (
            <span>
              {rebuild.data.element_count} elements · rev{" "}
              {rebuild.data.revision}
            </span>
          )}
        </div>
        {rebuild.isError && (
          <p className="error">{(rebuild.error as Error).message}</p>
        )}
        <form className="row" onSubmit={onSearch}>
          <input
            type="text"
            value={q}
            onChange={(e) => setQ(e.target.value)}
            placeholder="Search elements"
          />
          <button type="submit">Search</button>
        </form>
        {hits && (
          <table>
            <thead>
              <tr>
                <th>Element</th>
                <th>Kind</th>
                <th>Name</th>
                <th>Layer</th>
              </tr>
            </thead>
            <tbody>
              {hits.map((h) => (
                <tr key={`${h.element_id}-${h.element_kind}`}>
                  <td>
                    <code>{h.element_id}</code>
                  </td>
                  <td>{h.element_kind}</td>
                  <td>{h.name}</td>
                  <td>{h.layer}</td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </section>
  );
}
