from __future__ import annotations

import logging

from fastapi import FastAPI

from app.api.messenger import router as messenger_router
from app.api.reading import router as reading_router
from app.api.unlock_demo import router as unlock_demo_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

app = FastAPI(
    title="TuVi Messenger Bot Backend MVP",
    version="0.1.0",
)

app.include_router(reading_router)
app.include_router(messenger_router)
app.include_router(unlock_demo_router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
