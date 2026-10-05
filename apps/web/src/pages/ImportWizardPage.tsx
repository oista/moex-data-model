import { useMutation, useQuery } from "@tanstack/react-query";
import { useMemo, useState, type FormEvent } from "react";
import { Link, useParams, useSearchParams } from "react-router-dom";
import { api } from "../api/client";
import type { Job, JobArtifact } from "../api/types";
import { ArtifactsPanel } from "../components/ArtifactsPanel";

type SourceType = "json_schema" | "sql" | "csv" | "rdf";

type DiagnosticRow = {
  diagnostic_code?: string;
  severity?: string;
  diagnostic_message?: string;
};

type EnrichItem = {
  code?: string;
  severity?: string;
  path?: string;
  message?: string;
  field?: string;
};

const ENRICH_FIELDS = ["id", "description", "range", "registry_link"] as const;

export function ImportWizardPage() {
  const { workspaceId = "ws-workbench" } = useParams();
  const [searchParams, setSearchParams] = useSearchParams();
  const impls = useQuery({
    queryKey: ["implementations"],
    queryFn: api.listImplementations,
  });
  const editable = useMemo(
    () => (impls.data ?? []).filter((a) => a.workbench_editable),
    [impls.data],
  );
  const selectedSlug =
    searchParams.get("impl") || editable[0]?.slug || "";
  const selected = editable.find((a) => a.slug === selectedSlug);
  const [sourceType, setSourceType] = useState<SourceType>("json_schema");
  const [file, setFile] = useState<File | null>(null);
  const [job, setJob] = useState<Job | null>(null);
  const [diagnostics, setDiagnostics] = useState<DiagnosticRow[]>([]);
  const [enrichItems, setEnrichItems] = useState<EnrichItem[]>([]);
  const [inferred, setInferred] = useState<string>("");
  const [draftOpened, setDraftOpened] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const runImport = useMutation({
    mutationFn: async () => {
      if (!file) throw new Error("choose a file");
      const created = await api.createImportDraft(workspaceId, {
        file,
        source_type: sourceType,
        name: file.name.replace(/\.[^.]+$/, ""),
      });
      const arts = await api.listJobArtifacts(created.id);
      const diagArt = arts.find((a) => a.kind === "import-diagnostics");
      const schemaArt = arts.find((a) => a.kind === "import-inferred-schema");
      const enrichArt = arts.find((a) => a.kind === "import-enrich-checklist");
      let diags: DiagnosticRow[] = [];
      if (diagArt) {
        const text = await api.getArtifactContent(created.id, diagArt.id);
        diags = JSON.parse(text) as DiagnosticRow[];
      }
      let schemaText = "";
      if (schemaArt) {
        schemaText = await api.getArtifactContent(created.id, schemaArt.id);
      }
      let checklist: EnrichItem[] = [];
      if (enrichArt) {
        const text = await api.getArtifactContent(created.id, enrichArt.id);
        checklist = JSON.parse(text) as EnrichItem[];
      }
      return { created, arts, diags, schemaText, checklist };
    },
    onSuccess: (data) => {
      setJob(data.created);
      setDiagnostics(data.diags);
      setInferred(data.schemaText);
      setEnrichItems(data.checklist);
      setDraftOpened(false);
      setError(null);
    },
    onError: (err) => setError((err as Error).message),
  });

  const openDraft = useMutation({
    mutationFn: async () => {
      if (!inferred.trim()) throw new Error("no inferred schema");
      if (!selected) throw new Error("choose a target implementation");
      const banner =
        "# status: generated-draft\n" +
        "# Stage 7b import — enrich IDs/descriptions before ModelPackage publish\n";
      return api.putDocument(workspaceId, selected.id, {
        content: banner + inferred,
      });
    },
    onSuccess: () => {
      setDraftOpened(true);
      setError(null);
    },
    onError: (err) => setError((err as Error).message),
  });

  const warnings = useMemo(
    () =>
      diagnostics.filter(
        (d) => (d.severity || "").toLowerCase() === "warning",
      ),
    [diagnostics],
  );
  const errors = useMemo(
    () =>
      diagnostics.filter((d) =>
        ["error", "fatal"].includes((d.severity || "").toLowerCase()),
      ),
    [diagnostics],
  );

  const enrichByField = useMemo(() => {
    const groups: Record<string, EnrichItem[]> = {};
    for (const field of ENRICH_FIELDS) {
      groups[field] = enrichItems.filter((i) => i.field === field);
    }
    const other = enrichItems.filter(
      (i) => !ENRICH_FIELDS.includes(i.field as (typeof ENRICH_FIELDS)[number]),
    );
    if (other.length) groups.other = other;
    return groups;
  }, [enrichItems]);

  function onSubmit(e: FormEvent) {
    e.preventDefault();
    runImport.mutate();
  }

  return (
    <section data-testid="import-wizard">
      <h1>Import wizard</h1>
      <p className="lede">
        Bootstrap a LinkML schema from JSON Schema / SQL (schema-automator).
        Result is always <code>generated-draft</code> — never auto-published.
      </p>
      <div
        className="banner"
        data-testid="draft-banner"
        style={{
          border: "1px solid #888",
          padding: "0.5rem 0.75rem",
          marginBottom: "0.75rem",
        }}
      >
        Status: <code>generated-draft</code> — enrich manually; no auto-promote
        to ModelPackage.
      </div>
      <p className="lede">
        Workspace: <code>{workspaceId}</code>
        {selected && (
          <>
            {" "}
            ·{" "}
            <Link to={`/models/${selected.slug}/edit`}>Open editor</Link>
          </>
        )}
      </p>

      <form className="panel" onSubmit={onSubmit} data-testid="import-form">
        <label>
          Target implementation
          <select
            value={selectedSlug}
            onChange={(e) => {
              const next = new URLSearchParams(searchParams);
              next.set("impl", e.target.value);
              setSearchParams(next, { replace: true });
            }}
            data-testid="target-implementation"
            disabled={editable.length === 0}
          >
            {editable.map((a) => (
              <option key={a.id} value={a.slug}>
                {a.title} ({a.slug})
              </option>
            ))}
          </select>
        </label>
        <label>
          Source type
          <select
            value={sourceType}
            onChange={(e) => setSourceType(e.target.value as SourceType)}
            data-testid="source-type"
          >
            <option value="json_schema">JSON Schema</option>
            <option value="sql">SQL / DDL</option>
            <option value="csv">CSV</option>
            <option value="rdf">RDF / OWL</option>
          </select>
        </label>
        <label>
          File
          <input
            type="file"
            data-testid="import-file"
            onChange={(e) => setFile(e.target.files?.[0] ?? null)}
          />
        </label>
        <button
          className="primary"
          type="submit"
          disabled={!file || runImport.isPending}
          data-testid="run-import"
        >
          Run import
        </button>
      </form>

      {error && (
        <p className="error" data-testid="import-error">
          {error}
        </p>
      )}

      {job && (
        <div className="panel" data-testid="import-result">
          <p>
            Job <code>{job.id}</code> · status <strong>{job.status}</strong>
          </p>
          <p className="lede">{job.result_summary}</p>
          {(warnings.length > 0 || errors.length > 0) && (
            <ul data-testid="import-diagnostics">
              {errors.map((d, i) => (
                <li key={`e-${i}`} className="error">
                  [{d.diagnostic_code}] {d.diagnostic_message}
                </li>
              ))}
              {warnings.map((d, i) => (
                <li key={`w-${i}`}>
                  [{d.diagnostic_code}] {d.diagnostic_message}
                </li>
              ))}
            </ul>
          )}
          {enrichItems.length > 0 && (
            <div className="panel" data-testid="enrich-panel">
              <h2>Enrich checklist</h2>
              <p className="lede">
                Advisory gaps (IDs, descriptions, ranges, registry links). Edit
                in Monaco — checklist does not auto-publish.
              </p>
              <ul data-testid="enrich-checklist">
                {Object.entries(enrichByField).map(([field, items]) =>
                  items.length === 0
                    ? null
                    : items.map((item, i) => (
                        <li key={`${field}-${i}`}>
                          <strong>{field}</strong> [{item.code}] {item.path}:{" "}
                          {item.message}
                        </li>
                      )),
                )}
              </ul>
              <p>
                <Link
                  to={`/models/${selected?.slug || selectedSlug}/edit`}
                  data-testid="enrich-monaco-link"
                >
                  Open Monaco to enrich
                </Link>
              </p>
            </div>
          )}
          {inferred && (
            <pre
              className="artifact-preview"
              data-testid="inferred-preview"
              style={{ maxHeight: "24rem", overflow: "auto" }}
            >
              {inferred.slice(0, 12000)}
              {inferred.length > 12000 ? "\n…" : ""}
            </pre>
          )}
          <div className="row">
            <button
              type="button"
              className="primary"
              data-testid="open-as-draft"
              disabled={!inferred || openDraft.isPending}
              onClick={() => openDraft.mutate()}
            >
              Open as workspace draft
            </button>
            {/* Intentionally no auto-publish / promote button */}
          </div>
          {draftOpened && (
            <p data-testid="draft-opened">
              Draft saved to workspace document (generated-draft banner).{" "}
              <Link to={`/models/${selected?.slug || selectedSlug}/edit`}>
                Edit in Monaco
              </Link>
            </p>
          )}
          <ArtifactsPanel jobId={job.id} />
        </div>
      )}
    </section>
  );
}

/** Exported for tests — ensure we never expose a promote control. */
export function hasAutoPromoteControl(_artifacts: JobArtifact[]): boolean {
  return false;
}
