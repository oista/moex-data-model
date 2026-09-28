"""FastAPI application factory."""

from __future__ import annotations

import hashlib
import json
import tempfile
from datetime import datetime, timezone
from io import StringIO
from pathlib import Path
from uuid import uuid4

import yaml
from fastapi import Depends, FastAPI, Header, HTTPException, Request, Response
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel, Field
from ruamel.yaml import YAML
from sqlalchemy.orm import Session, sessionmaker

from moex_dams.application.assess import assess_implementation
from moex_dams.application.diff import diff_implementations
from moex_drawdb import DrawDbProjectionService
from moex_git import FileChange, make_git_provider
from moex_git.ports import GitProvider
from moex_model_cli.bootstrap import SlicePaths, find_repo_root
from moex_model_cli.commands.compile import run_compile
from moex_model_api.auth import DevAuthMiddleware
from moex_model_api.db import models as orm
from moex_model_api.db.session import init_db, make_engine, session_factory
from moex_model_api.db.stores import (
    SqlAuditStore,
    SqlDocumentStore,
    SqlIdentityStore,
    SqlJobStore,
    SqlModelIndexProvider,
    SqlPublicationStore,
    SqlValidationRunStore,
    SqlWorkspaceStore,
)
from moex_model_api.diagnostics import diagnostic_record
from moex_model_api.diagram_sessions import DiagramSession, DiagramSessionStore
from moex_model_api.indexing import elements_from_package
from moex_model_api.ports import (
    ArtifactRecord,
    JobRecord,
    PublicationRecord,
    ValidationRunRecord,
)
from moex_model_api.yaml_mutate import MutationConflict, MutationError, apply_mutation


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
    source: str = Field(default="published", pattern="^(published|draft)$")


class ImplementationBodyOut(BaseModel):
    content: str
    content_digest: str
    path: str


class DocumentOut(BaseModel):
    workspace_id: str
    doc_key: str
    content: str
    base_digest: str
    updated_by: str


class DocumentPut(BaseModel):
    content: str
    base_digest: str = ""


class MutationRequest(BaseModel):
    op: str = Field(
        pattern=(
            "^(add_logical_entity|add_logical_attribute|"
            "update_logical_entity|delete_logical_entity|"
            "update_logical_attribute|delete_logical_attribute|"
            "add_relationship|update_relationship|delete_relationship|"
            "add_mapping|update_mapping|delete_mapping|"
            "add_physical_object|update_physical_object|delete_physical_object|"
            "add_physical_field|update_physical_field|delete_physical_field)$"
        )
    )
    entity: dict | None = None
    attribute: dict | None = None
    relationship: dict | None = None
    mapping: dict | None = None
    physical_object: dict | None = None
    physical_field: dict | None = None
    owner_element_id: str | None = None
    element_id: str | None = None
    patch: dict | None = None


class SemanticDiffChangeOut(BaseModel):
    change_code: str
    category: str
    subject_ref: str | None = None
    message: str
    path: str | None = None


class SemanticDiffOut(BaseModel):
    id: str
    base_label: str
    target_label: str
    changes: list[SemanticDiffChangeOut]
    has_breaking: bool
    counts: dict[str, int]


class PublicationCreate(BaseModel):
    workspace_id: str
    implementation_id: str = "moex:implementation:trading:1.0.0"
    title: str = "Workbench publish trading draft"
    base_ref: str = "HEAD"


class PublicationOut(BaseModel):
    id: str
    workspace_id: str
    implementation_id: str
    branch_name: str
    base_revision: str
    commit_sha: str
    review_url: str
    review_id: str
    status: str


class JobOut(BaseModel):
    id: str
    workspace_id: str
    kind: str
    status: str
    implementation_id: str
    result_summary: str
    finished_at: str | None = None


class ArtifactOut(BaseModel):
    id: str
    job_id: str
    kind: str
    path_or_uri: str
    content_digest: str


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


class DiagramCreate(BaseModel):
    profile: str = Field(default="logical", pattern="^(logical|physical)$")


class DiagramSessionOut(BaseModel):
    session_id: str
    workspace_id: str
    profile: str
    dbml: str


class DiagramLayoutPut(BaseModel):
    nodes: dict[str, dict] = Field(default_factory=dict)
    model_revision: str = ""


