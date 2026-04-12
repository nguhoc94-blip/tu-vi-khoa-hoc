GỬI: COO
TỪ: Engineering
LOẠI: plan
NGÀY: 2026-04-10

## ENGINEERING LANE PLAN
Từ: Engineering
Gửi: COO
Ngày: 2026-04-10
Phase: Phase 1
Trạng thái: BẢN CHỈNH TIMEBOX SAU REVIEW COO/QA — SẴN SÀNG ĐỂ COO NÂNG MASTER PLAN GATE PLAN
---

1. Cách tiếp cận kỹ thuật

### 1.1. Kết luận điều chỉnh vòng này
- Giữ nguyên toàn bộ hướng kỹ thuật đã khóa trước đó.
- Không phát hiện blocker kỹ thuật mới thật sự.
- Không cần mở lại tranh luận Product ở cấp plan.
- Không cần gọi Builder điều chỉnh sub-plan chỉ để chuẩn hóa timebox, vì input timebox và dependency đã đủ để Engineering tự hấp thụ ở cấp lane plan.

### 1.2. Hướng kỹ thuật giữ nguyên
- Render primary, Railway fallback.
- DB-first, additive migration.
- Engine tử vi deterministic là nguồn sự thật.
- conversation bridge thi công bắt buộc theo 4 lát.
- Admin release đầu: FastAPI + Jinja2 server-rendered templates.
- Auth admin: JWT trong HttpOnly secure cookie.
- Metric pack release đầu tính từ event mapping business -> technical đã khóa.

2. Kiến trúc hoặc flow ngắn

### 2.1. Tóm tắt kiến trúc giữ nguyên
- 1 FastAPI service + 1 managed PostgreSQL.
- Webhook vào `/webhook` -> signature verify -> dedupe DB -> attribution/return detection -> handler/conversation bridge.
- Engine deterministic giữ nguyên cho chart.
- OpenAI chỉ dùng cho diễn giải/hội thoại/upsell.
- Admin cùng service: API + HTML views + auth/RBAC/audit.
- Config động lấy từ `app_config` và `campaigns`.

### 2.2. Các cụm thi công giữ nguyên
- Foundation + Data/Migration.
- Webhook hardening + conversation bridge lát 1-2.
- Admin API/views + conversation bridge lát 3-4.
- Ops/Observability + Trust/Safety + Regression.

3. Các task triển khai

### 3.1. Nhịp 1 — Foundation + Data + Webhook hardening + bridge lát 1-2
Phạm vi:
- `app/db.py` connection pool
- `app/db_init.py` migration runner
- structured logging
- Dockerfile + `.dockerignore`
- `/health` + `/readiness`
- webhook signature verification
- migration 001-011
- DB dedupe
- messenger retry + typing indicator
- attribution capture
- funnel logger
- return-event detection
- conversation bridge lát 1-2

Điều kiện xong nhịp 1:
- Schema additive chạy idempotent
- Webhook production-safe baseline đã có
- Event pipeline nền đã ghi được các mốc cốt lõi
- Có thể log source/return/funnel baseline

### 3.2. Nhịp 2 — Admin API/views + bridge lát 3-4
Phạm vi:
- auth service + RBAC + audit
- admin API: config, campaigns, dashboard, leads, transcript, export
- admin HTML views Jinja2
- config service đọc runtime từ DB
- conversation bridge lát 3 (KB-2 confirm)
- conversation bridge lát 4 (multi-profile awareness baseline)

Điều kiện xong nhịp 2:
- Admin dùng được cho vận hành cơ bản
- Product governance surfaces có bề mặt thật để publish/config
- Confirm flow và multi-profile baseline chạy được theo plan đã khóa

### 3.3. Nhịp 3 — Ops/Observability + Trust/Safety + Regression
Phạm vi:
- `render.yaml`
- runbook deploy/redeploy/restart/rollback/verify webhook
- health/errors/token aggregation
- cleanup job cho `webhook_dedupe`
- profile deletion/anonymization
- guardrail route + redact log
- full regression `pytest`
- smoke test online cho webhook/admin/dashboard/health/rollback cơ bản

Điều kiện xong nhịp 3:
- Release 1 đạt readiness vận hành online bước đầu
- Có surface health/errors/funnel đủ cho admin và QA
- Có regression confidence trước Gate Output phase sau

