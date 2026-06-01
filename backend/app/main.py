from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.customers import router as customers_router
from app.api.orders import router as orders_router
from app.api.products import router as products_router
from app.core.config import settings
from app.core.database import init_engine
from app.models import Base


def create_app() -> FastAPI:
    @asynccontextmanager
    async def lifespan(_: FastAPI):
        init_engine(settings.database_url)
        if settings.auto_create_tables:
            from app.core.database import engine

            assert engine is not None
            Base.metadata.create_all(bind=engine)
        yield

    app = FastAPI(
        title="Ethara Inventory & Order Management API",
        version="1.0.0",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(products_router, prefix="/api")
    app.include_router(customers_router, prefix="/api")
    app.include_router(orders_router, prefix="/api")

    @app.get("/healthz")
    def healthz():
        return {"ok": True}

    return app


app = create_app()
