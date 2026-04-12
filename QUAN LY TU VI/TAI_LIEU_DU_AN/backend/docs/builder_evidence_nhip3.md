# BUILDER EVIDENCE REPORT — Nhịp 3
**Ngày:** 2026-04-12  
**Người thực hiện:** Builder  
**Môi trường:** Local (Windows 10, Python 3.10.11, PostgreSQL 18)

---

## 1. Kết quả Pytest — 66/66 PASSED

```
platform win32 -- Python 3.10.11, pytest-8.4.2, pluggy-1.6.0
rootdir: .../TAI_LIEU_DU_AN/backend

collected 66 items

tests/test_admin_portal.py::test_admin_login_get_ok PASSED
tests/test_admin_portal.py::test_admin_dashboard_redirects_without_cookie PASSED
tests/test_conversational_bridge.py::test_webhook_returns_200_immediately PASSED
tests/test_conversational_bridge.py::test_webhook_schedules_background_task PASSED
tests/test_conversational_bridge.py::test_duplicate_event_is_skipped PASSED
tests/test_conversational_bridge.py::test_natural_chat_gets_reply PASSED
tests/test_conversational_bridge.py::test_birth_data_extraction_from_natural_language PASSED
tests/test_conversational_bridge.py::test_missing_fields_trigger_targeted_question PASSED
tests/test_conversational_bridge.py::test_targeted_parse_birth_hour_16_not_loop PASSED
tests/test_conversational_bridge.py::test_targeted_parse_16h30p_sets_hour_and_minute PASSED
tests/test_conversational_bridge.py::test_parse_targeted_fields_unit PASSED
tests/test_conversational_bridge.py::test_kb2_shows_summary_before_generate PASSED
tests/test_conversational_bridge.py::test_kb2_confirm_triggers_chart_generation PASSED
tests/test_conversational_bridge.py::test_followup_after_chart_uses_chart_context PASSED
tests/test_conversational_bridge.py::test_long_messages_split_safely PASSED
tests/test_conversational_bridge.py::test_background_failure_is_logged PASSED
tests/test_data_subject_unit.py::test_anonymize_rejects_empty_sender PASSED
tests/test_env_merge.py::test_merge_preserves_unrelated_keys PASSED
tests/test_env_merge.py::test_merge_appends_new_keys PASSED
tests/test_env_merge.py::test_merge_creates_file PASSED
tests/test_event_dedupe_key.py::test_dedupe_key_uses_message_mid PASSED
tests/test_event_dedupe_key.py::test_dedupe_key_postback_fallback PASSED
tests/test_flow_routing.py::test_priority_intake_over_paid PASSED
tests/test_flow_routing.py::test_priority_paid_over_returning PASSED
tests/test_flow_routing.py::test_returning_unpaid_before_entry_source PASSED
tests/test_flow_routing.py::test_entry_love_career_general PASSED
tests/test_flow_routing.py::test_default_entry_organic PASSED
tests/test_generate_error_handling.py::test_case1_happy_path_reading_created_and_completed PASSED
tests/test_generate_error_handling.py::test_case2_config_error_does_not_reset_session PASSED
tests/test_generate_error_handling.py::test_case3_db_storage_error_does_not_reset_session PASSED
tests/test_generate_error_handling.py::test_case4_unexpected_exception_graceful_response PASSED
tests/test_log_redact_nhip3.py::test_redact_log_line_patterns[...sk-...] PASSED
tests/test_log_redact_nhip3.py::test_redact_log_line_patterns[OPENAI_API_KEY=...] PASSED
tests/test_log_redact_nhip3.py::test_redact_log_line_patterns[postgresql://...] PASSED
tests/test_log_redact_nhip3.py::test_redact_log_line_patterns[Bearer ...] PASSED
tests/test_log_redact_nhip3.py::test_redacting_formatter_masks_secret_in_output PASSED
tests/test_messenger_footer_env.py::test_build_messenger_outbound_reads_env PASSED
tests/test_messenger_footer_env.py::test_build_messenger_outbound_order_reading_bank_ceo PASSED
tests/test_messenger_footer_env.py::test_missing_env_raises PASSED
tests/test_messenger_footer_env.py::test_getters_strip_whitespace PASSED
tests/test_messenger_footer_env.py::test_redact_log_line_masks_openai_key_assignment PASSED
tests/test_messenger_footer_env.py::test_redact_log_line_masks_database_url PASSED
tests/test_messenger_footer_env.py::test_restart_banner_text_nonempty PASSED
tests/test_nhip3_health.py::test_health_ok PASSED
tests/test_nhip3_health.py::test_health_includes_git_metadata_when_set PASSED
tests/test_payload_handler.py::test_secondary_returning_unpaid_emits_upsell_secondary PASSED
tests/test_profile_awareness.py::test_profile_clarification_once_for_returning_flow PASSED
tests/test_profile_awareness.py::test_no_clarification_when_already_shown PASSED
tests/test_tuvi_engine.py::test_anchor_1911_01_01_tan_mui PASSED
tests/test_tuvi_engine.py::test_no_day_shift_hour_does_not_change_day_pillar PASSED
tests/test_tuvi_engine.py::test_lunar_input_path_converts_to_solar_before_domain PASSED
tests/test_tuvi_engine.py::test_lunar_roundtrip_solar_present PASSED
tests/test_tuvi_engine.py::test_determinism_same_normalized_same_chart_hash PASSED
tests/test_tuvi_engine.py::test_final_message_order PASSED
tests/test_tuvi_engine.py::test_golden_sample_a_anchor_1911 PASSED
tests/test_tuvi_engine.py::test_golden_sample_b_nguyen_manh_linh_1994 PASSED
tests/test_webhook_background.py::test_case1_webhook_returns_200_immediately PASSED
tests/test_webhook_background.py::test_case2_background_task_scheduled_with_correct_args PASSED
tests/test_webhook_background.py::test_case3_duplicate_mid_is_skipped PASSED
tests/test_webhook_background.py::test_case4_pipeline_calls_handle_then_send PASSED
tests/test_webhook_background.py::test_case5_pipeline_failure_is_logged PASSED
tests/test_webhook_dedupe_cleanup.py::test_retention_hours_locked_24 PASSED
tests/test_webhook_dedupe_cleanup.py::test_cleanup_returns_zero_when_table_missing PASSED
tests/test_webhook_payload_limit.py::test_webhook_post_rejects_oversized_body PASSED
tests/test_webhook_signature.py::test_verify_meta_webhook_signature_ok PASSED
tests/test_webhook_signature.py::test_verify_meta_webhook_signature_rejects_bad_sig PASSED

========================= 66 passed in 2.36s =========================
```

