"""breaking-gate — allow breaking semantic-diff only with Maintainer label."""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from typing import Any


MAINTAINER_ACCESS = 40
LABEL_NAME = "approved-breaking"


@dataclass(frozen=True)
class LabelApproval:
    user_id: int
    username: str
    created_at: str


@dataclass(frozen=True)
class MrHeadVersion:
    head_commit_sha: str
    created_at: str


def _api_get(url: str, token: str) -> Any:
    req = urllib.request.Request(
        url,
        headers={"PRIVATE-TOKEN": token, "Accept": "application/json"},
        method="GET",
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def fetch_label_events(
    *,
    api_base: str,
    project_id: str,
    mr_iid: str,
    token: str,
) -> list[dict[str, Any]]:
    base = api_base.rstrip("/")
    pid = urllib.parse.quote(str(project_id), safe="")
    url = (
        f"{base}/projects/{pid}/merge_requests/{mr_iid}/resource_label_events"
        f"?per_page=100"
    )
    data = _api_get(url, token)
    if not isinstance(data, list):
        raise ValueError("resource_label_events must return a list")
    return data


def fetch_mr_versions(
    *,
    api_base: str,
    project_id: str,
    mr_iid: str,
    token: str,
) -> list[dict[str, Any]]:
    base = api_base.rstrip("/")
    pid = urllib.parse.quote(str(project_id), safe="")
    url = f"{base}/projects/{pid}/merge_requests/{mr_iid}/versions?per_page=20"
    data = _api_get(url, token)
    if not isinstance(data, list):
        raise ValueError("merge_request versions must return a list")
    return data


def fetch_member_access(
    *,
    api_base: str,
    project_id: str,
    user_id: int,
    token: str,
) -> int:
    base = api_base.rstrip("/")
    pid = urllib.parse.quote(str(project_id), safe="")
    url = f"{base}/projects/{pid}/members/all/{user_id}"
    try:
        data = _api_get(url, token)
    except urllib.error.HTTPError as exc:
        if exc.code == 404:
            return 0
        raise
    return int(data.get("access_level") or 0)


def latest_approved_breaking(
    events: list[dict[str, Any]],
    *,
    label: str = LABEL_NAME,
) -> LabelApproval | None:
    """Return the latest add of ``label`` that was not later removed."""
    relevant = []
    for event in events:
        label_obj = event.get("label") or {}
        name = label_obj.get("name") if isinstance(label_obj, dict) else None
        if name != label:
            continue
        relevant.append(event)
    relevant.sort(key=lambda e: str(e.get("created_at") or ""))
    last_add: dict[str, Any] | None = None
    for event in relevant:
        action = str(event.get("action") or "")
        if action == "add":
            last_add = event
        elif action == "remove":
            last_add = None
    if last_add is None:
        return None
    user = last_add.get("user") or {}
    return LabelApproval(
        user_id=int(user.get("id") or 0),
        username=str(user.get("username") or ""),
        created_at=str(last_add.get("created_at") or ""),
    )


def latest_mr_head(versions: list[dict[str, Any]]) -> MrHeadVersion | None:
    """Newest MR diff version (GitLab returns newest first; sort to be safe)."""
    if not versions:
        return None
    ordered = sorted(
        versions,
        key=lambda v: str(v.get("created_at") or ""),
        reverse=True,
    )
    top = ordered[0]
    sha = str(top.get("head_commit_sha") or "")
    if not sha:
        return None
    return MrHeadVersion(
        head_commit_sha=sha,
        created_at=str(top.get("created_at") or ""),
    )


def report_has_breaking(payload: dict) -> bool:
    """True when the semantic-diff JSON marks a breaking change."""
    if payload.get("has_breaking") is True:
        return True
    for change in payload.get("changes") or []:
        if isinstance(change, dict) and change.get("category") == "breaking":
            return True
    return False


def evaluate_breaking_gate(
    *,
    has_breaking: bool,
    api_base: str,
    project_id: str,
    mr_iid: str,
    token: str,
    head_sha: str,
    label: str = LABEL_NAME,
    min_access: int = MAINTAINER_ACCESS,
    fetch_events=fetch_label_events,
    fetch_versions=fetch_mr_versions,
    fetch_access=fetch_member_access,
) -> tuple[int, str]:
    if not has_breaking:
        return 0, "breaking-gate OK (no breaking changes)\n"

    events = fetch_events(
        api_base=api_base,
        project_id=project_id,
        mr_iid=mr_iid,
        token=token,
    )
    approval = latest_approved_breaking(events, label=label)
    if approval is None:
        return (
            1,
            f"breaking-gate FAILED: breaking changes require label {label!r} "
            f"from Maintainer (access_level>={min_access})\n",
        )

    access = fetch_access(
        api_base=api_base,
        project_id=project_id,
        user_id=approval.user_id,
        token=token,
    )
    if access < min_access:
        return (
            1,
            f"breaking-gate FAILED: label {label!r} was added by "
            f"@{approval.username} (access_level={access}), "
            f"need >={min_access}\n",
        )

    versions = fetch_versions(
        api_base=api_base,
        project_id=project_id,
        mr_iid=mr_iid,
        token=token,
    )
    head = latest_mr_head(versions)
    if head is None:
        return 1, "breaking-gate FAILED: cannot read merge request versions\n"
    if head.head_commit_sha != head_sha:
        return (
            1,
            f"breaking-gate FAILED: MR head is {head.head_commit_sha[:12]}, "
            f"pipeline SHA is {head_sha[:12]}\n",
        )
    # Label must be added at or after the current MR version was created.
    if approval.created_at and head.created_at and approval.created_at < head.created_at:
        return (
            1,
            f"breaking-gate FAILED: label {label!r} was added before the "
            f"latest push; re-add the label after the new commits\n",
        )

    return (
        0,
        f"breaking-gate OK label={label!r} by @{approval.username} "
        f"access_level={access}\n",
    )


def run_breaking_gate_from_env(*, has_breaking: bool) -> tuple[int, str]:
    token = os.environ.get("MOEX_CI_TOKEN") or os.environ.get("GITLAB_TOKEN") or ""
    api_base = os.environ.get("CI_API_V4_URL") or ""
    project_id = os.environ.get("CI_PROJECT_ID") or ""
    mr_iid = os.environ.get("CI_MERGE_REQUEST_IID") or ""
    head_sha = os.environ.get("CI_COMMIT_SHA") or ""
    if not has_breaking:
        return 0, "breaking-gate OK (no breaking changes)\n"
    missing = [
        name
        for name, value in (
            ("MOEX_CI_TOKEN|GITLAB_TOKEN", token),
            ("CI_API_V4_URL", api_base),
            ("CI_PROJECT_ID", project_id),
            ("CI_MERGE_REQUEST_IID", mr_iid),
            ("CI_COMMIT_SHA", head_sha),
        )
        if not value
    ]
    if missing:
        return 1, f"breaking-gate FAILED: missing env {', '.join(missing)}\n"
    return evaluate_breaking_gate(
        has_breaking=True,
        api_base=api_base,
        project_id=project_id,
        mr_iid=mr_iid,
        token=token,
        head_sha=head_sha,
    )
