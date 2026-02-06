import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.db import Base, engine
from app import models  # noqa: F401

from app.api.auth import router as auth_router
from app.api.documents import router as documents_router
from app.api.qa import router as qa_router
from app.api.history import router as history_router


def create_app() -> FastAPI:
    app = FastAPI(title="GenAI EDU QA MVP", version="0.1.0")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Ensure storage dir exists
    os.makedirs(settings.STORAGE_DIR, exist_ok=True)

    # Create tables (MVP). In production use Alembic migrations.
    # Base.metadata.create_all(bind=engine)

    @app.get("/health")
    def health():
        return {"ok": True}

    app.include_router(auth_router, prefix="/api")
    app.include_router(documents_router, prefix="/api")
    app.include_router(qa_router, prefix="/api")
    app.include_router(history_router, prefix="/api")

    return app


app = create_app()


@app.on_event("startup")
def on_startup():
    try:
        Base.metadata.create_all(bind=engine)
    except Exception as e:
        print(f"[startup] DB not ready, skip create_all: {e}")
