# Hướng dẫn team — Evidence Nhịp 3 (lane completion)

Tài liệu **chuẩn thứ tự**: làm từ trên xuống. Không bỏ qua **Phần 1**; **Phần 2** và **Phần 3** tùy bạn đã có DB/host hay chưa.

**Tham chiếu thêm:** `runbook_deploy.md`, `smoke_checklist_nhip3.md`, `render.yaml` (trong cùng thư mục `backend/`).

---

## Thuật ngữ

| Thuật ngữ | Ý nghĩa |
|-----------|---------|
| **Thư mục backend** | Thư mục chứa `app/`, `requirements.txt`, `render.yaml` — trong repo: `QUAN LY TU VI/TAI_LIEU_DU_AN/backend` |
| **`<PUBLIC_URL>`** | URL công khai sau khi deploy (ví dụ `https://tuvi-backend-xxxx.onrender.com`). **Chỉ tồn tại sau Phần 3.** Trước đó dùng `http://127.0.0.1:8000` (Phần 2). |
| **Placeholder trong tài liệu** | Viết dạng `<...>` là **ô trống bạn phải thay** bằng giá trị thật — **không** copy nguyên chuỗi có dấu `<` `>` lên trình duyệt. |

---

## Phần 1 — Regression cục bộ (bắt buộc, không cần Internet)

**Mục đích:** chứng minh test tự động xanh trên bản code hiện tại.

1. Mở terminal (PowerShell).
2. Vào thư mục backend (đường dẫn mẫu trên Windows):

   ```powershell
   cd "C:\Users\<TÊN_USER>\Desktop\NGHỀ LẬP TRÌNH\tu vi khoa hoc\QUAN LY TU VI\TAI_LIEU_DU_AN\backend"
   ```

   *(Thay `<TÊN_USER>` bằng user Windows của bạn.)*

3. Cài dependency (nếu cần):

   ```powershell
   pip install -r requirements.txt
   ```

4. Chạy pytest:

   ```powershell
   python -m pytest tests/ -q
   ```

5. **Kỳ vọng:** dòng cuối dạng `NN passed`, **0 failed**.
6. **Lưu evidence:** copy toàn bộ output vào `docs/pytest_last_run.txt` (ghi thêm ngày giờ ở đầu file).

---

## Phần 2 — Chạy API trên máy (local) — nên làm trước khi deploy

**Mục đích:** thấy `/health` và (nếu có DB) `/readiness` chạy thật, **không** cần Render.

### 2.1. Chuẩn bị file `.env`

1. Trong thư mục backend, copy `.env.example` thành `.env` (nếu chưa có).
2. Mở `.env` và điền tối thiểu:
   - **`DATABASE_URL`** — nếu có PostgreSQL local hoặc instance cloud: chuỗi `postgresql://...`
   - Các biến khác (OpenAI, Facebook, Admin…) xem `runbook_deploy.md` — chỉ bắt buộc khi test webhook/admin thật.

### 2.2. Chạy server

Trong thư mục backend:

```powershell
uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Giữ cửa sổ terminal mở. Nếu báo thiếu module: `pip install -r requirements.txt`.

### 2.3. Kiểm tra bằng trình duyệt

1. Mở **thanh địa chỉ** (không phải ô tìm kiếm):
   - `http://127.0.0.1:8000/health` → JSON có `"status":"ok"`.
2. Tiếp:
   - `http://127.0.0.1:8000/readiness`
3. **Kỳ vọng:**
   - `DATABASE_URL` đúng và DB chạy → HTTP **200**, `"status":"ready"`.
   - Chưa có DB / sai URL → HTTP **503** — chấp nhận được tới khi cấu hình DB.

### 2.4. (Tuỳ chọn) Bỏ qua bootstrap DB khi chỉ thử nhanh

- Trong `.env`: `SKIP_DB_BOOTSTRAP=1`
- `/health` vẫn OK; nhiều tính năng cần DB sẽ lỗi — **không** thay cho deploy thật.

---

## Phần 3 — Lần đầu deploy lên Render (có URL public)

**Sau bước này bạn mới có `<PUBLIC_URL>`.**

### 3.1. Tài khoản & mã nguồn

