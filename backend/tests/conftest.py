from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.core.database import init_engine
from app.main import create_app
from app.models import Base


@pytest.fixture()
def client():
    # Default unit tests run on SQLite (no Docker required).
    os.environ["DATABASE_URL"] = "sqlite+pysqlite:///:memory:"
    os.environ["AUTO_CREATE_TABLES"] = "true"

    init_engine(os.environ["DATABASE_URL"])
    from app.core.database import engine

    assert engine is not None
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    app = create_app()
    with TestClient(app) as c:
        yield c
