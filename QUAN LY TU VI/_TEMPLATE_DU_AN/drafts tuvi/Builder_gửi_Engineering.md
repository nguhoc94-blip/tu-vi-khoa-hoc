## BUILDER → ENGINEERING
Từ: Builder  
Gửi: Engineering  
Ngày: 2026-04-11 (**cập nhật: deploy production + vòng bảo mật khẩn cấp — 2026-04-12**)  
Phase: Phase 2 / **Nhịp 3 — BUILDER REPORT (thi công xong + deploy production + remediation bảo mật)**  

---

## VÒNG KHẮC PHỤC BẢO MẬT (memo `Engineering_gửi_Builder.md` — 2026-04-12)

**Căn cứ:** Engineering mở vòng làm sạch secret / repo trước khi khóa `LANE COMPLETION REPORT` gửi COO.

### 1. Secret hygiene — việc đã làm

| Hạng mục | Kết quả |
|----------|---------|
| `.env` chứa secret thật | **Không** nằm trong Git — chỉ `.env.example` (placeholder `user:pass@localhost`) được track |
| `.gitignore` gốc repo | Đã có `**/.env`, `.env.txt`, `bot tuvi.txt`, `*.zip`, venv, `__pycache__` — bổ sung **`ngrok.exe` / `ngrok`** |
| Rà soát docs tracked | Không thấy API key / token thật trong `.md`/`.txt` commit (chỉ mẫu test redact trong `test_log_redact_nhip3.py` và log pytest — placeholder) |
| `ngrok.exe` | **Đã `git rm --cached`** — binary không còn trong tree Git; file có thể giữ local, không bàn giao qua repo |

### 2. Repo visibility

| Trước | Sau remediation |
|-------|-----------------|
| Repo từng **public** (phục vụ tích hợp Render API) | **`private: true`** trên GitHub `nguhoc94-blip/tu-vi-khoa-hoc` (2026-04-12) |

**Lưu ý:** Nếu auto-deploy Render ngừng nhận push sau khi private, owner cần xác nhận **Render ↔ GitHub** đã kết nối qua **GitHub App** (Dashboard Render → repo settings).

### 3. Rotate secret (chỉ tên key — không ghi giá trị)

| Key / nhóm | Builder đã rotate? | Ghi chú |
|--------------|-------------------|---------|
| `OPENAI_API_KEY` | **Không** | Rotate trên OpenAI dashboard nếu key từng lộ qua kênh không tin cậy |
| `FB_PAGE_ACCESS_TOKEN` | **Không** | Rotate trong Meta Developer / Page settings nếu có nguy cơ |
| `FB_APP_SECRET` | **Không** | Nếu dùng verify chữ ký webhook — rotate trong App settings nếu cần |
| `DATABASE_URL` / mật khẩu Postgres | **Không** | Reset password instance `tuvi-db` trên Render nếu URL đầy đủ từng lộ |
| Render **API key** (`rnd_…`) | **Không** | Thu hồi / tạo key mới trong Render Account → API Keys nếu từng lộ |
| GitHub **PAT** (nếu dùng automation) | **Không** | Thu hồi token cũ, tạo PAT mới nếu từng lộ |

**Basis:** Builder **không** có quyền thay thế secret trên tài khoản owner; không kết luận cảm tính “chưa lộ”. Theo policy memo: nếu secret **có khả năng** đã xuất hiện ngoài vault — **owner phải rotate** và cập nhật env trên Render.

### 4. Verify sau remediation

| Kiểm tra | Kết quả (2026-04-12) |
|-----------|----------------------|
| `GET https://tuvi-backend-ocgd.onrender.com/health` | `200` — `status=ok` |
| `GET …/readiness` | `200` — `status=ready` |

**Git — chuỗi commit remediation trên `main`:** bắt đầu `004979c` (ngrok + private + docs); **HEAD evidence khuyến nghị:** `4b088ec`.

### 5. Kết luận cho Engineering

- **Artifact Git (tracking + visibility):** **Đạt** — không còn `ngrok.exe` trong repo; `.env` không track; repo **private**.
- **Rotation:** **Chưa thực hiện bởi Builder** — checklist tên key ở mục 3; **quyết định khóa lane / yêu cầu rotate** thuộc Engineering/owner.
- **Không có blocker quyền** cho bước đặt repo private (đã thực hiện được).

---

## BÁO CÁO E — NHIỆM VỤ ĐÃ HOÀN THÀNH (Deploy Render Production — 2026-04-12)

**Trạng thái:** backend đã **live** trên Render; `/health` và `/readiness` xác nhận OK sau khi sửa lỗi build/start.

### 1. URL & service

| Mục | Giá trị |
|-----|---------|
| **Public URL** | `https://tuvi-backend-ocgd.onrender.com` |
| **Webhook** | `https://tuvi-backend-ocgd.onrender.com/webhook` |
| **Render service** | `tuvi-backend` (slug `tuvi-backend-ocgd`) |
| **Region** | Oregon (US West) — cùng region với Postgres Free `tuvi-db` |
| **GitHub** | `https://github.com/nguhoc94-blip/tu-vi-khoa-hoc` (branch `main`, **private** sau remediation) |

### 2. Bằng chứng kỹ thuật (sau deploy live)

| Kiểm tra | Kết quả |
|----------|---------|
| `GET /health` | `200` — `{"status":"ok","service":"tuvi-backend"}` |
| `GET /readiness` | `200` — `{"status":"ready"}` (DB PostgreSQL Render kết nối OK) |
| Migrations | Chạy qua bootstrap `db_init` trên DB production (fresh) |

### 3. Commit liên quan deploy (sau `b481e3a`)

| SHA | Nội dung |
|-----|----------|
| `f5a7204` | Thêm `python-multipart` vào `requirements.txt` — sửa lỗi FastAPI Form khi start trên Render |
| `9f9d874` | `db_init.py`: rollback sau `UndefinedTable` trong `_is_applied`; mỗi migration một connection — sửa `InFailedSqlTransaction` khi DB trống |

**HEAD production (khuyến nghị ghi evidence):** `9f9d874`

### 4. Cấu hình đã áp dụng trên Render (tóm tắt — không ghi secret)

- **Root Directory:** `QUAN LY TU VI/TAI_LIEU_DU_AN/backend`
- **Build:** `pip install -r requirements.txt`
- **Start:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- **Health check path:** `/health` (khóa Engineering)
- **Env:** `DATABASE_URL` (Postgres Render), OpenAI, Facebook, Messenger blocks, Admin bootstrap, `ADMIN_COOKIE_SECURE=1`, `DEBOUNCE_SECONDS`, v.v. — giá trị thật chỉ trên Render Dashboard

### 5. Việc còn lại cho vận hành / Product

