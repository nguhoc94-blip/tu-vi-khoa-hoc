# Runbook cơ bản

**Ranh giới:** khởi động / restart / đọc log cơ bản có thể do vận hành **nếu** đã được cấp quyền server và hướng dẫn. Sửa `.env` production, DB, Meta app — **Engineering**. Xem `docs/handoff_checklist.md`.

## Khởi động

1. Kích hoạt venv, `pip install -r requirements.txt`.
2. Đặt biến môi trường (DB, OpenAI, Messenger).
3. Chạy: `uvicorn app.main:app --host 0.0.0.0 --port 8000` (hoặc port reverse proxy).

## Dừng / restart

- Dừng tiến trình uvicorn (Ctrl+C hoặc signal trên process manager).
- Restart sau khi đổi `.env` hoặc deploy bản mới.

## Kiểm tra sức khỏe

- `GET /health`.
- Log: được phép `request_id`, `sender_id`, `state`, `event`; không log full PII theo README.

## Sự cố thường gặp

| Hiện tượng | Hướng xử lý |
|------------|-------------|
| Lỗi kết nối DB | Kiểm tra `DATABASE_URL`, firewall, Postgres đã chạy |
| OpenAI timeout / 401 | Key, quota, mạng; bot vẫn có thể trả fallback tùy luồng |
| Webhook 403/verify fail | So khớp verify token và URL Meta |

## Tham chiếu

- `docs/deployment_guide_step_by_step.md`
- `docs/handoff_checklist.md`
