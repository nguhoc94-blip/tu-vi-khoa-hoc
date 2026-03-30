from __future__ import annotations

import json
import logging
import os
import urllib.error
import urllib.request
import uuid

from app.db import DatabaseUnavailableError
from app.schemas.reading import GenerateReadingRequest
from app.services.messenger_state import (
    ConversationState,
    RESET_COMMANDS,
)
from app.services.messenger_state_db import DbMessengerStateStore
from app.services.openai_paid import generate_full_reading_direct, unlock_demo_for_sender
from app.services.reading_store_db import ReadingStoreDb
from app.services.reading_service import process_generate_reading

logger = logging.getLogger(__name__)

_store = DbMessengerStateStore()
_reading_store = ReadingStoreDb()
DEFAULT_DONATION_TEXT = "Neu thay huu ich, ban co the ung ho de du an duy tri."


def send_text_message(sender_id: str, text: str, *, request_id: str) -> None:
    page_access_token = (os.environ.get("FB_PAGE_ACCESS_TOKEN") or "").strip()
    if not page_access_token:
        logger.warning(
            "messenger_send_skipped_missing_token request_id=%s sender_id=%s event=send_skipped",
            request_id,
            sender_id,
        )
        return

    url = f"https://graph.facebook.com/v21.0/me/messages?access_token={page_access_token}"
    payload = {
        "messaging_type": "RESPONSE",
        "recipient": {"id": sender_id},
        "message": {"text": text},
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url=url,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            status = resp.getcode()
            logger.info(
                "messenger_send_ok request_id=%s sender_id=%s event=send_text status=%s",
                request_id,
                sender_id,
                status,
            )
    except urllib.error.URLError:
        logger.warning(
            "messenger_send_failed request_id=%s sender_id=%s event=send_text_failed",
            request_id,
            sender_id,
        )


def _parse_int(text: str) -> int | None:
    try:
        return int(text.strip())
    except ValueError:
        return None


def _parse_gender(text: str) -> str | None:
    v = text.strip().lower()
    mapping = {
        "male": "male",
        "female": "female",
        "nam": "male",
        "nu": "female",
        "nữ": "female",
    }
    return mapping.get(v)


def _parse_calendar_type(text: str) -> str | None:
    v = text.strip().lower()
    mapping = {
        "solar": "solar",
        "lunar": "lunar",
        "duong": "solar",
        "dương": "solar",
        "am": "lunar",
        "âm": "lunar",
    }
    return mapping.get(v)


def _parse_bool(text: str) -> bool | None:
    v = text.strip().lower()
    true_values = {"true", "1", "yes", "co", "có"}
    false_values = {"false", "0", "no", "khong", "không"}
    if v in true_values:
        return True
    if v in false_values:
        return False
    return None


def _ask_for_state(state: ConversationState) -> str:
    prompts = {
        ConversationState.WAIT_FULL_NAME: "Xin cho biết họ và tên của bạn.",
        ConversationState.WAIT_BIRTH_DAY: "Ngày sinh (1-31) của bạn là bao nhiêu?",
        ConversationState.WAIT_BIRTH_MONTH: "Tháng sinh (1-12) là bao nhiêu?",
        ConversationState.WAIT_BIRTH_YEAR: "Năm sinh (1900-2100) là bao nhiêu?",
        ConversationState.WAIT_BIRTH_HOUR: "Giờ sinh (0-23) là bao nhiêu?",
        ConversationState.WAIT_BIRTH_MINUTE: "Phút sinh (0-59) là bao nhiêu?",
        ConversationState.WAIT_GENDER: "Giới tính (male/female hoặc nam/nu)?",
        ConversationState.WAIT_CALENDAR_TYPE: "Loại lịch (solar/lunar hoặc duong/am)?",
        ConversationState.WAIT_IS_LEAP_LUNAR_MONTH: "Tháng âm nhuận? (true/false hoặc co/khong)",
    }
    return prompts.get(state, "Vui lòng nhập lại.")


def _build_donation_cta() -> str:
    donation_text = (os.environ.get("DONATION_TEXT") or "").strip()
    donation_url = (os.environ.get("DONATION_URL") or "").strip()
    if not donation_text and not donation_url:
        return ""
    if donation_url and not donation_text:
        donation_text = DEFAULT_DONATION_TEXT
    if donation_url:
        return f"{donation_text}\n{donation_url}"
    return donation_text


def _request_reset(sender_id: str, *, request_id: str) -> str:
    _store.mark_cancelled(sender_id)
    _store.reset(sender_id)
    logger.info(
        "messenger_session_reset request_id=%s sender_id=%s state=%s event=session_reset",
        request_id,
        sender_id,
        ConversationState.WAIT_FULL_NAME.value,
    )
    return "Đã bắt đầu lại. Xin cho biết họ và tên của bạn."


def handle_incoming_text(sender_id: str, text: str, *, request_id: str) -> str:
    try:
        normalized_text = text.strip()
        if normalized_text.lower() == "unlock_demo":
            return unlock_demo_for_sender(sender_id=sender_id, request_id=request_id)
        if normalized_text.lower() in RESET_COMMANDS:
            return _request_reset(sender_id, request_id=request_id)

        session = _store.get_or_create(sender_id)
        if session.state == ConversationState.NEW:
            session.state = ConversationState.WAIT_FULL_NAME
            _store.save(session)
            logger.info(
                "messenger_session_started request_id=%s sender_id=%s state=%s event=session_started",
                request_id,
                sender_id,
                session.state.value,
            )
            return "Chào bạn! Mình sẽ giúp tạo teaser tử vi. Trước tiên, xin cho biết họ và tên của bạn."

        if session.state == ConversationState.COMPLETED:
            return "Phiên đã hoàn tất. Muốn xem lại từ đầu, nhắn 'start'."

        if session.state == ConversationState.CANCELLED:
            session.state = ConversationState.WAIT_FULL_NAME
            _store.save(session)
            return _ask_for_state(session.state)

        if session.state == ConversationState.WAIT_FULL_NAME:
            if not normalized_text:
                return "Họ tên chưa hợp lệ. Xin nhập lại họ và tên."
            session.data["full_name"] = normalized_text
            session.state = ConversationState.WAIT_BIRTH_DAY
            _store.save(session)
            return _ask_for_state(session.state)

        if session.state == ConversationState.WAIT_BIRTH_DAY:
            value = _parse_int(normalized_text)
            if value is None or value < 1 or value > 31:
                return "Ngày sinh chưa hợp lệ. Vui lòng nhập số từ 1 đến 31."
            session.data["birth_day"] = value
            session.state = ConversationState.WAIT_BIRTH_MONTH
            _store.save(session)
            return _ask_for_state(session.state)

        if session.state == ConversationState.WAIT_BIRTH_MONTH:
            value = _parse_int(normalized_text)
            if value is None or value < 1 or value > 12:
                return "Tháng sinh chưa hợp lệ. Vui lòng nhập số từ 1 đến 12."
            session.data["birth_month"] = value
            session.state = ConversationState.WAIT_BIRTH_YEAR
            _store.save(session)
            return _ask_for_state(session.state)

        if session.state == ConversationState.WAIT_BIRTH_YEAR:
            value = _parse_int(normalized_text)
            if value is None or value < 1900 or value > 2100:
                return "Năm sinh chưa hợp lệ. Vui lòng nhập số từ 1900 đến 2100."
            session.data["birth_year"] = value
            session.state = ConversationState.WAIT_BIRTH_HOUR
            _store.save(session)
            return _ask_for_state(session.state)

        if session.state == ConversationState.WAIT_BIRTH_HOUR:
            value = _parse_int(normalized_text)
            if value is None or value < 0 or value > 23:
                return "Giờ sinh chưa hợp lệ. Vui lòng nhập số từ 0 đến 23."
            session.data["birth_hour"] = value
            session.state = ConversationState.WAIT_BIRTH_MINUTE
            _store.save(session)
            return _ask_for_state(session.state)

        if session.state == ConversationState.WAIT_BIRTH_MINUTE:
            value = _parse_int(normalized_text)
            if value is None or value < 0 or value > 59:
                return "Phút sinh chưa hợp lệ. Vui lòng nhập số từ 0 đến 59."
            session.data["birth_minute"] = value
            session.state = ConversationState.WAIT_GENDER
            _store.save(session)
            return _ask_for_state(session.state)

        if session.state == ConversationState.WAIT_GENDER:
            value = _parse_gender(normalized_text)
            if value is None:
                return "Giới tính chưa hợp lệ. Vui lòng nhập male/female (hoặc nam/nu)."
            session.data["gender"] = value
            session.state = ConversationState.WAIT_CALENDAR_TYPE
            _store.save(session)
            return _ask_for_state(session.state)

        if session.state == ConversationState.WAIT_CALENDAR_TYPE:
            value = _parse_calendar_type(normalized_text)
            if value is None:
                return "Loại lịch chưa hợp lệ. Vui lòng nhập solar/lunar (hoặc duong/am)."
            session.data["calendar_type"] = value
            if value == "lunar":
                session.state = ConversationState.WAIT_IS_LEAP_LUNAR_MONTH
                _store.save(session)
                return _ask_for_state(session.state)

            session.data["is_leap_lunar_month"] = False
            session.state = ConversationState.READY_TO_GENERATE

        if session.state == ConversationState.WAIT_IS_LEAP_LUNAR_MONTH:
            value = _parse_bool(normalized_text)
            if value is None:
                return "Giá trị tháng nhuận chưa hợp lệ. Vui lòng nhập true/false (hoặc co/khong)."
            session.data["is_leap_lunar_month"] = value
            session.state = ConversationState.READY_TO_GENERATE

        if session.state == ConversationState.READY_TO_GENERATE:
            try:
                payload = GenerateReadingRequest(**session.data)
                result = process_generate_reading(payload, request_id=request_id)
                full_reading, full_status = generate_full_reading_direct(
                    chart_json=result.chart_json.model_dump(mode="json"),
                    request_id=request_id,
                )
                reading_id = _reading_store.create_full_free_reading(
                    sender_id=sender_id,
                    normalized_input_json=result.normalized_input.model_dump(mode="json"),
                    chart_json=result.chart_json.model_dump(mode="json"),
                    free_teaser=result.teaser,
                    full_reading=full_reading,
                    status=full_status,
                )
                logger.info(
                    "reading_created request_id=%s sender_id=%s event=reading_created reading_id=%s",
                    request_id,
                    sender_id,
                    reading_id,
                )
                session.state = ConversationState.COMPLETED
                _store.save(session)
                logger.info(
                    "messenger_generate_completed request_id=%s sender_id=%s state=%s event=generate_completed",
                    request_id,
                    sender_id,
                    session.state.value,
                )
                donation_cta = _build_donation_cta()
                if donation_cta:
                    return f"{full_reading}\n\n{donation_cta}\n\nMuốn xem lại từ đầu, nhắn 'start'."
                return f"{full_reading}\n\nMuốn xem lại từ đầu, nhắn 'start'."
            except Exception:
                logger.warning(
                    "messenger_generate_failed request_id=%s sender_id=%s state=%s event=generate_failed",
                    request_id,
                    sender_id,
                    session.state.value,
                )
                session.state = ConversationState.WAIT_FULL_NAME
                session.data = {}
                _store.save(session)
                return "Hiện chưa xử lý được dữ liệu vừa nhập. Mình bắt đầu lại nhé, vui lòng nhập họ và tên."

        logger.info(
            "messenger_unknown_state request_id=%s sender_id=%s state=%s event=unknown_state",
            request_id,
            sender_id,
            session.state.value,
        )
        return "Mình chưa hiểu trạng thái hiện tại. Vui lòng nhắn 'start' để bắt đầu lại."
    except DatabaseUnavailableError:
        logger.warning(
            "messenger_db_unavailable request_id=%s sender_id=%s event=messenger_db_unavailable",
            request_id,
            sender_id,
        )
        return "Hệ thống đang bận, vui lòng thử lại sau."


def process_incoming_text(sender_id: str, text: str) -> None:
    request_id = str(uuid.uuid4())
    reply = handle_incoming_text(sender_id, text, request_id=request_id)
    send_text_message(sender_id, reply, request_id=request_id)

