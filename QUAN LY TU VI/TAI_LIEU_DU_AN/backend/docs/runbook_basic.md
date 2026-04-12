# Runbook cơ bản (backend TuVi)

**Ranh giới:** khởi động / restart / đọc log cơ bản có thể do vận hành **nếu** đã được cấp quyền server. Sửa `.env` production, DB, Meta app — **Engineering**. Xem gói `docs/ban giao khach/` nếu được bàn giao kèm checklist.

## Khởi động API

1. `cd backend`, kích hoạt venv, `pip install -r requirements.txt`.
2. Đặt `.env` (tối thiểu: `MESSENGER_PART_2_BANK_BLOCK`, `MESSENGER_PART_3_CEO_NOTE`, và các biến DB/Meta/OpenAI theo nhu cầu).
3. `uvicorn app.main:app --host 0.0.0.0 --port 8000` (hoặc `--reload` khi dev).

## Admin Panel (Streamlit)

Hai lệnh COO khóa:

```bash
pip install streamlit
streamlit run admin.py
```

Chi tiết: `docs/admin_panel_local.md`.

**Sau khi đổi bank/CEO hoặc Wizard lưu `.env`:** phải **restart uvicorn** để process đọc lại biến môi trường.

## Kiểm tra sức khỏe

- `GET http://localhost:8000/health` → JSON `status: ok`.

## Sự cố thường gặp

| Hiện tượng | Hướng xử lý |
|------------|-------------|
| `RuntimeError` thiếu `MESSENGER_PART_*` | Điền `.env` hoặc Wizard; restart server |
| Webhook lỗi verify | So khớp `FB_VERIFY_TOKEN` với Meta |
| Panel không gọi được `/health` | Backend có chạy port 8000 không; firewall |

## Tham chiếu

- `docs/admin_panel_local.md`
- `README.md`
