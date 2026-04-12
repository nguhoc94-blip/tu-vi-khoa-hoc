"""Lát 3 — KB-2 birthdata confirmation trước generate (CP3 wording)."""

from __future__ import annotations

import re
from typing import Any

from app.services.app_config_store import get_config_text_first
from app.services.messenger_state import MessengerSession


def format_birth_summary(session: MessengerSession) -> str:
    b = session.birth_data
    parts: list[str] = []
    if b.get("full_name"):
        parts.append(f"Họ tên: {b['full_name']}")
    dm = (b.get("birth_day"), b.get("birth_month"), b.get("birth_year"))
    if all(dm):
        parts.append(f"Ngày sinh: {dm[0]}/{dm[1]}/{dm[2]}")
    hm = (b.get("birth_hour"), b.get("birth_minute"))
    if all(x is not None for x in hm):
        parts.append(f"Giờ sinh: {hm[0]}h{hm[1]:02d}")
    g = b.get("gender")
    if g:
        parts.append("Giới tính: nam" if g == "male" else "Giới tính: nữ")
    ct = b.get("calendar_type")
    if ct:
        parts.append("Lịch: dương" if ct == "solar" else "Lịch: âm")
    if b.get("calendar_type") == "lunar" and "is_leap_lunar_month" in b:
        parts.append("Tháng nhuận: có" if b["is_leap_lunar_month"] else "Tháng nhuận: không")
    return "; ".join(parts) if parts else "(chưa đủ để hiển thị)"


_KB2_YES = frozenset(
    {
        "đúng rồi",
        "dung roi",
        "ok",
        "yes",
        "chính xác",
        "chinh xac",
        "xác nhận",
        "xac nhan",
    }
)


def is_kb2_confirm_text(text: str) -> bool:
    t = text.strip().lower()
    if not t:
        return False
    if t in _KB2_YES:
        return True
    return bool(re.search(r"đúng|dung\s+roi|chính\s+xác|chinh\s+xac", t))


_KB2_EDIT = frozenset(
    {
        "sửa lại",
        "sua lai",
        "sai rồi",
        "sai roi",
        "nhập lại",
        "nhap lai",
    }
)


def is_kb2_edit_text(text: str) -> bool:
    t = text.strip().lower()
    if not t:
        return False
    if t in _KB2_EDIT:
        return True
    return "sửa" in t or "sua" in t


def build_confirmation_summary_message(session: MessengerSession) -> str:
    tmpl = get_config_text_first(
        "confirmation_birthdata_summary",
        default=(
            "Mình chốt lại thông tin để xem cho bạn chính xác hơn nhé: [tóm tắt dữ liệu]. "
            "Nếu đúng rồi mình xem tiếp, còn nếu chưa đúng bạn sửa lại giúp mình ở đây."
        ),
    )
    return tmpl.replace("[tóm tắt dữ liệu]", format_birth_summary(session))


def kb2_reminder_when_awaiting(session: MessengerSession) -> str:
    yes = get_config_text_first("confirmation_birthdata_yes", default="Đúng rồi")
    edit = get_config_text_first("confirmation_birthdata_edit", default="Sửa lại thông tin")
    return (
        f"Mình đang chờ bạn xác nhận trước khi xem lá số.\n"
        f"Bạn nhắn \"{yes}\" hoặc \"{edit}\" giúp mình nhé."
    )