class DiagramLayoutOut(BaseModel):
    diagram_id: str
    workspace_id: str
    profile: str
    model_revision: str
    nodes: dict[str, dict]


class DiagramSubmit(BaseModel):
    dbml: str


class DiagramRejectedOut(BaseModel):
    code: str
    message: str
    path: str | None = None


class DiagramSubmitOut(BaseModel):
    session_id: str
    rejected: list[DiagramRejectedOut]
    op_count: int
    semantic_diff: SemanticDiffOut


class DiagramApplyOut(BaseModel):
    workspace_id: str
    doc_key: str
    content: str
    base_digest: str


class ImplementationOut(BaseModel):
    id: str
    slug: str
    title: str
    implementation_path: str


def _actor(request: Request) -> str:
    return str(getattr(request.state, "actor", "dev") or "dev")


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _fingerprint(
    kind: str, workspace_id: str, implementation_id: str, source: str = "published"
) -> str:
    raw = f"{kind}|{workspace_id}|{implementation_id}|{source}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]


def _content_digest(text: str) -> str:
    return "sha256:" + hashlib.sha256(text.encode("utf-8")).hexdigest()


def _publication_fingerprint(
    workspace_id: str, implementation_id: str, content: str
) -> str:
    raw = f"{workspace_id}|{implementation_id}|{_content_digest(content)}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]


