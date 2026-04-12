from __future__ import annotations

import re
import unicodedata

FULL_SAFE_FALLBACK = "Ban doc day du tam thoi chua san sang. Vui long thu lai sau."
FREE_SAFE_FALLBACK = "Tom tat hien tai chi mang tinh tham khao an toan. Ban co the thu lai de nhan noi dung day du hon."

_HARD_BLOCK_PATTERNS = [
    r"\bchac chan se\b",
    r"\btuyet doi\b",
    r"\b100%\b",
    r"\bdinh menh\b",
    r"\bkhong the thay doi\b",
    r"\bse chet\b",
    r"\btan gia bai san\b",
    r"\bkhong cuu duoc\b",
    r"\bdoa\b",
    r"\btat yeu phai\b",
]


def _contains_hard_block(text: str) -> bool:
    lowered = _normalize_text(text)
    return any(re.search(pattern, lowered) for pattern in _HARD_BLOCK_PATTERNS)


def _section_count(text: str) -> int:
    # Loose parser for common section markers.
    markers = [
        "tong quan",
        "cong viec",
        "tai chinh",
        "tinh cam",
        "loi khuyen",
        "1)",
        "2)",
        "3)",
    ]
    lowered = _normalize_text(text)
    count = 0
    for marker in markers:
        if marker in lowered:
            count += 1
    return count


def _normalize_text(text: str) -> str:
    lowered = text.lower()
    normalized = unicodedata.normalize("NFD", lowered)
    accentless = "".join(ch for ch in normalized if unicodedata.category(ch) != "Mn")
    # Vietnamese "đ" is not removed by Mn filter.
    accentless = accentless.replace("đ", "d")
    return accentless


def postcheck_full_text(text: str) -> tuple[bool, str]:
    """
    hard block -> fallback immediately
    soft structure -> ensure at least 3 sections; else fallback
    """
    cleaned = (text or "").strip()
    if not cleaned:
        return False, FULL_SAFE_FALLBACK
    if _contains_hard_block(cleaned):
        return False, FULL_SAFE_FALLBACK
    if _section_count(cleaned) < 3:
        return False, FULL_SAFE_FALLBACK
    return True, cleaned


def postcheck_free_text(text: str) -> tuple[bool, str]:
    """
    hard block -> fallback immediately
    soft structure -> free should not fully reveal 3 sections:
      if it seems too detailed, return minimal safe correction.
    """
    cleaned = (text or "").strip()
    if not cleaned:
        return False, FREE_SAFE_FALLBACK
    if _contains_hard_block(cleaned):
        return False, FREE_SAFE_FALLBACK
    if _section_count(cleaned) >= 3:
        return False, (
            "Tom tat teaser: Ban co nhieu diem tiem nang dang chu y trong cong viec, tai chinh va tinh cam. "
            "Ban doc day du se phan tich ky hon theo tung phan."
        )
    return True, cleaned

