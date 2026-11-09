"""mr-summary — post or update a diagnostics summary note on a GitLab MR."""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

MARKER = "<!-- moex-ci-summary -->"


def _api_request(
    method: str,
    url: str,
    token: str,
    body: dict[str, Any] | None = None,
) -> Any:
    data = None if body is None else json.dumps(body).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={
            "PRIVATE-TOKEN": token,
            "Accept": "application/json",
            "Content-Type": "application/json",
        },
        method=method,
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        raw = resp.read().decode("utf-8")
        return json.loads(raw) if raw else None


def build_summary_markdown(
    *,
    ci_validate: dict[str, Any] | None,
    semantic_diff_text: str | None,
    matrix_check: dict[str, Any] | None,
) -> str:
    lines = [MARKER, "## MOEX CI summary", ""]
    if ci_validate is not None:
        lines.append("### Validate")
        lines.append("")
        lines.append("| Implementation | Overall | Errors | Soft |")
        lines.append("|---|---|---:|---:|")
        for impl in ci_validate.get("implementations") or []:
            lines.append(
                f"| `{impl.get('implementation_id')}` | {impl.get('overall')} | "
                f"{len(impl.get('errors') or [])} | {impl.get('soft_count', 0)} |"
            )
        problems = ci_validate.get("problems") or []
        if problems:
            lines.append("")
            lines.append("Problems:")
            for problem in problems[:20]:
                lines.append(f"- {problem}")
        lines.append("")
    if semantic_diff_text:
        lines.append("### Semantic diff")
        lines.append("")
        lines.append("```")
        lines.append(semantic_diff_text.strip()[:2000])
        lines.append("```")
        lines.append("")
    if matrix_check is not None:
        lines.append("### Matrix / traceability")
        lines.append("")
        ok = matrix_check.get("ok")
        lines.append(f"ok={ok}")
        trace = matrix_check.get("traceability") or {}
        counts = trace.get("counts") or {}
        if counts:
            lines.append(
                f"pass={counts.get('pass', 0)} fail={counts.get('fail', 0)} "
                f"waived={counts.get('waived', 0)} missing={counts.get('missing', 0)}"
            )
        for key in ("expiry_errors", "expiry_warnings"):
            items = matrix_check.get(key) or []
            if items:
                lines.append(f"{key}:")
                for item in items[:10]:
                    lines.append(f"- {item}")
        lines.append("")
    return "\n".join(lines) + "\n"


def upsert_mr_note(
    *,
    api_base: str,
    project_id: str,
    mr_iid: str,
    token: str,
    body: str,
) -> str:
    base = api_base.rstrip("/")
    pid = urllib.parse.quote(str(project_id), safe="")
    list_url = f"{base}/projects/{pid}/merge_requests/{mr_iid}/notes?per_page=100"
    notes = _api_request("GET", list_url, token)
    existing_id = None
    if isinstance(notes, list):
        for note in notes:
            if MARKER in str(note.get("body") or ""):
                existing_id = note.get("id")
                break
    if existing_id is not None:
        url = f"{base}/projects/{pid}/merge_requests/{mr_iid}/notes/{existing_id}"
        _api_request("PUT", url, token, {"body": body})
        return f"updated note {existing_id}"
    url = f"{base}/projects/{pid}/merge_requests/{mr_iid}/notes"
    created = _api_request("POST", url, token, {"body": body})
    return f"created note {created.get('id') if isinstance(created, dict) else '?'}"


def run_mr_summary(
    *,
    ci_validate_json: Path | None = None,
    semantic_diff_file: Path | None = None,
    matrix_json: Path | None = None,
    dry_run: bool = False,
) -> tuple[int, str]:
    ci_payload = None
    if ci_validate_json and ci_validate_json.is_file():
        ci_payload = json.loads(ci_validate_json.read_text(encoding="utf-8"))
    sem_text = None
    if semantic_diff_file and semantic_diff_file.is_file():
        sem_text = semantic_diff_file.read_text(encoding="utf-8")
    matrix_payload = None
    if matrix_json and matrix_json.is_file():
        matrix_payload = json.loads(matrix_json.read_text(encoding="utf-8"))

    markdown = build_summary_markdown(
        ci_validate=ci_payload,
        semantic_diff_text=sem_text,
        matrix_check=matrix_payload,
    )
    if dry_run:
        return 0, markdown

    token = os.environ.get("MOEX_CI_TOKEN") or os.environ.get("GITLAB_TOKEN") or ""
    api_base = os.environ.get("CI_API_V4_URL") or ""
    project_id = os.environ.get("CI_PROJECT_ID") or ""
    mr_iid = os.environ.get("CI_MERGE_REQUEST_IID") or ""
    if not all([token, api_base, project_id, mr_iid]):
        return 1, "mr-summary: missing CI env or token\n"
    try:
        action = upsert_mr_note(
            api_base=api_base,
            project_id=project_id,
            mr_iid=mr_iid,
            token=token,
            body=markdown,
        )
    except urllib.error.URLError as exc:
        return 1, f"mr-summary failed: {exc}\n"
    return 0, f"mr-summary {action}\n"