1. Đăng ký / đăng nhập [dashboard.render.com](https://dashboard.render.com).
2. Đưa code lên Git (GitHub/GitLab/Bitbucket) **hoặc** phương án Render hỗ trợ.  
   *(Không dùng Git vẫn cần nguồn Render kéo được — xem tài liệu Render theo gói bạn chọn.)*

### 3.2. Tạo PostgreSQL (managed)

1. **New +** → **PostgreSQL** → tạo instance.
2. Sau khi xong: copy **Internal Database URL** hoặc dùng **Link database** từ Web Service (khuyến nghị).

### 3.3. Tạo Web Service (API)

1. **New +** → **Web Service** → chọn repository.
2. **Cấu hình quan trọng:**
   - **Root Directory:** thư mục có `requirements.txt` và `app/main.py`.  
     Monorepo: thường `QUAN LY TU VI/TAI_LIEU_DU_AN/backend` — **đối chiếu đúng cấu trúc repo trên Git**.
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - **Health Check Path:** `/health` (**không** dùng `/readiness` cho probe nền tảng — khóa Engineering).

### 3.4. Biến môi trường trên Render

Trang Web Service → **Environment** (không commit secret vào Git):

| Biến | Ghi chú |
|------|---------|
| `DATABASE_URL` | Link Postgres hoặc dán URL nội bộ Render. |
| `OPENAI_API_KEY` | Nếu bot gọi OpenAI. |
| `FB_*`, `ADMIN_*`, … | Theo `runbook_deploy.md` và `.env.example`. |
| `GIT_SHA`, `BUILD_TIME` | *(Tuỳ chọn)* hiển thị trên `GET /health` khi không dùng Git. |

### 3.5. Deploy và lấy URL thật

1. **Save** / **Deploy** → chờ trạng thái **Live**.
2. Trên trang service: mục **URL** — dạng `https://<tên-service>.onrender.com` = **`<PUBLIC_URL>`** (ghi lại cho team).
3. Trình duyệt (thanh địa chỉ), ví dụ URL là `https://tuvi-backend-abc.onrender.com`:

   `https://tuvi-backend-abc.onrender.com/health`

   *(Luôn thay bằng URL thật — không gõ ký tự `<` `>`.)*

---

## Phần 4 — Smoke trên môi trường có URL (staging hoặc prod)

**Điều kiện:** đã có `<PUBLIC_URL>` (Phần 3) hoặc host tương đương.

Mở `smoke_checklist_nhip3.md`, đánh dấu `[x]` từng mục. Thay `<PUBLIC_URL>` bằng URL thật.

| Bước | Hành động |
|------|-----------|
| S1 | `https://<PUBLIC_URL>/health` → 200, `"status":"ok"`. |
| S2 | `https://<PUBLIC_URL>/readiness` → 200 `"ready"` khi DB nối đúng. |
| S3 | *(Tuỳ chọn, staging)* 503 khi DB tắt — **không** làm trên prod. |
| S4 | Facebook Developer → Webhook → Verify; callback `https://<PUBLIC_URL>/webhook` (route mặc định). |
| S5 | Tin test từ Page → bot phản hồi; log không lộ secret. |
| S6 | `https://<PUBLIC_URL>/admin/login` → Dashboard. |
| S7 | `https://<PUBLIC_URL>/admin/privacy` — role **writer**: cleanup dedupe + audit. |
| S8 | Máy có `DATABASE_URL` trỏ đúng DB đó: `python scripts/cleanup_webhook_dedupe.py`. |
| S9 | Đính kèm kết quả Phần 1 (pytest). |

**Cuối checklist:** ghi **staging/prod**, **người thực hiện**, **ngày giờ**.

---

## Phần 5 — Khi chưa deploy (chưa có `<PUBLIC_URL>`)

Hợp lệ cho báo cáo tạm nếu Engineering chấp nhận:

1. Hoàn thành **Phần 1** (pytest + `pytest_last_run.txt`).
2. Hoàn thành **Phần 2** tối thiểu: `/health` local OK; ghi rõ `/readiness` 200 hay 503 và lý do.
3. Trong báo cáo: **“Chưa deploy public; đã verify local theo TEAM_EVIDENCE_STEPS Phần 1–2.”**
4. Làm **Phần 3–4** khi team lên staging.

---

## Phần 6 — Định danh bản (SHA / không Git)

- **Có Git:** từ thư mục gốc repo: `git rev-parse HEAD` → `docs/git_sha_for_evidence.txt` hoặc báo cáo.
- **Không Git:** screenshot deploy Render (deploy id), hoặc env `GIT_SHA` + `BUILD_TIME`, hoặc mã release nội bộ.

---

## Phần 7 — Gói nộp Engineering (tối thiểu)

1. Định danh bản (Phần 6).  
2. `docs/pytest_last_run.txt` (hoặc log pytest tương đương).  
3. `smoke_checklist_nhip3.md` đã tick + ghi chú môi trường — hoặc tóm tắt **Phần 5** nếu chưa deploy.  
4. *(Tuỳ chọn)* Ảnh `/health` và `/readiness` (local hoặc public).

---

## Checklist nhanh (copy cho meeting)

- [ ] Phần 1 — pytest xanh + lưu `pytest_last_run.txt`  
- [ ] Phần 2 — `/health` local OK  
- [ ] Phần 3 — Render: Postgres + Web Service + env + URL + `/health` public OK  
- [ ] Phần 4 — `smoke_checklist_nhip3.md` đã tick (hoặc Phần 5 nếu chưa deploy)  
- [ ] Phần 6–7 — định danh bản + gói evidence  
