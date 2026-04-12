## BUILDER REPORT
Từ: Builder
Gửi: Engineering
Ngày: 2026-04-09
Phase: Phase 1 sub-plan
---
Việc đã làm: Rà soát toàn bộ codebase backend hiện tại (37 source files, 2 SQL schemas, 8 prompts, 6 test files, Streamlit admin); đọc CEO brief, brief khách hàng 22 mục, COO_gửi_Engineering, Engineering_gửi_Builder; lập implementation sub-plan chi tiết cho lane kỹ thuật release đầu KB-1.

File đã sửa: không có (chỉ lập sub-plan)

Build/test đã chạy: không có (rà soát source-level, không chạy lệnh — codebase nằm trong thư mục tài liệu, không phải working project)

Kết quả: PASS — sub-plan đủ chi tiết để Engineering tổng hợp thành lane plan kỹ thuật

Lỗi còn lại: xem mục I (open questions cần Product làm rõ — đã giảm từ 7 xuống 4 sau khi khóa admin frontend và timebox)

Vượt scope: không

Bằng chứng: đường dẫn file/module trích dẫn cụ thể trong từng mục bên dưới; kết luận rút từ đọc source code thực tế, không suy diễn

---

# IMPLEMENTATION SUB-PLAN — LANE KỸ THUẬT RELEASE ĐẦU (KB-1)

---

## A. CÁCH TIẾP CẬN KỸ THUẬT TỔNG THỂ

### Nguyên tắc

1. **Giữ nguyên stack**: FastAPI + PostgreSQL + OpenAI — không đổi framework, không thêm ORM nặng ở release đầu
2. **Refactor incremental**: không rewrite toàn bộ — giữ nguyên tuvi engine deterministic (`tuvi_core_engine.py`, `tuvi_can_chi_engine.py`, `tuvi_calendar_engine.py`, `tuvi_constants.py`) vì đã pass test và là nguồn sự thật
3. **Database-first**: mở rộng schema trước, viết migration script idempotent, service layer chỉ viết sau khi schema khóa
4. **Shared-store dedupe**: thay in-memory `event_deduplicator.py` bằng PostgreSQL-based dedupe — giải quyết blocker multi-worker
5. **Online-first**: mọi quyết định kiến trúc phải chạy được trên cloud platform (Railway / Render) không cần ngrok
6. **Không đụng scope Product**: Builder không tự chốt flow Messenger mới, CTA copy, tone giọng — chỉ đề xuất surface kỹ thuật, ghi rõ dependency cần Product

### Phân loại tổng thể

| Loại | Modules/Files |
|---|---|
| **TÁI SỬ DỤNG nguyên trạng** | `tuvi_core_engine.py`, `tuvi_can_chi_engine.py`, `tuvi_calendar_engine.py`, `tuvi_constants.py`, `normalizer.py`, `reading_service.py`, `schemas/reading.py`, prompts engine-level (`system_extraction.txt`) |
| **REFACTOR** | `event_deduplicator.py` (→ shared-store), `db.py` (→ connection pool), `messenger_handler.py` (→ hỗ trợ postback/quick_reply + campaign ref), `messenger_state.py` + `messenger_state_db.py` (→ tách user profile ra bảng riêng), `conversation_bridge.py` (→ inject campaign context, multi-profile awareness, xác nhận trước generate), `openai_teaser.py` + `openai_paid.py` (→ token logging), `reading_postcheck.py` (→ thêm guardrail trust/safety), `final_message_builder.py` (→ đọc config từ DB thay env), `admin.py` (→ chuyển sang FastAPI web admin) |
| **XÂY MỚI** | Migration runner, schema tables mới (user_profiles, profile_entities, conversation_history, funnel_events, campaigns, orders, admin_users, admin_audit_log, app_config), auth middleware (JWT hoặc session), RBAC service, admin API routes, health/readiness probe nâng cao, Dockerfile + deploy config, backup script |

---

## B. KIẾN TRÚC TARGET RELEASE ĐẦU

### Tổng quan kiến trúc

```
┌──────────────────────────────────────────────────────────┐
│                     CLOUD PLATFORM                        │
│  (Railway / Render — 1 service + managed PostgreSQL)     │
│                                                           │
│  ┌─────────────────────────────────────────────────────┐  │
│  │                  FastAPI App                         │  │
│  │                                                     │  │
│  │  /webhook (GET verify + POST receive)               │  │
│  │  /health + /readiness                               │  │
│  │  /api/v1/reading/*                                  │  │
│  │  /api/v1/admin/*  (auth + RBAC)                     │  │
│  │                                                     │  │
│  │  ┌───────────┐  ┌────────────┐  ┌───────────────┐  │  │
│  │  │ Messenger │  │ TuVi Engine│  │ OpenAI Service│  │  │
│  │  │ Handler   │→ │(determin.) │→ │ (teaser/full/ │  │  │
│  │  │           │  │            │  │  conversation)│  │  │
│  │  └───────────┘  └────────────┘  └───────────────┘  │  │
│  │                                                     │  │
│  │  ┌──────────────────────────────────────────────┐   │  │
│  │  │ DB Layer (psycopg pool, sync)                │   │  │
│  │  │  messenger_sessions | readings               │   │  │
│  │  │  user_profiles | profile_entities            │   │  │
│  │  │  conversation_history | funnel_events        │   │  │
│  │  │  campaigns | orders | app_config             │   │  │
│  │  │  admin_users | admin_audit_log               │   │  │
│  │  │  webhook_dedupe                              │   │  │
│  │  └──────────────────────────────────────────────┘   │  │
│  └─────────────────────────────────────────────────────┘  │
│                                                           │
│  ┌──────────────┐                                         │
│  │ PostgreSQL   │ (managed — Railway / Render built-in)   │
│  │ (single DB)  │                                         │
│  └──────────────┘                                         │
└──────────────────────────────────────────────────────────┘
```

### Thay đổi so với hiện tại

| Thành phần | Hiện tại | Target |
|---|---|---|
| Dedupe | In-memory `_BoundedSet` | Bảng `webhook_dedupe` (PostgreSQL) — TTL-based cleanup |
| DB connection | `psycopg.connect()` mỗi request | `psycopg_pool.ConnectionPool` — tạo 1 lần lúc startup |
| User identity | Chỉ `sender_id` trong `messenger_sessions` | Bảng `user_profiles` riêng (1 sender → 1 profile), `profile_entities` cho multi-profile |
| Session data | JSON blob lớn (`birth + history + chart + reading_id`) | Tách: session giữ state + active_profile_id; birth/chart → profile_entities; history → conversation_history |
| Funnel tracking | Không có | Bảng `funnel_events` — ghi 8 event cốt lõi (brief khách §9.4) |
| Campaign/Attribution | Không có | Bảng `campaigns` + `ref` param trên webhook entry + `attribution_ref` trên user_profiles |
| Orders/Payment | Không có | Bảng `orders` (readiness — chưa tích hợp payment gateway) |
| Admin | Streamlit local (`admin.py`) | FastAPI routes `/api/v1/admin/*` + Jinja2 server-rendered templates (KHÓA — không SPA, không low-code ở release đầu) |
| Auth | Không có | JWT-based admin auth + RBAC (xem/sửa/vận hành/xem lead) |
| Config storage | `.env` file | Bảng `app_config` — admin sửa greeting/CTA/offer/disclaimer/footer/bank block qua API |
| Health | `/health` trả `{"status":"ok"}` | `/health` (liveness) + `/readiness` (DB ping + OpenAI key check) |
| Deploy | Local `uvicorn` + ngrok | Dockerfile → Railway/Render auto-deploy từ git push |
| Logging | `logging.basicConfig` | Structured JSON logging + token usage tracking |

