from __future__ import annotations

from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session

from app.core.database import get_session
from app.crud import create_customer, delete_customer, get_customer, list_customers, update_customer
from app.schemas import CustomerCreate, CustomerOut, CustomerUpdate

router = APIRouter(prefix="/customers", tags=["customers"])


@router.get("", response_model=list[CustomerOut])
def customers_index(session: Session = Depends(get_session)):
    return list_customers(session)


@router.post("", response_model=CustomerOut, status_code=201)
def customers_create(payload: CustomerCreate, session: Session = Depends(get_session)):
    return create_customer(session, payload)


@router.get("/{customer_id}", response_model=CustomerOut)
def customers_get(customer_id: int, session: Session = Depends(get_session)):
    return get_customer(session, customer_id)


@router.patch("/{customer_id}", response_model=CustomerOut)
def customers_update(customer_id: int, payload: CustomerUpdate, session: Session = Depends(get_session)):
    return update_customer(session, customer_id, payload)


@router.delete("/{customer_id}", status_code=204)
def customers_delete(customer_id: int, session: Session = Depends(get_session)):
    delete_customer(session, customer_id)
    return Response(status_code=204)

