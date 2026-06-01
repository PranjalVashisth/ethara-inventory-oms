from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_session
from app.crud import create_order, get_order, list_orders
from app.schemas import OrderCreate, OrderOut

router = APIRouter(prefix="/orders", tags=["orders"])


@router.get("", response_model=list[OrderOut])
def orders_index(session: Session = Depends(get_session)):
    return list_orders(session)


@router.post("", response_model=OrderOut, status_code=201)
def orders_create(payload: OrderCreate, session: Session = Depends(get_session)):
    return create_order(session, payload)


@router.get("/{order_id}", response_model=OrderOut)
def orders_get(order_id: int, session: Session = Depends(get_session)):
    return get_order(session, order_id)