---

## C. KẾ HOẠCH MIGRATION DỮ LIỆU

### Nguyên tắc migration

- **Không phá dữ liệu cũ**: tất cả migration dùng `CREATE TABLE IF NOT EXISTS`, `ALTER TABLE ... ADD COLUMN IF NOT EXISTS`
- **Idempotent**: chạy lại bao nhiêu lần cũng an toàn
- **Có rollback script đi kèm**: mỗi migration lên có migration xuống
- **Thứ tự chạy**: đánh số tuần tự `001_`, `002_`, ...

### Migration runner

Thay `db_init.py` (hiện chỉ chạy 2 file SQL cứng) bằng migration runner đơn giản:
- Bảng `schema_migrations(version TEXT PRIMARY KEY, applied_at TIMESTAMPTZ)`
- Startup: đọc thư mục `sql/migrations/`, chạy các file chưa có trong `schema_migrations`
- Không cần Alembic ở release đầu — quá nặng cho scope này

### Danh sách migration files

```
sql/migrations/
  001_baseline_sessions_readings.sql       -- giữ nguyên 2 bảng cũ, thêm bảng schema_migrations
  002_webhook_dedupe.sql                   -- CREATE TABLE webhook_dedupe
  003_user_profiles.sql                    -- CREATE TABLE user_profiles; backfill từ messenger_sessions
  004_profile_entities.sql                 -- CREATE TABLE profile_entities
  005_conversation_history.sql             -- CREATE TABLE conversation_history
  006_funnel_events.sql                    -- CREATE TABLE funnel_events
  007_campaigns.sql                        -- CREATE TABLE campaigns
  008_orders.sql                           -- CREATE TABLE orders
  009_app_config.sql                       -- CREATE TABLE app_config; seed defaults
  010_admin_users_and_audit.sql            -- CREATE TABLE admin_users, admin_audit_log
  011_sessions_add_profile_fk.sql          -- ALTER messenger_sessions ADD active_profile_id
```

### Schema chi tiết

#### `webhook_dedupe` (thay in-memory deduplicator)
```sql
CREATE TABLE IF NOT EXISTS webhook_dedupe (
    event_id TEXT PRIMARY KEY,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_webhook_dedupe_created ON webhook_dedupe(created_at);
-- Cleanup job: DELETE FROM webhook_dedupe WHERE created_at < NOW() - INTERVAL '24 hours'
```

#### `user_profiles`
```sql
CREATE TABLE IF NOT EXISTS user_profiles (
    id BIGSERIAL PRIMARY KEY,
    sender_id TEXT UNIQUE NOT NULL,          -- Messenger PSID
    display_name TEXT,
    first_seen_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    last_active_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    attribution_ref TEXT,                     -- campaign ref khi vào lần đầu
    lead_stage TEXT NOT NULL DEFAULT 'new',   -- new / intake / free_seen / upsell_clicked / paid / returning
    total_readings INT NOT NULL DEFAULT 0,
    total_paid INT NOT NULL DEFAULT 0,
    metadata_json JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_user_profiles_lead ON user_profiles(lead_stage);
CREATE INDEX IF NOT EXISTS idx_user_profiles_attr ON user_profiles(attribution_ref);
```

#### `profile_entities` (multi-profile: xem cho mình + người thân)
```sql
CREATE TABLE IF NOT EXISTS profile_entities (
    id BIGSERIAL PRIMARY KEY,
    user_profile_id BIGINT NOT NULL REFERENCES user_profiles(id),
    label TEXT NOT NULL DEFAULT 'self',       -- self / partner / child / relative
    full_name TEXT NOT NULL,
    birth_day INT NOT NULL,
    birth_month INT NOT NULL,
    birth_year INT NOT NULL,
    birth_hour INT NOT NULL,
    birth_minute INT NOT NULL,
    gender TEXT NOT NULL,
    calendar_type TEXT NOT NULL,
    is_leap_lunar_month BOOLEAN NOT NULL DEFAULT FALSE,
    chart_json JSONB,                         -- cached chart
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_profile_entities_user ON profile_entities(user_profile_id);
```

#### `conversation_history` (thay history[] trong session JSON)
```sql
CREATE TABLE IF NOT EXISTS conversation_history (
    id BIGSERIAL PRIMARY KEY,
    sender_id TEXT NOT NULL,
    role TEXT NOT NULL,                       -- user / assistant / system
    content TEXT NOT NULL,
    profile_entity_id BIGINT,                -- NULL nếu chưa xác định
    turn_index INT NOT NULL DEFAULT 0,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_convo_sender ON conversation_history(sender_id, created_at DESC);
```

#### `funnel_events` (8 nhóm event kinh doanh brief khách §9.4, triển khai thành 11 event types kỹ thuật)
```sql
CREATE TABLE IF NOT EXISTS funnel_events (
    id BIGSERIAL PRIMARY KEY,
    sender_id TEXT NOT NULL,
    event_type TEXT NOT NULL,                 -- conversation_start / intake_complete / free_generated / free_failed / upsell_click / payment_click / purchase_success / purchase_abandoned / return_1d / return_7d / return_30d
    event_data JSONB NOT NULL DEFAULT '{}'::jsonb,
    campaign_ref TEXT,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_funnel_sender ON funnel_events(sender_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_funnel_type ON funnel_events(event_type, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_funnel_campaign ON funnel_events(campaign_ref, event_type);
```

**Cơ chế ghi return events (KHÓA):**

Events `return_1d` / `return_7d` / `return_30d` dùng **real-time detection khi user quay lại**, KHÔNG dùng cron job hay metric derived.

Implementation path:
1. Khi nhận message từ sender_id, load `user_profiles.last_active_at`
2. Tính `gap = NOW() - last_active_at`
3. Ghi **1 event loại lớn nhất**: gap >= 30d → `return_30d`; else >= 7d → `return_7d`; else >= 1d → `return_1d`; else → không ghi return event
4. Cập nhật `user_profiles.last_active_at = NOW()`
5. Logic nằm trong `app/services/funnel_logger.py`, gọi từ `messenger_handler.py` ngay đầu pipeline (trước conversation_bridge)

Lý do chọn real-time thay vì cron:
- Cron phải scan toàn bộ user_profiles hàng ngày → nặng khi scale, phức tạp
- Metric derived (query theo last_active_at) không ghi vào funnel_events → admin không xem được trong dashboard cùng pipeline
- Real-time detection: đơn giản, chính xác, chỉ ghi khi user thực sự quay lại, không đếm trùng (ghi 1 event per visit sau gap)

