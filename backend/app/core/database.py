from __future__ import annotations

from contextlib import contextmanager
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings

engine = None
SessionLocal: sessionmaker[Session] | None = None


def init_engine(database_url: str | None = None) -> None:
    global engine, SessionLocal
    db_url = database_url or settings.database_url
    if db_url.startswith("sqlite+pysqlite:///") or db_url.startswith("sqlite+pysqlite:///:memory:"):
        connect_args = {"check_same_thread": False}
        if db_url.endswith(":memory:"):
            engine = create_engine(db_url, connect_args=connect_args, poolclass=StaticPool)
        else:
            engine = create_engine(db_url, connect_args=connect_args)
    else:
        engine = create_engine(db_url, pool_pre_ping=True)
    SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


@contextmanager
def session_scope() -> Generator[Session, None, None]:
    if SessionLocal is None:
        init_engine()
    assert SessionLocal is not None
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def get_session() -> Generator[Session, None, None]:
    with session_scope() as session:
        yield session
