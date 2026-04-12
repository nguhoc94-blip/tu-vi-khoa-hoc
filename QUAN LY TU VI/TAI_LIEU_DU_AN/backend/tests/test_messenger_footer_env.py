"""Messenger footer từ env — tách khỏi suite engine tử vi."""

from __future__ import annotations

import pytest

from app.services.final_message_builder import (
    ENV_PART_2_BANK,
    ENV_PART_3_CEO,
    build_messenger_outbound,
    get_bank_block_from_env,
    get_ceo_note_from_env,
)
from app.utils.admin_strings import RESTART_BANNER_TEXT
from app.utils.log_redact import redact_log_line


def test_build_messenger_outbound_reads_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv(ENV_PART_2_BANK, "BANK_TEST")
    monkeypatch.setenv(ENV_PART_3_CEO, "CEO_TEST")
    out = build_messenger_outbound(reading_body="BODY")
    assert out.index("BODY") < out.index("BANK_TEST") < out.index("CEO_TEST")


def test_build_messenger_outbound_order_reading_bank_ceo(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv(ENV_PART_2_BANK, "P2")
    monkeypatch.setenv(ENV_PART_3_CEO, "P3")
    out = build_messenger_outbound(reading_body="R")
    parts = out.split("\n\n")
    assert parts[0] == "R"
    assert parts[1] == "P2"
    assert parts[2] == "P3"


def test_missing_env_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv(ENV_PART_2_BANK, raising=False)
    monkeypatch.delenv(ENV_PART_3_CEO, raising=False)
    with pytest.raises(RuntimeError, match=ENV_PART_2_BANK):
        build_messenger_outbound(reading_body="x")


def test_getters_strip_whitespace(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv(ENV_PART_2_BANK, "  x  ")
    monkeypatch.setenv(ENV_PART_3_CEO, "  y ")
    assert get_bank_block_from_env() == "x"
    assert get_ceo_note_from_env() == "y"


def test_redact_log_line_masks_openai_key_assignment() -> None:
    line = 'OPENAI_API_KEY=sk-1234567890abcdefghij'
    assert "sk-" not in redact_log_line(line)
    assert "[REDACTED]" in redact_log_line(line)


def test_redact_log_line_masks_database_url() -> None:
    line = "DATABASE_URL=postgresql://u:p@host/db"
    out = redact_log_line(line)
    assert "postgresql://" not in out


def test_restart_banner_text_nonempty() -> None:
    assert len(RESTART_BANNER_TEXT) > 20
    assert "uvicorn" in RESTART_BANNER_TEXT.lower() or "server" in RESTART_BANNER_TEXT.lower()
