"""Redact sensitive patterns from log lines (Admin Panel tail — COO 6.3.C)."""

from __future__ import annotations

import logging
import re

# Substrings / patterns that must not appear raw in log output
_SENSITIVE_PATTERNS = (
    re.compile(r"sk-[A-Za-z0-9]{10,}", re.I),
    re.compile(r"OPENAI_API_KEY\s*=\s*\S+"),
    re.compile(r"FB_PAGE_ACCESS_TOKEN\s*=\s*\S+"),
    re.compile(r"FB_VERIFY_TOKEN\s*=\s*\S+"),
    re.compile(r"DATABASE_URL\s*=\s*\S+"),
    re.compile(r"postgresql://[^\s]+", re.I),
    re.compile(r"https://graph\.facebook\.com/[^\s]+access_token=[^\s&]+", re.I),
    re.compile(r"access_token=[A-Za-z0-9_\-.]{20,}", re.I),
    re.compile(r"Bearer\s+[A-Za-z0-9_\-.]{20,}", re.I),
)


def redact_log_line(line: str) -> str:
    out = line
    for pat in _SENSITIVE_PATTERNS:
        out = pat.sub("[REDACTED]", out)
    return out


def redact_log_text(text: str, *, max_lines: int = 200) -> str:
    lines = text.splitlines()
    tail = lines[-max_lines:] if len(lines) > max_lines else lines
    return "\n".join(redact_log_line(L) for L in tail)


class RedactingFormatter(logging.Formatter):
    """Apply redact_log_line to final formatted log lines (Nhịp 3)."""

    def format(self, record: logging.LogRecord) -> str:
        return redact_log_line(super().format(record))


def attach_redacting_formatter_to_root(*, fmt: str, datefmt: str | None = None) -> None:
    for h in logging.getLogger().handlers:
        h.setFormatter(RedactingFormatter(fmt, datefmt=datefmt))
