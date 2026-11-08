import { useEffect, useState } from "react";

const POLL_MS = 30_000;
const BUILD_INFO_URL = "/viewer/build-info.json";

type BuildInfo = {
  commit: string;
  built_at: string;
};

function minutesSince(iso: string, now: number): number {
  const then = Date.parse(iso);
  if (Number.isNaN(then)) return 0;
  return Math.max(0, Math.floor((now - then) / 60_000));
}

function statusLine(info: BuildInfo, now: number): string {
  const short = info.commit.slice(0, 12);
  const built = new Date(info.built_at);
  const stamp = Number.isNaN(built.getTime())
    ? info.built_at
    : built.toISOString().replace("T", " ").slice(0, 16);
  const mins = minutesSince(info.built_at, now);
  return `коммит ${short}, ${stamp} UTC, собран ${mins} мин назад`;
}

export function ViewerPage() {
  const [info, setInfo] = useState<BuildInfo | null>(null);
  const [missing, setMissing] = useState(true);

  useEffect(() => {
    let cancelled = false;

    async function load() {
      try {
        const response = await fetch(BUILD_INFO_URL, { cache: "no-store" });
        if (!response.ok) {
          if (!cancelled) {
            setInfo(null);
            setMissing(true);
          }
          return;
        }
        const body = (await response.json()) as Partial<BuildInfo>;
        if (!body.commit || !body.built_at) {
          if (!cancelled) {
            setInfo(null);
            setMissing(true);
          }
          return;
        }
        if (!cancelled) {
          setInfo({ commit: body.commit, built_at: body.built_at });
          setMissing(false);
        }
      } catch {
        if (!cancelled) {
          setInfo(null);
          setMissing(true);
        }
      }
    }

    void load();
    const timer = window.setInterval(() => {
      void load();
    }, POLL_MS);
    return () => {
      cancelled = true;
      window.clearInterval(timer);
    };
  }, []);

  const now = Date.now();

  return (
    <section className="viewer-page">
      <h1>Viewer</h1>
      {missing || !info ? (
        <p className="lede">Viewer ещё не собран: модели не подключены</p>
      ) : (
        <>
          <p className="lede">{statusLine(info, now)}</p>
          <p className="row">
            <a href="/viewer/" target="_blank" rel="noreferrer">
              Открыть в новой вкладке
            </a>
          </p>
          <iframe
            key={info.commit}
            className="viewer-frame"
            title="Viewer"
            src="/viewer/"
          />
        </>
      )}
    </section>
  );
}