**Ghi chú fix:** 3 test fail trước đó do thiếu env var trong test isolation.
- `test_birth_data_extraction_from_natural_language` → thêm `OPENAI_API_KEY` fake vào monkeypatch
- `test_case1_happy_path_reading_created_and_completed` → thêm `MESSENGER_PART_2_BANK_BLOCK` / `MESSENGER_PART_3_CEO_NOTE`
- `test_final_message_order` → tạo `tests/conftest.py` với autouse fixture

---

## 2. Health Check — Local API

```
GET http://127.0.0.1:8000/health
→ {"status": "ok", "service": "tuvi-backend"}

GET http://127.0.0.1:8000/readiness
→ {"status": "ready"}
```

---

## 3. Database — PostgreSQL Local

**Host:** localhost:5432  
**Database:** `messenger_bot`  
**Migrations áp dụng:** 15/15 (001 → 015)

| Version | Applied At |
|---------|------------|
| 001 | 2026-04-12 14:53:26 |
| 002 | 2026-04-12 14:53:26 |
| 003 | 2026-04-12 14:53:26 |
| 004 | 2026-04-12 14:53:26 |
| 005 | 2026-04-12 14:53:26 |
| 006 | 2026-04-12 14:53:26 |
| 007 | 2026-04-12 14:53:26 |
| 008 | 2026-04-12 14:53:26 |
| 009 | 2026-04-12 14:53:26 |
| 010 | 2026-04-12 14:53:26 |
| 011 | 2026-04-12 14:53:26 |
| 012 | 2026-04-12 14:53:26 |
| 013 | 2026-04-12 14:53:26 |
| 014 | 2026-04-12 14:53:26 |
| 015 | 2026-04-12 14:53:26 |

**Tables tạo thành công (14 tables):**
`admin_audit_log`, `admin_sessions`, `admin_users`, `app_config`, `campaigns`,
`conversation_history`, `funnel_events`, `messenger_sessions`, `orders`,
`profile_entities`, `readings`, `schema_migrations`, `user_profiles`, `webhook_dedupe`

---

## 4. Ngrok Tunnel — Smoke Test Local

```
Public URL : https://subdivine-bewilderedly-joni.ngrok-free.dev
Webhook URL: https://subdivine-bewilderedly-joni.ngrok-free.dev/webhook
Verify Token: duyen_store_verify_2026
Status: ACTIVE (khớp URL cũ, không cần đổi cấu hình Facebook)
```

**Trạng thái:** Tunnel đang chạy, backend phản hồi đúng.

---

## 5. Smoke Test — Messenger Live (PASSED)

**Thời gian:** 2026-04-12 ~15:15–15:16 (GMT+7)  
**Facebook API Version:** v25.0  
**User-Agent:** `facebookexternalua` (Facebook server thật)

| Request | Method | URI | Response |
|---|---|---|---|
| Tin nhắn 1 (`mình kinh doanh thời trang hè`) | POST | `/webhook` | `200 OK` |
| Tin nhắn 2 (`thử là tôi hợp làm hay không?`) | POST | `/webhook` | `200 OK` |

