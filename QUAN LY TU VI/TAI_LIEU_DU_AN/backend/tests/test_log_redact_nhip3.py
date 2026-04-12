"""Nhịp 3 — log redaction patterns + formatter."""

from __future__ import annotations

import logging

import pytest

from app.utils.log_redact import RedactingFormatter, redact_log_line


@pytest.mark.parametrize(
    "raw,expect_sub",
    [
        ("prefix sk-12345678901234567890 suffix", "[REDACTED]"),
        ("OPENAI_API_KEY=secret_here", "[REDACTED]"),
        ("postgresql://u:p@host:5432/db", "[REDACTED]"),
        ("Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0", "[REDACTED]"),
    ],
)
def test_redact_log_line_patterns(raw: str, expect_sub: str) -> None:
    out = redact_log_line(raw)
    assert expect_sub in out
    if expect_sub == "[REDACTED]":
        assert "secret_here" not in out
        assert "sk-12345678901234567890" not in out


def test_redacting_formatter_masks_secret_in_output() -> None:
    fmt = RedactingFormatter("%(message)s")
    record = logging.LogRecord(
        name="t",
        level=logging.INFO,
        pathname="x",
        lineno=1,
        msg="token sk-abcdefghijklmnopqrstuvwxyz012345 end",
        args=(),
        exc_info=None,
    )
    s = fmt.format(record)
    assert "[REDACTED]" in s
    assert "sk-abc" not in s