def create_app(
    *,
    database_url: str | None = None,
    git_provider: GitProvider | None = None,
) -> FastAPI:
    engine = make_engine(database_url)
    init_db(engine)
    factory: sessionmaker[Session] = session_factory(engine)

    app = FastAPI(title="MOEX Model API", version="0.5.0")
    app.add_middleware(DevAuthMiddleware)
    app.state.engine = engine
    app.state.session_factory = factory
    app.state.git_provider = git_provider or make_git_provider(
        repo_root=find_repo_root()
    )
    app.state.diagram_sessions = DiagramSessionStore()
    app.state.drawdb = DrawDbProjectionService()

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
        "/implementations/trading/body",
        response_model=ImplementationBodyOut,
    )
    def trading_body() -> ImplementationBodyOut:
        root = find_repo_root()
        paths = SlicePaths.resolve(root=root)
        text = paths.implementation.read_text(encoding="utf-8")
        try:
            rel = paths.implementation.relative_to(paths.root).as_posix()
        except ValueError:
            rel = paths.implementation.as_posix()
        return ImplementationBodyOut(
            content=text,
            content_digest=_content_digest(text),
            path=rel,
        )

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

    @app.get(
        "/workspaces/{workspace_id}/documents/trading",
        response_model=DocumentOut,
    )
    def get_trading_document(
        workspace_id: str,
        request: Request,
        session: Session = Depends(get_session),
    ) -> DocumentOut:
        ensure_actor(request, session)
        doc = SqlDocumentStore(session).get(workspace_id, "trading")
        if doc is None:
            raise HTTPException(status_code=404, detail="document not found")
        return DocumentOut(
            workspace_id=doc.workspace_id,
            doc_key=doc.doc_key,
            content=doc.content,
            base_digest=doc.base_digest,
            updated_by=doc.updated_by,
        )

    @app.put(
        "/workspaces/{workspace_id}/documents/trading",
        response_model=DocumentOut,
    )
    def put_trading_document(
        workspace_id: str,
        body: DocumentPut,
        request: Request,
        session: Session = Depends(get_session),
    ) -> DocumentOut:
        actor = ensure_actor(request, session)
        workspaces = SqlWorkspaceStore(session)
        if workspaces.get(workspace_id) is None:
            workspaces.create(workspace_id, workspace_id)
            workspaces.add_member(workspace_id, actor, role="owner")
        else:
            workspaces.add_member(workspace_id, actor, role="editor")
        digest = body.base_digest or _content_digest(body.content)
        doc = SqlDocumentStore(session).upsert(
            workspace_id=workspace_id,
            doc_key="trading",
            content=body.content,
            base_digest=digest,
            updated_by=actor,
        )
        SqlAuditStore(session).record(
            "document.put", actor, f"{workspace_id}:trading"
        )
        return DocumentOut(
            workspace_id=doc.workspace_id,
            doc_key=doc.doc_key,
            content=doc.content,
            base_digest=doc.base_digest,
            updated_by=doc.updated_by,
        )

    @app.post(
        "/workspaces/{workspace_id}/documents/trading/mutations",
        response_model=DocumentOut,
    )
    def mutate_trading_document(
        workspace_id: str,
        body: MutationRequest,
        request: Request,
        session: Session = Depends(get_session),
    ) -> DocumentOut:
        actor = ensure_actor(request, session)
        workspaces = SqlWorkspaceStore(session)
        docs = SqlDocumentStore(session)
        if workspaces.get(workspace_id) is None:
            workspaces.create(workspace_id, workspace_id)
            workspaces.add_member(workspace_id, actor, role="owner")
        else:
            workspaces.add_member(workspace_id, actor, role="editor")

        existing = docs.get(workspace_id, "trading")
        root = find_repo_root()
        paths = SlicePaths.resolve(root=root)
        published = paths.implementation.read_text(encoding="utf-8")
        published_digest = _content_digest(published)
        if existing is None:
            base_text = published
            base_digest = published_digest
        else:
            base_text = existing.content
            base_digest = existing.base_digest or published_digest

        payload = body.model_dump()
        try:
            new_text = apply_mutation(base_text, payload)
        except MutationConflict as exc:
            raise HTTPException(status_code=409, detail=str(exc)) from exc
        except MutationError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

        doc = docs.upsert(
            workspace_id=workspace_id,
            doc_key="trading",
            content=new_text,
            base_digest=base_digest,
            updated_by=actor,
        )
        SqlAuditStore(session).record(
            "document.mutate", actor, f"{workspace_id}:trading:{body.op}"
        )
        return DocumentOut(
            workspace_id=doc.workspace_id,
            doc_key=doc.doc_key,
            content=doc.content,
            base_digest=doc.base_digest,
            updated_by=doc.updated_by,
        )

    @app.post(
        "/workspaces/{workspace_id}/semantic-diff",
        response_model=SemanticDiffOut,
    )
    def preview_semantic_diff(
        workspace_id: str,
        request: Request,
        session: Session = Depends(get_session),
    ) -> SemanticDiffOut:
        """Compare published trading YAML (base) vs workspace draft (target)."""
        actor = ensure_actor(request, session)
        draft = SqlDocumentStore(session).get(workspace_id, "trading")
        if draft is None:
            raise HTTPException(status_code=400, detail="draft document missing")

        root = find_repo_root()
        paths = SlicePaths.resolve(root=root)
        tmp_path: Path | None = None
        try:
            tmp = tempfile.NamedTemporaryFile(
                mode="w", suffix=".yaml", encoding="utf-8", delete=False
            )
            tmp.write(draft.content)
            tmp.close()
            tmp_path = Path(tmp.name)
            report = diff_implementations(
                schema_path=paths.schema,
                left_path=paths.implementation,
                right_path=tmp_path,
                base_label="published",
                target_label=f"draft:{workspace_id}",
            )
        finally:
            if tmp_path is not None:
                tmp_path.unlink(missing_ok=True)

        SqlAuditStore(session).record(
            "semantic_diff.preview",
            actor,
            f"{workspace_id}:trading",
        )
        return SemanticDiffOut(
            id=report.id,
            base_label=report.base_label,
            target_label=report.target_label,
            changes=[
                SemanticDiffChangeOut(
                    change_code=c.change_code,
                    category=c.category.value,
                    subject_ref=c.subject_ref,
                    message=c.message,
                    path=c.path,
                )
                for c in report.changes
            ],
            has_breaking=report.has_breaking,
            counts=report.counts_by_category(),
        )

    def _draft_yaml(workspace_id: str, session: Session) -> str:
        draft = SqlDocumentStore(session).get(workspace_id, "trading")
        if draft is not None:
            return draft.content
        root = find_repo_root()
        paths = SlicePaths.resolve(root=root)
        return paths.implementation.read_text(encoding="utf-8")

    def _dump_yaml(data: dict) -> str:
        y = YAML()
        y.preserve_quotes = True
        buf = StringIO()
        y.dump(data, buf)
        return buf.getvalue()

    @app.post(
        "/workspaces/{workspace_id}/diagrams",
        response_model=DiagramSessionOut,
    )
    def open_diagram(
        workspace_id: str,
        body: DiagramCreate,
        request: Request,
        session: Session = Depends(get_session),
    ) -> DiagramSessionOut:
        actor = ensure_actor(request, session)
        workspaces = SqlWorkspaceStore(session)
        if workspaces.get(workspace_id) is None:
            workspaces.create(workspace_id, workspace_id)
            workspaces.add_member(workspace_id, actor, role="owner")
        yaml_text = _draft_yaml(workspace_id, session)
        data = yaml.safe_load(yaml_text)
        if not isinstance(data, dict):
            raise HTTPException(status_code=400, detail="draft is not a mapping")
        profile = body.profile  # type: ignore[assignment]
        dbml = app.state.drawdb.to_dbml(data, profile=profile)
        sid = str(uuid4())
        app.state.diagram_sessions.put(
            DiagramSession(
                session_id=sid,
                workspace_id=workspace_id,
                profile=profile,
                dbml=dbml,
                base_yaml=yaml_text,
            )
        )
        SqlAuditStore(session).record(
            "diagram.open", actor, f"{workspace_id}:{profile}:{sid}"
        )
        return DiagramSessionOut(
            session_id=sid,
            workspace_id=workspace_id,
            profile=profile,
            dbml=dbml,
        )

    @app.get(
        "/workspaces/{workspace_id}/diagrams/{session_id}",
        response_model=DiagramSessionOut,
    )
    def get_diagram(
        workspace_id: str,
        session_id: str,
        request: Request,
        session: Session = Depends(get_session),
    ) -> DiagramSessionOut:
        ensure_actor(request, session)
        ds = app.state.diagram_sessions.get(session_id)
        if ds is None or ds.workspace_id != workspace_id:
            raise HTTPException(status_code=404, detail="diagram session not found")
        return DiagramSessionOut(
            session_id=ds.session_id,
            workspace_id=ds.workspace_id,
            profile=ds.profile,
            dbml=ds.dbml,
        )

    @app.put(
        "/workspaces/{workspace_id}/diagrams/{session_id}/layout",
        response_model=DiagramLayoutOut,
    )
    def put_diagram_layout(
        workspace_id: str,
        session_id: str,
        body: DiagramLayoutPut,
        request: Request,
        session: Session = Depends(get_session),
    ) -> DiagramLayoutOut:
        actor = ensure_actor(request, session)
        ds = app.state.diagram_sessions.get(session_id)
        if ds is None or ds.workspace_id != workspace_id:
            raise HTTPException(status_code=404, detail="diagram session not found")
        diagram_id = f"moex:diagram:{workspace_id}:{ds.profile}"
        nodes_json = json.dumps(body.nodes, sort_keys=True)
        row = session.get(orm.DiagramLayout, diagram_id)
        if row is None:
            row = orm.DiagramLayout(
                diagram_id=diagram_id,
                workspace_id=workspace_id,
                implementation_id="moex:implementation:trading:1.0.0",
                profile=ds.profile,
                model_revision=body.model_revision,
                nodes_json=nodes_json,
            )
            session.add(row)
        else:
            row.nodes_json = nodes_json
            row.model_revision = body.model_revision
        session.flush()
        SqlAuditStore(session).record(
            "diagram.layout", actor, diagram_id
        )
        return DiagramLayoutOut(
            diagram_id=diagram_id,
            workspace_id=workspace_id,
            profile=ds.profile,
            model_revision=body.model_revision,
            nodes=body.nodes,
        )

    @app.post(
        "/workspaces/{workspace_id}/diagrams/{session_id}/submit",
        response_model=DiagramSubmitOut,
    )
    def submit_diagram(
        workspace_id: str,
        session_id: str,
        body: DiagramSubmit,
        request: Request,
        session: Session = Depends(get_session),
    ) -> DiagramSubmitOut:
        actor = ensure_actor(request, session)
        ds = app.state.diagram_sessions.get(session_id)
        if ds is None or ds.workspace_id != workspace_id:
            raise HTTPException(status_code=404, detail="diagram session not found")
        base = yaml.safe_load(ds.base_yaml)
        if not isinstance(base, dict):
            raise HTTPException(status_code=400, detail="base yaml invalid")
        merged, patch = app.state.drawdb.from_dbml(
            base, body.dbml, profile=ds.profile
        )
        merged_yaml = _dump_yaml(merged)
        ds.dbml = body.dbml
        ds.last_merged_yaml = merged_yaml
        ds.last_patch = patch.model_dump()
        ds.last_rejected = [r.model_dump() for r in patch.rejected]
        app.state.diagram_sessions.put(ds)

        root = find_repo_root()
        paths = SlicePaths.resolve(root=root)
        left_tmp = right_tmp = None
        try:
            left = tempfile.NamedTemporaryFile(
                mode="w", suffix=".yaml", encoding="utf-8", delete=False
            )
            left.write(ds.base_yaml)
            left.close()
            left_tmp = Path(left.name)
            right = tempfile.NamedTemporaryFile(
                mode="w", suffix=".yaml", encoding="utf-8", delete=False
            )
            right.write(merged_yaml)
            right.close()
            right_tmp = Path(right.name)
            report = diff_implementations(
                schema_path=paths.schema,
                left_path=left_tmp,
                right_path=right_tmp,
                base_label="diagram-base",
                target_label=f"diagram:{session_id}",
            )
        finally:
            if left_tmp is not None:
                left_tmp.unlink(missing_ok=True)
            if right_tmp is not None:
                right_tmp.unlink(missing_ok=True)

        SqlAuditStore(session).record(
            "diagram.submit", actor, f"{workspace_id}:{session_id}"
        )
        return DiagramSubmitOut(
            session_id=session_id,
            rejected=[
                DiagramRejectedOut(
                    code=r.code.value,
                    message=r.message,
                    path=r.path,
                )
                for r in patch.rejected
            ],
            op_count=len(patch.ops),
            semantic_diff=SemanticDiffOut(
                id=report.id,
                base_label=report.base_label,
                target_label=report.target_label,
                changes=[
                    SemanticDiffChangeOut(
                        change_code=c.change_code,
                        category=c.category.value,
                        subject_ref=c.subject_ref,
                        message=c.message,
                        path=c.path,
                    )
                    for c in report.changes
                ],
                has_breaking=report.has_breaking,
                counts=report.counts_by_category(),
            ),
        )

    @app.post(
        "/workspaces/{workspace_id}/diagrams/{session_id}/apply",
        response_model=DiagramApplyOut,
    )
    def apply_diagram(
        workspace_id: str,
        session_id: str,
        request: Request,
        session: Session = Depends(get_session),
    ) -> DiagramApplyOut:
        actor = ensure_actor(request, session)
        ds = app.state.diagram_sessions.get(session_id)
        if ds is None or ds.workspace_id != workspace_id:
            raise HTTPException(status_code=404, detail="diagram session not found")
        if not ds.last_merged_yaml:
            raise HTTPException(
                status_code=400, detail="submit diagram before apply"
            )
        if ds.last_rejected:
            raise HTTPException(
                status_code=400,
                detail="cannot apply while rejected ops remain; fix DBML and re-submit",
            )
        root = find_repo_root()
        paths = SlicePaths.resolve(root=root)
        published = paths.implementation.read_text(encoding="utf-8")
        published_digest = _content_digest(published)
        docs = SqlDocumentStore(session)
        existing = docs.get(workspace_id, "trading")
        base_digest = (
            existing.base_digest if existing is not None else published_digest
        )
        doc = docs.upsert(
            workspace_id=workspace_id,
            doc_key="trading",
            content=ds.last_merged_yaml,
            base_digest=base_digest,
            updated_by=actor,
        )
        SqlAuditStore(session).record(
            "diagram.apply", actor, f"{workspace_id}:{session_id}"
        )
        return DiagramApplyOut(
            workspace_id=doc.workspace_id,
            doc_key=doc.doc_key,
            content=doc.content,
            base_digest=doc.base_digest,
        )

    def _publication_out(row: PublicationRecord) -> PublicationOut:
        return PublicationOut(
            id=row.id,
            workspace_id=row.workspace_id,
            implementation_id=row.implementation_id,
            branch_name=row.branch_name,
            base_revision=row.base_revision,
            commit_sha=row.commit_sha,
            review_url=row.review_url,
            review_id=row.review_id,
            status=row.status,
        )

    @app.post("/publications", response_model=PublicationOut)
    def create_publication(
        body: PublicationCreate,
        request: Request,
        session: Session = Depends(get_session),
        idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
    ) -> PublicationOut:
        actor = ensure_actor(request, session)
        workspaces = SqlWorkspaceStore(session)
        docs = SqlDocumentStore(session)
        pubs = SqlPublicationStore(session)

        draft = docs.get(body.workspace_id, "trading")
        if draft is None:
            raise HTTPException(status_code=400, detail="draft document missing")

        fp = _publication_fingerprint(
            body.workspace_id, body.implementation_id, draft.content
        )
        if idempotency_key:
            prior = pubs.get_by_idempotency(idempotency_key)
            if prior is not None:
                if prior.payload_fingerprint != fp:
                    raise HTTPException(
                        status_code=409,
                        detail="idempotency key reused with different payload",
                    )
                return _publication_out(prior)

        if workspaces.get(body.workspace_id) is None:
            raise HTTPException(status_code=404, detail="workspace not found")

        root = find_repo_root()
        paths = SlicePaths.resolve(root=root)

        from moex_model_cli.gates.publish_gate import verify_publish_gate

        gate_errors = verify_publish_gate(root=root, refresh_bundle=False)
        if gate_errors:
            raise HTTPException(
                status_code=422,
                detail={
                    "message": "publish-gate failed",
                    "errors": gate_errors[:20],
                },
            )

        tmp_path: Path | None = None
        try:
            tmp = tempfile.NamedTemporaryFile(
                mode="w", suffix=".yaml", encoding="utf-8", delete=False
            )
            tmp.write(draft.content)
            tmp.close()
            tmp_path = Path(tmp.name)
            result = assess_implementation(
                schema_path=paths.schema,
                implementation_path=tmp_path,
                implementation_id=body.implementation_id,
            )
        finally:
            if tmp_path is not None:
                tmp_path.unlink(missing_ok=True)

        if not result.report.is_conformant:
            raise HTTPException(
                status_code=422,
                detail=(
                    "draft is not conformant; "
                    f"overall={result.report.overall_result.value}"
                ),
            )

        try:
            rel = paths.implementation.relative_to(paths.root).as_posix()
        except ValueError:
            rel = paths.implementation.name

        git: GitProvider = request.app.state.git_provider
        base_revision = git.resolve_revision(body.base_ref)
        short = uuid4().hex[:8]
        branch_name = f"workbench/publish-{short}"
        pub_id = f"pub:{short}"

        try:
            git.create_branch(base_revision, branch_name)
            commit_sha = git.commit_files(
                branch_name,
                [
                    FileChange(
                        path=rel,
                        content=draft.content.encode("utf-8"),
                    )
                ],
            )
            review = git.create_review(branch_name, body.title)
            status = "submitted"
        except Exception as exc:  # noqa: BLE001
            failed = PublicationRecord(
                id=pub_id,
                workspace_id=body.workspace_id,
                implementation_id=body.implementation_id,
                doc_key="trading",
                branch_name=branch_name,
                base_revision=base_revision,
                commit_sha="",
                review_url="",
                review_id="",
                status="failed",
                actor=actor,
                idempotency_key=idempotency_key,
                payload_fingerprint=fp,
            )
            pubs.create(failed)
            SqlAuditStore(session).record(
                "publication.failed", actor, f"{pub_id}:{exc}"
            )
            raise HTTPException(
                status_code=500, detail=f"publication failed: {exc}"
            ) from exc

        row = PublicationRecord(
            id=pub_id,
            workspace_id=body.workspace_id,
            implementation_id=body.implementation_id,
            doc_key="trading",
            branch_name=branch_name,
            base_revision=base_revision,
            commit_sha=commit_sha,
            review_url=review.url,
            review_id=review.identifier,
            status=status,
            actor=actor,
            idempotency_key=idempotency_key,
            payload_fingerprint=fp,
        )
        pubs.create(row)
        SqlAuditStore(session).record(
            "publication.submit", actor, f"{pub_id}:{branch_name}"
        )
        return _publication_out(row)

    @app.get("/publications/{publication_id}", response_model=PublicationOut)
    def get_publication(
        publication_id: str,
        request: Request,
        session: Session = Depends(get_session),
    ) -> PublicationOut:
        ensure_actor(request, session)
        row = SqlPublicationStore(session).get(publication_id)
        if row is None:
            raise HTTPException(status_code=404, detail="publication not found")
        return _publication_out(row)

    @app.post("/jobs", response_model=JobOut)
    def create_job(
        body: JobCreate,
        request: Request,
        session: Session = Depends(get_session),
        idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
    ) -> JobOut:
        actor = ensure_actor(request, session)
        if body.kind == "compile" and body.source == "draft":
            raise HTTPException(
                status_code=400, detail="compile does not support source=draft"
            )
        jobs = SqlJobStore(session)
        workspaces = SqlWorkspaceStore(session)
        fp = _fingerprint(
            body.kind, body.workspace_id, body.implementation_id, body.source
        )

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
        tmp_path: Path | None = None
        summary = ""
        status = "failed"

        try:
            if body.kind == "validate":
                impl_path = paths.implementation
                if body.source == "draft":
                    draft = SqlDocumentStore(session).get(
                        body.workspace_id, "trading"
                    )
                    if draft is None:
                        jobs.update_status(
                            job_id,
                            "failed",
                            result_summary="draft document missing",
                            finished_at=finished,
                        )
                        raise HTTPException(
                            status_code=400, detail="draft document missing"
                        )
                    tmp = tempfile.NamedTemporaryFile(
                        mode="w",
                        suffix=".yaml",
                        encoding="utf-8",
                        delete=False,
                    )
                    tmp.write(draft.content)
                    tmp.close()
                    tmp_path = Path(tmp.name)
                    impl_path = tmp_path
                result = assess_implementation(
                    schema_path=paths.schema,
                    implementation_path=impl_path,
                    implementation_id=body.implementation_id,
                )
                run_id = f"run:{uuid4().hex[:12]}"
                diags = []
                for assessment in result.report.assessments:
                    for d in assessment.diagnostics:
                        diags.append(diagnostic_record(run_id, d))
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
                    f" source={body.source} run={run_id} diags={len(diags)}"
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
        finally:
            if tmp_path is not None:
                tmp_path.unlink(missing_ok=True)

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

    @app.get("/jobs/{job_id}/artifacts", response_model=list[ArtifactOut])
    def list_job_artifacts(
        job_id: str,
        request: Request,
        session: Session = Depends(get_session),
    ) -> list[ArtifactOut]:
        ensure_actor(request, session)
        jobs = SqlJobStore(session)
        if jobs.get_job(job_id) is None:
            raise HTTPException(status_code=404, detail="job not found")
        return [
            ArtifactOut(
                id=a.id,
                job_id=a.job_id,
                kind=a.kind,
                path_or_uri=a.path_or_uri,
                content_digest=a.content_digest,
            )
            for a in jobs.list_artifacts(job_id)
        ]

    @app.get("/jobs/{job_id}/artifacts/{artifact_id}/content")
    def get_job_artifact_content(
        job_id: str,
        artifact_id: str,
        request: Request,
        session: Session = Depends(get_session),
    ) -> Response:
        ensure_actor(request, session)
        jobs = SqlJobStore(session)
        if jobs.get_job(job_id) is None:
            raise HTTPException(status_code=404, detail="job not found")
        artifacts = jobs.list_artifacts(job_id)
        match = next((a for a in artifacts if a.id == artifact_id), None)
        if match is None:
            raise HTTPException(status_code=404, detail="artifact not found")

        root = find_repo_root()
        path = Path(match.path_or_uri)
        if not path.is_absolute():
            path = root / path
        if path.is_file():
            try:
                text = path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                return Response(
                    content=path.read_bytes(),
                    media_type="application/octet-stream",
                    headers={
                        "Content-Disposition": f'attachment; filename="{path.name}"'
                    },
                )
            return PlainTextResponse(text)
        if path.is_dir():
            lines = [f"# directory: {match.path_or_uri}"]
            for child in sorted(path.rglob("*")):
                if child.is_file():
                    rel = child.relative_to(path).as_posix()
                    lines.append(rel)
            return PlainTextResponse("\n".join(lines) + "\n")
        raise HTTPException(status_code=404, detail="artifact path not found on disk")

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
        diags = []
        for assessment in result.report.assessments:
            for d in assessment.diagnostics:
                diags.append(diagnostic_record(run_id, d))
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