- **Facebook Developer:** cập nhật Callback URL webhook sang `https://tuvi-backend-ocgd.onrender.com/webhook` (Verify Token giữ đúng giá trị đã cấu hình trên Render).
- **Smoke prod:** tick `docs/smoke_checklist_nhip3.md` trên môi trường production.
- **Bảo mật:** repo đã **private** lại (xem § *VÒNG KHẮC PHỤC BẢO MẬT*). Xác nhận Render vẫn pull được từ GitHub App; owner xử lý **rotate secret** theo checklist trong báo cáo bảo mật nếu Engineering yêu cầu.

### 6. Đối chiếu memo Engineering (cập nhật sau deploy)

- **Deploy path Render + runbook:** đã có service thật + runbook vẫn dùng được.
- **Evidence prod:** URL public + health/readiness như trên; SHA `9f9d874`.

---

### Đối chiếu `Engineering_gửi_Builder.md` (memo lệnh mở Nhịp 3 — 2026-04-11)

Bảng dưới đây map trực tiếp **Output mong muốn**, **Điều kiện done**, **Khóa triển khai** trong memo Engineering → trạng thái Builder.

#### Output mong muốn (memo § Output)

| # | Yêu cầu Engineering | Trạng thái | Tham chiếu |
|---|---------------------|------------|------------|
| 1 | Thi công xong Nhịp 3 trên codebase chuẩn | Đã xong | Bảng hạng mục Nhịp 3 bên dưới + code `TAI_LIEU_DU_AN/backend/` |
| 2 | Gửi lại báo cáo BUILDER REPORT (việc làm, file, test, pass/fail, lỗi, scope, bằng chứng) | Đã nộp (bản này) | Mục này + § evidence + `docs/builder_evidence_nhip3.md` |
| 3 | Không gửi COO trực tiếp | Tuân thủ | Không có outbound COO từ Builder |

#### Điều kiện done (memo § Điều kiện done)

| Điều kiện | Trạng thái | Ghi chú |
|-----------|------------|---------|
| Deploy path Render + runbook | Đạt | `render.yaml` + `docs/runbook_deploy.md` |
| `/health`, `/readiness` dùng được | Đạt | Liveness = `/health`; readiness DB = `/readiness` (pytest + runbook) |
| Log redact / trust-safety / anonymization baseline | Đạt | `log_redact`, `data_subject_service`, admin privacy + audit |
| Procedure cleanup `webhook_dedupe` | Đạt | 24h retention; CLI + admin maintenance; test `test_webhook_dedupe_cleanup` |
| Full pytest pass | Đạt | **66/66** — `docs/pytest_last_run.txt` (2026-04-12) |
| Smoke evidence đủ lane completion | Đạt (local + tài liệu); **staging/prod** chờ team | `smoke_checklist_nhip3.md`, `builder_evidence_nhip3.md`, `TEAM_EVIDENCE_STEPS.md` |

#### Khóa triển khai bổ sung (memo § Khóa)

| Khóa | Tuân thủ |
|------|----------|
| Platform liveness = `/health`; `/readiness` không làm default platform liveness | Có — `render.yaml` `healthCheckPath: /health` |
| Retention `webhook_dedupe` = **24h**, không đổi semantics | Có — code + test khóa 24h |
| Anonymization baseline + audit; route sau auth/RBAC | Có — Nhịp 2 admin + Nhịp 3 privacy |
| Không kéo scope Nhịp 3 (no platform dashboard mới, no monitoring stack, không sửa 4 lát bridge ngoài hook tối thiểu) | **Nhịp 3 gốc:** không vượt. **Sau lane:** có thay đổi theo **CEO Direct** (model, prompt, lock/debounce) — đã tách mục § *BỔ SUNG SAU TRIỂN KHAI* |
| Evidence: SHA/artifact, pytest, smoke, runbook; ghi rõ staging vs prod | Có — `git_sha_for_evidence.txt`, `pytest_last_run.txt`, checklist, runbook; **prod Render live** — xem § *BÁO CÁO E* |

#### Lỗi còn lại / blocker

- **Không có blocker** mở lane theo memo.  
- **Hạn chế:** tick đủ smoke **prod** trên checklist + xác nhận webhook Facebook trỏ đúng URL production (xem § *BÁO CÁO E*).

#### Vượt scope so với memo Engineering

- **Phạm vi Nhịp 3 (memo):** không vượt.  
- **Ngoài scope memo (sau CEO chỉ đạo):** nâng model OpenAI, viết lại prompt, bỏ `max_tokens` tương thích model, fix test isolation dedupe, **per-sender lock + debounce** — toàn bộ ghi trong § *Nhịp 3 — BỔ SUNG SAU TRIỂN KHAI*.

---

### Nhịp 3 — báo cáo thi công (theo `Engineering_gửi_Builder.md` lệnh mở Nhịp 3)

**Trạng thái:** đã thi công trên `QUAN LY TU VI/TAI_LIEU_DU_AN/backend/`. **pytest: 66 passed** (`python -m pytest tests/ -v` trong `backend/`; thời gian ~10.5s do debounce trong pipeline — xem `docs/pytest_last_run.txt`).

| Hạng mục | Đã giao | Ghi chú |
|----------|---------|---------|
| Deploy path Render | `backend/render.yaml` | **healthCheckPath = `/health`** (liveness); `/readiness` chỉ runbook/DB verify — đúng khóa Engineering |
| Runbook | `backend/docs/runbook_deploy.md` | deploy / redeploy / rollback / verify webhook / dedupe CLI |
| Observability | `backend/docs/observability_queries.md` | SQL mẫu, không mở stack monitoring mới |
| Smoke checklist | `backend/docs/smoke_checklist_nhip3.md` | checklist tay; đánh dấu staging vs prod trong runbook |
| `/health` | `app/main.py` | `status`, `service`, optional `GIT_SHA`, `BUILD_TIME` — không gọi DB |
| `/readiness` | `app/main.py` | Giữ kiểm tra DB qua `check_connection_ok()` |
| Log redact | `app/utils/log_redact.py` + `RedactingFormatter` gắn root | Mở rộng pattern Bearer/access_token; format log đi qua redact |
| Middleware | `app/main.py` | `X-Request-ID`; bắt lỗi chưa xử lý → JSON `internal_error` + request_id (không đổi logic bridge) |
| Webhook | `app/api/messenger.py` | Giới hạn body (`MAX_WEBHOOK_BODY_BYTES`, default 256KiB) → 413; excerpt dedupe qua `redact_log_line` |
| Guardrail text | `app/services/messenger_handler.py` | `MAX_INBOUND_TEXT_CHARS` (default 8000) → tin nhắn thân thiện, không vào bridge |
| Cleanup dedupe 24h | `app/services/webhook_dedupe_cleanup.py` | Retention **24 giờ** cố định; batch 500; CLI `scripts/cleanup_webhook_dedupe.py`; Admin POST `/admin/maintenance/webhook-dedupe-cleanup` + audit |
| Anonymization | `app/services/data_subject_service.py` | Baseline: session scrub, readings text/json redacted, funnel/dedupe/profile xóa hoặc scrub; **admin** `GET/POST /admin/privacy*` + audit `data_subject_anonymized` |
| Migration | `sql/migrations/015_nhip3_placeholder.sql` | No-op có chủ đích (DDL không bắt buộc); chain migration tiếp tục additive |
| Tests mới | `tests/test_nhip3_health.py`, `test_webhook_payload_limit.py`, `test_log_redact_nhip3.py`, `test_data_subject_unit.py`, `test_webhook_dedupe_cleanup.py` | — |

