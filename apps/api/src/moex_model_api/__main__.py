"""uvicorn entry."""

from __future__ import annotations

import os

import uvicorn


def listen_address() -> tuple[str, int]:
    """Host and port from ``MOEX_API_HOST`` / ``MOEX_API_PORT``.

    Defaults stay ``127.0.0.1:8000``. A non-integer port stops the process.
    """
    host = os.environ.get("MOEX_API_HOST", "127.0.0.1") or "127.0.0.1"
    raw = os.environ.get("MOEX_API_PORT", "8000") or "8000"
    try:
        port = int(raw)
    except ValueError as exc:
        raise SystemExit(f"MOEX_API_PORT must be an integer, got {raw!r}") from exc
    if port < 1 or port > 65535:
        raise SystemExit(f"MOEX_API_PORT out of range: {port}")
    return host, port


def main() -> None:
    host, port = listen_address()
    uvicorn.run(
        "moex_model_api.app:app",
        host=host,
        port=port,
        reload=False,
    )


if __name__ == "__main__":
    main()
