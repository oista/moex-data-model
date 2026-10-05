import { useMutation, useQuery } from "@tanstack/react-query";
import { useState, type FormEvent } from "react";
import { Link, useParams } from "react-router-dom";
import { api } from "../api/client";
import { StatusBadge } from "../components/StatusBadge";
import { useImplementation } from "../model/useImplementation";

export function ModelDetailPage() {
  const { slug = "" } = useParams();
  const { asset, editable, isLoading, error } = useImplementation(slug);
  const [q, setQ] = useState("");
  const [hits, setHits] = useState<
    Awaited<ReturnType<typeof api.searchIndex>> | null
  >(null);

  const conformance = useQuery({
    queryKey: ["conformance", asset?.id],
    queryFn: () => api.implementationConformance(asset!.id),
    enabled: Boolean(asset?.id),
  });

  const rebuild = useMutation({
    mutationFn: () => api.rebuildIndex(asset!.id),
    onSuccess: async () => {
      setHits(await api.searchIndex(q || "a", asset!.id));
    },
  });

  async function onSearch(e: FormEvent) {
    e.preventDefault();
    if (!asset) return;
    setHits(await api.searchIndex(q, asset.id));
  }

  if (isLoading) {
    return (
      <section>
        <h1>Model</h1>
        <p className="lede">Loading…</p>
      </section>
    );
  }

  if (error) {
    return (
      <section>
        <h1>Model</h1>
        <p className="error">{error.message}</p>
        <Link to="/models">Back</Link>
      </section>
    );
  }

  if (!asset) {
    return (
      <section>
        <h1>Unknown model</h1>
        <p className="lede">No implementation registered for “{slug}”.</p>
        <Link to="/models">Back</Link>
      </section>
    );
  }

  return (
    <section>
      <h1>{asset.title}</h1>
      <p className="lede">
        <code>{asset.id}</code> · Conformance and searchable model index.
      </p>

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
          {editable ? (
            <>
              <Link to={`/models/${asset.slug}/edit`}>Edit YAML</Link>
              <Link to={`/models/${asset.slug}/validate`}>Run validation job</Link>
              <Link to={`/models/${asset.slug}/diagram`}>Open diagram</Link>
            </>
          ) : (
            <span className="lede">
              Not editable in Workbench (requires LinkML DAMS data model).
            </span>
          )}
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
        <form className="row" onSubmit={onSearch}>
          <input
            value={q}
            onChange={(e) => setQ(e.target.value)}
            placeholder="Search elements"
            aria-label="Search elements"
          />
          <button type="submit">Search</button>
        </form>
        {hits && (
          <ul className="model-list">
            {hits.map((h) => (
              <li key={`${h.implementation_id}:${h.element_id}`}>
                <code>{h.element_id}</code> · {h.name} · {h.element_kind}
              </li>
            ))}
          </ul>
        )}
      </div>
    </section>
  );
}
