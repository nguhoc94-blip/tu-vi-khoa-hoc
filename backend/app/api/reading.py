from __future__ import annotations

import logging
import uuid

from fastapi import APIRouter

from app.schemas.reading import GenerateReadingRequest, GenerateReadingResponse
from app.services.reading_service import process_generate_reading

logger = logging.getLogger(__name__)

router = APIRouter(tags=["reading"])


@router.post("/generate-reading", response_model=GenerateReadingResponse)
def generate_reading(payload: GenerateReadingRequest) -> GenerateReadingResponse:
    request_id = str(uuid.uuid4())
    result = process_generate_reading(payload, request_id=request_id)
    n = result.normalized_input
    logger.info(
        "generate_reading_ok request_id=%s calendar_type=%s birth_year=%s "
        "leap=%s timezone=%s rule_set_id=%s",
        request_id,
        n.calendar_type,
        n.birth_year,
        n.is_leap_lunar_month,
        n.timezone,
        n.rule_set_id,
    )
    return result
