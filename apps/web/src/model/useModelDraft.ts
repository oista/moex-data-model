import { useCallback, useEffect, useRef, useState } from "react";
import { api } from "../api/client";
import type { DocumentMutation, WorkspaceDocument } from "../api/types";
import { parseDraftYaml } from "./draft";
import { applyMutationOptimistic } from "./yamlMutate";

const PUT_DEBOUNCE_MS = 400;

type SourceLabel = "draft" | "published" | "";

export type UseModelDraftResult = {
  content: string;
  baseDigest: string;
  dirty: boolean;
  sourceLabel: SourceLabel;
  loading: boolean;
  loadError: string | null;
  parseError: string | null;
  setContentFromMonaco: (next: string) => void;
  applyLocalOp: (op: DocumentMutation) => void;
  rollbackOptimistic: () => void;
  replaceFromServer: (doc: WorkspaceDocument) => void;
  ensureSaved: () => Promise<void>;
  load: () => Promise<void>;
  putNow: () => Promise<WorkspaceDocument>;
  discardToPublished: (content: string, digest: string) => void;
};

export function useModelDraft(
  workspaceId: string,
  implementationId: string | undefined,
): UseModelDraftResult {
  const [content, setContent] = useState("");
  const [baseDigest, setBaseDigest] = useState("");
  const [dirty, setDirty] = useState(false);
  const [sourceLabel, setSourceLabel] = useState<SourceLabel>("");
  const [loading, setLoading] = useState(true);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [parseError, setParseError] = useState<string | null>(null);

  const contentRef = useRef(content);
  const digestRef = useRef(baseDigest);
  const dirtyRef = useRef(dirty);
  const rollbackRef = useRef<string | null>(null);
  const putTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  contentRef.current = content;
  digestRef.current = baseDigest;
  dirtyRef.current = dirty;

  useEffect(() => {
    const { error } = parseDraftYaml(content);
    setParseError(error);
  }, [content]);

  const clearPutTimer = useCallback(() => {
    if (putTimerRef.current !== null) {
      clearTimeout(putTimerRef.current);
      putTimerRef.current = null;
    }
  }, []);

  const putNow = useCallback(async () => {
    if (!implementationId) {
      throw new Error("implementation not resolved");
    }
    clearPutTimer();
    const doc = await api.putDocument(workspaceId, implementationId, {
      content: contentRef.current,
      base_digest: digestRef.current,
    });
    setBaseDigest(doc.base_digest);
    digestRef.current = doc.base_digest;
    setSourceLabel("draft");
    setDirty(false);
    dirtyRef.current = false;
    return doc;
  }, [workspaceId, implementationId, clearPutTimer]);

  const schedulePut = useCallback(() => {
    clearPutTimer();
    putTimerRef.current = setTimeout(() => {
      putTimerRef.current = null;
      void putNow().catch(() => {
        /* surfaced by callers that put explicitly */
      });
    }, PUT_DEBOUNCE_MS);
  }, [clearPutTimer, putNow]);

  useEffect(() => () => clearPutTimer(), [clearPutTimer]);

  const load = useCallback(async () => {
    if (!implementationId) {
      setLoading(false);
      return;
    }
    setLoading(true);
    setLoadError(null);
    clearPutTimer();
    try {
      await api.createWorkspace({ id: workspaceId, name: "Workbench" });
      try {
        const draft = await api.getDocument(workspaceId, implementationId);
        setContent(draft.content);
        setBaseDigest(draft.base_digest);
        setSourceLabel("draft");
      } catch {
        const published = await api.implementationBody(implementationId);
        setContent(published.content);
        setBaseDigest(published.content_digest);
        setSourceLabel("published");
      }
      setDirty(false);
      rollbackRef.current = null;
    } catch (err) {
      setLoadError((err as Error).message);
    } finally {
      setLoading(false);
    }
  }, [workspaceId, implementationId, clearPutTimer]);

  useEffect(() => {
    void load();
  }, [load]);

  const setContentFromMonaco = useCallback(
    (next: string) => {
      setContent(next);
      setDirty(true);
      dirtyRef.current = true;
      schedulePut();
    },
    [schedulePut],
  );

  const applyLocalOp = useCallback((op: DocumentMutation) => {
    rollbackRef.current = contentRef.current;
    const next = applyMutationOptimistic(contentRef.current, op);
    setContent(next);
    contentRef.current = next;
  }, []);

  const rollbackOptimistic = useCallback(() => {
    if (rollbackRef.current === null) return;
    setContent(rollbackRef.current);
    contentRef.current = rollbackRef.current;
    rollbackRef.current = null;
  }, []);

  const replaceFromServer = useCallback(
    (doc: WorkspaceDocument) => {
      clearPutTimer();
      rollbackRef.current = null;
      setContent(doc.content);
      contentRef.current = doc.content;
      setBaseDigest(doc.base_digest);
      digestRef.current = doc.base_digest;
      setSourceLabel("draft");
      setDirty(false);
      dirtyRef.current = false;
    },
    [clearPutTimer],
  );

  const ensureSaved = useCallback(async () => {
    if (!dirtyRef.current) return;
    await putNow();
  }, [putNow]);

  const discardToPublished = useCallback(
    (publishedContent: string, digest: string) => {
      clearPutTimer();
      rollbackRef.current = null;
      setContent(publishedContent);
      contentRef.current = publishedContent;
      setBaseDigest(digest);
      digestRef.current = digest;
      setSourceLabel("published");
      setDirty(false);
      dirtyRef.current = false;
    },
    [clearPutTimer],
  );

  return {
    content,
    baseDigest,
    dirty,
    sourceLabel,
    loading,
    loadError,
    parseError,
    setContentFromMonaco,
    applyLocalOp,
    rollbackOptimistic,
    replaceFromServer,
    ensureSaved,
    load,
    putNow,
    discardToPublished,
  };
}
