from __future__ import annotations

from app.schemas.reading import (
    GenerateReadingRequest,
    GenerateReadingResponse,
)
from app.services.chart_builder import build_chart_json
from app.services.normalizer import normalize_generate_reading_input
from app.services.openai_teaser import generate_free_teaser


def process_generate_reading(
    payload: GenerateReadingRequest,
    *,
    request_id: str,
    sender_id: str | None = None,
) -> GenerateReadingResponse:
    normalized = normalize_generate_reading_input(payload, request_id=request_id)
    chart = build_chart_json(normalized)
    teaser = generate_free_teaser(
        chart,
        request_id=request_id,
        sender_id=sender_id,
    )

    return GenerateReadingResponse(
        ok=True,
        message="Input accepted and normalized successfully",
        normalized_input=normalized,
        chart_json=chart,
        teaser=teaser,
    )
