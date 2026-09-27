import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import { api } from "../api/client";

export function ModelsPage() {
  const impls = useQuery({
    queryKey: ["implementations"],
    queryFn: api.listImplementations,
  });

  return (
    <section>
      <h1>Models</h1>
      <p className="lede">Registered specification implementations.</p>

      {impls.isLoading && <p>Loading…</p>}
      {impls.isError && (
        <p className="error">{(impls.error as Error).message}</p>
      )}
      {impls.data && (
        <ul className="model-list">
          {impls.data.map((impl) => (
            <li key={impl.id}>
              <Link to={`/models/${impl.slug}`}>
                <strong>{impl.title}</strong>
              </Link>
              <div className="lede" style={{ margin: "0.25rem 0 0" }}>
                <code>{impl.id}</code> · {impl.implementation_path}
              </div>
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}
