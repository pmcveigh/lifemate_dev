import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import ValidationError

from app.api.v1.auth import router as auth_router
from app.api.v1.tickets import router as tickets_router
from app.core import get_settings
from app.db import run_migrations

logger = logging.getLogger(__name__)

app = FastAPI()

origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(tickets_router)


@app.on_event("startup")
def validate_configuration() -> None:
    try:
        get_settings()
    except ValidationError as exc:  # pragma: no cover - defensive logging
        logger.critical("Invalid application configuration: %s", exc)
        raise RuntimeError("Invalid application configuration") from exc


@app.on_event("startup")
def apply_database_migrations() -> None:
    run_migrations()


@app.get("/health")
def health():
    return {"status": "ok"}