4. File/module nên sửa
- `app/db.py`
- `app/db_init.py`
- `app/main.py`
- `app/api/messenger.py`
- `app/services/messenger_handler.py`
- `app/services/messenger_state.py`
- `app/services/messenger_state_db.py`
- `app/services/conversation_bridge.py`
- `app/services/openai_teaser.py`
- `app/services/openai_paid.py`
- `app/services/final_message_builder.py`
- `app/services/reading_postcheck.py`
- `app/utils/log_redact.py`
- `requirements.txt`
- `sql/migrations/*.sql`
- `app/api/admin.py`
- `app/api/admin_views.py`
- `templates/*.html`
- `render.yaml`
- `Dockerfile`
- `.dockerignore`
- test files mới theo lane

5. File/module không nên đụng
- `app/services/tuvi_core_engine.py`
- `app/services/tuvi_can_chi_engine.py`
- `app/services/tuvi_calendar_engine.py`
- `app/services/tuvi_constants.py`
- `app/services/normalizer.py`
- `app/services/prompt_adapter.py`
- `prompts/system_extraction.txt`
- prompt nội dung runtime thuộc scope Product
- `tests/test_tuvi_engine.py`

6. Rủi ro kỹ thuật lớn nhất
- `conversation_bridge.py` là critical risk P0 nếu không giữ đúng 4 lát thi công.
- Migration/backfill có rủi ro làm bẩn dữ liệu cũ nếu không giữ additive-only.
- Admin sẽ không hữu dụng nếu API, HTML views và config governance không đi cùng nhau.
- Timebox lane có thể trượt nếu input Product cho payload/content đến muộn, dù không chặn việc khóa plan.

7. Test strategy tối thiểu
- Unit test: pool, migration runner, signature verification, dedupe DB, auth, RBAC, retry logic.
- Integration test: funnel logger, campaign attribution, return events, config/campaign CRUD, transcript visibility, export.
- Flow test: confirm flow, returning resume logic, guardrail route, multi-profile baseline.
- Smoke test online: webhook verify, inbound event, `/health`, `/readiness`, admin login, dashboard query, redeploy/restart/rollback cơ bản.
- Regression rule: mỗi lát `conversation_bridge` phải pass full `pytest` suite trước khi merge lát tiếp theo.

8. Dependency

### 8.1. Dependency với Product còn có thể làm trượt timebox nhưng không blocker plan
1. Payload spec cho quick replies/postbacks
- Ảnh hưởng chính: route `message.quick_reply.payload`, `postback.payload`, CTA path trong nhịp 1/2.
- Tác động timebox: có thể làm chậm phần hoàn thiện task 3.4 và một phần bridge/CTA routing nếu Product bàn giao muộn.
- Mức độ: không chặn nhịp 1 tổng thể; chỉ chặn phần payload routing hoàn chỉnh.

2. Seed content mặc định cho `app_config`
- Ảnh hưởng chính: greeting mặc định, CTA, offer label, disclaimer, privacy notice, footer, social proof, reactivation copy.
- Tác động timebox: có thể làm chậm phần seed/publish-ready trong nhịp 2, nhưng không chặn việc dựng admin/config surface.
- Mức độ: không blocker plan; chỉ là input để hoàn thiện trạng thái publish-ready.

3. Wording final cho static content blocks
- Ảnh hưởng chính: preview/publish cuối của static blocks trong admin.
- Tác động timebox: có thể làm trượt phần polish cuối nhịp 2 hoặc đầu nhịp 3 nếu Product bàn giao chậm.
- Mức độ: không chặn coding surface; chỉ chặn nội dung vận hành bản cuối.

### 8.2. Dependency nội bộ kỹ thuật đã khóa
- Jinja2 admin.
- HttpOnly cookie auth.
- Render primary / Railway fallback.
- Event mapping business -> technical.
- Admin preview chỉ cho static content blocks.
- Human handoff release đầu chỉ minimal surface.

9. Timebox ước lượng

### 9.1. Timebox Phase 1 còn lại để chốt plan sạch cho Gate Plan
- **0.5 ngày làm việc còn lại trong loop hiện tại**.
- Phạm vi của 0.5 ngày này: chuẩn hóa timebox, critical path, parallelization và dependency risk cho COO nâng lên master plan.
- Engineering xác nhận đã tự hấp thụ xong trong vòng này; không cần loop Builder hay Product mới nếu không phát sinh blocker timebox thật.

### 9.2. Timebox Phase 2 / Release 1 ở cấp lane thực tế
- **28-35 ngày lane thực tế** cho 1 Builder full-time dưới điều phối Engineering.
- Trong đó lớp thi công thuần (code-only) là **20-24 ngày**.
- Buffer 8-11 ngày còn lại dành cho integration, review loop, deploy/smoke/fix, regression cuối và độ trễ input Product không-blocker.

