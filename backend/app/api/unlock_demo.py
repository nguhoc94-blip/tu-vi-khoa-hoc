from __future__ import annotations

import uuid

from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.db import DatabaseUnavailableError
from app.services.openai_paid import unlock_demo_for_sender

router = APIRouter(prefix="/demo", tags=["demo"])


class UnlockDemoRequest(BaseModel):
    sender_id: str = Field(..., min_length=1)


class UnlockDemoResponse(BaseModel):
    ok: bool
    message: str
    full_reading: str


@router.post("/unlock-latest", response_model=UnlockDemoResponse)
def unlock_latest(payload: UnlockDemoRequest) -> UnlockDemoResponse:
    request_id = str(uuid.uuid4())
    try:
        full_reading = unlock_demo_for_sender(sender_id=payload.sender_id, request_id=request_id)
    except DatabaseUnavailableError:
        full_reading = "Hệ thống đang bận, vui lòng thử lại sau."
    return UnlockDemoResponse(
        ok=True,
        message="Unlock demo processed",
        full_reading=full_reading,
    )

