"""Request actor middleware.

Dev mode (default) reads ``X-Moex-Actor`` and falls back to ``dev``.
``MOEX_AUTH_MODE=trusted-header`` trusts a single header set by the reverse
proxy (``MOEX_AUTH_HEADER``, default ``X-Remote-User``). The client-supplied
``X-Moex-Actor`` is ignored in that mode. Probes ``/health`` and ``/ready``
stay open so a container check does not need a user.

Until OIDC exists, trusted-header is safe only when the network in front of
the process cannot be reached except through that proxy. A caller who can
hit the API port directly can set the header.
"""

from __future__ import annotations

import os

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

PUBLIC_PATHS = frozenset({"/health", "/ready"})


class DevAuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        request.state.actor = request.headers.get("X-Moex-Actor", "dev")
        return await call_next(request)


class TrustedHeaderAuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        if request.url.path in PUBLIC_PATHS:
            request.state.actor = "anonymous"
            return await call_next(request)
        header = os.environ.get("MOEX_AUTH_HEADER", "X-Remote-User") or "X-Remote-User"
        actor = request.headers.get(header, "").strip()
        if not actor:
            return JSONResponse(
                {"detail": f"missing trusted user header {header}"},
                status_code=401,
            )
        request.state.actor = actor
        return await call_next(request)


def select_auth_middleware() -> type[BaseHTTPMiddleware]:
    mode = (os.environ.get("MOEX_AUTH_MODE") or "dev").strip().lower()
    if mode == "dev":
        return DevAuthMiddleware
    if mode == "trusted-header":
        return TrustedHeaderAuthMiddleware
    raise ValueError(
        f"unknown MOEX_AUTH_MODE={mode!r} (use dev|trusted-header)"
    )
