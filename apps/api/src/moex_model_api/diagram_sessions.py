"""In-memory diagram session state (submit/apply)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class DiagramSession:
    session_id: str
    workspace_id: str
    profile: str
    dbml: str
    base_yaml: str
    last_merged_yaml: str | None = None
    last_patch: dict[str, Any] | None = None
    last_rejected: list[dict[str, Any]] = field(default_factory=list)


class DiagramSessionStore:
    def __init__(self) -> None:
        self._sessions: dict[str, DiagramSession] = {}

    def put(self, session: DiagramSession) -> None:
        self._sessions[session.session_id] = session

    def get(self, session_id: str) -> DiagramSession | None:
        return self._sessions.get(session_id)
