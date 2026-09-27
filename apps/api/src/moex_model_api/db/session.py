"""Engine / session factory (adapter)."""

from __future__ import annotations

import os
from collections.abc import Iterator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from moex_model_api.db.models import Base

DEFAULT_URL = "sqlite:///:memory:"


def database_url() -> str:
    return os.environ.get("MOEX_DATABASE_URL", DEFAULT_URL)


def make_engine(url: str | None = None):
    url = url or database_url()
    if url.startswith("sqlite"):
        # StaticPool keeps a single :memory: connection across sessions.
        return create_engine(
            url,
            future=True,
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
    return create_engine(url, future=True)


def init_db(engine) -> None:
    Base.metadata.create_all(engine)


def session_factory(engine) -> sessionmaker[Session]:
    return sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)


def iter_sessions(factory: sessionmaker[Session]) -> Iterator[Session]:
    session = factory()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
