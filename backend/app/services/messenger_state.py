from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum


class ConversationState(str, Enum):
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


RESET_COMMANDS = {"start", "bat dau", "xem lai", "reset"}


@dataclass
class MessengerSession:
    sender_id: str
    state: ConversationState = ConversationState.NEW
    data: dict[str, object] = field(default_factory=dict)
    updated_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc),
    )


class InMemoryMessengerStateStore:
    def __init__(self) -> None:
        self._sessions: dict[str, MessengerSession] = {}

    def get_or_create(self, sender_id: str) -> MessengerSession:
        session = self._sessions.get(sender_id)
        if session is None:
            session = MessengerSession(sender_id=sender_id)
            self._sessions[sender_id] = session
        return session

    def reset(self, sender_id: str) -> MessengerSession:
        session = MessengerSession(
            sender_id=sender_id,
            state=ConversationState.WAIT_FULL_NAME,
        )
        self._sessions[sender_id] = session
        return session

    def save(self, session: MessengerSession) -> None:
        session.updated_at = datetime.now(timezone.utc)
        self._sessions[session.sender_id] = session

    def set_state(self, sender_id: str, state: ConversationState) -> MessengerSession:
        session = self.get_or_create(sender_id)
        session.state = state
        self.save(session)
        return session

    def mark_cancelled(self, sender_id: str) -> MessengerSession:
        session = self.get_or_create(sender_id)
        session.state = ConversationState.CANCELLED
        session.data = {}
        self.save(session)
        return session

