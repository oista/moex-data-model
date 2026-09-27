"""FastAPI application factory."""

from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from uuid import uuid4

import yaml
from fastapi import Depends, FastAPI, Header, HTTPException, Request
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session, sessionmaker

from moex_dams.application.assess import assess_implementation
from moex_model_cli.bootstrap import SlicePaths, find_repo_root
from moex_model_cli.commands.compile import run_compile
from moex_model_api.auth import DevAuthMiddleware
from moex_model_api.db.session import init_db, make_engine, session_factory
from moex_model_api.db.stores import (
    SqlAuditStore,
    SqlIdentityStore,
    SqlJobStore,
    SqlModelIndexProvider,
    SqlValidationRunStore,
    SqlWorkspaceStore,
)
from moex_model_api.indexing import elements_from_package
from moex_model_api.ports import (
    ArtifactRecord,
    DiagnosticRecord,
    JobRecord,
    ValidationRunRecord,
)


class ConformanceResponse(BaseModel):
    implementation_id: str
    overall_result: str
    is_conformant: bool
    diagnostic_count: int


class ValidationRunRequest(BaseModel):
    implementation_id: str = Field(default="moex:implementation:trading:1.0.0")
    workspace_id: str = Field(default="ws-default")


class ValidationRunResponse(BaseModel):
    id: str
    implementation_id: str
    overall_result: str
    reported_at: str


class WorkspaceCreate(BaseModel):
    id: str | None = None
    name: str = "default"


class WorkspaceMemberOut(BaseModel):
    user_id: str
    role: str


class WorkspaceOut(BaseModel):
    id: str
    name: str
    members: list[WorkspaceMemberOut] = Field(default_factory=list)


class JobCreate(BaseModel):
    kind: str = Field(pattern="^(validate|compile)$")
    workspace_id: str
    implementation_id: str = "moex:implementation:trading:1.0.0"


class JobOut(BaseModel):
    id: str
    workspace_id: str
    kind: str
    status: str
    implementation_id: str
    result_summary: str
    finished_at: str | None = None


class ModelIndexRebuildOut(BaseModel):
    index_id: str
    implementation_id: str
    revision: str
    element_count: int


class ElementHitOut(BaseModel):
    element_id: str
    element_kind: str
    name: str
    layer: str
    implementation_id: str


class ImplementationOut(BaseModel):
    id: str
    slug: str
    title: str
    implementation_path: str


def _actor(request: Request) -> str:
    return str(getattr(request.state, "actor", "dev") or "dev")


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _fingerprint(kind: str, workspace_id: str, implementation_id: str) -> str:
    raw = f"{kind}|{workspace_id}|{implementation_id}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]


