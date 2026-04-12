from __future__ import annotations

import json
import logging
import os
from pathlib import Path

from openai import OpenAI

from app.schemas.reading import ChartJson
from app.services.messenger_funnel_bridge import record_openai_token_usage
from app.services.prompt_adapter import to_prompt_input_json
from app.services.reading_postcheck import postcheck_free_text

logger = logging.getLogger(__name__)

DEFAULT_OPENAI_MODEL = "gpt-4o-mini"
OPENAI_TIMEOUT_SECONDS = 60.0

MOCK_TEASER_FALLBACK = (
    "mock teaser: lá số đang được dựng (MVP). "
    "Bản đầy đủ sẽ có sau khi nối engine và thanh toán."
)


def _backend_dir() -> Path:
    return Path(__file__).resolve().parents[2]


def _prompts_dir() -> Path:
    return _backend_dir() / "prompts"


def _load_prompt_file(name: str) -> str:
    path = _prompts_dir() / name
    return path.read_text(encoding="utf-8")


def _chart_to_json_text(chart: ChartJson) -> str:
    return json.dumps(chart.model_dump(mode="json"), ensure_ascii=False)


def _inject_json_hoso(template: str, chart: ChartJson) -> str:
    prompt_input_json = to_prompt_input_json(chart.model_dump(mode="json"))
    payload = json.dumps(prompt_input_json, ensure_ascii=False)
    return template.replace("{{JSON_HOSO}}", payload)


def generate_free_teaser(
    chart: ChartJson,
    *,
    request_id: str,
    sender_id: str | None = None,
) -> str:
    """
    Calls OpenAI for FREE teaser only. Never raises to the route.
    Logs openai_teaser_success or openai_teaser_fallback_mock.
    """
    api_key = (os.environ.get("OPENAI_API_KEY") or "").strip()
    if not api_key:
        logger.warning(
            "openai_teaser_fallback_mock event=openai_teaser_fallback_mock "
            "request_id=%s reason=missing_api_key",
            request_id,
        )
        return MOCK_TEASER_FALLBACK

    model = (os.environ.get("OPENAI_MODEL") or "").strip() or DEFAULT_OPENAI_MODEL

    try:
        system_content = _inject_json_hoso(_load_prompt_file("system_free_production.txt"), chart)
        user_content = _inject_json_hoso(_load_prompt_file("user_free_production.txt"), chart)

        client = OpenAI(api_key=api_key, timeout=OPENAI_TIMEOUT_SECONDS)
        completion = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_content},
                {"role": "user", "content": user_content},
            ],
        )
        usage = getattr(completion, "usage", None)
        if sender_id and usage is not None:
            record_openai_token_usage(
                sender_id=sender_id,
                request_id=request_id,
                model=model,
                prompt_tokens=getattr(usage, "prompt_tokens", None),
                completion_tokens=getattr(usage, "completion_tokens", None),
                total_tokens=getattr(usage, "total_tokens", None),
            )
        text = (completion.choices[0].message.content or "").strip()
        if not text:
            logger.warning(
                "openai_teaser_fallback_mock event=openai_teaser_fallback_mock "
                "request_id=%s reason=empty_response",
                request_id,
            )
            return MOCK_TEASER_FALLBACK

        ok, checked_text = postcheck_free_text(text)
        if not ok:
            logger.warning(
                "openai_teaser_fallback_mock event=openai_teaser_fallback_mock "
                "request_id=%s reason=postcheck_blocked",
                request_id,
            )
            return checked_text

        logger.info(
            "openai_teaser_success event=openai_teaser_success request_id=%s model=%s",
            request_id,
            model,
        )
        return checked_text

    except Exception as e:
        logger.warning(
            "openai_teaser_fallback_mock event=openai_teaser_fallback_mock "
            "request_id=%s reason=%s",
            request_id,
            type(e).__name__,
            exc_info=True,
        )
        return MOCK_TEASER_FALLBACK
