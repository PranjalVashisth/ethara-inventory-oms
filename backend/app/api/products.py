from __future__ import annotations

from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session

from app.core.database import get_session
from app.crud import create_product, delete_product, get_product, list_products, update_product
from app.schemas import ProductCreate, ProductOut, ProductUpdate

router = APIRouter(prefix="/products", tags=["products"])


@router.get("", response_model=list[ProductOut])
def products_index(session: Session = Depends(get_session)):
    return list_products(session)


@router.post("", response_model=ProductOut, status_code=201)
def products_create(payload: ProductCreate, session: Session = Depends(get_session)):
    return create_product(session, payload)


@router.get("/{product_id}", response_model=ProductOut)
def products_get(product_id: int, session: Session = Depends(get_session)):
    return get_product(session, product_id)


@router.patch("/{product_id}", response_model=ProductOut)
def products_update(product_id: int, payload: ProductUpdate, session: Session = Depends(get_session)):
    return update_product(session, product_id, payload)


@router.delete("/{product_id}", status_code=204)
def products_delete(product_id: int, session: Session = Depends(get_session)):
    delete_product(session, product_id)
    return Response(status_code=204)

