"""Check that a models checkout matches the contracts baked into this process.

The models tree (``MOEX_MODELS_ROOT``, otherwise the repository that contains
the DAMS schema marker) must hold that marker and
``generated/manifests/moex-dams-contracts.json``. The image copy of the same
manifest (``MOEX_IMAGE_CONTRACTS_MANIFEST``, otherwise the first one found by
walking up from this file) is the contracts this process was built with.
``schema_digest``, ``schema_version`` and ``content_digest`` must match.
"""

from __future__ import annotations

import json
import os
import sys
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from moex_model_api.auth import PUBLIC_PATHS
from moex_model_cli.bootstrap import MARKER, find_repo_root

CONTRACTS_MANIFEST_REL = Path("generated/manifests/moex-dams-contracts.json")
_COMPARE_KEYS = ("schema_digest", "schema_version", "content_digest")


@dataclass(frozen=True, slots=True)
class ModelsPreflight:
    status: str
    marker_present: bool
    contracts_match: bool
    schema_version: str | None
    problems: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


def models_root() -> Path:
    raw = os.environ.get("MOEX_MODELS_ROOT")
    if raw:
        return Path(raw)
    return find_repo_root()


def image_manifest_path() -> Path:
    raw = os.environ.get("MOEX_IMAGE_CONTRACTS_MANIFEST")
    if raw:
        return Path(raw)
    here = Path(__file__).resolve()
    for candidate in (here, *here.parents):
        manifest = candidate / CONTRACTS_MANIFEST_REL
        if manifest.is_file():
            return manifest
    return here.parents[4] / CONTRACTS_MANIFEST_REL


def _read_manifest(path: Path) -> tuple[dict[str, object] | None, str | None]:
    if not path.is_file():
        return None, f"missing manifest {path}"
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return None, f"unreadable manifest {path}: {exc}"
    if not isinstance(raw, dict):
        return None, f"manifest {path} is not an object"
    return raw, None


def check_models(models: Path, image_manifest: Path) -> ModelsPreflight:
    problems: list[str] = []
    marker = models / MARKER
    marker_present = marker.is_file()
    if not marker_present:
        problems.append(f"marker missing: {marker}")

    clone_path = models / CONTRACTS_MANIFEST_REL
    clone, clone_problem = _read_manifest(clone_path)
    image, image_problem = _read_manifest(image_manifest)
    if clone_problem:
        problems.append(clone_problem)
    if image_problem:
        problems.append(image_problem)

    mismatches: list[str] = []
    if clone is not None and image is not None:
        for key in _COMPARE_KEYS:
            if clone.get(key) != image.get(key):
                mismatches.append(key)
                problems.append(
                    f"{key} differs: models={clone.get(key)!r} image={image.get(key)!r}"
                )
    contracts_match = clone is not None and image is not None and not mismatches

    version = None
    if clone is not None and isinstance(clone.get("schema_version"), str):
        version = clone["schema_version"]
    elif image is not None and isinstance(image.get("schema_version"), str):
        version = image["schema_version"]

    status = "ready" if marker_present and contracts_match else "not_ready"
    return ModelsPreflight(
        status=status,
        marker_present=marker_present,
        contracts_match=contracts_match,
        schema_version=version,
        problems=problems,
    )


def models_ready_required() -> bool:
    raw = os.environ.get("MOEX_REQUIRE_MODELS_READY", "").strip().lower()
    return raw in {"1", "true", "yes"}


def _ready_ttl_seconds() -> float:
    raw = os.environ.get("MOEX_MODELS_READY_TTL", "5").strip()
    try:
        return max(0.0, float(raw))
    except ValueError:
        return 5.0


class ModelsReadyMiddleware(BaseHTTPMiddleware):
    """Answer 503 until the models checkout matches this process.

    The process stays up: on a first install the models volume is empty
    until sync clones it. ``/health`` and ``/ready`` stay open. The flag
    defaults off so a local process accepts requests immediately.
    """

    def __init__(self, app: object) -> None:
        super().__init__(app)  # type: ignore[arg-type]
        self._cached_at = 0.0
        self._cached: ModelsPreflight | None = None

    def _report(self) -> ModelsPreflight:
        now = time.monotonic()
        if self._cached is not None and now - self._cached_at < _ready_ttl_seconds():
            return self._cached
        report = check_models(models_root(), image_manifest_path())
        self._cached = report
        self._cached_at = now
        return report

    async def dispatch(self, request: Request, call_next) -> Response:
        if not models_ready_required() or request.url.path in PUBLIC_PATHS:
            return await call_next(request)
        report = self._report()
        if report.status != "ready":
            return JSONResponse(report.to_dict(), status_code=503)
        return await call_next(request)


def main(argv: list[str] | None = None) -> int:
    del argv
    report = check_models(models_root(), image_manifest_path())
    print(json.dumps(report.to_dict(), ensure_ascii=False))
    return 0 if report.status == "ready" else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
