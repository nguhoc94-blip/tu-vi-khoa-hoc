"""
Admin Panel cục bộ (Streamlit) — Setup Wizard + vận hành hằng ngày.
Chạy từ thư mục backend: streamlit run admin.py
"""

from __future__ import annotations

import os
from pathlib import Path

import httpx
import streamlit as st
from dotenv import load_dotenv

from app.utils.admin_strings import RESTART_BANNER_TEXT
from app.utils.env_file import merge_env_file
from app.utils.log_redact import redact_log_text

BACKEND_ROOT = Path(__file__).resolve().parent
ENV_PATH = BACKEND_ROOT / ".env"

# COO 6.2: mặc định localhost:8000; không thuộc 6 field Wizard
PANEL_BACKEND_DEFAULT = "http://localhost:8000"


def _backend_base_url() -> str:
    v = os.environ.get("BACKEND_BASE_URL", "").strip()
    return v or PANEL_BACKEND_DEFAULT


load_dotenv(ENV_PATH)

def _init_session() -> None:
    if "restart_banner" not in st.session_state:
        st.session_state.restart_banner = False


def _mark_saved() -> None:
    st.session_state.restart_banner = True


def _render_restart_banner(*, ack_button_key: str) -> None:
    """ack_button_key phải duy nhất mỗi nơi gọi (Wizard vs Vận hành) — tránh StreamlitDuplicateElementId."""
    if st.session_state.get("restart_banner"):
        st.warning(RESTART_BANNER_TEXT)
        if st.button(
            "Tôi đã restart server — ẩn nhắc này",
            key=ack_button_key,
        ):
            st.session_state.restart_banner = False
            st.rerun()


def _restart_commands() -> None:
    st.subheader("Lệnh restart (copy-paste)")
    st.code(
        "cd backend\n"
        ".\\.venv\\Scripts\\Activate.ps1\n"
        "uvicorn app.main:app --reload --host 0.0.0.0 --port 8000",
        language="powershell",
    )
    st.code(
        "cd backend && source .venv/bin/activate && "
        "uvicorn app.main:app --reload --host 0.0.0.0 --port 8000",
        language="bash",
    )


def _check_health() -> None:
    url = f"{_backend_base_url().rstrip('/')}/health"
    try:
        r = httpx.get(url, timeout=5.0)
        if r.status_code == 200:
            st.success(f"Kết nối OK: {url} → {r.status_code}")
        else:
            st.error(f"HTTP {r.status_code} từ {url}")
    except Exception as e:
        st.error(f"Không gọi được {url}: {e}")


def main() -> None:
    st.set_page_config(page_title="TuVi Bot — Admin local", layout="wide")
    _init_session()

    st.title("TuVi Messenger Bot — Admin Panel (local)")
    st.caption(
        f"File cấu hình: `{ENV_PATH}` — Backend kiểm tra: `{_backend_base_url()}` "
        "(mặc định http://localhost:8000, không nhập trong Wizard)."
    )

    tab_wizard, tab_ops = st.tabs(["Setup lần đầu (Wizard)", "Vận hành hằng ngày"])

    with tab_wizard:
        st.markdown("Nhập **đúng 6** biến (3 secret dạng ô ẩn). `BACKEND_BASE_URL` không nằm đây.")
        w_openai = st.text_input("OPENAI_API_KEY", type="password", key="wiz_openai")
        w_fb_page = st.text_input("FB_PAGE_ACCESS_TOKEN", type="password", key="wiz_fb_page")
        w_fb_verify = st.text_input("FB_VERIFY_TOKEN", type="password", key="wiz_fb_verify")
        w_db = st.text_input("DATABASE_URL", key="wiz_db")
        w_bank = st.text_input(
            "Bank block → MESSENGER_PART_2_BANK_BLOCK",
            key="wiz_bank",
        )
        w_ceo = st.text_input(
            "CEO note → MESSENGER_PART_3_CEO_NOTE",
            key="wiz_ceo",
        )

        c1, c2 = st.columns(2)
        with c1:
            if st.button("Lưu cấu hình (Wizard)", type="primary", key="wiz_save_env"):
                updates = {
                    "OPENAI_API_KEY": w_openai,
                    "FB_PAGE_ACCESS_TOKEN": w_fb_page,
                    "FB_VERIFY_TOKEN": w_fb_verify,
                    "DATABASE_URL": w_db,
                    "MESSENGER_PART_2_BANK_BLOCK": w_bank,
                    "MESSENGER_PART_3_CEO_NOTE": w_ceo,
                }
                merge_env_file(ENV_PATH, updates)
                load_dotenv(ENV_PATH, override=True)
                _mark_saved()
                st.success("Đã ghi .env")
        with c2:
            if st.button("Kiểm tra kết nối (/health)", key="wiz_check_health"):
                _check_health()

        _render_restart_banner(ack_button_key="restart_banner_ack_setup")
        _restart_commands()

    with tab_ops:
        st.subheader("Trạng thái bot")
        if st.button("Làm mới /health", key="ops_refresh_health"):
            _check_health()

        st.subheader("Sửa bank block + CEO note")
        load_dotenv(ENV_PATH, override=True)
        o_bank = st.text_input(
            "MESSENGER_PART_2_BANK_BLOCK",
            value=os.environ.get("MESSENGER_PART_2_BANK_BLOCK", ""),
            key="ops_bank",
        )
        o_ceo = st.text_input(
            "MESSENGER_PART_3_CEO_NOTE",
            value=os.environ.get("MESSENGER_PART_3_CEO_NOTE", ""),
            key="ops_ceo",
        )
        if st.button("Lưu bank + CEO note", key="ops_save_bank_ceo"):
            merge_env_file(
                ENV_PATH,
                {
                    "MESSENGER_PART_2_BANK_BLOCK": o_bank,
                    "MESSENGER_PART_3_CEO_NOTE": o_ceo,
                },
            )
            load_dotenv(ENV_PATH, override=True)
            _mark_saved()
            st.success("Đã cập nhật .env")

        _render_restart_banner(ack_button_key="restart_banner_ack_daily")
        _restart_commands()

        st.subheader("Log tail (đã lọc secret)")
        log_path = st.text_input(
            "Đường dẫn file log",
            value=os.environ.get("ADMIN_LOG_TAIL_PATH", ""),
            key="ops_log_path",
        )
        if st.button("Đọc tail", key="ops_read_log_tail") and log_path.strip():
            p = Path(log_path.strip())
            if not p.is_file():
                st.error("File không tồn tại.")
            else:
                raw = p.read_text(encoding="utf-8", errors="replace")
                st.text_area(
                    "Nội dung (đã redact)",
                    redact_log_text(raw),
                    height=320,
                    key="ops_log_tail_view",
                )


if __name__ == "__main__":
    main()
