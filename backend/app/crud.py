from __future__ import annotations

from typing import Iterable

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models import Customer, Order, OrderItem, Product
from app.schemas import CustomerCreate, CustomerUpdate, OrderCreate, ProductCreate, ProductUpdate


def create_product(session: Session, data: ProductCreate) -> Product:
    product = Product(name=data.name, sku=data.sku, price=data.price, stock_qty=data.stock_qty)
    session.add(product)
    try:
        session.flush()
    except IntegrityError:
        raise HTTPException(status_code=409, detail="SKU must be unique")
    return product


def list_products(session: Session) -> list[Product]:
    return list(session.scalars(select(Product).order_by(Product.id)))


def get_product(session: Session, product_id: int) -> Product:
    product = session.get(Product, product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


def update_product(session: Session, product_id: int, data: ProductUpdate) -> Product:
    product = get_product(session, product_id)
    if data.name is not None:
        product.name = data.name
    if data.price is not None:
        product.price = data.price
    if data.stock_qty is not None:
        product.stock_qty = data.stock_qty
    session.add(product)
    session.flush()
    return product


def delete_product(session: Session, product_id: int) -> None:
    product = get_product(session, product_id)
    session.delete(product)
    session.flush()


def create_customer(session: Session, data: CustomerCreate) -> Customer:
    customer = Customer(name=data.name, email=str(data.email).lower())
    session.add(customer)
    try:
        session.flush()
    except IntegrityError:
        raise HTTPException(status_code=409, detail="Customer email must be unique")
    return customer


def list_customers(session: Session) -> list[Customer]:
    return list(session.scalars(select(Customer).order_by(Customer.id)))


def get_customer(session: Session, customer_id: int) -> Customer:
    customer = session.get(Customer, customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer


def update_customer(session: Session, customer_id: int, data: CustomerUpdate) -> Customer:
    customer = get_customer(session, customer_id)
    if data.name is not None:
        customer.name = data.name
    if data.email is not None:
        customer.email = str(data.email).lower()
    session.add(customer)
    try:
        session.flush()
    except IntegrityError:
        raise HTTPException(status_code=409, detail="Customer email must be unique")
    return customer


def delete_customer(session: Session, customer_id: int) -> None:
    customer = get_customer(session, customer_id)
    session.delete(customer)
    session.flush()


def _dedupe_items(items: Iterable[tuple[int, int]]) -> dict[int, int]:
    merged: dict[int, int] = {}
    for product_id, qty in items:
        merged[product_id] = merged.get(product_id, 0) + qty
    return merged


def create_order(session: Session, data: OrderCreate) -> Order:
    customer = get_customer(session, data.customer_id)

    merged = _dedupe_items([(i.product_id, i.quantity) for i in data.items])
    product_ids = list(merged.keys())
    stmt = select(Product).where(Product.id.in_(product_ids))
    # SQLite doesn't support SELECT ... FOR UPDATE; PostgreSQL does.
    if session.bind is not None and session.bind.dialect.name != "sqlite":
        stmt = stmt.with_for_update()
    products = list(session.scalars(stmt))
    products_by_id = {p.id: p for p in products}

    missing = [pid for pid in product_ids if pid not in products_by_id]
    if missing:
        raise HTTPException(status_code=404, detail=f"Products not found: {missing}")

    insufficient = []
    for pid, qty in merged.items():
        if products_by_id[pid].stock_qty < qty:
            insufficient.append({"product_id": pid, "available": products_by_id[pid].stock_qty, "requested": qty})
    if insufficient:
        raise HTTPException(status_code=400, detail={"message": "Insufficient stock", "items": insufficient})

    order = Order(customer=customer, status="created")
    session.add(order)
    session.flush()  # get order.id

    for pid, qty in merged.items():
        product = products_by_id[pid]
        product.stock_qty -= qty
        session.add(product)
        session.add(OrderItem(order_id=order.id, product_id=pid, quantity=qty, unit_price=product.price))

    session.flush()
    session.refresh(order)
    return order


def list_orders(session: Session) -> list[Order]:
    return list(session.scalars(select(Order).order_by(Order.id.desc())))


def get_order(session: Session, order_id: int) -> Order:
    order = session.get(Order, order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return order
