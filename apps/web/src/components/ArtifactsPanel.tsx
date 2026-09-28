import { useMutation } from "@tanstack/react-query";
import { useEffect, useState } from "react";
import { api } from "../api/client";
import type { JobArtifact } from "../api/types";

type Props = {
  jobId: string | null;
};

export function ArtifactsPanel({ jobId }: Props) {
  const [artifacts, setArtifacts] = useState<JobArtifact[]>([]);
  const [preview, setPreview] = useState<{ id: string; text: string } | null>(
    null,
  );
  const [error, setError] = useState<string | null>(null);

  const load = useMutation({
    mutationFn: async (id: string) => api.listJobArtifacts(id),
    onSuccess: (items) => {
      setArtifacts(items);
      setError(null);
    },
    onError: (err) => setError((err as Error).message),
  });

  useEffect(() => {
    if (jobId) {
      load.mutate(jobId);
    } else {
      setArtifacts([]);
      setPreview(null);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps -- reload when jobId changes
  }, [jobId]);

  const previewMut = useMutation({
    mutationFn: async (art: JobArtifact) => {
      if (!jobId) throw new Error("no job");
      const text = await api.getArtifactContent(jobId, art.id);
      return { id: art.id, text };
    },
    onSuccess: (data) => {
      setPreview(data);
      setError(null);
    },
    onError: (err) => setError((err as Error).message),
  });

  if (!jobId) {
    return null;
  }

  return (
    <div className="panel" data-testid="artifacts-panel">
      <div className="row">
        <strong>Artifacts</strong>
        <code>{jobId}</code>
        <button
          type="button"
          onClick={() => load.mutate(jobId)}
          disabled={load.isPending}
          data-testid="load-artifacts"
        >
          Refresh
        </button>
      </div>
      {error && <p className="error">{error}</p>}
      <ul className="entity-list" data-testid="artifact-list">
        {artifacts.map((art) => (
          <li key={art.id}>
            <span>
              <code>{art.kind}</code> · {art.path_or_uri}
              {art.content_digest && (
                <>
                  {" "}
                  · <code>{art.content_digest.slice(0, 18)}…</code>
                </>
              )}
            </span>
            <button
              type="button"
              onClick={() => previewMut.mutate(art)}
              disabled={previewMut.isPending}
              data-testid={`preview-artifact-${art.id}`}
            >
              Preview
            </button>
          </li>
        ))}
        {artifacts.length === 0 && !load.isPending && (
          <li className="lede">No artifacts for this job</li>
        )}
      </ul>
      {preview && (
        <pre className="artifact-preview" data-testid="artifact-preview">
          {preview.text.slice(0, 8000)}
          {preview.text.length > 8000 ? "\n…" : ""}
        </pre>
      )}
    </div>
  );
}
