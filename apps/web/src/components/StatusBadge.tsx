type Props = { status: string };

export function StatusBadge({ status }: Props) {
  const lower = status.toLowerCase();
  const kind =
    lower === "conformant" || lower === "succeeded" || lower === "ok"
      ? "ok"
      : lower === "failed" || lower === "non_conformant" || lower === "error"
        ? "bad"
        : "neutral";
  return <span className={`badge ${kind}`}>{status}</span>;
}
