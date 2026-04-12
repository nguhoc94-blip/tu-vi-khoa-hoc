"""
Ghép tin nhắn outbound cuối: part_1 reading (GPT) -> part_2 bank -> part_3 CEO note.
Bank block và CEO note đọc từ biến môi trường (master plan Admin Panel).
"""

from __future__ import annotations

import os

ENV_PART_2_BANK = "MESSENGER_PART_2_BANK_BLOCK"
ENV_PART_3_CEO = "MESSENGER_PART_3_CEO_NOTE"


def get_bank_block_from_env() -> str:
    return os.environ.get(ENV_PART_2_BANK, "").strip()


def get_ceo_note_from_env() -> str:
    return os.environ.get(ENV_PART_3_CEO, "").strip()


def build_messenger_outbound(*, reading_body: str) -> str:
    body = (reading_body or "").rstrip()
    bank = get_bank_block_from_env()
    ceo = get_ceo_note_from_env()
    if not bank or not ceo:
        raise RuntimeError(
            f"Thiếu {ENV_PART_2_BANK} hoặc {ENV_PART_3_CEO} trong môi trường. "
            "Sao chép .env.example thành .env và điền hai biến này, hoặc dùng Admin Panel."
        )
    return f"{body}\n\n{bank}\n\n{ceo}"