**Xác nhận kỹ thuật:**
- Header `X-Hub-Signature-256` có mặt → Facebook ký đúng
- Header `X-Request-Id` trong response → middleware Nhịp 3 hoạt động
- Backend trả về `{"status":"ok"}` trong < 3s cho mỗi request
- Bot đã trả lời user trên Messenger ✅

---

## 6. Fix Race Condition — Per-sender Lock + Debounce (CEO chỉ đạo — 2026-04-12)

> **Nguồn gốc chỉ đạo:** CEO phát hiện trong phiên test: "khách nhắn quá nhanh dường như mỗi lần trả lời đều không cùng 1 chat" → CEO yêu cầu xử lý theo cách tốt nhất.

**Vấn đề:** FastAPI `BackgroundTasks` chạy mỗi webhook event trong thread pool độc lập. Khi user nhắn nhiều tin liên tiếp nhanh (< 1–2s), mỗi tin được xử lý song song, gây ra:
- Nhiều call OpenAI đồng thời cho cùng 1 user
- Race condition trên session DB → câu trả lời lộn xộn, mất ngữ cảnh

**Giải pháp implement:** `app/services/messenger_handler.py`

| Thành phần | Mô tả |
|---|---|
| `_sender_pending` | Dict lưu `request_id` mới nhất của từng sender |
| `_sender_locks` | Dict lưu `threading.Lock()` riêng mỗi sender |
| `_register_pending()` | Ghi nhận request mới nhất khi tin đến |
| `_is_still_latest()` | Kiểm tra xem task này có còn là mới nhất không |
| `_get_debounce_seconds()` | Đọc `DEBOUNCE_SECONDS` từ env (default 1.5s) |

**Luồng xử lý:**
```
Tin A đến → pending[sender]=A → sleep 1.5s → wake → pending≠A → SKIP
Tin B đến → pending[sender]=B → sleep 1.5s → wake → pending≠B → SKIP
Tin C đến → pending[sender]=C → sleep 1.5s → wake → pending=C → acquire lock → XỬ LÝ ✓
```

**Đảm bảo:** Postback và Quick Reply **không bị debounce** (pass through ngay lập tức).

**Cấu hình:** thêm `DEBOUNCE_SECONDS=1.5` vào `.env` nếu muốn tuỳ chỉnh.

**Pytest sau thay đổi:**
```
66 passed in 10.57s  (platform win32, Python 3.10.11, pytest-8.4.2)
Timestamp: 2026-04-12
```
_(Thời gian tăng so với trước debounce do sleep 1.5s trong background pipeline — không phải regression.)_

---

## 7. Tóm tắt

| Hạng mục | Kết quả |
|---|---|
| Unit tests | ✅ 66/66 PASSED |
| Server startup | ✅ `Application startup complete` |
| `/health` | ✅ `{"status":"ok"}` |
| `/readiness` (DB ping) | ✅ `{"status":"ready"}` |
| Database migrations | ✅ 15/15 applied, 14 tables |
| Ngrok tunnel | ✅ URL khớp, không thay đổi |
| Webhook signature verify | ✅ `X-Hub-Signature-256` hợp lệ |
| Smoke test Messenger live | ✅ Bot nhận và trả lời tin nhắn thật |
| Race condition fix (Lock+Debounce) | ✅ CEO chỉ đạo — implemented & tested |

---

## 8. Production Render (BÁO CÁO E — 2026-04-12)

| Mục | Giá trị |
|-----|---------|
| Public URL | `https://tuvi-backend-ocgd.onrender.com` |
| Webhook | `https://tuvi-backend-ocgd.onrender.com/webhook` |
| `GET /health` | `200` — `{"status":"ok","service":"tuvi-backend"}` |
| `GET /readiness` | `200` — `{"status":"ready"}` |
| Git HEAD (sau fix deploy) | `9f9d874` |
| Fix deploy | `python-multipart` trong `requirements.txt`; `db_init.py` rollback + migration per-connection |

**Việc còn lại:** cập nhật Callback URL webhook trên Facebook Developer; tick `smoke_checklist_nhip3.md` cho prod.

---

## 9. Vòng bảo mật khẩn cấp (memo Engineering 2026-04-12)

| Hạng mục | Trạng thái |
|----------|------------|
| `.env` không track | OK |
| `.gitignore` + `ngrok.exe` | Đã ignore; `git rm --cached` khỏi repo |
| GitHub repo | **private** |
| `/health` + `/readiness` sau remediation | OK (2026-04-12) |
| Rotate secret (OpenAI, FB, DB, Render API, GitHub PAT) | **Owner** — xem checklist tên key trong `Builder_gửi_Engineering.md` § *VÒNG KHẮC PHỤC BẢO MẬT* |
