from __future__ import annotations

import os

import pytest
from fastapi.testclient import TestClient

try:
    from testcontainers.postgres import PostgresContainer
except Exception:  # pragma: no cover
    PostgresContainer = None

from app.core.database import init_engine
from app.main import create_app
from app.models import Base


def _docker_available() -> bool:
    import shutil
    import subprocess

    if shutil.which("docker") is None:
        return False
    try:
        subprocess.check_output(["docker", "info"], stderr=subprocess.STDOUT, timeout=3)
        return True
    except Exception:
        return False


@pytest.mark.integration
@pytest.mark.skipif(
    os.getenv("RUN_INTEGRATION") != "1" or PostgresContainer is None or not _docker_available(),
    reason="Set RUN_INTEGRATION=1 and ensure Docker daemon is running to execute PostgreSQL integration tests.",
)
def test_postgres_smoke_order_flow():
    assert PostgresContainer is not None
    with PostgresContainer("postgres:16") as pg:
        db_url = pg.get_connection_url().replace("postgresql://", "postgresql+psycopg://")
        os.environ["DATABASE_URL"] = db_url
        os.environ["AUTO_CREATE_TABLES"] = "true"

        init_engine(db_url)
        from app.core.database import engine

        assert engine is not None
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)

        app = create_app()
        with TestClient(app) as client:
            p = client.post(
                "/api/products",
                json={"name": "P1", "sku": "SKU-PG-1", "price": "10.00", "stock_qty": 3},
            ).json()
            c = client.post("/api/customers", json={"name": "C", "email": "pg@example.com"}).json()
            r = client.post("/api/orders", json={"customer_id": c["id"], "items": [{"product_id": p["id"], "quantity": 2}]})
            assert r.status_code == 201
            p_after = client.get(f"/api/products/{p['id']}").json()
            assert p_after["stock_qty"] == 1