#### `campaigns`
```sql
CREATE TABLE IF NOT EXISTS campaigns (
    id BIGSERIAL PRIMARY KEY,
    ref_code TEXT UNIQUE NOT NULL,            -- URL param ?ref=xxx
    name TEXT NOT NULL,
    greeting_override TEXT,                   -- lời chào riêng cho campaign
    default_topic TEXT,                       -- tình duyên / công việc / tổng quan...
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

#### `orders` (payment readiness — chưa tích hợp gateway)
```sql
CREATE TABLE IF NOT EXISTS orders (
    id BIGSERIAL PRIMARY KEY,
    sender_id TEXT NOT NULL,
    user_profile_id BIGINT REFERENCES user_profiles(id),
    product_type TEXT NOT NULL,               -- topic_deep / forecast_30d / forecast_90d / compatibility / consult_human
    amount_vnd INT,
    currency TEXT NOT NULL DEFAULT 'VND',
    status TEXT NOT NULL DEFAULT 'pending',   -- pending / paid / failed / refunded
    promo_code TEXT,
    payment_ref TEXT,
    reading_id BIGINT REFERENCES readings(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_orders_sender ON orders(sender_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_orders_status ON orders(status);
```

#### `app_config` (thay .env cho nội dung admin sửa)
```sql
CREATE TABLE IF NOT EXISTS app_config (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL,
    updated_by TEXT,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
-- Seed:
-- INSERT INTO app_config VALUES ('greeting_default', '...', 'system', NOW()) ON CONFLICT DO NOTHING;
-- INSERT INTO app_config VALUES ('cta_after_free', '...', 'system', NOW()) ON CONFLICT DO NOTHING;
-- INSERT INTO app_config VALUES ('disclaimer', '...', 'system', NOW()) ON CONFLICT DO NOTHING;
-- INSERT INTO app_config VALUES ('bank_block', '...', 'system', NOW()) ON CONFLICT DO NOTHING;
-- INSERT INTO app_config VALUES ('ceo_note', '...', 'system', NOW()) ON CONFLICT DO NOTHING;
-- INSERT INTO app_config VALUES ('donation_text', '...', 'system', NOW()) ON CONFLICT DO NOTHING;
-- INSERT INTO app_config VALUES ('donation_url', '...', 'system', NOW()) ON CONFLICT DO NOTHING;
```

#### `admin_users` + `admin_audit_log`
```sql
CREATE TABLE IF NOT EXISTS admin_users (
    id BIGSERIAL PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL DEFAULT 'viewer',       -- viewer / editor / operator / admin
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS admin_audit_log (
    id BIGSERIAL PRIMARY KEY,
    admin_user_id BIGINT REFERENCES admin_users(id),
    action TEXT NOT NULL,
    detail JSONB,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

### Backfill strategy cho `user_profiles`

```sql
-- Migration 003 backfill:
INSERT INTO user_profiles (sender_id, first_seen_at, last_active_at, lead_stage)
SELECT DISTINCT
    sender_id,
    MIN(created_at),
    MAX(updated_at),
    CASE
        WHEN EXISTS (SELECT 1 FROM readings r WHERE r.sender_id = ms.sender_id AND r.is_unlocked = TRUE)
            THEN 'free_seen'
        ELSE 'intake'
    END
FROM messenger_sessions ms
WHERE NOT EXISTS (SELECT 1 FROM user_profiles up WHERE up.sender_id = ms.sender_id)
GROUP BY sender_id;
```

---

## D. KẾ HOẠCH WEBHOOK HARDENING

### Hiện trạng

- **Dedupe**: `event_deduplicator.py` — in-memory `_BoundedSet`, 2000 entries max, mất khi restart, không hoạt động multi-worker
- **Retry**: không có retry khi gửi Messenger (`send_text_message` dùng raw `urllib`, fail = log warning)
- **Concurrency**: FastAPI BackgroundTasks — single-threaded per worker, không queue
- **Logging**: basic Python logging, không structured

### Thay đổi

| # | Hạng mục | Hành động |
|---|---|---|
| D0 | **Webhook signature verification** | Verify `X-Hub-Signature-256` header bằng HMAC-SHA256 với `FB_APP_SECRET`. Middleware chặn request không hợp lệ trước khi vào handler. Cần thêm env var `FB_APP_SECRET`. Đây là security bắt buộc cho production online — không có thì bất kỳ ai biết URL webhook đều gửi được event giả. |
| D1 | Dedupe → shared-store | Thay `event_deduplicator.py` bằng module mới `event_dedupe_db.py`: `INSERT INTO webhook_dedupe ... ON CONFLICT DO NOTHING RETURNING event_id` — nếu RETURNING trống = duplicate. Cleanup cronjob xóa event > 24h. |
| D2 | Retry gửi Messenger | Thay `urllib.request` bằng `httpx` (đã có trong requirements) với retry 2 lần, backoff 1s-3s. Nếu 3 lần fail → log error cụ thể, không retry tiếp. |
| D3 | Typing indicator | Gửi `sender_action: typing_on` trước khi xử lý (API Messenger Send hỗ trợ). Giúp UX — người dùng thấy "đang gõ" thay vì chờ trống. |
| D4 | Postback + Quick Reply | `messenger.py` hiện chỉ xử lý `message.text`. Cần thêm xử lý `message.quick_reply.payload` và `postback.payload` — routing tới handler tương ứng. [Dependency Product: định nghĩa payload format cho quick replies và postbacks] |
| D5 | Campaign ref extraction | Khi nhận webhook, check `referral.ref` field (Meta gửi khi user đến từ click-to-Messenger ad). Lưu vào `user_profiles.attribution_ref` và `funnel_events`. |
| D6 | Structured logging | Đổi `logging.basicConfig` sang JSON structured logging (dùng `python-json-logger` hoặc custom formatter). Mỗi log entry có: `timestamp`, `level`, `event`, `request_id`, `sender_id`, `duration_ms`. |
| D7 | Token usage logging | Sau mỗi OpenAI call, log `completion.usage.prompt_tokens`, `completion_tokens`, `total_tokens`, `model`. Aggregate để admin xem chi phí. |

### Module thay đổi cụ thể

- **Xóa**: `app/services/event_deduplicator.py`
- **Tạo mới**: `app/services/event_dedupe_db.py`
- **Tạo mới**: `app/middleware/webhook_signature.py` (HMAC-SHA256 verification)
- **Sửa**: `app/api/messenger.py` (thêm signature middleware, postback/quick_reply/referral handling, gọi dedupe mới)
- **Sửa**: `app/services/messenger_handler.py` (thêm typing indicator, retry logic, `httpx` thay `urllib`)
- **Sửa**: `app/main.py` (structured logging setup)

---

## E. KẾ HOẠCH ADMIN / AUTH / RBAC / AUDIT / LOG / DASHBOARD DATA SOURCE

### Hiện trạng

- `admin.py` là Streamlit app chạy local, đọc/ghi `.env` file, không có auth
- Không có phân quyền, không có audit log, không có dashboard dữ liệu

### Target

**Admin chuyển sang FastAPI routes** phục vụ qua cùng 1 web service, ở prefix `/api/v1/admin/`. Frontend: **Jinja2 server-rendered templates** serve bởi FastAPI (KHÓA cho release đầu). Lý do: không cần build pipeline, Builder làm luôn, đủ cho admin không kỹ thuật, deploy cùng 1 service. React/SPA và low-code ngoài scope release đầu.

### Auth flow

1. `POST /api/v1/admin/login` → nhận username + password → tạo JWT → set **HttpOnly secure cookie** (exp 24h)
2. Middleware đọc JWT từ cookie trên mọi route `/api/v1/admin/*` — người dùng admin KHÔNG cần tự cầm bearer token
3. Token chứa `user_id`, `role`
4. Thư viện: `PyJWT` + bcrypt
5. Cookie flags: `HttpOnly`, `SameSite=Lax`, `Secure` (khi production HTTPS)

> **Quyết định Engineering**: với admin Jinja2 server-rendered cho người vận hành không kỹ thuật, auth qua HttpOnly cookie phù hợp hơn bearer token. Brief khách yêu cầu vận hành dễ dùng, ít phụ thuộc thao tác kỹ thuật — người dùng admin chỉ cần đăng nhập trên trình duyệt, không cần biết JWT là gì.

### RBAC tối thiểu (4 roles brief khách §17)

| Role | Xem số liệu | Sửa nội dung | Vận hành/deploy | Xem lead |
|---|---|---|---|---|
| viewer | ✓ | ✗ | ✗ | ✗ |
| editor | ✓ | ✓ | ✗ | ✗ |
| operator | ✓ | ✓ | ✓ | ✗ |
| admin | ✓ | ✓ | ✓ | ✓ |

### Admin API routes

```
POST   /api/v1/admin/login
GET    /api/v1/admin/me

# Config management (editor+)
GET    /api/v1/admin/config                    -- lấy tất cả app_config
PUT    /api/v1/admin/config/{key}              -- sửa 1 config (greeting, CTA, disclaimer, bank, footer, offer...)
GET    /api/v1/admin/campaigns                 -- danh sách campaigns
POST   /api/v1/admin/campaigns                 -- tạo campaign
PUT    /api/v1/admin/campaigns/{id}            -- sửa campaign

# Dashboard data (viewer+)
GET    /api/v1/admin/dashboard/funnel          -- funnel metrics (count by event_type, grouped by day/campaign)
GET    /api/v1/admin/dashboard/health          -- bot health: DB ping, webhook status, OpenAI key valid, last error
GET    /api/v1/admin/dashboard/recent-errors   -- last N error log entries
GET    /api/v1/admin/dashboard/token-usage     -- OpenAI token cost aggregate

# Lead management (admin only)
GET    /api/v1/admin/leads                     -- list user_profiles with filters (lead_stage, campaign, date)
GET    /api/v1/admin/leads/{id}                -- detail 1 lead
GET    /api/v1/admin/leads/export              -- CSV export

# Audit (admin only)
GET    /api/v1/admin/audit-log                 -- paginated audit log
```

### Dashboard data source

Funnel dashboard query:

```sql
SELECT
    event_type,
    DATE(created_at) AS day,
    campaign_ref,
    COUNT(*) AS count
FROM funnel_events
WHERE created_at >= NOW() - INTERVAL '30 days'
GROUP BY event_type, day, campaign_ref
ORDER BY day DESC, event_type;
```

Conversion pipeline:
```
conversation_start → intake_complete → free_generated → upsell_click → payment_click → purchase_success
```

Admin nhìn vào dashboard sẽ thấy: số người ở mỗi bước, tỷ lệ drop-off giữa các bước, filter theo campaign — đáp ứng brief khách §10.2 và tiêu chí nghiệm thu §5-6.

### Audit log

Mỗi thao tác sửa config / campaign / lead sẽ ghi:
```python
admin_audit_log(admin_user_id=current_user.id, action="config_update", detail={"key": key, "old": old_val, "new": new_val})
```

### Module thay đổi

- **Xóa (hoặc archive)**: `admin.py` (Streamlit local)
- **Tạo mới**:
  - `app/api/admin.py` — admin API routes
  - `app/services/auth_service.py` — JWT create/verify, password hash (bcrypt)
  - `app/services/admin_service.py` — config CRUD, funnel aggregation queries, lead queries
  - `app/middleware/auth.py` — JWT middleware + RBAC decorator
  - `app/services/audit_service.py` — audit log writer
  - `templates/` — Jinja2 admin templates (login, dashboard, config editor, lead list, campaign manager)

---

## F. KẾ HOẠCH DEPLOY / OPS / BACKUP / ROLLBACK / HEALTH / RESTART

### Khuyến nghị deploy platform

| Platform | Chi phí/tháng (ước) | Độ phức tạp setup | GUI vận hành | PostgreSQL managed | Auto-deploy | Trade-off |
|---|---|---|---|---|---|---|
| **Railway** | $5–20 (hobby) | Thấp | ✓ (dashboard web) | ✓ (add-on) | ✓ (git push) | Dễ nhất cho team không kỹ thuật; giá tăng theo traffic; cold start nhẹ |
| **Render** | $7–25 | Thấp | ✓ (dashboard web) | ✓ (managed) | ✓ (git push) | Tương tự Railway; free tier có cold start 15 phút — cần ít nhất Starter plan |
| **Fly.io** | $5–15 | Trung bình | ✓ (dashboard + CLI) | ✓ (Fly Postgres) | ✓ (flyctl deploy) | Gần VPS hơn, flexible hơn, nhưng setup phức tạp hơn Railway/Render |
| **VPS + Coolify** | $5–10 VPS + Coolify free | Cao (setup lần đầu) | ✓ (Coolify UI) | Tự host | ✓ (Coolify) | Rẻ nhất khi scale; nhưng team kỹ thuật phải setup + maintain hạ tầng |

**KHÓA — Quyết định Engineering**: **Render là phương án số 1**, Railway là fallback gần nhất.

Lý do Render ưu tiên:
- Dashboard rõ ràng, dễ bàn giao vận hành không kỹ thuật
- PostgreSQL managed có backup tự động
- Auto-deploy từ git push
- Không cần SSH hàng ngày
- Health check endpoint cấu hình từ dashboard
- Giá Starter plan (~$7/tháng) hợp lý cho traffic ban đầu

Railway là fallback nếu: team muốn tốc độ setup nhanh hơn hoặc Render gặp issue cụ thể.

Fly.io và VPS+Coolify ngoài scope release đầu.

### Dockerfile

```dockerfile
FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Lưu ý:
- Không COPY `.env`, `ngrok.exe`, `.venv`, `.pytest_cache` → cần `.dockerignore`
- Healthcheck dùng Python one-liner (không dùng `curl` — `python:3.10-slim` không có `curl` mặc định)
- Railway/Render cũng hỗ trợ platform-level health check gọi `/health` từ ngoài container — nên bật cả hai

### Health + Readiness

Hiện tại `/health` chỉ trả `{"status":"ok"}` — không kiểm tra gì.

Target:
- `/health` (liveness): trả ok nếu process sống — giữ đơn giản
- `/readiness` (readiness probe): kiểm tra:
  1. DB connection pool healthy (thử `SELECT 1`)
  2. OpenAI API key có (không gọi API, chỉ check env)
  3. Trả `{"ready": true/false, "checks": {"db": "ok"/"fail", "openai_key": "present"/"missing"}}`

### Backup

- **Render managed PostgreSQL**: backup tự động hàng ngày (built-in)
- **Bổ sung**: script `pg_dump` chạy cron hàng ngày, upload S3 — nhưng ngoài scope release đầu nếu platform có backup built-in
- **Dữ liệu cũ**: migration idempotent, không DROP table — dữ liệu cũ trong `messenger_sessions` và `readings` được giữ nguyên

### Rollback

- **Code rollback**: Render hỗ trợ rollback deploy về commit trước qua dashboard (1 click)
- **DB rollback**: mỗi migration có reverse script — nhưng release đầu dùng `CREATE IF NOT EXISTS` + `ADD COLUMN IF NOT EXISTS` nên rollback chỉ cần deploy code cũ, bảng mới không gây conflict với code cũ
- **Quy trình**: nếu deploy mới lỗi → admin bấm "Rollback" trên dashboard hosting → service quay về image trước → DB schema vẫn forward-compatible

### Restart flow

- **Dashboard hosting**: nút "Restart" / "Redeploy" có sẵn
- **Admin panel nội bộ**: endpoint `GET /api/v1/admin/dashboard/health` cho biết trạng thái — admin biết khi nào cần restart
- **Tự động**: Render tự restart nếu process crash

### Ops qua admin panel (sau setup ban đầu)

Vận hành thường ngày KHÔNG cần terminal:
1. Sửa greeting/CTA/disclaimer/offer → Admin panel → sửa config → có hiệu lực ngay (đọc từ DB, không cần restart)
2. Xem health → Admin dashboard
3. Xem funnel → Admin dashboard
4. Xem lỗi → Admin dashboard (recent errors)
5. Restart → Dashboard hosting
6. Deploy mới → Git push → auto-deploy
7. Rollback → Dashboard hosting

Setup ban đầu DO team kỹ thuật:
1. Tạo project trên Render (hoặc Railway nếu fallback)
2. Tạo PostgreSQL managed instance
3. Set env vars (OPENAI_API_KEY, FB_PAGE_ACCESS_TOKEN, FB_VERIFY_TOKEN, FB_APP_SECRET, DATABASE_URL, JWT_SECRET)
4. Connect git repo → auto-deploy
5. First deploy + verify health endpoint
6. Verify webhook trên Meta Developer Console (cập nhật webhook URL sang domain Render)
7. Tạo admin user đầu tiên (qua CLI 1 lần duy nhất hoặc migration seed)

---

## G. DANH SÁCH TASK TRIỂN KHAI THEO THỨ TỰ

### Nhóm 1: FOUNDATION (phải xong trước mọi thứ khác)

| # | Task | File/module | Loại | Dependency |
|---|---|---|---|---|
| 1.1 | Connection pool — thay `get_connection()` bằng `psycopg_pool.ConnectionPool` | `app/db.py` | Refactor | — |
| 1.2 | Migration runner | `app/db_init.py` (refactor), `sql/migrations/001_*.sql` | Refactor + Mới | 1.1 |
| 1.3 | Structured logging | `app/main.py`, thêm `app/utils/logging_setup.py` | Refactor + Mới | — |
| 1.4 | Dockerfile + .dockerignore | `Dockerfile`, `.dockerignore` | Mới | — |
| 1.5 | Health + Readiness endpoint | `app/main.py` | Refactor | 1.1 |
| 1.6 | **Webhook signature verification** (X-Hub-Signature-256) | `app/middleware/webhook_signature.py`, `app/api/messenger.py` | Mới + Refactor | — (chỉ cần env `FB_APP_SECRET`) |

### Nhóm 2: DATA (schema mở rộng)

| # | Task | File/module | Loại | Dependency |
|---|---|---|---|---|
| 2.1 | Migration 001 baseline | `sql/migrations/001_baseline.sql` | Mới | 1.2 |
| 2.2 | Migration 002 webhook_dedupe | `sql/migrations/002_webhook_dedupe.sql` | Mới | 2.1 |
| 2.3 | Migration 003-004 user_profiles + profile_entities | `sql/migrations/003_*.sql`, `004_*.sql` | Mới | 2.1 |
| 2.4 | Migration 005 conversation_history | `sql/migrations/005_*.sql` | Mới | 2.3 |
| 2.5 | Migration 006-008 funnel_events + campaigns + orders | `sql/migrations/006-008_*.sql` | Mới | 2.3 |
| 2.6 | Migration 009 app_config | `sql/migrations/009_*.sql` | Mới | 2.1 |
| 2.7 | Migration 010 admin_users + audit | `sql/migrations/010_*.sql` | Mới | 2.1 |
| 2.8 | Migration 011 sessions add profile FK | `sql/migrations/011_*.sql` | Mới | 2.3 |

### Nhóm 3: WEBHOOK HARDENING

| # | Task | File/module | Loại | Dependency |
|---|---|---|---|---|
| 3.1 | Shared-store dedupe | `app/services/event_dedupe_db.py` | Mới (thay `event_deduplicator.py`) | 2.2 |
| 3.2 | Messenger send retry (httpx) | `app/services/messenger_handler.py` | Refactor | — |
| 3.3 | Typing indicator | `app/services/messenger_handler.py` | Refactor | — |
| 3.4 | Postback + quick_reply handling | `app/api/messenger.py`, `app/services/messenger_handler.py` | Refactor | Cần Product: payload spec |
| 3.5 | Campaign ref extraction | `app/api/messenger.py` | Refactor | 2.5 (campaigns table), 2.3 (user_profiles) |
| 3.6 | Token usage logging | `app/services/openai_teaser.py`, `openai_paid.py`, `conversation_bridge.py`, `birth_extractor.py` | Refactor | 1.3 |

### Nhóm 4: ADMIN / AUTH

| # | Task | File/module | Loại | Dependency |
|---|---|---|---|---|
| 4.1 | Auth service (JWT + bcrypt) | `app/services/auth_service.py` | Mới | 2.7 |
| 4.2 | Auth middleware + RBAC | `app/middleware/auth.py` | Mới | 4.1 |
| 4.3 | Admin config CRUD API | `app/api/admin.py` | Mới | 4.2, 2.6 |
| 4.4 | Campaign CRUD API | `app/api/admin.py` | Mới | 4.2, 2.5 |
| 4.5 | Dashboard funnel query API | `app/api/admin.py` | Mới | 4.2, 2.5 |
| 4.6 | Dashboard health + errors API | `app/api/admin.py` | Mới | 4.2, 1.5 |
| 4.7 | Lead list + export API | `app/api/admin.py` | Mới | 4.2, 2.3 |
| 4.8 | Audit log service | `app/services/audit_service.py` | Mới | 4.2, 2.7 |
| 4.9 | Config reader thay env | `app/services/config_service.py` (thay `final_message_builder.py` đọc env) | Mới + Refactor | 2.6 |
| 4.10 | **Jinja2 admin templates** (login, dashboard funnel/health/errors/token, config editor, campaign manager, lead list + export) | `templates/*.html`, `app/api/admin_views.py` (HTML routes) | Mới | 4.3–4.7 (API phải có trước) |

### Nhóm 5: OPS / OBSERVABILITY

| # | Task | File/module | Loại | Dependency |
|---|---|---|---|---|
| 5.1 | Deploy config (Render primary) | `render.yaml` (Blueprint spec) — Railway `railway.toml` chỉ nếu fallback | Mới | 1.4 |
| 5.2 | Webhook dedupe cleanup cron | Có thể dùng `@app.on_event("startup")` background task chạy mỗi 1h | Mới | 3.1 |
| 5.3 | Token cost aggregation table/view | View SQL hoặc logic trong admin_service | Mới | 3.6 |

### Nhóm 6: TRUST / SAFETY (Engineering scope)

| # | Task | File/module | Loại | Dependency |
|---|---|---|---|---|
| 6.1 | Data protection: không lộ log thô | Verify `log_redact.py` đã redact birth data, PII; bổ sung nếu thiếu | Refactor | 1.3 |
| 6.2 | Profile deletion endpoint | `DELETE /api/v1/admin/leads/{id}` — anonymize hoặc xóa | Mới | 4.7 |
| 6.3 | Guardrail nâng cao trong reading_postcheck | Thêm pattern cho tình huống nhạy cảm (tự hại, bệnh nặng) | Refactor | — |

### Nhóm 7: TESTS

| # | Task | File/module | Loại | Dependency |
|---|---|---|---|---|
| 7.1 | Test migration runner | `tests/test_migration.py` | Mới | 1.2 |
| 7.2 | Test dedupe DB | `tests/test_dedupe_db.py` | Mới | 3.1 |
| 7.3 | Test auth + RBAC | `tests/test_auth.py` | Mới | 4.1, 4.2 |
| 7.4 | Test funnel event logging | `tests/test_funnel_events.py` | Mới | 2.5, 3.5 |
| 7.5 | Test admin config CRUD | `tests/test_admin_config.py` | Mới | 4.3 |
| 7.6 | Test webhook signature verification | `tests/test_webhook_signature.py` | Mới | 1.6 |
| 7.7 | Test return event detection | `tests/test_return_events.py` | Mới | bridge lát 2 |
| 7.8 | Giữ tests hiện có pass | Cập nhật conftest nếu cần | Refactor | — |

### Thứ tự thi công đề xuất

```
Foundation (1.1–1.6) → Data (2.1–2.8) → Webhook (3.1–3.6) + bridge lát 1-2 → Admin API (4.1–4.9) → Admin templates (4.10) → bridge lát 3-4 (khi Product spec sẵn) → Ops (5.1–5.3) → Trust (6.1–6.3) → Tests (7.1–7.6)
```

Lưu ý: bridge lát 3-4 phụ thuộc Product spec → nếu chưa có, Builder thi công Admin + Ops + Trust trước, quay lại bridge lát 3-4 sau. Mỗi lát bridge merge riêng, test riêng.

---

## H. FILE/MODULE NÊN SỬA VÀ KHÔNG NÊN ĐỤNG

### NÊN SỬA (release đầu)

| File | Lý do | Rủi ro |
|---|---|---|
| `app/db.py` | Thêm connection pool | Thấp — interface `get_connection()` giữ nguyên signature |
| `app/db_init.py` | Thay bằng migration runner | Thấp — logic mới bao trùm logic cũ |
| `app/main.py` | Structured logging, thêm router admin, readiness endpoint | Thấp |
| `app/api/messenger.py` | Postback/quick_reply/referral, dedupe mới | Trung bình — core webhook path |
| `app/services/messenger_handler.py` | httpx retry, typing indicator | Trung bình |
| `app/services/event_deduplicator.py` | Thay bằng DB-based (xóa file này) | Thấp — logic đơn giản |
| `app/services/messenger_state.py` | Thêm `active_profile_id` vào session | Thấp |
| `app/services/messenger_state_db.py` | Hỗ trợ profile FK, tách history ra bảng riêng | Trung bình |
| `app/services/conversation_bridge.py` | Funnel event logging, campaign context, xác nhận trước generate (KB-2), multi-profile awareness | Cao — module phức tạp nhất |
| `app/services/openai_teaser.py` | Token logging | Thấp |
| `app/services/openai_paid.py` | Token logging | Thấp |
| `app/services/final_message_builder.py` | Đọc config từ DB thay env | Thấp |
| `app/services/reading_postcheck.py` | Thêm guardrail trust/safety | Thấp |
| `app/utils/log_redact.py` | Bổ sung redact PII | Thấp |
| `admin.py` | Archive — chuyển sang FastAPI admin | N/A (file cũ không dùng nữa) |
| `requirements.txt` | Thêm `psycopg_pool`, `PyJWT`, `bcrypt`, `python-json-logger`, `jinja2` | Thấp |

### KHÔNG NÊN ĐỤNG (release đầu)

| File | Lý do |
|---|---|
| `app/services/tuvi_core_engine.py` | Engine deterministic đã pass test — nguồn sự thật, không sửa trừ khi phát hiện bug logic tử vi |
| `app/services/tuvi_can_chi_engine.py` | Như trên |
| `app/services/tuvi_calendar_engine.py` | Như trên |
| `app/services/tuvi_constants.py` | Lookup tables cố định |
| `app/schemas/reading.py` | Schema ổn, backward-compatible; chỉ sửa nếu thêm field mới (ít khả năng release đầu) |
| `app/services/normalizer.py` | Logic normalize đủ tốt |
| `app/services/prompt_adapter.py` | Adapter hoạt động đúng — chỉ sửa nếu Product đổi prompt structure |
| `app/services/birth_extractor.py` | Logic extraction ổn; chỉ sửa nếu Product đổi yêu cầu NLU |
| `prompts/system_extraction.txt` | Prompt extraction hoạt động — scope Product nếu muốn sửa |
| `prompts/system_free_production.txt`, `user_free_production.txt`, `system_full_production.txt`, `user_full_production.txt` | Prompt nội dung — scope Product |
| `tests/test_tuvi_engine.py` | Giữ nguyên test engine |

---

## I. TEST STRATEGY + RỦI RO LỚN NHẤT + DEPENDENCY / OPEN QUESTIONS CHO PRODUCT

### Test strategy tối thiểu

| Nhóm thay đổi | Test approach | Acceptance criteria |
|---|---|---|
| Foundation (DB pool, migration, webhook sig) | Unit test: pool khởi tạo + trả connection; migration runner idempotent 2 lần; webhook signature: request với valid HMAC → pass, invalid → 403 | Pool healthy; migration safe; unsigned requests blocked |
| Webhook hardening (dedupe DB) | Unit test: `is_new_event` trả True lần 1, False lần 2; cleanup xóa entry > 24h | Không duplicate xử lý |
| Messenger send retry | Unit test mock httpx: fail 2 lần + pass lần 3 → gửi OK; fail 3 lần → log error | Retry hoạt động, không retry vô hạn |
| Auth + RBAC | Unit test: login trả JWT hợp lệ; middleware reject token sai; RBAC block viewer truy cập lead | 4 roles hoạt động đúng |
| Admin config CRUD | Integration test: PUT config → GET config → value đúng; audit log ghi | CRUD hoạt động, audit ghi |
| Funnel events | Integration test: gọi log_funnel_event → query funnel dashboard → đúng count | 8 event types ghi đúng |
| Trust/safety | Unit test reading_postcheck: input có pattern nhạy cảm → blocked | Guardrail hoạt động |
| Existing tests | Chạy `pytest` full suite — phải pass không regression | 0 test fail |

### 3 rủi ro lớn nhất

| # | Rủi ro | Mức | Mitigation |
|---|---|---|---|
| R1 | **conversation_bridge.py quá phức tạp để refactor an toàn** — file này là orchestrator chính, sửa nhiều chỗ có thể gây regression flow Messenger | P0 | Tách thành 4 lát thi công cụ thể (xem bảng CONVERSATION_BRIDGE SLICING bên dưới), mỗi lát merge độc lập + có test riêng |
| R2 | **Migration data loss** — nếu ALTER TABLE sai hoặc backfill query có bug, dữ liệu cũ có thể mất | P1 | Mọi migration là additive (chỉ CREATE/ADD, không DROP/RENAME); backup DB trước khi chạy migration; test migration trên DB copy trước |
| R3 | **Admin frontend** — nếu không có frontend thì admin API = useless cho người không kỹ thuật | P1 | KHÓA: Jinja2 server-rendered templates, Builder thi công luôn trong scope. Xem task 4.10 |

### CONVERSATION_BRIDGE SLICING — 4 lát thi công cụ thể

`conversation_bridge.py` là module phức tạp nhất (491 dòng, 4 mode, orchestrator chính). Refactor chia thành 4 lát merge độc lập, thứ tự bắt buộc:

| Lát | Scope | File tạo/sửa | Test đi kèm | Có thể merge khi |
|---|---|---|---|---|
| **Lát 1: Funnel logging + token usage** | Extract `funnel_logger.py` module. Inject `log_funnel_event()` calls tại 6 điểm trong conversation_bridge: conversation_start (**chỉ khi phiên mới thật sự** — rule: user chưa có session hoặc session đã inactive > ngưỡng Engineering định nghĩa trong lane plan; KHÔNG bắn mỗi inbound message), intake_complete (khi `is_birth_complete()` chuyển True), free_generated/free_failed (trong `_mode_generate`), upsell_click (khi xử lý postback payload "upsell"). Thêm token usage logging vào `_call_openai_conversation()`. **Không đổi logic flow** — chỉ thêm side-effect logging. | Tạo: `app/services/funnel_logger.py`. Sửa: `conversation_bridge.py` (thêm import + gọi logger), `openai_teaser.py`, `openai_paid.py`, `birth_extractor.py` (token log) | `tests/test_funnel_logger.py`: gọi log_funnel_event → verify row in DB; integration: user mới → conversation_start ghi 1 lần; user gửi tiếp message → KHÔNG ghi thêm conversation_start | Flow Messenger hiện tại vẫn pass; funnel_events bảng có data; conversation_start không phình |
| **Lát 2: Campaign/ref context** | Thêm `attribution_ref` vào pipeline. Khi messenger_handler nhận message, lookup `user_profiles.attribution_ref`. Nếu user mới + có referral → lưu ref. Truyền campaign context vào conversation_bridge để log kèm `campaign_ref` trong funnel_events. Thêm return event detection (real-time, xem mục C). **Không đổi mode routing** — chỉ thêm context param. | Sửa: `messenger_handler.py` (thêm user profile lookup + ref + return detection), `conversation_bridge.py` (nhận `campaign_ref` param, truyền xuống funnel_logger) | `tests/test_campaign_ref.py`: user mới với ref → attribution_ref lưu; return detection: user quay lại sau 2 ngày → return_1d event ghi | Lát 1 đã merge; campaign ref ghi đúng; return events ghi đúng |
| **Lát 3: KB-2 confirmation flow** | Thêm mode CONFIRM trước GENERATE. Khi `is_birth_complete()` = True nhưng có field đến từ NLU suy đoán (birth_extractor gán confidence flag), bot tóm tắt dữ liệu đã thu + hỏi xác nhận trước khi chạy engine. User trả lời "đúng rồi" → generate; "sửa ..." → quay lại intake field cụ thể. **Đổi mode routing logic** — thêm 1 nhánh giữa INTAKE và GENERATE. | Sửa: `conversation_bridge.py` (thêm `_mode_confirm`), `messenger_state.py` (thêm state `CONFIRMING`), `birth_extractor.py` (thêm `_confidence` metadata). [Dependency Product: câu hỏi xác nhận ra sao — Q4] | `tests/test_confirm_flow.py`: birth complete từ NLU → bot hỏi xác nhận → user confirm → generate; user sửa → quay lại intake | Lát 2 đã merge; flow xác nhận hoạt động; test cũ `test_conversational_bridge.py` vẫn pass |
| **Lát 4: Multi-profile awareness** | Khi user đã có > 1 profile_entity, bot hỏi ngắn "Bạn muốn xem cho ai?" trước khi vào flow. Thêm `active_profile_id` vào session, resolve đúng profile_entity khi vào GENERATE hoặc HAS_CHART. Tách history ra `conversation_history` table (thay JSON blob trong session). | Tạo: `app/services/profile_resolver.py`. Sửa: `conversation_bridge.py` (inject profile resolver ở đầu pipeline), `messenger_state.py` (thêm `active_profile_id`), `messenger_state_db.py` (tách history sang bảng riêng) | `tests/test_multi_profile.py`: user có 2 profile → bot hỏi chọn; user chọn → session set active_profile_id; generate dùng đúng profile entity | Lát 3 đã merge; multi-profile routing đúng; history persist ở bảng riêng |

**Quy tắc merge**: mỗi lát phải pass full `pytest` suite trước khi merge. Nếu 1 lát fail → không merge, không bắt đầu lát tiếp theo. Lát 3 phụ thuộc Product spec (Q4) — nếu Product chưa trả lời, Builder thi công lát 1+2 trước, lát 3 chờ.

### Dependency cần Product làm rõ (Builder không tự chốt)

| # | Câu hỏi | Cần ai trả lời | Ảnh hưởng task | Block lát nào |
|---|---|---|---|---|
| Q1 | **Payload format cho quick replies và postbacks**: Product định nghĩa các nút bấm nào, payload gì (ví dụ `{"action":"view_deep","topic":"tinh_duyen"}`). Builder cần spec để code handler. | Product | Task 3.4 | Không block lát 1-2; block 3.4 |
| Q2 | **Flow Messenger mới cho người quay lại**: khi user đã có profile, bot mở đầu thế nào? Product cần spec. Engineering chỉ code logic routing. | Product | conversation_bridge lát 4 | Block lát 4 |
| Q3 | **Greeting/CTA/offer nội dung cụ thể**: Builder tạo bảng `app_config` và Jinja2 admin UI để admin sửa — nhưng cần Product cung cấp default values cho: greeting, CTA sau free, disclaimer text, offer text. | Product | Task 4.3, 4.9 (seed data) | Không block thi công; block seed data |
| Q4 | **KB-2 xác nhận trước generate — UX cụ thể**: Builder code logic "nếu có field mơ hồ → hỏi xác nhận", nhưng Product cần định nghĩa: ngưỡng mơ hồ là gì, câu hỏi xác nhận ra sao, UX nút bấm hay text. | Product | conversation_bridge lát 3 | Block lát 3 |

Các câu hỏi đã KHÓA (không còn mở):
- ~~Q5 Admin frontend~~: **KHÓA = Jinja2 server-rendered templates** (Engineering feedback, Builder đồng ý)
- ~~Q6 Deploy platform~~: **KHÓA = Render ưu tiên, Railway fallback** (quyết định Engineering)
- ~~Q7 Timebox~~: **KHÓA = xem bảng TIMEBOX 2 LỚP bên dưới**

### TIMEBOX 2 LỚP (1 Builder)

| Lớp | Phạm vi | Ước lượng | Ghi chú |
|---|---|---|---|
| **Lớp 1 — Code-only** | Thi công kỹ thuật thuần: Foundation + Data + Webhook + Admin (API + Jinja2 templates) + Ops + Trust + Tests. Không tính chờ Product, không tính loop chỉnh. | **20–24 ngày** | Giả định: 1 builder full-time; codebase đã quen; không gặp blocker kỹ thuật lớn bất ngờ |
| **Lớp 2 — Lane thực tế** | Lớp 1 + buffer cho: chờ Product spec (Q1-Q4, ước 3-5 ngày chờ rải rác nếu Product song song), loop chỉnh sau review (2-3 ngày), deploy lên platform + smoke test + fix phát sinh production (3-4 ngày), test hồi quy cuối (1-2 ngày) | **28–35 ngày** | Nếu Product trả spec chậm hoặc nối tiếp → cộng thêm 5-7 ngày (tổng lên 35-42 ngày) |

Phân bổ code-only (Lớp 1) theo nhóm:

| Nhóm | Ngày ước | Chi tiết |
|---|---|---|
| Foundation (1.1–1.6) | 3–4 | Pool + migration runner + logging + Dockerfile + health + webhook signature |
| Data (2.1–2.8) | 2–3 | 11 migration files, phần lớn là SQL |
| Webhook hardening (3.1–3.6) | 3–4 | Dedupe DB + httpx retry + typing + postback + campaign ref + token log |
| conversation_bridge lát 1–2 | 3–4 | Funnel logging + campaign context + return detection |
| conversation_bridge lát 3–4 | 3–4 | KB-2 confirm + multi-profile (phụ thuộc Product spec) |
| Admin API + Jinja2 templates (4.1–4.10) | 4–5 | Auth + RBAC + 12 endpoints + 5-6 template pages |
| Ops + Trust + Tests (5-6-7) | 2–3 | Deploy config + cleanup cron + guardrails + full test suite |
| **Tổng Lớp 1** | **20–24** | |

Lưu ý quan trọng: lát 3-4 của conversation_bridge phụ thuộc Product (Q2, Q4). Builder có thể thi công lát 1-2 + toàn bộ nhóm khác trước, rồi quay lại lát 3-4 khi Product trả spec. Nếu Product trả sớm → lane rút ngắn; nếu trả chậm → lát 3-4 trượt nhưng không block các nhóm khác.

---

## TỔNG KẾT

Sub-plan cover đầy đủ lane kỹ thuật cho release đầu KB-1:
- ✅ Kiến trúc target
- ✅ Đánh giá tái sử dụng / refactor / xây mới
- ✅ Migration path không mất dữ liệu cũ
- ✅ Webhook hardening (shared-store dedupe, **signature verification**, retry, logging, observability)
- ✅ Admin surface (auth, RBAC, audit, config, dashboard, lead, campaign, **Jinja2 templates KHÓA**)
- ✅ Deploy platform options + trade-off
- ✅ Backup / rollback / health / restart flow
- ✅ Task triển khai theo thứ tự
- ✅ File nên sửa / không nên đụng
- ✅ Test strategy + risk + dependency Product
- ✅ **conversation_bridge tách 4 lát thi công cụ thể + test riêng**
- ✅ **Return events khóa cơ chế real-time detection**
- ✅ **Timebox 2 lớp: code-only 20-24d / lane thực tế 28-35d**
- ✅ **Dockerfile healthcheck sửa lỗi curl → Python one-liner**
- ✅ **Open questions giảm từ 7 → 4 (Q5/Q6/Q7 đã khóa)**

---

## CHANGELOG

### Review loop 1 (v1 → v2)

| # | Feedback Engineering | Hành động Builder |
|---|---|---|
| 1 | Khóa admin frontend, không để mở 3 ngả | ĐIỀU CHỈNH: chốt Jinja2 server-rendered templates, thêm task 4.10, xóa Q5 |
| 2 | Docker healthcheck lỗi curl | ĐIỀU CHỈNH: đổi sang Python one-liner, thêm note platform probe |
| 3 | Thiếu webhook signature verification | ĐIỀU CHỈNH: thêm task 1.6 + D0 + test 7.6, thêm env FB_APP_SECRET |
| 4 | Return events chưa khóa cơ chế | ĐIỀU CHỈNH: khóa real-time detection, ghi implementation path 5 bước |
| 5 | conversation_bridge cần tách lát cụ thể | ĐIỀU CHỈNH: tách thành 4 lát merge độc lập, mỗi lát có scope file + test riêng |
| 6 | Timebox 15-20d lạc quan | ĐIỀU CHỈNH: chia 2 lớp (code-only 20-24d / lane thực tế 28-35d) |

### Review loop 2 — FINAL (v2 → v2-final, Engineering duyệt)

| # | Quyết định Engineering | Hành động Builder |
|---|---|---|
| E1 | Event taxonomy: "8 event cốt lõi" sai đếm → sửa thành "8 nhóm event kinh doanh, 11 event types kỹ thuật" | CẬP NHẬT: sửa wording funnel_events section |
| E2 | conversation_start không được log mỗi inbound message — chỉ bắn khi phiên mới thật sự | CẬP NHẬT: sửa lát 1 scope + test criteria — conversation_start chỉ ghi khi user chưa có session hoặc session inactive > ngưỡng Engineering định nghĩa |
| E3 | Admin auth phải dùng HttpOnly cookie, không bearer token thuần — phù hợp server-rendered + người vận hành không kỹ thuật | CẬP NHẬT: sửa auth flow section — JWT trong HttpOnly secure cookie, không yêu cầu user cầm bearer token |
| E4 | Deploy platform: Render ưu tiên, Railway fallback | CẬP NHẬT: khóa Render, sửa toàn bộ reference Railway/Render → Render primary, cập nhật task 5.1 + setup steps |

**Trạng thái: Engineering DUYỆT. Sub-plan đạt chuẩn để Engineering hấp thụ vào lane plan kỹ thuật.**

Open questions còn lại (4, tất cả chờ Product): Q1 payload quick replies/postbacks, Q2 flow người quay lại, Q3 default content seed, Q4 KB-2 confirmation UX.