### 9.3. Mapping 20-24 ngày code-only vào 3 nhịp điều phối
| Nhịp | Phạm vi | Code-only ước lượng | Ghi chú điều phối |
|---|---|---:|---|
| Nhịp 1 | Foundation + Data + Webhook hardening + bridge lát 1-2 | **8-11 ngày** | Critical path mở lane; chậm nhịp này là trượt toàn lane |
| Nhịp 2 | Admin API/views + bridge lát 3-4 | **7-9 ngày** | Phụ thuộc một phần input Product, nhưng admin surfaces có thể đi trước |
| Nhịp 3 | Ops/Observability + Trust/Safety + Regression | **5-6 ngày** | Chốt readiness online, health/errors/runbook, regression |
| **Tổng** |  | **20-24 ngày** |  |

### 9.4. Mapping 28-35 ngày lane thực tế vào 3 nhịp điều phối
| Nhịp | Phạm vi lane thực tế | Lane thực tế ước lượng | Phần buffer chính |
|---|---|---:|---|
| Nhịp 1 | Foundation + Data + Webhook hardening + bridge lát 1-2 | **10-13 ngày** | migration verify, webhook smoke, event/funnel baseline tune |
| Nhịp 2 | Admin API/views + bridge lát 3-4 | **10-12 ngày** | chờ payload/content từ Product, fix integration, confirm flow polish |
| Nhịp 3 | Ops/Observability + Trust/Safety + Regression | **8-10 ngày** | deploy online, health/error tuning, rollback verify, regression |
| **Tổng** |  | **28-35 ngày** |  |

10. Critical path và phần có thể đi song song

### 10.1. Critical path bắt buộc
1. Foundation (`db.py`, `db_init.py`, logging, health/readiness)
2. Data migrations 001-011
3. Webhook hardening nền (signature, dedupe DB, retry, attribution baseline)
4. bridge lát 1-2 (funnel/event/source/return baseline)
5. Admin API nền (auth/RBAC/config/campaign/dashboard data plumbing)
6. bridge lát 3-4
7. Ops/Observability + Regression cuối

Lý do critical path:
- Nếu chưa có Foundation/Data thì webhook/admin không có nền chạy ổn định.
- Nếu chưa có bridge lát 1-2 thì metric pack KB-8 và campaign/source funnel chưa đủ source of truth.
- Nếu chưa có bridge lát 3-4 thì KB-2 confirmation và multi-profile baseline chưa đạt acceptance release đầu.
- Nếu chưa có nhịp 3 thì chưa đạt readiness vận hành online để bàn giao.

### 10.2. Phần có thể đi song song
Có thể song song sau khi Foundation/Data đã đủ nền tối thiểu:
- Admin API và HTML views song song với một phần webhook polish.
- Campaign/config CRUD song song với dashboard queries.
- Trust/Safety redact/anonymization song song với một phần admin lead/transcript.
- `render.yaml`, runbook draft, health panels và token/error aggregation song song ở nửa sau nhịp 2.
- Product có thể bàn giao seed content và wording final song song với thi công admin surfaces.

### 10.3. Điểm tách nhịp an toàn cho COO tổng hợp phase/sprint
- Sau Nhịp 1: có nền schema + webhook + metric/event baseline.
- Sau Nhịp 2: có admin usable + confirm/multi-profile baseline.
- Sau Nhịp 3: có release 1 ready cho vận hành online bước đầu.

11. Kết luận
- Engineering **không cần mở lại loop với Product** ở vòng timebox-only này vì chưa phát hiện blocker timebox thật; các dependency Product còn lại chỉ là risk làm trượt nhịp, không chặn việc khóa plan.
- Engineering **không cần gọi Builder** chỉ để chỉnh sub-plan vì timebox tổng hợp đã đủ dữ liệu từ sub-plan cũ và lane plan hiện tại.
- Bản này giữ nguyên toàn bộ hướng kỹ thuật đã khóa, chỉ chuẩn hóa thêm timebox/critical-path/parallelization đúng yêu cầu COO.

## KẾT LUẬN ENGINEERING GỬI COO
Bản lane plan chỉnh này:
- giữ nguyên giải pháp kỹ thuật đã khóa;
- đã chuẩn hóa timebox Phase 1 còn lại và timebox Phase 2/Release 1;
- đã map 20-24 ngày code-only và 28-35 ngày lane thực tế vào 3 nhịp điều phối rõ;
- đã chỉ rõ dependency có thể làm trượt timebox nhưng không blocker plan;
- đã tách rõ phần nào critical path và phần nào có thể chạy song song.

Kết luận lane plan Engineering: **ĐẠT — đủ để COO nâng timebox lên master plan Gate Plan, không cần mở thêm loop cấp dưới trong vòng này.**
