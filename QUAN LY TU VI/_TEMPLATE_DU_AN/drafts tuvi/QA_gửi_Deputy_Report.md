## QA REPORT
Từ: QA
Gửi: Deputy (chính) / COO (copy)
Ngày: 2026-04-08
---
Đạt spec chưa: có

Lỗi P0 (chặn demo): không có

Lỗi P1 (cần sửa sớm): không có

Lỗi P2 (để sau được): không có

Thiếu năng lực thực thi: không

Kết luận: đủ điều kiện demo / Gate Output

Bằng chứng:
1. Bám spec/acceptance đã khóa:
- COO Phase 2 giao QA review đúng các điểm: Setup Wizard 6 field, lưu `.env`, `BACKEND_BASE_URL` mặc định `http://localhost:8000` không nằm trong Wizard, `/health`, sửa/lưu bank + CEO note, restart banner, outbound đúng thứ tự, helper merge `.env`, log tail không lộ raw secret, docs local-only, và không vượt scope.
- CEO INFORM QA Phase 2 cũng khóa đúng 5 trọng tâm: Setup Wizard, Admin Panel, `.env` safety, restart banner, secret không lộ.

2. Tái kiểm trực tiếp trên artifact `backend.zip`:
- `app/services/final_message_builder.py` đã bỏ hard-code và đọc 2 giá trị từ env:
  - `MESSENGER_PART_2_BANK_BLOCK`
  - `MESSENGER_PART_3_CEO_NOTE`
- Repro trực tiếp bằng import module:
  - set env `BANKX` / `CEOX`
  - gọi `build_messenger_outbound(reading_body='BODYX')`
  - output nhận được đúng thứ tự `BODYX -> BANKX -> CEOX`.
- `app/utils/env_file.py` có helper merge `.env` chỉ thay key trong scope, giữ key ngoài scope.
- Repro trực tiếp bằng file tạm:
  - input: `KEEP_ME=1`, comment, `OPENAI_API_KEY=old`
  - update key mục tiêu
  - kết quả: `KEEP_ME=1` và comment vẫn còn, key mục tiêu được cập nhật đúng.
- `app/utils/log_redact.py` redact được secret/log nhạy cảm.
- Repro trực tiếp:
  - input chứa `OPENAI_API_KEY=sk-...`, `DATABASE_URL=postgresql://...`, `FB_VERIFY_TOKEN=...`
  - output bị thay bằng `[REDACTED]`, không lộ raw secret.

3. Kiểm tra code/UI:
- `admin.py` có đúng 3 field secret dùng `type="password"`:
  - `OPENAI_API_KEY`
  - `FB_PAGE_ACCESS_TOKEN`
  - `FB_VERIFY_TOKEN`
- Wizard có đúng 6 field scope:
  - `OPENAI_API_KEY`
  - `FB_PAGE_ACCESS_TOKEN`
  - `FB_VERIFY_TOKEN`
  - `DATABASE_URL`
  - `MESSENGER_PART_2_BANK_BLOCK` (label bank block)
  - `MESSENGER_PART_3_CEO_NOTE` (label CEO note)
- Không có `st.text_input("BACKEND_BASE_URL"... )`; `BACKEND_BASE_URL` được giữ ngoài Wizard.
- `admin.py` khóa mặc định `PANEL_BACKEND_DEFAULT = "http://localhost:8000"`.
- Có restart banner rõ ràng sau mỗi lần lưu config và có lệnh restart copy-paste PowerShell/bash.
- `app/main.py` vẫn có `GET /health` trả `{"status": "ok"}`.

4. Docs/handoff:
- `README.md` có đúng 2 lệnh COO khóa:
  - `pip install streamlit`
  - `streamlit run admin.py`
- `docs/admin_panel_local.md` và `docs/runbook_basic.md` đều nêu local-only, giữ `BACKEND_BASE_URL` mặc định `http://localhost:8000`, nhắc restart backend sau khi đổi config, và phân biệt phần vận hành cơ bản với phần cần Engineering hỗ trợ.
- `.env.example` có đủ các key mới cho footer message và ghi rõ `BACKEND_BASE_URL` là tùy chọn, không thuộc 6 field Wizard.

5. Scope boundary:
- Không thấy evidence route HTTP mới cho admin panel; panel dùng route sẵn có `/health`.
- Không thấy evidence thay DB schema hoặc mở flow Messenger mới để phục vụ admin panel.
- Builder report chính thức trong `04_reports.md` cũng liệt kê file touched tập trung vào:
  - `admin.py`
  - `app/utils/env_file.py`
  - `app/utils/log_redact.py`
  - `app/services/final_message_builder.py`
  - docs / `.env.example` / `requirements.txt`
  và kết quả pytest tổng là `18 passed`, không còn blocker kỹ thuật.

6. Ghi chú về replay môi trường QA:
- Khi thử chạy full `pytest` trong container QA hiện tại, môi trường Python của container bị xung đột `pydantic`/`pydantic-core` ở tầng runner chung, nên tôi không dùng lỗi đó để gắn blocker cho artifact.
- Tôi dùng tái kiểm trực tiếp trên các module thuần của artifact + code inspection + đối chiếu builder evidence để kết luận.