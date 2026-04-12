# Smoke checklist — Nhịp 3 (staging khuyến nghị)

Đánh dấu `[x]` khi đã thực hiện. Ghi **staging** hoặc **prod** và thời gian.

| # | Mục | Kết quả mong đợi | Đã tick |
|---|-----|------------------|---------|
| 1 | `GET /health` | 200, `status=ok` | [ ] |
| 2 | `GET /readiness` (DB bình thường) | 200 `ready` | [ ] |
| 3 | `GET /readiness` (ngắt DB / sai URL) | 503 `not_ready` | [ ] |
| 4 | Webhook GET verify Facebook | 200 + challenge | [ ] |
| 5 | Webhook POST tin nhắn thật | Bot phản hồi, log không lộ token | [ ] |
| 6 | Admin login | Vào dashboard | [ ] |
| 7 | Admin Privacy → cleanup dedupe (nếu có quyền writer) | Thông báo số dòng + audit | [ ] |
| 8 | Chạy `python scripts/cleanup_webhook_dedupe.py` | In `rows deleted`, exit 0 | [ ] |
| 9 | `pytest tests/ -q` trên CI hoặc local | All passed | [ ] |

**Ghi chú evidence:** định danh bản (Git SHA *hoặc* deploy ID / `GIT_SHA` trên `/health` / mã release — xem `TEAM_EVIDENCE_STEPS.md`), môi trường (staging/prod), người chạy, ngày.

---

## Bản ghi nhận local (Builder — đối chiếu `Engineering_gửi_Builder.md`)

Môi trường **local dev** (không thay thế tick staging/prod ở bảng trên). Cập nhật: 2026-04-12.

| # | Mục | Local |
|---|-----|-------|
| 1 | `GET /health` | Đã xác nhận trong phiên test (xem `builder_evidence_nhip3.md`) |
| 2 | `GET /readiness` DB OK | Đã xác nhận |
| 3 | `GET /readiness` DB fail → 503 | Chưa bắt buộc ghi nhận local; làm trên staging theo checklist |
| 4 | Webhook GET verify | Theo cấu hình Facebook + ngrok local |
| 5 | Webhook POST Messenger | Đã: bot trả lời, log redact (evidence trong báo cáo Builder) |
| 6 | Admin login | Có trong regression pytest; smoke tay local tùy team |
| 7 | Admin Privacy / dedupe cleanup | Có route + audit (pytest unit/integration tối thiểu) |
| 8 | CLI `cleanup_webhook_dedupe.py` | Có trong runbook; chạy tay khi cần |
| 9 | `pytest tests/` | **66/66 passed** — `docs/pytest_last_run.txt` |
