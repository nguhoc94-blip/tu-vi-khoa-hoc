from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any


class ConversationState(str, Enum):
    # Active states for conversational bridge MVP
    CHATTING = "CHATTING"    # no birth data yet, or general chat
    HAS_CHART = "HAS_CHART"  # chart generated; follow-up mode

    # Legacy states kept for DB backward-compat migration only.
    # New sessions are never created in these states.
    NEW = "NEW"
    WAIT_FULL_NAME = "WAIT_FULL_NAME"
    WAIT_BIRTH_DAY = "WAIT_BIRTH_DAY"
    WAIT_BIRTH_MONTH = "WAIT_BIRTH_MONTH"
    WAIT_BIRTH_YEAR = "WAIT_BIRTH_YEAR"
    WAIT_BIRTH_HOUR = "WAIT_BIRTH_HOUR"
    WAIT_BIRTH_MINUTE = "WAIT_BIRTH_MINUTE"
    WAIT_GENDER = "WAIT_GENDER"
    WAIT_CALENDAR_TYPE = "WAIT_CALENDAR_TYPE"
    WAIT_IS_LEAP_LUNAR_MONTH = "WAIT_IS_LEAP_LUNAR_MONTH"
    READY_TO_GENERATE = "READY_TO_GENERATE"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


# Any legacy state that should be treated as CHATTING when loading from DB
LEGACY_CHATTING_STATES: frozenset[ConversationState] = frozenset(
    {
        ConversationState.NEW,
        ConversationState.WAIT_FULL_NAME,
        ConversationState.WAIT_BIRTH_DAY,
        ConversationState.WAIT_BIRTH_MONTH,
        ConversationState.WAIT_BIRTH_YEAR,
        ConversationState.WAIT_BIRTH_HOUR,
        ConversationState.WAIT_BIRTH_MINUTE,
        ConversationState.WAIT_GENDER,
        ConversationState.WAIT_CALENDAR_TYPE,
        ConversationState.WAIT_IS_LEAP_LUNAR_MONTH,
        ConversationState.READY_TO_GENERATE,
        ConversationState.COMPLETED,
        ConversationState.CANCELLED,
    }
)

RESET_COMMANDS: frozenset[str] = frozenset({"start", "bat dau", "xem lai", "reset"})

# Fields required to attempt chart generation
REQUIRED_BIRTH_FIELDS: list[str] = [
    "full_name",
    "birth_day",
    "birth_month",
    "birth_year",
    "birth_hour",
    "birth_minute",
    "gender",
    "calendar_type",
]

# Max chat turns kept in session — controls context window sent to OpenAI
MAX_HISTORY = 8

# Human-readable labels for targeted intake questions
FIELD_QUESTION: dict[str, str] = {
    "full_name": "Bạn cho mình biết họ và tên nhé?",
    "birth_day": "Ngày sinh của bạn là ngày mấy (1–31)?",
    "birth_month": "Tháng sinh là tháng mấy (1–12)?",
    "birth_year": "Năm sinh là năm nào?",
    "birth_hour": "Giờ sinh là mấy giờ (0–23)?",
    "birth_minute": "Phút sinh là phút mấy (0–59)?",
    "gender": "Giới tính của bạn là nam hay nữ?",
    "calendar_type": "Ngày sinh theo lịch dương (solar) hay âm (lunar)?",
    "is_leap_lunar_month": "Tháng âm của bạn có phải tháng nhuận không? (có/không)",
}


@dataclass
class MessengerSession:
    sender_id: str
    state: ConversationState = ConversationState.CHATTING
    birth_data: dict[str, Any] = field(default_factory=dict)
    history: list[dict[str, str]] = field(default_factory=list)
    chart_json: dict[str, Any] | None = None
    reading_id: int | None = None
    routing: dict[str, Any] = field(default_factory=dict)
    updated_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc),
    )

    def missing_birth_fields(self) -> list[str]:
        """Return required fields not yet present in birth_data."""
        missing = [f for f in REQUIRED_BIRTH_FIELDS if f not in self.birth_data]
        if (
            "is_leap_lunar_month" not in self.birth_data
            and self.birth_data.get("calendar_type") == "lunar"
        ):
            missing.append("is_leap_lunar_month")
        return missing

    def has_any_birth_data(self) -> bool:
        return bool(self.birth_data)

    def has_partial_intake(self) -> bool:
        """Intake dở: có birth nhưng chưa đủ và chưa có lá số."""
        return (
            self.has_any_birth_data()
            and not self.is_birth_complete()
            and not self.chart_json
        )

    def is_birth_complete(self) -> bool:
        return len(self.missing_birth_fields()) == 0

    def add_turn(self, role: str, content: str) -> None:
        """Append a turn and trim history to MAX_HISTORY entries."""
        self.history.append({"role": role, "content": content})
        if len(self.history) > MAX_HISTORY:
            self.history = self.history[-MAX_HISTORY:]
