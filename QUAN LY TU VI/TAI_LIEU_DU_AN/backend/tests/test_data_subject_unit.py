"""Unit checks for data_subject_service."""

from __future__ import annotations

import pytest

from app.services.data_subject_service import anonymize_sender_baseline


def test_anonymize_rejects_empty_sender() -> None:
    with pytest.raises(ValueError, match="sender_id"):
        anonymize_sender_baseline("  ")