def create_app(*, database_url: str | None = None) -> FastAPI:
    engine = make_engine(database_url)
    init_db(engine)
    factory: sessionmaker[Session] = session_factory(engine)

    app = FastAPI(title="MOEX Model API", version="0.2.0")
    app.add_middleware(DevAuthMiddleware)
    app.state.engine = engine
    app.state.session_factory = factory

    def get_session():
        session = factory()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def ensure_actor(request: Request, session: Session) -> str:
        actor = _actor(request)
        SqlIdentityStore(session).ensure_user(actor)
        return actor

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/implementations", response_model=list[ImplementationOut])
    def list_implementations() -> list[ImplementationOut]:
        root = find_repo_root()
        paths = SlicePaths.resolve(root=root)
        try:
            rel = paths.implementation.relative_to(paths.root).as_posix()
        except ValueError:
            rel = paths.implementation.as_posix()
        return [
            ImplementationOut(
                id="moex:implementation:trading:1.0.0",
                slug="trading",
                title="Trading platform",
                implementation_path=rel,
            )
        ]

    @app.get(
        "/implementations/trading/conformance",
        response_model=ConformanceResponse,
    )
    def trading_conformance() -> ConformanceResponse:
        root = find_repo_root()
        paths = SlicePaths.resolve(root=root)
        result = assess_implementation(
            schema_path=paths.schema,
            implementation_path=paths.implementation,
            implementation_id="moex:implementation:trading:1.0.0",
        )
        diags = []
        for assessment in result.report.assessments:
            diags.extend(assessment.diagnostics)
        return ConformanceResponse(
            implementation_id=result.implementation.id,
            overall_result=result.report.overall_result.value,
            is_conformant=result.report.is_conformant,
            diagnostic_count=len(diags),
        )

    @app.post("/workspaces", response_model=WorkspaceOut)
    def create_workspace(
        body: WorkspaceCreate,
        request: Request,
        session: Session = Depends(get_session),
    ) -> WorkspaceOut:
        actor = ensure_actor(request, session)
        ws_id = body.id or f"ws:{uuid4().hex[:10]}"
        store = SqlWorkspaceStore(session)
        ws = store.create(ws_id, body.name)
        store.add_member(ws.id, actor, role="owner")
        SqlAuditStore(session).record("workspace.create", actor, ws.id)
        members = store.list_members(ws.id)
        return WorkspaceOut(
            id=ws.id,
            name=ws.name,
            members=[
                WorkspaceMemberOut(user_id=m.user_id, role=m.role) for m in members
            ],
        )

    @app.get("/workspaces", response_model=list[WorkspaceOut])
    def list_workspaces(
        request: Request,
        session: Session = Depends(get_session),
    ) -> list[WorkspaceOut]:
        actor = ensure_actor(request, session)
        store = SqlWorkspaceStore(session)
        out: list[WorkspaceOut] = []
        for ws in store.list_for_user(actor):
            members = store.list_members(ws.id)
            out.append(
                WorkspaceOut(
                    id=ws.id,
                    name=ws.name,
                    members=[
                        WorkspaceMemberOut(user_id=m.user_id, role=m.role)
                        for m in members
                    ],
                )
            )
        return out

    @app.get("/workspaces/{workspace_id}", response_model=WorkspaceOut)
    def get_workspace(
        workspace_id: str,
        request: Request,
        session: Session = Depends(get_session),
    ) -> WorkspaceOut:
        ensure_actor(request, session)
        store = SqlWorkspaceStore(session)
        ws = store.get(workspace_id)
        if ws is None:
            raise HTTPException(status_code=404, detail="workspace not found")
        members = store.list_members(ws.id)
        return WorkspaceOut(
            id=ws.id,
            name=ws.name,
            members=[
                WorkspaceMemberOut(user_id=m.user_id, role=m.role) for m in members
            ],
        )

    @app.post("/jobs", response_model=JobOut)
    def create_job(
        body: JobCreate,
        request: Request,
        session: Session = Depends(get_session),
        idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
    ) -> JobOut:
        actor = ensure_actor(request, session)
        jobs = SqlJobStore(session)
        workspaces = SqlWorkspaceStore(session)
        fp = _fingerprint(body.kind, body.workspace_id, body.implementation_id)

        if idempotency_key:
            prior = jobs.get_by_idempotency(idempotency_key)
            if prior is not None:
                if prior.payload_fingerprint != fp:
                    raise HTTPException(
                        status_code=409,
                        detail="idempotency key reused with different payload",
                    )
                return JobOut(
                    id=prior.id,
                    workspace_id=prior.workspace_id,
                    kind=prior.kind,
                    status=prior.status,
                    implementation_id=prior.implementation_id,
                    result_summary=prior.result_summary,
                    finished_at=prior.finished_at,
                )

        if workspaces.get(body.workspace_id) is None:
            workspaces.create(body.workspace_id, body.workspace_id)
            workspaces.add_member(body.workspace_id, actor, role="owner")

        job_id = f"job:{uuid4().hex[:12]}"
        jobs.create_job(
            JobRecord(
                id=job_id,
                workspace_id=body.workspace_id,
                kind=body.kind,
                status="running",
                implementation_id=body.implementation_id,
                idempotency_key=idempotency_key,
                payload_fingerprint=fp,
                result_summary="",
            )
        )
        SqlAuditStore(session).record("job.create", actor, job_id)

        root = find_repo_root()
        paths = SlicePaths.resolve(root=root)
        finished = _now()

        try:
            if body.kind == "validate":
                result = assess_implementation(
                    schema_path=paths.schema,
                    implementation_path=paths.implementation,
                    implementation_id=body.implementation_id,
                )
                run_id = f"run:{uuid4().hex[:12]}"
                diags: list[DiagnosticRecord] = []
                for assessment in result.report.assessments:
                    for d in assessment.diagnostics:
                        diags.append(
                            DiagnosticRecord(
                                run_id=run_id,
                                code=d.diagnostic_code,
                                severity=d.severity.value,
                                message=d.diagnostic_message,
                            )
                        )
                SqlValidationRunStore(session).save_run(
                    ValidationRunRecord(
                        id=run_id,
                        implementation_id=result.implementation.id,
                        overall_result=result.report.overall_result.value,
                        reported_at=result.report.reported_at or finished,
                        workspace_id=body.workspace_id,
                        job_id=job_id,
                    ),
                    diags,
                    actor=actor,
                )
                summary = (
                    f"validate:{result.report.overall_result.value}"
                    f" run={run_id} diags={len(diags)}"
                )
                status = "succeeded"
            else:
                code, out = run_compile(paths, with_json_schema=False)
                if code != 0:
                    jobs.update_status(
                        job_id,
                        "failed",
                        result_summary=out[-2000:],
                        finished_at=finished,
                    )
                    raise HTTPException(status_code=500, detail="compile failed")
                manifest = (
                    paths.root / "generated" / "manifests" / "moex-dams-contracts.json"
                )
                digest = ""
                if manifest.is_file():
                    digest = (
                        "sha256:"
                        + hashlib.sha256(manifest.read_bytes()).hexdigest()
                    )
                art_id = f"art:{uuid4().hex[:12]}"
                jobs.attach_artifact(
                    ArtifactRecord(
                        id=art_id,
                        job_id=job_id,
                        kind="pydantic-contracts",
                        path_or_uri="generated/contracts/moex-dams/0.1",
                        content_digest=digest,
                    )
                )
                summary = f"compile:ok artifact={art_id}"
                status = "succeeded"
        except HTTPException:
            raise
        except Exception as exc:  # noqa: BLE001 — persist failure on job row
            jobs.update_status(
                job_id,
                "failed",
                result_summary=str(exc)[:2000],
                finished_at=finished,
            )
            raise HTTPException(status_code=500, detail=str(exc)) from exc

        updated = jobs.update_status(
            job_id, status, result_summary=summary, finished_at=finished
        )
        return JobOut(
            id=updated.id,
            workspace_id=updated.workspace_id,
            kind=updated.kind,
            status=updated.status,
            implementation_id=updated.implementation_id,
            result_summary=updated.result_summary,
            finished_at=updated.finished_at,
        )

    @app.get("/jobs/{job_id}", response_model=JobOut)
    def get_job(
        job_id: str,
        request: Request,
        session: Session = Depends(get_session),
    ) -> JobOut:
        ensure_actor(request, session)
        job = SqlJobStore(session).get_job(job_id)
        if job is None:
            raise HTTPException(status_code=404, detail="job not found")
        return JobOut(
            id=job.id,
            workspace_id=job.workspace_id,
            kind=job.kind,
            status=job.status,
            implementation_id=job.implementation_id,
            result_summary=job.result_summary,
            finished_at=job.finished_at,
        )

    @app.post("/model-index/rebuild", response_model=ModelIndexRebuildOut)
    def rebuild_model_index(
        request: Request,
        session: Session = Depends(get_session),
        implementation_id: str = "moex:implementation:trading:1.0.0",
    ) -> ModelIndexRebuildOut:
        actor = ensure_actor(request, session)
        root = find_repo_root()
        paths = SlicePaths.resolve(root=root)
        raw = paths.implementation.read_bytes()
        digest = "sha256:" + hashlib.sha256(raw).hexdigest()
        revision = digest.removeprefix("sha256:")[:12]
        data = yaml.safe_load(raw.decode("utf-8"))
        if not isinstance(data, dict):
            raise HTTPException(status_code=400, detail="invalid implementation YAML")
        elements = elements_from_package(data)
        index_id = f"idx:{implementation_id}:{revision}"
        SqlModelIndexProvider(session).rebuild(
            index_id=index_id,
            implementation_id=implementation_id,
            revision=revision,
            content_digest=digest,
            indexed_at=_now(),
            elements=elements,
        )
        SqlAuditStore(session).record("model_index.rebuild", actor, index_id)
        return ModelIndexRebuildOut(
            index_id=index_id,
            implementation_id=implementation_id,
            revision=revision,
            element_count=len(elements),
        )

    @app.get("/model-index/search", response_model=list[ElementHitOut])
    def search_model_index(
        q: str,
        request: Request,
        session: Session = Depends(get_session),
    ) -> list[ElementHitOut]:
        ensure_actor(request, session)
        hits = SqlModelIndexProvider(session).search(q)
        return [
            ElementHitOut(
                element_id=h.element_id,
                element_kind=h.element_kind,
                name=h.name,
                layer=h.layer,
                implementation_id=h.implementation_id,
            )
            for h in hits
        ]

    @app.post("/validation-runs", response_model=ValidationRunResponse)
    def create_validation_run(
        body: ValidationRunRequest,
        request: Request,
        session: Session = Depends(get_session),
    ) -> ValidationRunResponse:
        actor = ensure_actor(request, session)
        root = find_repo_root()
        paths = SlicePaths.resolve(root=root)
        result = assess_implementation(
            schema_path=paths.schema,
            implementation_path=paths.implementation,
            implementation_id=body.implementation_id,
        )
        SqlWorkspaceStore(session).ensure_workspace(body.workspace_id, body.workspace_id)
        run_id = f"run:{uuid4().hex[:12]}"
        diags: list[DiagnosticRecord] = []
        for assessment in result.report.assessments:
            for d in assessment.diagnostics:
                diags.append(
                    DiagnosticRecord(
                        run_id=run_id,
                        code=d.diagnostic_code,
                        severity=d.severity.value,
                        message=d.diagnostic_message,
                    )
                )
        record = ValidationRunRecord(
            id=run_id,
            implementation_id=result.implementation.id,
            overall_result=result.report.overall_result.value,
            reported_at=result.report.reported_at or "",
            workspace_id=body.workspace_id,
        )
        SqlValidationRunStore(session).save_run(record, diags, actor=actor)
        return ValidationRunResponse(
            id=record.id,
            implementation_id=record.implementation_id,
            overall_result=record.overall_result,
            reported_at=record.reported_at,
        )

    @app.get("/validation-runs/{run_id}", response_model=ValidationRunResponse)
    def get_validation_run(
        run_id: str,
        session: Session = Depends(get_session),
    ) -> ValidationRunResponse:
        row = SqlValidationRunStore(session).get_run(run_id)
        if row is None:
            raise HTTPException(status_code=404, detail="run not found")
        return ValidationRunResponse(
            id=row.id,
            implementation_id=row.implementation_id,
            overall_result=row.overall_result,
            reported_at=row.reported_at,
        )

    return app


app = create_app()
