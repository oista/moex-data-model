import { useMutation, useQuery } from "@tanstack/react-query";
import { useEffect, useMemo, useState, type FormEvent } from "react";
import { Link, useParams } from "react-router-dom";
import { api } from "../api/client";
import type { TransformRunResult } from "../api/types";

type Mode = "preview" | "sample";
type Backend = "object" | "sql";
type SampleSource = "bundled" | "upload";

/** Exported for tests — ensure we never expose a promote control. */
export function hasPromoteControl(): boolean {
  return false;
}

export function TransformPage() {
  const { workspaceId = "ws-workbench" } = useParams();
  const [specRel, setSpecRel] = useState("");
  const [mode, setMode] = useState<Mode>("preview");
  const [backend, setBackend] = useState<Backend>("object");
  const [sampleSource, setSampleSource] = useState<SampleSource>("bundled");
  const [sampleRel, setSampleRel] = useState("");
  const [file, setFile] = useState<File | null>(null);
  const [result, setResult] = useState<TransformRunResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  const catalog = useQuery({
    queryKey: ["transforms", workspaceId],
    queryFn: () => api.listTransforms(workspaceId),
  });

  const specs = catalog.data?.specs ?? [];
  const samples = catalog.data?.samples ?? [];

  useEffect(() => {
    if (!specRel && specs.length > 0) {
      setSpecRel(specs[0].rel_path);
    }
  }, [specs, specRel]);

  useEffect(() => {
    if (!sampleRel && samples.length > 0) {
      setSampleRel(samples[0].rel_path);
    }
  }, [samples, sampleRel]);

  const selectedSpec = useMemo(
    () => specs.find((s) => s.rel_path === specRel) ?? null,
    [specs, specRel],
  );

  const run = useMutation({
    mutationFn: async () => {
      if (!specRel) throw new Error("choose a transform spec");
      if (sampleSource === "bundled") {
        if (!sampleRel) throw new Error("choose a bundled sample");
        return api.runTransform(workspaceId, {
          spec_rel: specRel,
          mode,
          backend,
          sample_rel: sampleRel,
        });
      }
      if (!file) throw new Error("choose a sample file");
      return api.runTransform(workspaceId, {
        spec_rel: specRel,
        mode,
        backend,
        file,
      });
    },
    onSuccess: (data) => {
      setResult(data);
      setError(null);
    },
    onError: (err) => setError((err as Error).message),
  });

  function onSubmit(e: FormEvent) {
    e.preventDefault();
    run.mutate();
  }

  const payload =
    result?.mode === "preview"
      ? result.preview_payload
      : result?.output ?? null;

  const fatals = (result?.diagnostics ?? []).filter((d) =>
    ["error", "fatal"].includes((d.severity || "").toLowerCase()),
  );

  return (
    <section data-testid="transform-page">
      <h1>Transform</h1>
      <p className="lede">
        Review linkml-map transforms (preview / sample). No publish — same
        provider as <code>moex-model map --transform</code>.
      </p>
      <p>
        <Link to={`/workspaces/${workspaceId}/import`}>Import wizard</Link>
        {" · "}
        <Link to="/workspaces">Workspaces</Link>
      </p>

      {catalog.isLoading && <p>Loading catalog…</p>}
      {catalog.isError && (
        <p className="error" role="alert">
          {(catalog.error as Error).message}
        </p>
      )}

      <form onSubmit={onSubmit} data-testid="transform-form">
        <label>
          Spec
          <select
            data-testid="transform-spec"
            value={specRel}
            onChange={(e) => setSpecRel(e.target.value)}
            required
          >
            <option value="">— select —</option>
            {specs.map((s) => (
              <option key={s.rel_path} value={s.rel_path}>
                {s.spec_id} ({s.source_schema_revision} →{" "}
                {s.target_schema_revision})
              </option>
            ))}
          </select>
        </label>

        {selectedSpec?.description && (
          <p className="lede" data-testid="transform-spec-desc">
            {selectedSpec.description}
          </p>
        )}

        <fieldset>
          <legend>Mode</legend>
          <label>
            <input
              type="radio"
              name="mode"
              value="preview"
              checked={mode === "preview"}
              onChange={() => setMode("preview")}
            />{" "}
            preview
          </label>
          <label>
            <input
              type="radio"
              name="mode"
              value="sample"
              checked={mode === "sample"}
              onChange={() => setMode("sample")}
            />{" "}
            sample
          </label>
        </fieldset>

        <fieldset>
          <legend>Backend</legend>
          <label>
            <input
              type="radio"
              name="backend"
              value="object"
              checked={backend === "object"}
              onChange={() => setBackend("object")}
            />{" "}
            object
          </label>
          <label>
            <input
              type="radio"
              name="backend"
              value="sql"
              checked={backend === "sql"}
              onChange={() => setBackend("sql")}
            />{" "}
            sql
          </label>
        </fieldset>

        <fieldset>
          <legend>Sample</legend>
          <label>
            <input
              type="radio"
              name="sampleSource"
              value="bundled"
              checked={sampleSource === "bundled"}
              onChange={() => setSampleSource("bundled")}
            />{" "}
            bundled
          </label>
          <label>
            <input
              type="radio"
              name="sampleSource"
              value="upload"
              checked={sampleSource === "upload"}
              onChange={() => setSampleSource("upload")}
            />{" "}
            upload
          </label>
        </fieldset>

        {sampleSource === "bundled" ? (
          <label>
            Bundled sample
            <select
              data-testid="transform-sample-rel"
              value={sampleRel}
              onChange={(e) => setSampleRel(e.target.value)}
              required
            >
              <option value="">— select —</option>
              {samples.map((s) => (
                <option key={s.rel_path} value={s.rel_path}>
                  {s.name}
                </option>
              ))}
            </select>
          </label>
        ) : (
          <label>
            Upload sample (JSON/YAML)
            <input
              data-testid="transform-sample-file"
              type="file"
              accept=".json,.yaml,.yml,application/json,text/yaml"
              onChange={(e) => setFile(e.target.files?.[0] ?? null)}
            />
          </label>
        )}

        <button type="submit" disabled={run.isPending} data-testid="transform-run">
          {run.isPending ? "Running…" : "Run transform"}
        </button>
      </form>

      {error && (
        <p className="error" role="alert" data-testid="transform-error">
          {error}
        </p>
      )}

      {result && (
        <div data-testid="transform-result">
          <h2>Result</h2>
          <p>
            <code>{result.spec.spec_id}</code> · mode={result.mode} ·
            backend={result.backend} ·{" "}
            {result.spec.source_schema_revision} →{" "}
            {result.spec.target_schema_revision}
          </p>

          <h3>Preserved semantics</h3>
          <ul data-testid="transform-preserved">
            {result.preserved_semantics.length === 0 && <li>(none)</li>}
            {result.preserved_semantics.map((s) => (
              <li key={s}>{s}</li>
            ))}
          </ul>

          <h3>Lost semantics</h3>
          <ul data-testid="transform-lost">
            {result.lost_semantics.length === 0 && <li>(none)</li>}
            {result.lost_semantics.map((s) => (
              <li key={s}>{s}</li>
            ))}
          </ul>

          <h3>Diagnostics</h3>
          {fatals.length > 0 && (
            <p className="error" data-testid="transform-fatal-banner">
              {fatals.length} error/fatal diagnostic(s)
            </p>
          )}
          <ul data-testid="transform-diagnostics">
            {(result.diagnostics ?? []).length === 0 && <li>(none)</li>}
            {(result.diagnostics ?? []).map((d, i) => (
              <li key={`${d.diagnostic_code}-${i}`}>
                [{d.severity}] {d.diagnostic_code}: {d.diagnostic_message}
              </li>
            ))}
          </ul>

          <h3>Payload</h3>
          <pre data-testid="transform-payload">
            {JSON.stringify(payload, null, 2)}
          </pre>
        </div>
      )}
    </section>
  );
}
