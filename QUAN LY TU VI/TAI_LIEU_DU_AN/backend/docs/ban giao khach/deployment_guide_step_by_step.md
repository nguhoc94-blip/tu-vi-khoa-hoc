# Hướng dẫn triển khai từng bước (backend TuVi)

## 0. Thứ tự đọc tài liệu (khuyến nghị)

Làm **lần lượt** trước khi lên server:

1. `docs/config_checklist.md` — biết cần env / quyền gì.
2. File này (`deployment_guide_step_by_step.md`) — clone, venv, chạy API.
3. `docs/runbook_basic.md` — vận hành hằng ngày, sự cố.
4. `docs/expected_result_examples.md` — đối chiếu kết quả đúng.
5. `docs/handoff_checklist.md` — checklist nghiệm thu + **ranh giới khách / Engineering**.

Mục **Ranh giới** trong `handoff_checklist.md` và `config_checklist.md` cho biết bước nào khách (không IT) có thể tự làm và khi nào cần Engineering.

## 1. Chuẩn bị

- Python 3.10+ (đã kiểm tra với 3.10).
- PostgreSQL nếu dùng webhook + lưu session/reading (theo `sql/*.sql`).

## 2. Lấy mã và môi trường ảo

Thực hiện **theo thứ tự** (bước sau phụ thuộc bước trước).

```bash
cd QUAN_LY_TU_VI/TAI_LIEU_DU_AN/backend
python -m venv .venv
# Windows PowerShell:
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## 3. Biến môi trường

- Sao chép `.env.example` → `.env` (nếu có trong repo) và điền giá trị thật.
- Xem thêm `docs/config_checklist.md`.

## 4. Chạy API

```bash
# Từ thư mục backend, PYTHONPATH trỏ vào app
set PYTHONPATH=.
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## 5. Kiểm tra nhanh

- `GET http://localhost:8000/health` → 200.
- `POST /generate-reading` với body hợp lệ → có `normalized_input`, `chart_json`, `teaser`.

## 6. Messenger (Meta)

- Cấu hình URL webhook trỏ tới `GET/POST /webhook` theo tài liệu Product/Engineering.
- Verify token khớp cấu hình server.

## 7. Sau deploy

- Chạy `python -m pytest tests/ -v` trên môi trường build/CI nếu có pipeline.