**Chưa làm / giới hạn:** **đã deploy production Render** (2026-04-12); cần team **cập nhật webhook Facebook** + tick smoke checklist prod. **Không vượt scope** Nhịp 3 (không dashboard platform mới, không đổi 4 lát bridge ngoài guardrail/log).

**Hướng dẫn team (từng bước):** `backend/docs/TEAM_EVIDENCE_STEPS.md` (pytest local + smoke tay; **SHA Git không bắt buộc** — có thể dùng deploy ID / `GIT_SHA` env / mã release).

**Evidence đề xuất đính kèm lane completion:** định danh bản (SHA **hoặc** tương đương trong `docs/git_sha_for_evidence.txt`), `docs/pytest_last_run.txt`, `smoke_checklist_nhip3.md` đã tick, ảnh `/health` + `/readiness` nếu có.

**Git SHA baseline lớn:** `b481e3a` (feat: add full backend Phase 2 + Render deploy config — 2026-04-12)  
**Git SHA production live (sau fix):** `9f9d874`  
**GitHub remote:** [https://github.com/nguhoc94-blip/tu-vi-khoa-hoc](https://github.com/nguhoc94-blip/tu-vi-khoa-hoc) — **private** (sau vòng remediation 2026-04-12)  
**Trạng thái:** ✅ **PUSHED** + ✅ **Render LIVE** — `https://tuvi-backend-ocgd.onrender.com` (chi tiết § *BÁO CÁO E*).

---

## Nhịp 3 — BỔ SUNG SAU TRIỂN KHAI (CEO Direct Instruction — 2026-04-12)

> **Ghi chú quan trọng:** Toàn bộ phần này được thực hiện **theo chỉ đạo trực tiếp từ CEO** sau khi Nhịp 3 hoàn thành, trong phiên test thực tế với Facebook Messenger. Không nằm trong scope Engineering ban đầu.

### A. Thiết lập môi trường local đầy đủ

| Hạng mục | Chi tiết |
|---|---|
| `.env` điền thật | Tất cả key thật từ `bot tuvi.txt` + `.env.txt`; password DB đúng `123456` |
| PostgreSQL | Database `messenger_bot` tạo mới; 15 migrations chạy thành công (001→015) |
| `python-multipart` | Cài thêm vào venv (thiếu gây lỗi Form Data FastAPI) |
| Uvicorn | Khởi động `http://127.0.0.1:8000`, `Application startup complete` |
| ngrok | Tunnel `https://subdivine-bewilderedly-joni.ngrok-free.dev` — URL khớp cũ, không cần đổi Facebook config |

### B. Smoke Test Live — Messenger thật (PASSED)

**Thời gian:** 2026-04-12 ~15:15–16:21 (GMT+7)

| Tin nhắn | HTTP | Kết quả |
|---|---|---|
| `mình kinh doanh thời trang hè` | `POST /webhook → 200 OK` | Bot trả lời ✅ |
| `thử là tôi hợp làm hay không?` | `POST /webhook → 200 OK` | Bot trả lời ✅ |
| `alo` | `POST /webhook → 200 OK` | Bot trả lời ✅ |

Xác nhận: `X-Hub-Signature-256` hợp lệ, `X-Request-Id` có trong response, `User-Agent: facebookexternalua`.

### C. Nâng cấp Model OpenAI — CEO chỉ đạo

> **Nguồn gốc:** CEO yêu cầu nâng model lên cao nhất để test chất lượng.

| Thay đổi | Trước | Sau |
|---|---|---|
| `OPENAI_MODEL` trong `.env` | `gpt-4o-mini` | `gpt-5.4` |
| Timeout conversation | 25s | 60s |
| Timeout teaser + paid | 25s | 60s |

**Lý do chọn `gpt-5.4`:** Đây là model frontier mới nhất của OpenAI (tính đến 2026-04), hỗ trợ Chat Completions API, context 1M token, tốt nhất cho hội thoại đa bước. Chi phí ~3–4x so với `gpt-4o` — phù hợp cho giai đoạn test, cần đánh giá lại khi scale production.

**File thay đổi:**
- `backend/.env` — `OPENAI_MODEL=gpt-5.4`
- `app/services/conversation_bridge.py` — `_CONVERSATION_TIMEOUT = 60.0`
- `app/services/openai_teaser.py` — `OPENAI_TIMEOUT_SECONDS = 60.0`
- `app/services/openai_paid.py` — `PAID_TIMEOUT_SECONDS = 60.0`

### D. Viết lại Prompt hệ thống — CEO chỉ đạo trực tiếp

> **Nguồn gốc:** CEO nhận xét bot trả lời "sơ sài, không giống hỏi trực tiếp ChatGPT" và chỉ đạo viết lại prompt chuyên sâu hơn + bỏ giới hạn 400 từ.

**Thay đổi prompt (6 file trong `backend/prompts/`):**

| File | Thay đổi |
|---|---|
| `system_free_production.txt` | Persona "chuyên gia 20 năm", 4 phần cấu trúc, 200–350 từ |
| `system_full_production.txt` | 6 phần có emoji (Tổng quan / Sự nghiệp / Tài chính / Tình cảm / Sức khỏe / Lời khuyên vàng), yêu cầu dẫn chứng tên sao/cung, **không giới hạn từ** |
| `system_conversation.txt` | Bỏ giới hạn 400 từ, được dùng emoji, chuyên sâu cụ thể dẫn chứng sao/cung |
| `system_free.txt` | Đồng bộ phong cách mới |
| `system_paid.txt` | Đồng bộ cấu trúc 6 phần |

**Thay đổi code đi kèm:**

| File | Thay đổi |
|---|---|
| `app/services/conversation_bridge.py` | Xóa `_CONVERSATION_MAX_TOKENS = 600`, xóa `max_tokens=` khỏi OpenAI call (gpt-5.4 không nhận tham số này) |

### E. Fix Bug phát sinh trong phiên test

**Bug 1 — `max_tokens` không được gpt-5.4 chấp nhận:**
- Triệu chứng: Bot trả lời "Mình đang gặp sự cố kết nối AI"
- Nguyên nhân: `gpt-5.4` qua Chat Completions API báo lỗi khi nhận `max_tokens`
- Fix: Xóa tham số `max_tokens` khỏi `client.chat.completions.create()`

**Bug 2 — Test isolation fail khi DB thật đang chạy:**
- Triệu chứng: `test_webhook_returns_200_immediately` và `test_webhook_schedules_background_task` fail vì MID cố định đã bị lưu vào `webhook_dedupe` từ lần test trước
- Fix: Thêm autouse fixture vào `tests/conftest.py` để xóa test-MID trước mỗi test

### F. Kết quả Pytest sau tất cả thay đổi

```
66 passed in 10.57s  (platform win32, Python 3.10.11, pytest-8.4.2)
```

Evidence đầy đủ tại: `backend/docs/builder_evidence_nhip3.md` và `backend/docs/pytest_last_run.txt` (refresh 2026-04-12).

### H. Xử lý Race Condition — Khách nhắn nhanh — CEO chỉ đạo

> **Nguồn gốc:** CEO phát hiện khi test: "khách nhắn quá nhanh dường như mỗi lần trả lời đều không cùng 1 chat" — mỗi tin nhắn bị xử lý độc lập, gây mất ngữ cảnh hội thoại. CEO chỉ đạo xử lý theo cách tốt nhất.

**Giải pháp implemented: Per-sender Lock + Debounce 1.5s**

| Thành phần | Chi tiết |
|---|---|
| `_sender_pending` dict | Lưu `request_id` mới nhất của từng sender — "latest wins" |
| `_sender_locks` dict | `threading.Lock()` riêng mỗi sender — serialise pipeline |
| Debounce 1.5s | Task mới ngủ 1.5s trước khi xử lý; nếu task khác đến trong thời gian đó → task cũ bị skip |
| Double-check after lock | Sau khi acquire lock, kiểm tra lại một lần nữa để tránh edge case |
| Postback/Quick Reply | **Bypass debounce** — không bị delay, vì đây là hành động rõ ràng của user |
| Cấu hình runtime | `DEBOUNCE_SECONDS` trong `.env` (default 1.5, có thể điều chỉnh không cần deploy lại) |

**File thay đổi:** `app/services/messenger_handler.py`

**Cơ chế:**
```
User gửi A → pending[user]=A → sleep 1.5s
User gửi B → pending[user]=B → sleep 1.5s   (A bị ghi đè)
User gửi C → pending[user]=C → sleep 1.5s   (B bị ghi đè)

Task A thức → pending≠A → SKIP (logged)
Task B thức → pending≠B → SKIP (logged)
Task C thức → pending=C → acquire lock → XỬ LÝ ✓ (full context)
```

**Nếu user gửi 2 tin cách nhau >1.5s → cả 2 đều được xử lý tuần tự** (serial, không song song).

**Pytest sau thay đổi:**
```
66 passed in 10.57s  (tăng so với trước do debounce sleep 1.5s trong background pipeline)
```

---

### G. Tóm tắt toàn bộ thay đổi bổ sung

| Hạng mục | Trạng thái | Ghi chú |
|---|---|---|
| Môi trường local đầy đủ | ✅ | DB + migrations + venv + ngrok |
| Smoke test Messenger thật | ✅ | 3 tin nhắn, bot trả lời |
| Model nâng lên gpt-5.4 | ✅ | CEO chỉ đạo |
| Prompt viết lại chuyên sâu | ✅ | CEO chỉ đạo |
| Giới hạn 400/600 từ bỏ | ✅ | CEO chỉ đạo |
| Fix max_tokens gpt-5.4 | ✅ | Bug phát sinh khi test |
| Fix test dedupe isolation | ✅ | Bug phát sinh khi DB thật chạy |
| **Lock + Debounce race condition** | ✅ | **CEO chỉ đạo** |
| Pytest 66/66 PASSED | ✅ | Xác nhận không regression |

---

## Hướng dẫn push & deploy Render (bước team cần làm)

### Bước 1 — Tạo GitHub repository

1. Vào [https://github.com/new](https://github.com/new)
2. **Repository name:** `tu-vi-khoa-hoc`  |  **Owner:** `nguhoc94-blip`
3. **Visibility:** Private (khuyến nghị)
4. **Không** chọn Initialize README/gitignore (đã có sẵn trong commit)
5. Click **Create repository**

### Bước 2 — Push code lên GitHub

Mở terminal trong thư mục `tu vi khoa hoc`:

```powershell
git push origin main
```

Nếu bị yêu cầu đăng nhập, dùng Personal Access Token tại [https://github.com/settings/tokens](https://github.com/settings/tokens).

### Bước 3 — Kết nối Render và deploy

1. Vào [https://dashboard.render.com](https://dashboard.render.com)
2. Click **New** → **Blueprint** → chọn repo `tu-vi-khoa-hoc` → branch `main`
3. Render tự đọc `render.yaml` ở root; xác nhận service name `tuvi-backend`
4. Điền **secret** trong tab **Environment** (không nằm trong `render.yaml`):

| Key | Giá trị |
|-----|---------|
| `DATABASE_URL` | PostgreSQL URL (Render managed DB hoặc external) |
| `OPENAI_API_KEY` | Key từ OpenAI |
| `OPENAI_MODEL` | `gpt-5.4` |
| `FB_PAGE_ACCESS_TOKEN` | Token Facebook Page |
| `FB_VERIFY_TOKEN` | Token xác minh webhook |
| `FB_APP_SECRET` | App Secret Facebook |
| `ADMIN_BOOTSTRAP_EMAIL` | Email tài khoản admin đầu tiên |
| `ADMIN_BOOTSTRAP_PASSWORD` | Mật khẩu admin đầu tiên |
| `MESSENGER_PART_2_BANK_BLOCK` | Nội dung block bank |
| `MESSENGER_PART_3_CEO_NOTE` | Nội dung CEO note |

5. Click **Apply** → Render build (~2–3 phút)

### Bước 4 — Verify sau deploy

```
GET https://tuvi-backend.onrender.com/health   → {"status":"ok"}
GET https://tuvi-backend.onrender.com/readiness → {"status":"ready"}
```

Sau đó cập nhật Facebook Webhook URL sang domain Render (thay URL ngrok cũ).

---

## Nhịp 2 — báo cáo thi công (lịch sử)

**Trạng thái:** đã triển khai trên cây `QUAN LY TU VI/TAI_LIEU_DU_AN/backend/` theo brief Nhịp 2. **pytest trước Nhịp 3: 55 passed** (KB-2 + lát 4 + admin baseline).

### 0.1 Tóm tắt giao hàng

- **Admin baseline:** cookie session (`admin_sessions`), login Jinja2, dashboard/config (draft → publish) / campaigns / transcript / export JSON; audit log; bootstrap user qua `ADMIN_BOOTSTRAP_*` (xem `.env.example`).
- **Lát 3 KB-2:** `routing.kb2_awaiting_confirm`, tóm tắt birth → xác nhận → `confirmation_pre_chart_safe_close` + `_mode_generate`; funnel `birthdata_*`.
- **Lát 4:** một lần `confirmation_profile_switch_check` khi flow returning/paid_repeat + tín hiệu “hộ người khác”; default copy nếu DB chưa seed key.
- **CP3 surfaces:** seed `014_cp3_config_seed.sql`; `app_config_store` / `flow_routing` / `payload_handler` ưu tiên key final + fallback CP2; social proof theo policy (không bắn snippet user khi chưa publish asset).

### 0.2 File chính (tham chiếu nhanh)

| Nhóm | Đường dẫn |
|------|-----------|
| Migration | `013`…`015` trong `sql/migrations/` (gồm `015_nhip3_placeholder.sql`) |
| Bridge | `app/services/conversation_bridge.py`, `kb2_confirmation.py` |
| CP3 / CTA | `app/services/app_config_store.py`, `flow_routing.py`, `payload_handler.py` |
| Admin | `app/api/admin_portal.py`, `app/templates/admin/*.html`, `admin_session_service.py`, `admin_audit_service.py`, `admin_bootstrap.py`, `admin_password.py` |
| Tests | `tests/test_conversational_bridge.py`, `test_profile_awareness.py`, `test_generate_error_handling.py`, `test_admin_portal.py`, … |

### 0.3 Ghi chú / hạn chế còn lại

- **Payment / link thật:** nhãn và CTA lấy từ config; URL thanh toán thật do vận hành điền khi sẵn sàng.
- **Social proof:** chỉ draft/preview/policy trong DB; runtime không gửi snippet cho user nếu chưa bật publish (theo key policy đã seed).

---

## NHIỆP 3 — PLAN CHI TIẾT (đã duyệt; thi công xong — xem BUILDER REPORT phía trên)

**Trạng thái:** bản plan gốc; implementation khớp khóa Engineering (**`/health` = liveness**, dedupe **24h**, anonymization + audit). Chi tiết file và pytest nằm ở mục **Nhịp 3 — báo cáo thi công** đầu tài liệu.  
**Căn cứ:** lane plan Nhịp 3 đã khóa; codebase `QUAN LY TU VI/TAI_LIEU_DU_AN/backend/` sau Nhịp 2 (pytest 55 passed); CP3 đã bàn giao.

### N3.1 Mục tiêu Nhịp 3

| # | Mục tiêu | Mô tả ngắn |
|---|----------|------------|
| O1 | **Online readiness** | Deploy baseline **Render primary**: `render.yaml` (hoặc tương đương), env/secrets, health/readiness phục vụ probe, runbook vận hành. |
| O2 | **Observability** | Log/metric tối thiểu: health, lỗi request, token/fallback OpenAI; job **cleanup** `webhook_dedupe`; hướng dẫn query/dashboard ở mức Engineering. |
| O3 | **Trust / Safety** | Redact log nhất quán; **xóa / ẩn danh** profile & dữ liệu liên quan (baseline); guardrail + fallback trong biên release đầu (không đổi logic nghiệp vụ đã khóa). |
| O4 | **Regression / evidence** | Full pytest; smoke online checklist; **artifact** để Engineering gắn vào LANE COMPLETION REPORT. |

### N3.2 Breakdown task theo cụm

#### Cụm O — Ops / Online readiness

- **O1 — `render.yaml`:** service web (FastAPI), env theo runbook; **`healthCheckPath` = `/health`** (liveness, không DB); `/readiness` dùng trong runbook để verify DB; start `uvicorn`; Python khớp `requirements.txt`.
- **O2 — Runbook** (markdown trong repo, vd. `docs/runbook_deploy.md` hoặc `TAI_LIEU_DU_AN/runbook/` — **chỉ nếu Engineering chốt đường dẫn**): deploy lần đầu, redeploy, restart service, rollback image/commit, verify webhook (Facebook challenge + 1 sự kiện test), verify admin login.
- **O3 — Health surfaces:** mở rộng tối thiểu so với hiện trạng `app/main.py` (`/health`, `/readiness`): thêm `git_sha` / `build_time` từ env `GIT_SHA`/`BUILD_TIME` (optional) để support verify sau deploy; không đưa secret vào response.
- **O4 — Error surface HTTP:** thống nhất JSON lỗi cho route public (webhook) ở mức “đủ debug, không lộ nội dung user” — trong boundary Nhịp 3 (wrapper exception handler FastAPI nếu chưa có).

#### Cụm V — Observability

- **V1 — Structured logging:** `request_id` / `sender_id` (đã có một phần) — rà soát `app/api/messenger.py` (webhook), `conversation_bridge`, OpenAI clients; thêm field `event=` thống nhất cho: `webhook_ok`, `webhook_duplicate_skipped`, `openai_fallback`, `db_unavailable`.
- **V2 — Token / fallback:** hook sẵn có `record_openai_token_usage` trong `messenger_funnel_bridge.py` — document cách query `funnel_events` (SQL mẫu trong runbook hoặc comment migration); đếm fallback khi thiếu API key / lỗi client.
- **V3 — Cleanup `webhook_dedupe`:** retention **24 giờ** (đã khóa); Python batch + CLI + admin; index `webhook_dedupe_created_at_idx` từ migration 002.
- **V4 — Dashboard tối thiểu:** không bắt buộc Grafana trong Nhịp 3 nếu lane chỉ yêu cầu “query + hướng dẫn”; deliverable: **tài liệu** (vd. 5 query mẫu: error rate theo `event`, dedupe table size, token usage theo ngày).

#### Cụm T — Trust / Safety

- **T1 — Redact log:** mở rộng `app/utils/log_redact.py` (đã có pattern) — áp dụng cho mọi log line ghi raw payload webhook / header nhạy cảm; tùy chọn `logging.Filter` gắn root logger để không bỏ sót.
- **T2 — Profile deletion / anonymization:** endpoint **admin-protected** hoặc script vận hành: theo `sender_id` — xóa hoặc anonymize `messenger_sessions`, rows liên quan (`readings` policy: xóa PII trong metadata hoặc soft-delete flag — **additive migration** nếu cần cột `anonymized_at`); không xóa schema đã khóa Nhịp 1–2.
- **T3 — Guardrail / fallback:** trong biên release đầu — vd. giới hạn độ dài text user trước khi vào bridge; timeout OpenAI đã có — document; response thân thiện khi abuse (429/413) không đổi flow KB-2/lát 1–4.

#### Cụm R — Regression / smoke / evidence

- **R1 — Pytest:** `python -m pytest tests/ -q` toàn bộ; thêm test cho redact, cleanup SQL (nếu logic trong module), handler health mở rộng.
- **R2 — Smoke online:** checklist: GET `/health` 200; GET `/readiness` 200 khi DB up; POST webhook (signature hợp lệ) 200; một vòng KB-2 trên staging; admin login; một query funnel/token.
- **R3 — Artifact nộp Engineering:** bản export checklist đã tick + timestamp deploy + commit SHA + kết quả pytest (log file hoặc CI).

### N3.3 File / module dự kiến sửa hoặc thêm

| Khu vực | File / artifact (dự kiến) |
|---------|-----------------------------|
| Deploy | `render.yaml` (repo root hoặc `backend/`), `.env.example` bổ sung biến deploy |
| App shell | `app/main.py` — middleware logging, exception handler, health metadata |
| Webhook | `app/api/messenger.py` — redact, guardrail độ dài, log fields |
| DB job | `sql/migrations/015_webhook_dedupe_retention.sql` (function/cron note) hoặc `scripts/cleanup_webhook_dedupe.sql` |
| Trust | `app/utils/log_redact.py`; service mới `app/services/data_subject_service.py` hoặc route trong `admin_portal.py` |
| Docs | `runbook_deploy.md` (hoặc đường dẫn COO/E chốt), `observability_queries.md` |
| Tests | `tests/test_log_redact.py`, `tests/test_health.py`, mở rộng webhook tests nếu có guardrail |

*(Điều chỉnh tên file nếu tree thực tế khác — ví dụ `messenger.py` nằm ngoài snapshot workspace thì vẫn giữ đích `app/api/messenger.py` theo import `main.py`.)*

### N3.4 File / module không nên đụng (hoặc chỉ hook tối thiểu)

- **Không gộp / không refactor** `conversation_bridge` lát 1–4, `flow_routing`, `payload_handler` opening/KB-2 trừ khi chỉ thêm log wrapper hoặc guardrail không đổi nhánh.
- **Không đổi** hợp đồng webhook signature/dedupe key semantics đã khóa Nhịp 1.
- **Không** thêm preview sinh lá số trong admin (ràng buộc Nhịp 2).
- Migration: **chỉ additive**; không DROP cột/bảng nghiệp vụ.

### N3.5 Critical path (gợi ý thứ tự)

1. Engineering duyệt plan N3 (bản này).  
2. `render.yaml` + deploy staging + runbook khung.  
3. Health metadata + readiness verify trên staging.  
4. Redact + webhook log hygiene.  
5. Cleanup `webhook_dedupe` + tài liệu query observability.  
6. Baseline delete/anonymize + test + smoke checklist.  
7. Full pytest + đóng artifact cho LANE COMPLETION.

### N3.6 Phần có thể chạy song song

- Runbook + query doc **song song** với `render.yaml`.  
- Redact utility + unit test **song song** với cleanup SQL thiết kế.  
- Admin route anonymize **song song** với mở rộng `/health` (khác file).

### N3.7 Test / smoke plan cụ thể

| Hạng mục | Kiểu | Nội dung |
|----------|------|----------|
| Redact | Unit | Chuỗi chứa `sk-`, `DATABASE_URL`, token FB → `[REDACTED]` |
| Health | Unit/integration | `/health` 200; `/readiness` 503 khi DB mock fail |
| Webhook | Integration | Signature fail → 403; dedupe → log `duplicate_skipped` (đã có pattern test) |
| Anonymize | Integration | Sau gọi API/script: session không còn PII theo field đã định nghĩa |
| Full | `pytest tests/ -q` | 0 fail |
| Smoke staging | Manual checklist | Runbook § verify |

### N3.8 Done criteria Nhịp 3

- Có **deploy path** Render (file + hướng dẫn env) và **runbook** đủ cho redeploy/rollback/webhook verify.  
- `/health` và `/readiness` dùng được cho probe; có cách biết **phiên bản deploy** (env metadata).  
- Log webhook/OpenAI không lộ secret/PII thô theo checklist redact.  
- Job hoặc procedure **cleanup** `webhook_dedupe` có tài liệu và đã chạy thử trên staging.  
- Có **luồng** xóa/ẩn danh baseline + test; guardrail tối thiểu documented.  
- Pytest xanh + **artifact** smoke đính kèm báo cáo Builder → Engineering.

### N3.9 Risk / blocker

| Risk | Mitigation |
|------|------------|
| Render free tier / cold start | Ghi rõ trong runbook; readiness timeout probe |
| Cleanup dedupe khóa bảng | Batch + chạy giờ thấp tải; EXPLAIN trước |
| GDPR-style delete scope | Chỉ baseline đã mô tả; escalation nếu Product yêu cầu mở rộng |
| Thiếu `messenger.py` trong workspace clone | Đồng bộ tree đầy đủ trước khi sửa |

**Escalation:** blocker làm không đóng lane trong 8–10 ngày → báo **Engineering** ngay (không tự báo COO theo brief).

### N3.10 Timebox Builder (Nhịp 3)

| Giai đoạn | Ngày (ước lượng) | Việc chính |
|-----------|------------------|------------|
| 1 | 2 | `render.yaml`, staging deploy, runbook khung |
| 2 | 2 | Health metadata, exception surface, redact + tests |
| 3 | 2 | Dedupe cleanup + doc query observability |
| 4 | 2 | Anonymize baseline + admin/script + tests |
| 5 | 1–2 | Full regression, smoke checklist, artifact |

Tổng **8–10 ngày** lane thực tế (khớp khung đã khóa).

### N3.11 Artifact / evidence nộp để Engineering làm LANE COMPLETION REPORT

1. Link/commit SHA deploy staging/production.  
2. File `render.yaml` + danh sách env keys (tên biến, không giá trị secret).  
3. Runbook (PDF/md) — mục rollback + webhook verify đã tick.  
4. Output `pytest tests/ -q` (timestamp).  
5. Smoke checklist đã ký tên (Builder) + 1–2 screenshot log/metric nếu có.  
6. Ghi chú N (retention dedupe) và SQL/job đã áp dụng.

---

**Phần dưới** giữ nguyên **plan Nhịp 2** làm tài liệu tham chiếu scope (đã khớp với thi công); không còn blocker “chờ duyệt plan” cho nhánh backend Nhịp 2.

---

## 1. Mục tiêu Nhịp 2

| # | Mục tiêu | Căn cứ |
|---|----------|--------|
| A | **Admin baseline dùng được:** đăng nhập (cookie/session), RBAC tối thiểu, audit, Jinja2 views + API nội bộ cho config / campaigns / dashboard / leads / transcript / export | Scope COO Nhịp 2 |
| B | **conversation_bridge lát 3:** luồng **KB-2 confirmation** (chốt birth trước chart), wording lấy từ config **CP3 confirmation pack** | Engineering task + CP3 §3 |
| C | **conversation_bridge lát 4:** **multi-profile awareness** mức tối thiểu — nhận biết “đang hỏi cho người khác” có điều kiện, **không** biến multi-profile thành trụ UX chính | Engineering task + CP3 §3.3 |
| D | **CP3 integration surfaces:** trust bridge final, CTA/footer/payment/premium intent/campaign labels; **social proof** chỉ draft/preview/policy cho đến khi có asset Product | CP3 §4–§7, ràng buộc Engineering |

**Baseline Release 1** (3 source, 6 flow, free result trọn vẹn, paid manual, v.v.) **không đổi** — chỉ hoàn thiện lớp admin + lát 3–4 + khóa wording/policy CP3 trên DB/runtime.

---

## 2. Breakdown task theo cụm

### Cụm A — Admin: auth, RBAC, audit, API, Jinja2

- **A1 — Auth service + session/cookie:** form login (hoặc baseline đã khóa), session server-side hoặc signed cookie, logout, middleware bảo vệ prefix `/admin`.
- **A2 — RBAC:** role tối thiểu (vd. `admin`, `viewer` hoặc matrix đã khóa); decorator/dependency FastAPI; từ chối thao tác ghi nếu không đủ quyền.
- **A3 — Audit:** mọi thao tác nhạy cảm (đăng nhập thất bại/thành công, publish config, export) ghi `admin_audit_log` (đã có migration nền) với actor, action, target, metadata.
- **A4 — Admin API (JSON):** CRUD/read cho `app_config` (draft vs published nếu có), `campaigns`, list readings/leads theo sender/time, transcript/conversation_history query, export CSV/JSON có giới hạn.
- **A5 — Admin HTML (Jinja2):** dashboard tóm tắt; trang config (key-value / nhóm block); campaigns; leads; transcript viewer; export trigger — UI đơn giản, không cần SPA.

### Cụm B — Config service & runtime đọc DB

- **B1 — Publish model:** mỗi key `app_config` có trạng thái `draft` | `published` (cột mới **additive** hoặc bảng phụ `app_config_published` — chọn một, ghi rõ trong impl); runtime Messenger **chỉ** đọc bản published (hoặc fallback an toàn).
- **B2 — `app_config_store` mở rộng:** `get_config_text_published(key)`, cache ngắn theo request/process tùy chọn; không đọc draft trong webhook path.
- **B3 — Admin không preview “dynamic free result”:** preview chỉ static block / placeholder; **không** chạy pipeline sinh lá số trong admin theo ràng buộc Engineering.

### Cụm C — conversation_bridge **lát 3** (KB-2)

- **C1 — Tách trạng thái:** khi `birth` đủ field (trước `_mode_generate`), không generate ngay; chuyển sang sub-state **KB2_PENDING_CONFIRM** trong `routing` (hoặc enum tương đương).
- **C2 — Tóm tắt + CTA:** một bước gửi `confirmation_birthdata_summary` (substitute `[tóm tắt dữ liệu]` từ birth đã chuẩn hóa); map payload/quick_reply `confirmation_birthdata_yes` / `confirmation_birthdata_edit` (có thể tái dùng `TV_CONFIRM_*` sau khi đồng bộ tên với CP3).
- **C3 — Nhánh calendar/gender nếu thiếu hoặc ambiguous:** dùng `confirmation_calendar_*`, `confirmation_gender_*`, `confirmation_birthhour_prompt` theo CP3; không kéo dài tư vấn.
- **C4 — Chốt an toàn:** sau “Đúng rồi”, gửi `confirmation_pre_chart_safe_close` rồi mới gọi generate (hiện tại `_mode_generate`).
- **C5 — Missing-field rescue (trong KB-2 / gần generate):** `confirmation_missing_field_resume` / `confirmation_missing_field_retry` khi phát hiện thiếu sót sau bước chốt — chỉ khi có tín hiệu phù hợp, không lạm dụng.

**Không gộp** logic KB-2 vào lát 1–2: lát 1–2 giữ routing/payload/disclaimer; lát 3 là lớp **confirm trước chart** rõ ràng.

### Cụm D — conversation_bridge **lát 4** (multi-profile awareness)

- **D1 — Tín hiệu “người khác”:** heuristic tối thiểu (keyword / intent nhẹ, hoặc quick_reply) — không cần NLU nặng; chỉ kích hoạt khi `active_flow` thuộc **returning** / resume có ngữ cảnh (theo CP3 §3.3).
- **D2 — Một lần clarification:** gửi `confirmation_profile_switch_check`; ghi `routing` / funnel event để không lặp vòng trong cùng session.
- **D3 — Không làm trụ UX:** không bắt user chọn profile DB đầy đủ; có thể chỉ “tiếp tục hồ sơ hiện tại” vs “đang hỏi giúp người khác → reset/snapshot” tùy thiết kế tối thiểu đã khóa với Engineering.
- **D4 — Schema:** tận dụng `profile_entities` / `user_profiles` nếu đã có; migration **additive** nếu cần cột `active_profile_id` hoặc tương đương — **không** phá dữ liệu Nhịp 1.

### Cụm E — CP3 trên runtime (Messenger)

- **E1 — Thay/thêm key:** trust bridge final (theo flow), CTA final (primary/secondary), `footer_final_common`, `payment_pre_cta_final`, `payment_link_label_final` — có thể migration `013_app_config_cp3_seed.sql` + **deprecate** dần key CP2 trùng nghĩa (runtime ưu tiên CP3 key nếu published).
- **E2 — Premium intent:** ladder giữ nguyên; surface `premium_trigger_final`, `premium_handoff_prompt_final`, `premium_expectation_setting_final`, `premium_secondary_cta_final` sau các bước đã khóa; **không** hứa SLA/owner trong text (đúng CP3 §5.3).
- **E3 — Campaign labels:** `campaign_label_*` cập nhật theo CP3 §7 (Tình duyên / Công việc / Tổng quan) + default_flow mapping trong admin/campaigns.

### Cụm F — Social proof (policy + admin only baseline)

- **F1 — Seed keys:** `social_proof_placeholder_policy_final`, `social_proof_preview_label_final` (+ tag `NEED_PRODUCT_FINAL` nếu cần), rule keys placement/blocking **chỉ** lưu config để admin hiển thị và runtime đọc **boolean publish**.
- **F2 — Runtime:** nếu không có asset Product duyệt → **không** gửi snippet user-facing; admin vẫn xem preview/policy.
- **F3 — Khi có asset sau này:** dùng `social_proof_publish_snippet_template` — **ngoài scope bắt buộc Nhịp 2** nếu chưa có asset.

---

## 3. File / module dự kiến sửa hoặc thêm

**Căn cứ cây chuẩn** `QUAN LY TU VI/TAI_LIEU_DU_AN/backend/` (sau Nhịp 1).

| Khu vực | File / module (dự kiến) |
|---------|-------------------------|
| Entry | `app/main.py` — mount admin router, templates, optional static |
| Admin API | `app/api/admin_*.py` hoặc `app/api/admin/` (config, campaigns, dashboard, leads, export) |
| Admin UI | `app/templates/admin/**/*.html`, `app/static/admin/*` |
| Auth | `app/services/admin_auth.py`, `app/middleware/admin_session.py` (hoặc tương đương) |
| Config | `app/services/app_config_store.py`, có thể `app/services/config_publish.py` |
| DB | `sql/migrations/013_*.sql` … (additive); seed CP3 |
| Lát 3 | `app/services/conversation_bridge.py`, có thể tách `app/services/kb2_confirmation.py` để tránh phình orchestrator |
| Lát 4 | `app/services/conversation_bridge.py` hoặc `app/services/profile_awareness.py`; `messenger_state.py` / `routing` |
| Payload | `payload_specs.py`, `payload_handler.py` — đồng bộ payload confirm với CP3 |
| Funnel | `messenger_funnel_bridge.py` — event cho KB2 confirm / profile check (nếu cần) |
| Tests | `tests/test_kb2_confirmation.py`, `tests/test_admin_auth.py`, `tests/test_config_publish.py`, mở rộng `test_conversational_bridge.py` |

---

## 4. File / module không nên đụng (hoặc chỉ hook tối thiểu)

- **`app/api/messenger.py` — signature webhook, dedupe:** giữ ổn định; chỉ nhận thêm dependency nếu bắt buộc.
- **`event_dedupe_db.py`, `webhook_signature.py`:** không đổi hành vi Nhịp 1.
- **Lát 1–2 đã khóa:** không gộp `flow_routing` / `payload_handler` opening vào KB-2; chỉ gọi tuần tự sau khi confirm xong.
- **Orchestrator:** không nhân đôi `process_generate_reading` / chart builder; KB-2 chỉ **cổng** trước generate.
- **Không** thêm preview runtime sinh free result trong admin.

---

## 5. Critical path (gợi ý thứ tự)

1. **Migration + model publish** `app_config` (additive).  
2. **Admin auth + session + RBAC + audit** (có route bảo vệ).  
3. **`app_config_store` published-only** + admin API publish/draft.  
4. **Seed / import CP3 keys** + admin form sửa block.  
5. **Lát 3 KB-2** trong `conversation_bridge` (+ module phụ).  
6. **Runtime CP3 trust/CTA/footer/premium** (đọc key mới).  
7. **Lát 4 profile awareness** (sau KB-2 ổn định).  
8. **Dashboard / transcript / export** (có thể song song sớm sau Bước 2–3).  

---

## 6. Phần có thể chạy song song

- **Admin Jinja2 pages** (UI) song song với **API JSON** sau khi auth xong.  
- **Seed CP3** + **admin config UI** song song với **thiết kế KB-2 state machine** (hợp đồng `routing` phải thống nhất sớm).  
- **Transcript viewer + export** song song với **lát 4** nếu không phụ thuộc routing.  
- **Tests contract** (payload + flow) song song với impl.

---

## 7. Test plan cụ thể

| Hạng mục | Kiểu test | Nội dung |
|----------|-----------|----------|
| Admin auth | Unit + integration | Login/logout, cookie/session, route 403 khi chưa auth |
| RBAC | Unit | Viewer không POST publish |
| Audit | Integration | Ghi log khi publish config / export |
| Config publish | Unit | Runtime đọc đúng bản published; draft không lộ ra webhook handler |
| KB-2 | Unit (mock OpenAI/DB) | Đủ birth → summary → yes → safe close → generate được gọi 1 lần; edit → quay về intake |
| KB-2 + payload | Unit | Postback/quick_reply map đúng CP3 keys |
| Multi-profile | Unit | Chỉ bắn `confirmation_profile_switch_check` khi flow + tín hiệu thỏa điều kiện |
| CP3 surfaces | Unit/snapshot | Trust/CTA/footer/premium text lấy từ store; social proof không render user khi `asset_approved=false` |
| Regression | Full pytest | Toàn bộ `tests/` Nhịp 1 không vỡ; thêm case mới |
| Smoke (manual) | Checklist | Đăng nhập admin, sửa 1 key published, gửi Messenger test: thấy wording mới |

---

## 8. Done criteria Nhịp 2

- Admin: **đăng nhập được**, **RBAC + audit** hoạt động; **config/campaign** chỉnh được; **transcript/export** tối thiểu dùng được.  
- Runtime: **KB-2** bắt buộc trước generate; wording **CP3 confirmation** từ DB (published).  
- **Multi-profile awareness:** có ít nhất một đường hành vi đã định nghĩa + test; không chiếm UX chính.  
- **CP3 trust/CTA/footer/payment/premium/campaign** đã cắm; **social proof** đúng policy (không publish giả).  
- **Migration chỉ additive**; pytest xanh; không vi phạm ràng buộc COO/Engineering (không gộp/nhảy lát).  

---

## 9. Risk / blocker

| Risk | Mitigation |
|------|------------|
| Chưa khóa chi tiết “baseline auth” (OAuth vs form, secret rotation) | Engineering chốt 1 trang spec auth trong 1 vòng duyệt plan |
| Trùng key CP2 vs CP3 | Bảng mapping migration + runtime precedence; có thể yêu cầu Product bảng business→technical (CP3 đã gợi ý) |
| KB-2 làm tăng latency perceived | Copy ngắn; một vòng confirm; test UX |
| Multi-profile phình scope | Giữ heuristic + một câu clarification; không bảng chọn profile phức tạp |
| Asset social proof chưa có | Chỉ draft/preview — đã align CP3 |

**Escalation COO:** nếu CP3 thiếu key / mâu thuẫn wording làm lệch nhịp — báo theo `COO_gửi_Engineering.md` §4.

---

## 10. Timebox Builder (ước lượng trong khung 10–12 ngày lane)

| Giai đoạn | Ngày (ước lượng) | Việc chính |
|-----------|------------------|------------|
| 1 | 2 | Auth + RBAC + audit + skeleton admin routes |
| 2 | 2 | Publish model + app_config_store + seed CP3 + admin config UI |
| 3 | 3 | KB-2 lát 3 + tests |
| 4 | 2 | CP3 runtime surfaces (trust/CTA/footer/premium) + campaign labels |
| 5 | 2 | Lát 4 multi-profile + tests + transcript/export hoàn thiện |
| 6 | 1 | Hardening, pytest full, checklist smoke |

Tổng **~12 ngày** tối đa; có thể rút nếu song song mạnh và auth baseline đã có sẵn từ trước.

---

## 11. CP3: dùng ngay vs placeholder / draft (policy)

| Nhóm | Dùng ngay trên runtime (published) | Chỉ draft / preview / tag NEED_PRODUCT_FINAL |
|------|-----------------------------------|-----------------------------------------------|
| Confirmation §3 | Toàn bộ key `confirmation_*` sau khi seed | — |
| Trust + CTA + footer §4 | `trust_bridge_*` final, CTA final, `footer_final_common`, `payment_pre_cta_final` | `payment_link_label_final` nếu link thật chưa có |
| Premium §5 | `premium_*` đầy đủ; luôn gắn `premium_expectation_setting_final` khi handoff | — (không SLA/owner) |
| Campaign §7 | Labels + default_flow trong admin | — |
| Social proof §6 | **Không** publish snippet user nếu chưa asset | `social_proof_preview_label_final`, policy keys; `social_proof_publish_snippet_template` chỉ khi Product xác nhận asset |

---

## 12. Phụ lục — Nhịp 1 (đã giao, tham chiếu)

Nhịp 1 đã có trên `QUAN LY TU VI/TAI_LIEU_DU_AN/backend/`: webhook hardening, funnel, `conversation_bridge` lát 1–2, CP1+CP2 (`012`, `payload_specs`, `flow_routing`, `payload_handler`, …). **pytest 50 passed** (báo cáo trước 2026-04-10). Chi tiết file list xem lịch sử commit / báo cáo Nhịp 1 trong cùng thư mục draft nếu cần.

---

**Kết luận:** Đây là **plan Nhịp 2** đủ để thi công mà không tự mở scope; **chờ Engineering duyệt** trước khi Builder bắt tay code. Sau duyệt, Builder cập nhật bản này thành báo cáo thi công + số liệu pytest/smoke thực tế.
