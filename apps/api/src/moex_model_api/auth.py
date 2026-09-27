"""Dev-only auth middleware (OIDC later)."""

from __future__ import annotations

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response


class DevAuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        request.state.actor = request.headers.get("X-Moex-Actor", "dev")
        return await call_next(request)
