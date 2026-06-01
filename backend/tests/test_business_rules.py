from __future__ import annotations

import pytest
from fastapi.testclient import TestClient


def test_unique_sku_enforced(client: TestClient):
    r1 = client.post("/api/products", json={"name": "A", "sku": "SKU1", "price": "10.00", "stock_qty": 5})
    assert r1.status_code == 201
    r2 = client.post("/api/products", json={"name": "B", "sku": "SKU1", "price": "12.00", "stock_qty": 1})
    assert r2.status_code == 409


def test_unique_email_enforced(client: TestClient):
    r1 = client.post("/api/customers", json={"name": "C1", "email": "x@example.com"})
    assert r1.status_code == 201
    r2 = client.post("/api/customers", json={"name": "C2", "email": "x@example.com"})
    assert r2.status_code == 409


def test_order_reduces_stock_and_prevents_insufficient(client: TestClient):
    p = client.post("/api/products", json={"name": "P1", "sku": "P1", "price": "5.00", "stock_qty": 2}).json()
    c = client.post("/api/customers", json={"name": "Cust", "email": "cust@example.com"}).json()

    ok = client.post(
        "/api/orders",
        json={"customer_id": c["id"], "items": [{"product_id": p["id"], "quantity": 2}]},
    )
    assert ok.status_code == 201

    p_after = client.get(f"/api/products/{p['id']}").json()
    assert p_after["stock_qty"] == 0

    bad = client.post(
        "/api/orders",
        json={"customer_id": c["id"], "items": [{"product_id": p["id"], "quantity": 1}]},
    )
    assert bad.status_code == 400
    detail = bad.json()["detail"]
    assert detail["message"] == "Insufficient stock"


def test_order_dedupes_items(client: TestClient):
    p = client.post("/api/products", json={"name": "P2", "sku": "P2", "price": "3.00", "stock_qty": 10}).json()
    c = client.post("/api/customers", json={"name": "Cust2", "email": "cust2@example.com"}).json()

    r = client.post(
        "/api/orders",
        json={
            "customer_id": c["id"],
            "items": [
                {"product_id": p["id"], "quantity": 2},
                {"product_id": p["id"], "quantity": 3},
            ],
        },
    )
    assert r.status_code == 201

    p_after = client.get(f"/api/products/{p['id']}").json()
    assert p_after["stock_qty"] == 5
