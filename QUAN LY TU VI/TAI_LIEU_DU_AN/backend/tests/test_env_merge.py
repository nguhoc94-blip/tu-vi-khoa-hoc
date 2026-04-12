"""Merge .env — giữ key ngoài scope (COO 6.3.A)."""

from __future__ import annotations

from pathlib import Path

from app.utils.env_file import merge_env_file


def test_merge_preserves_unrelated_keys(tmp_path: Path) -> None:
    p = tmp_path / ".env"
    p.write_text(
        "KEEP_ME=original\n"
        "# comment\n"
        "OPENAI_API_KEY=old\n",
        encoding="utf-8",
    )
    merge_env_file(p, {"OPENAI_API_KEY": "newkey"})
    text = p.read_text(encoding="utf-8")
    assert "KEEP_ME=original" in text
    assert "newkey" in text
    assert "old" not in text or text.count("OPENAI_API_KEY") == 1
    assert "# comment" in text


def test_merge_appends_new_keys(tmp_path: Path) -> None:
    p = tmp_path / ".env"
    p.write_text("A=1\n", encoding="utf-8")
    merge_env_file(p, {"B": "2"})
    t = p.read_text(encoding="utf-8")
    assert "A=1" in t
    assert "B=2" in t


def test_merge_creates_file(tmp_path: Path) -> None:
    p = tmp_path / ".env"
    merge_env_file(p, {"X": "y"})
    assert p.read_text(encoding="utf-8").strip() == "X=y"
