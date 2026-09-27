"""FastAPI application factory."""

from __future__ import annotations

from uuid import uuid4

from fastapi import Depends, FastAPI, HTTPException, Request
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session, sessionmaker

from moex_dams.application.assess import assess_implementation
from moex_model_cli.bootstrap import SlicePaths, find_repo_root
from moex_model_api.auth import DevAuthMiddleware
from moex_model_api.db.session import init_db, make_engine, session_factory
from moex_model_api.db.stores import SqlValidationRunStore, SqlWorkspaceStore
from moex_model_api.ports import DiagnosticRecord, ValidationRunRecord


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


def create_app(*, database_url: str | None = None) -> FastAPI:
    engine = make_engine(database_url)
    init_db(engine)
    factory: sessionmaker[Session] = session_factory(engine)

    app = FastAPI(title="MOEX Model API", version="0.1.0")
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

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

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

    @app.post("/validation-runs", response_model=ValidationRunResponse)
    def create_validation_run(
        body: ValidationRunRequest,
        request: Request,
        session: Session = Depends(get_session),
    ) -> ValidationRunResponse:
        _ = getattr(request.state, "actor", "dev")
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
        )
        SqlValidationRunStore(session).save_run(record, diags)
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
