# TuVi Messenger Bot Backend

## Bao cao tong hop hien trang MVP

### Muc tieu da dat duoc
- Hoan tat local MVP cho backend bot TuVi tren FastAPI.
- Co API noi bo `POST /generate-reading` de validate + normalize input va tra:
  - `normalized_input`
  - `chart_json` — **engine tu vi that** (12 cung, dai van, `menh`, `can_chi`) khi **khong** bat `USE_MOCK_CHART`; chi dung chart mock khi bat flag nay (debug/rollback pipeline)
  - `teaser` (OpenAI neu co key, fallback mock neu loi/thieu key — khac voi chart engine)
- Hoan tat Messenger webhook:
  - `GET /webhook` de verify voi Meta
  - `POST /webhook` de nhan event va xu ly hoi dap theo state machine luu DB

### Pham vi da lam
- Step 1 + 1.5:
  - normalize solar + leap=true => auto false, khong fail cung
  - giu validate date Gregorian cho solar
  - giu loi `MISSING_IS_LEAP_LUNAR_MONTH` cho lunar thieu flag
- Step 2:
  - teaser free goi OpenAI
  - fallback mock an toan neu loi API/network/khong co key
- Step 3:
  - state machine hoi tung truong du lieu qua Messenger
  - reset command toan cuc: `start`, `bat dau`, `xem lai`, `reset`
  - chi ho tro text message trong MVP
- Step 5A + Product update (full free mac dinh):
  - luu reading free/paid vao bang `readings`
  - flow mac dinh tra full reading truc tiep (khong paywall trong main flow)
  - ho tro donation CTA optional qua env
  - giu `unlock_demo`/endpoint de tuong thich ve sau
  - paid generation dung `system_paid.txt` + `user_paid.txt`, fallback an toan khi loi

### Pham vi chua lam (co y)
- Chua co cong thanh toan that
- Chua co payment
- Chua lam quick replies/buttons
- Chua tich hop Messenger production hardening day du

### API hien co
- `GET /health`
- `POST /generate-reading`
- `GET /webhook`
- `POST /webhook`
- `POST /demo/unlock-latest`

### Engine tu vi & kiem thu (Phase 2)
- Chart that (khong mock): `app/services/tuvi_calendar_engine.py` (**lunar-vn**, thuat toan Ho Ngoc Duc, lich am Viet UTC+7; `CALENDAR_ENGINE_VERSION` **1.1.0**), `tuvi_can_chi_engine.py`, `tuvi_core_engine.py`, `tuvi_constants.py`; `chart_builder.py` goi `build_chart_dict` khi khong bat `USE_MOCK_CHART`.
- **Luu y lich:** Truoc day dung `zhdate` (lich Trung UTC+8) co the lech 1 ngay am voi nguon VN o mot so ngay lich su; golden sample tuvi.vn doi chieu dung sau khi chuyen `lunar-vn`.
- `chart_json` co them `menh`, `can_chi`; `prompt_adapter` map `houses` -> `palaces`, `adapter_version` `2`.
- Tin nhan sau luong giai tren Messenger: reading -> block ngan hang -> ghi chu CEO (`final_message_builder.py` + `messenger_handler.py`).
- Test: `pip install -r requirements.txt` roi `python -m pytest tests/ -v` (engine **8** test trong `test_tuvi_engine.py`; them **10** test admin/footer/merge trong `test_messenger_footer_env.py`, `test_env_merge.py` — tong **18**).
- Tai lieu ban giao: thu muc `docs/` (`deployment_guide_step_by_step.md`, `config_checklist.md`, `runbook_basic.md`, `handoff_checklist.md`, `expected_result_examples.md`).
- Bao cao Builder -> Engineering (tong hop Phase 2 + lich VN): `QUAN LY TU VI/_TEMPLATE_DU_AN/drafts/Builder_gửi_Engineering.md` (muc BUILDER REPORT dinh dau file).

### Messenger flow MVP
- State:
  - `NEW`
  - `WAIT_FULL_NAME`
  - `WAIT_BIRTH_DAY`
  - `WAIT_BIRTH_MONTH`
  - `WAIT_BIRTH_YEAR`
  - `WAIT_BIRTH_HOUR`
  - `WAIT_BIRTH_MINUTE`
  - `WAIT_GENDER`
  - `WAIT_CALENDAR_TYPE`
  - `WAIT_IS_LEAP_LUNAR_MONTH`
  - `READY_TO_GENERATE`
  - `COMPLETED`
  - `CANCELLED`
- Thu thap lan luot:
  - `full_name`, `birth_day`, `birth_month`, `birth_year`, `birth_hour`, `birth_minute`, `gender`, `calendar_type`, va neu lunar thi hoi them `is_leap_lunar_month`
- Event khong phai text:
  - Reply: `Hien bot chi ho tro tin nhan van ban.`
- Sau khi generate xong:
  - gui full reading, sau do block ngan hang + ghi chu CEO (co dinh theo COO)
  - co the gui donation CTA (neu duoc cau hinh)
  - giu `COMPLETED`
  - hint: `Muon xem lai tu dau, nhan 'start'.`

### Logging va bao mat du lieu
- Cho phep log: `request_id`, `sender_id`, `state`, `event`
- Khong log:
  - `full_name`
  - full birth input raw tren 1 dong
  - full teaser/model output

### Danh gia nhanh
- Dat yeu cau release noi bo cho local MVP.
- He thong co the demo end-to-end: Messenger text -> thu thap du lieu -> tao full reading -> tra ket qua + donation CTA (neu co).
- Session Messenger da duoc luu DB, khong mat khi restart app (neu DB on dinh).

### Buoc tiep theo de xuat (sau Phase 2 baseline)
1. Tuning prompt production + postcheck theo data thuc te; bo sung test adapter/postcheck (Step 6C) khi COO/Engineering duyet.
2. Production hardening webhook (signature verify, retry, rate limit) khi co gate rieng — khong bat buoc cho MVP noi bo hien tai.
3. Mo rong golden sample / hoi quy lich neu Product yeu cau.
4. **Ngoai baseline MVP:** payment gateway, paywall, dashboard/ops — chi khi co quyet dinh Product/COO, khong ghi nhan la buoc tiep theo mac dinh cua Phase 2.

---

## Admin Panel (Streamlit — local)

**Hai lệnh COO đã khóa (ưu tiên hiển thị cho khách):**

```powershell
pip install streamlit
streamlit run admin.py
```

*(Có thể đã cài `streamlit` nhờ `pip install -r requirements.txt`; vẫn giữ hai lệnh trên trong tài liệu.)*

- Chạy từ thư mục `backend` (cùng cấp `app/`).
- Chi tiết: `docs/admin_panel_local.md`, `docs/runbook_basic.md`.
- `BACKEND_BASE_URL` mặc định **http://localhost:8000** trong panel; **không** là field thứ 7 của Wizard.

---

## Environment

| Bien | Bat buoc | Mo ta |
|------|----------|-------|
| `MESSENGER_PART_2_BANK_BLOCK` | **Co** (bot) | Noi dung block ngan hang trong tin nhac cuoi |
| `MESSENGER_PART_3_CEO_NOTE` | **Co** (bot) | Ghi chu CEO trong tin nhac cuoi |
| `OPENAI_API_KEY` | Khong | Thieu key thi teaser fallback mock |
| `OPENAI_MODEL` | Khong | Mac dinh `gpt-4o-mini` |
| `FB_VERIFY_TOKEN` | Co (khi test webhook) | Token verify voi Meta |
| `FB_PAGE_ACCESS_TOKEN` | Co (khi gui tin nhan that) | Token gui message qua Graph API |
| `DATABASE_URL` | Co | Ket noi PostgreSQL de luu `messenger_sessions` va `readings` |
| `PAID_OPENAI_MODEL` | Khong | Model uu tien cho full reading |
| `DONATION_TEXT` | Khong | Noi dung kieu goi ung ho |
| `DONATION_URL` | Khong | Link ung ho (neu co) |

Xem file `.env.example`.

## Khoi tao database (Step 4)

Tao bang session Messenger:

```powershell
psql "$env:DATABASE_URL" -f sql/init_messenger_sessions.sql
```

Bang `messenger_sessions` luu:
- `sender_id`
- `state`
- `data_json`
- `created_at`
- `updated_at`

Neu DB unavailable:
- khong crash webhook
- log event `messenger_db_unavailable`
- bot tra: `Hệ thống đang bận, vui lòng thử lại sau.`

## Khoi tao database (Step 5A)

Tao bang readings:

```powershell
psql "$env:DATABASE_URL" -f sql/init_readings.sql
```

Bang `readings` luu:
- `id`
- `sender_id`
- `normalized_input_json`
- `chart_json`
- `free_teaser`
- `full_reading`
- `is_unlocked`
- `status` (giu backward compatibility + flow moi):
  - legacy: `free_generated`, `unlock_requested`, `full_generated`, `full_fallback`
  - default free-full: `full_generated_free`, `full_fallback_free`
- `created_at`
- `updated_at`

## Main flow hien tai (khong paywall)

- Sau khi user nhap du du lieu sinh, he thong generate **full reading truc tiep**.
- Neu full OpenAI loi: tra fallback safe reading, khong crash.
- Donation CTA:
  - neu `DONATION_TEXT` va `DONATION_URL` deu rong: khong gui CTA
  - neu co `DONATION_URL` nhung `DONATION_TEXT` rong: dung cau CTA mac dinh
  - neu ca hai deu co: noi dung + URL

## Unlock demo (legacy, giu lai)

- Messenger command: `unlock_demo`
- API noi bo:
  - `POST /demo/unlock-latest`
  - body: `{ "sender_id": "USER_123" }`

Neu paid OpenAI loi:
- khong crash
- set `is_unlocked=true`
- set `status=full_fallback`
- luu fallback vao `full_reading`

## Run local

```powershell
cd backend
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload
```

API docs: `http://127.0.0.1:8000/docs`

## Test voi ngrok

1. Chay server local.
2. Tao tunnel: `ngrok http 8000`
3. Cau hinh Meta webhook:
   - Callback URL: `https://<your-ngrok>/webhook`
   - Verify token: dung voi `FB_VERIFY_TOKEN`
4. Subscribe event `messages`.

## Checklist nghiem thu noi bo

- [x] `GET /health` hoat dong.
- [x] `POST /generate-reading` hoat dong, giu dung response shape:
  - `ok`, `message`, `normalized_input`, `chart_json`, `teaser`.
- [x] Rule solar + `is_leap_lunar_month=true` duoc normalize ve `false` (khong fail cung).
- [x] Teaser free goi OpenAI khi co key, fallback mock an toan khi loi/thieu key.
- [x] `GET /webhook` verify token voi Meta.
- [x] `POST /webhook` nhan event text, hoi du lieu theo state machine va tra teaser.
- [x] Session Messenger luu PostgreSQL (`messenger_sessions`), khong mat khi restart app.
- [x] Khi DB unavailable:
  - webhook khong crash
  - log `messenger_db_unavailable`
  - bot tra: `Hệ thống đang bận, vui lòng thử lại sau.`
- [x] Product flow moi:
  - main flow khong paywall, tra full reading truc tiep
  - luu reading voi `is_unlocked=true`
  - success => `full_generated_free`; fail => `full_fallback_free`
  - donation CTA optional theo env
- [x] Legacy unlock van duoc giu de tuong thich:
  - `unlock_demo` va `POST /demo/unlock-latest`

## Luu y scope hien tai

- Chua co payment gateway that.
- Chua co subscription.
- Main flow hien tai la full-free; legacy unlock van duoc giu de tuong thich ve sau.
- Chua co quick replies/buttons.
- Chua hardening production day du (signature verify, retry strategy, rate limit).

## Build Report - 2026-03-24 Step 6B

### Build goal
- Them prompt adapter de backend khong dua raw engine JSON truc tiep vao model.
- Them production prompts (full/free) va hau kiem output an toan.

### Result
- PASS

### Files changed
- created: `app/services/prompt_adapter.py`
- created: `app/services/reading_postcheck.py`
- created: `prompts/system_full_production.txt`
- created: `prompts/user_full_production.txt`
- created: `prompts/system_free_production.txt`
- created: `prompts/user_free_production.txt`
- updated: `app/services/openai_paid.py`
- updated: `app/services/openai_teaser.py`
- updated: `README.md`

### Completed work
- Adapter `to_prompt_input_json(engine_raw_json)` tra dung shape:
  - `profile`, `chart_core`, `palaces`, `dai_van`, `reading_constraints`
- Mapping theo spec:
  - tong quan <- `chart_core + dai_van.current`
  - cong viec <- `palaces.quan_loc + chart_core.menh + dai_van.current`
  - tai chinh <- `palaces.tai_bach + palaces.dien_trach + dai_van.current`
  - tinh cam <- `palaces.phu_the + palaces.phuc_duc + chart_core.menh + dai_van.current`
- Hard-block postcheck:
  - prophecy / deterministic tu tuyet doi
  - hu doa / tuyet doi hoa
  - trigger => fallback ngay
- Soft-structure postcheck:
  - full can toi thieu 3 section
  - free khong lo day du 3 section
- OpenAI services da dung production prompts:
  - full: `system_full_production.txt`, `user_full_production.txt`
  - free: `system_free_production.txt`, `user_free_production.txt`

### Env vars needed
- `OPENAI_API_KEY`
- `OPENAI_MODEL` (optional)
- `PAID_OPENAI_MODEL` (optional)
- `DATABASE_URL`
- `FB_VERIFY_TOKEN`
- `FB_PAGE_ACCESS_TOKEN`
- `DONATION_TEXT` (optional)
- `DONATION_URL` (optional)

### Run steps
- `cd backend`
- `python -m venv .venv`
- `.venv\\Scripts\\Activate.ps1`
- `pip install -r requirements.txt`
- `uvicorn app.main:app --reload`

### Test steps
- Test full flow Messenger voi du lieu hop le -> nhan full reading.
- Test free flow API (`/generate-reading`) -> nhan teaser khong lo du 3 section.
- Test payload thieu field chart -> adapter van tra shape an toan.
- Test output co tu cam (qa mock) -> postcheck fallback.
- Test legacy unlock flow khong bi pha vo.

### Known limitations
- Chua co cong thuc TuVi that; adapter chi map/canonicalize du lieu.
- Kiem tra section dang o muc heuristic chuoi, chua parser semantic.
- Prompt production da bat dau dung, nhung can tuning them voi data thuc te.

### Next recommended step
- Step 6C: bo sung bo test tu dong cho prompt adapter + postcheck (unit tests + golden samples), va telemetry theo doi ty le fallback.

## Build Report - 2026-03-24 Step 6B.1

### Build goal
- Ap dung final pre-6C patch theo lenh TGD coder.

### Result
- PASS

### Files changed
- updated: `app/services/reading_postcheck.py`
- updated: `app/services/prompt_adapter.py`
- updated: `README.md`

### Completed work
- `reading_postcheck.py`:
  - them normalize tieng Viet khong dau truoc khi check hard-block regex
  - them normalize tieng Viet khong dau truoc khi detect section
  - giu nguyen behavior con lai
- `prompt_adapter.py`:
  - bo `palaces._raw` khoi `prompt_input_json`
  - giu nguyen mapping an toan va fallback unknown/[]/{}

### Env vars needed
- Khong co env moi cho patch nay.

### Run steps
- `cd backend`
- `uvicorn app.main:app --reload`

### Test steps
- Test teaser/full output co tu khoa tieng Viet co dau va khong dau -> hard-block van bat.
- Test section marker co dau/khong dau -> dem section nhat quan.
- Kiem tra payload prompt_input_json khong con field `palaces._raw`.

### Known limitations
- Section detection van la heuristic chuoi, chua semantic parser.

### Next recommended step
- Step 6C: viet unit tests cho `_normalize_text()`, hard-block, section rules va contract prompt_input_json.

## Build Report - 2026-04-07 Phase 2 + lich am Viet Nam

### Build goal
- Dong Phase 2 theo chi thi Engineering (engine that, adapter, final message, docs, test).
- Khac phuc lech golden sample do lich am: thay `zhdate` bang `lunar-vn` de khop tuvi.vn (UTC+7).

### Result
- PASS — `python -m pytest tests/test_tuvi_engine.py -v` => **8 passed**.

### Files changed (high level)
- `app/services/tuvi_calendar_engine.py` — dung `lunar-vn`; `CALENDAR_ENGINE_VERSION` = `1.1.0`.
- `requirements.txt` — `lunar-vn>=1.1.1`; bo `zhdate`.
- `tests/test_tuvi_engine.py` — golden sample A day du (khong con xfail); golden sample B giu nguyen.
- `QUAN LY TU VI/_TEMPLATE_DU_AN/drafts/Builder_gửi_Engineering.md` — BUILDER REPORT tong hop nop Engineering.
- `README.md` — muc nay + cap nhat muc "Engine tu vi & kiem thu".

### Evidence (mapping test)
- Anchor ngay: `test_anchor_1911_01_01_tan_mui`.
- No-day-shift: `test_no_day_shift_hour_does_not_change_day_pillar`.
- Lunar path: `test_lunar_input_path_converts_to_solar_before_domain`, `test_lunar_roundtrip_solar_present`.
- Determinism: `test_determinism_same_normalized_same_chart_hash`.
- Final message: `test_final_message_order`.
- Golden: `test_golden_sample_a_anchor_1911`, `test_golden_sample_b_nguyen_manh_linh_1994`.

### Known limitations
- Engine MVP chua co phu tinh / hoa / tieu han ngoai brief.
- Do chinh xac lich am rat xa trong qua khu van phu thuoc mo hinh `lunar-vn`; neu can doi chieu nguon khac, can quyet dinh SoT rieng.

### Next recommended step
- Mo rong golden sample hoac regression theo bang ngay neu Product yeu cau.
- Step 6C / telemetry adapter + postcheck neu van mo.

---

## BUILD REPORT — Fix TuVi Generate Bug (2026-04-08)

### Root cause

Log pattern: `openai_paid_success` → `messenger_generate_failed` (khong co `reading_created`).

**Root cause 1 (primary)**: Bang `readings` chua duoc tao trong DB vi `main.py` khong co startup hook chay SQL init. Loi psycopg `UndefinedRelation` bi nuot vao `except Exception:` (khong co stacktrace), session bi reset sai ve `WAIT_FULL_NAME`.

**Root cause 2 (secondary — se xay ra ngay sau khi fix RC1)**: `build_messenger_outbound()` hard-raise `RuntimeError` neu thieu `MESSENGER_PART_2_BANK_BLOCK` / `MESSENGER_PART_3_CEO_NOTE`. Cung bi nuot vao `except Exception:` cung reset sai.

**Van de phu**: `except Exception:` dung `logger.warning` (khong co stacktrace), moi loi generate deu silent va reset session — bat ke la loi he thong hay loi user.

### Files da sua

| File | Loai thay doi |
|------|---------------|
| `app/db_init.py` | Tao moi — best-effort `CREATE TABLE IF NOT EXISTS` cho ca hai bang |
| `app/main.py` | Them startup event goi `init_db()`; fail thi log `db_init_failed`, khong crash server |
| `app/services/messenger_handler.py` | Reorder `build_messenger_outbound` len truoc save COMPLETED; phan loai exception 4 nhanh |
| `tests/test_generate_error_handling.py` | Tao moi — 4 acceptance case |
| `.env.example` | Them comment bat buoc cho 2 bien footer |
| `README.md` | Muc nay |

### Exception classification da khoa cung

| Loai loi | Hanh dong | Reset session? |
|----------|-----------|----------------|
| `DatabaseUnavailableError` | re-raise (outer handler) | Khong |
| `psycopg.Error` (storage) | log `storage_error`, tra "loi luu tru" | Khong — data giu nguyen |
| `RuntimeError` (config/env) | log `config_error`, tra "loi cau hinh" | Khong — data giu nguyen |
| `Exception` bat ky khac | log `generate_failed` voi stacktrace day du, tra "bat dau lai" | Co — chi truong hop nay |

### Luu y db_init.py

Day la best-effort local/dev. Khong phai migration tool:
- Khong ALTER ban da ton tai.
- Neu schema lech (cot thieu/sai kieu), `init_db()` se fail va log `db_init_failed` ro rang — khong gia vo OK.

### Test results (22 passed)

```
tests/test_generate_error_handling.py::test_case1_happy_path_reading_created_and_completed PASSED
tests/test_generate_error_handling.py::test_case2_missing_footer_env_does_not_reset_session PASSED
tests/test_generate_error_handling.py::test_case3_db_storage_error_does_not_reset_session PASSED
tests/test_generate_error_handling.py::test_case4_unexpected_exception_resets_session PASSED
tests/test_messenger_footer_env.py (7 tests) PASSED
tests/test_tuvi_engine.py (8 tests) PASSED
tests/test_env_merge.py (3 tests) PASSED
Total: 22 passed in 0.83s
```

### Acceptance criteria — all pass

| Case | Dieu kien | Ket qua |
|------|-----------|---------|
| 1 | DB co bang + env du | `reading_created` logged, outbound hoan chinh tra ve user, COMPLETED | PASS |
| 2 | Thieu footer env | Response "loi cau hinh", session KHONG reset, data con nguyen | PASS |
| 3 | DB loi insert | Response "loi luu tru", session KHONG reset, data con nguyen | PASS |
| 4 | Loi khong mong doi | Session reset ve WAIT_FULL_NAME, data xoa, log exception day du | PASS |

---

## BUILD REPORT — Fix Webhook Blocking + Meta Retry (2026-04-08)

### Root cause moi

**Hien tuong**: user nhan "Phien da hoan tat. Muon xem lai tu dau, nhan 'start'." ngay sau khi nhap du lieu, khong thay ban doc GPT.

**Root cause**: Webhook xu ly dong bo (blocking). Toan bo flow — chart engine + OpenAI teaser + OpenAI paid (10–15 giay) + DB write + send_text_message — chay TRUOC KHI tra 200 cho Meta.

Meta yeu cau HTTP 200 trong 5 giay. Khi khong nhan duoc, Meta tu dong retry cung webhook event. Luc do:
- Lan 1 van dang chay (OpenAI chua xong)
- Lan 2 bat dau: session da COMPLETED (tu lan 1 hoan tat) → tra "Phien da hoan tat"
- User nhan tin nhan sai, khong thay ban doc

### Files da sua

| File | Loai thay doi |
|------|---------------|
| `app/api/messenger.py` | Chuyen sang BackgroundTasks; return 200 ngay; them dedupe by message mid |
| `app/services/event_deduplicator.py` | Tao moi — in-memory bounded set idempotency key store |
| `app/services/messenger_handler.py` | Them logging background_started/completed/failed; them event_id param |
| `tests/test_webhook_background.py` | Tao moi — 5 acceptance case |
| `README.md` | Muc nay |

### Dedupe strategy da chon

**In-memory bounded set** (`event_deduplicator.py`):
- Dung `message.mid` cua Meta lam idempotency key
- Luu trong `OrderedDict` co max size 2000 (FIFO eviction)
- Thread-safe voi `threading.Lock`
- Neu Meta retry cung `mid`, lan 2 bi skip va log `webhook_event_duplicate_skipped`
- Neu event khong co `mid` (edge case), fallback sang `uuid` moi → khong dedupe duoc nhung khong loi

**Gioi han (can biet)**:
- Store nay la in-process memory. Restart server → mat toan bo keys (chap nhan duoc vi retry sau restart it xay ra va vo hai).
- KHONG hoat dong trong multi-process / multi-worker deployment (cac worker khong chia se memory).
- De scale production: thay bang Redis SETNX hoac DB table voi unique constraint tren `mid`.

### Logging events moi

| Event key | Y nghia |
|-----------|---------|
| `webhook_event_received` | Event den, da parse duoc sender_id + mid |
| `webhook_event_scheduled` | Event moi, da add vao BackgroundTasks |
| `webhook_event_duplicate_skipped` | Event da xu ly truoc do, bo qua |
| `webhook_background_started` | Worker bat dau chay |
| `webhook_background_completed` | Worker hoan tat OK |
| `webhook_background_failed` | Worker loi, log stacktrace day du |

### Test results (27 passed)

```
tests/test_webhook_background.py::test_case1_webhook_returns_200_immediately PASSED
tests/test_webhook_background.py::test_case2_background_task_scheduled_with_correct_args PASSED
tests/test_webhook_background.py::test_case3_duplicate_mid_is_skipped PASSED
tests/test_webhook_background.py::test_case4_background_worker_calls_handle_then_send PASSED
tests/test_webhook_background.py::test_case5_background_failure_is_logged PASSED
tests/test_generate_error_handling.py (4 tests) PASSED
tests/test_messenger_footer_env.py (7 tests) PASSED
tests/test_tuvi_engine.py (8 tests) PASSED
tests/test_env_merge.py (3 tests) PASSED
Total: 27 passed in 0.82s
```

### Acceptance criteria — all pass

| Case | Dieu kien | Ket qua |
|------|-----------|---------|
| 1 | POST /webhook | Tra 200 ngay, khong cho OpenAI/DB/send message | PASS |
| 2 | Event hop le | Da schedule background task dung sender_id + text | PASS |
| 3 | Duplicate mid | Chi xu ly 1 lan, lan 2 bi skip | PASS |
| 4 | Background worker | Goi handle_incoming_text truoc, sau do send_text_message | PASS |
| 5 | Worker loi | logger.exception day du, khong crash webhook | PASS |

---

## BUILD REPORT — Conversational Bridge MVP

### Root cause kien truc wizard cu

Kien truc cu dung rigid state machine 12 state (WAIT_FULL_NAME -> ... -> COMPLETED). Van de chinh:

1. COMPLETED block follow-up: sau khi generate xong, moi tin nhan deu bi tra "Phien da hoan tat" — user khong the hoi tiep.
2. Thu thap du lieu cung nhac: moi luot chi nhan dung 1 field, khong parse cau noi tu nhien.
3. Khong co chat mode: khong the tra loi cau hoi tong quat ve tu vi truoc khi co du lieu sinh.
4. send_text_message nuot loi HTTP 400 (message qua dai) ma khong log ro status code.

### Kien truc moi — Conversational Bridge MVP

```
User → Webhook (200 ngay) → BackgroundTask
  → handle_incoming_text()
    → reset/unlock_demo commands
    → conversation_bridge.handle_conversation()
        → birth_extractor (NLU): trich field tu natural language
        → merge vao birth_data
        → Mode Router (hard logic):
            HAS_CHART   → follow-up OpenAI voi chart context
            GENERATE    → du data → chart engine + OpenAI reading
            INTAKE      → co partial birth_data → hoi field con thieu
            CHAT        → khong co birth_data → chat tu nhien ve tu vi
        → save session (birth_data + history + chart_json)
  → _split_text (<=1500 ky tu/chunk) → send tung chunk
```

**Files moi:**
- `app/services/birth_extractor.py` — NLU extraction via OpenAI, contract: chi tra fields, khong tra loi tu vi, omit neu khong chac
- `app/services/conversation_bridge.py` — Orchestrator chinh: mode routing, error handling, session save
- `prompts/system_extraction.txt` — Extraction system prompt
- `prompts/system_conversation.txt` — Follow-up conversation prompt

**Files sua:**
- `app/services/messenger_state.py` — them CHATTING/HAS_CHART states; MessengerSession moi: birth_data, history, chart_json, reading_id; FIELD_QUESTION map; add_turn() + missing_birth_fields()
- `app/services/messenger_state_db.py` — nested data_json format (birth/history/chart/reading_id); tu dong migrate flat format cu
- `app/services/messenger_handler.py` — don gian hoa: chi giu send_text_message, _split_text, reset/unlock routing; delegate xuong conversation_bridge
- `app/api/messenger.py` — fix BackgroundTasks signature (bo = BackgroundTasks() default, dat truoc payload)
- `tests/test_generate_error_handling.py` — cap nhat patch target sang conversation_bridge; case 4 doi thanh "birth_data intact" thay vi "reset to WAIT_FULL_NAME"

### Dedupe strategy

In-memory BoundedSet(2000) trong `event_deduplicator.py`. Key la `message.mid`. Gioi han: single-process, local/dev only. Khong hoat dong tren multi-worker production — can Redis/DB cho moi truong do.

### Cost control strategy

| Diem | Giai phap |
|------|-----------|
| birth_extractor | max_tokens=300, temperature=0; chi current message |
| conversation follow-up | max_tokens=600; chi 6 turns gan nhat + chart summary (khong full JSON) |
| chart generation | goi 1 lan/bo data (khong goi lai neu chart da co) |
| history | trim to MAX_HISTORY=8 sau moi turn |

### Ràng buộc hanh vi

- birth_extractor khong bao gio tra loi tu vi, khong bao gio doan neu khong chac (omit key).
- **Targeted intake parse:** khi session da partial va chua du field, truoc khi goi birth_extractor, `conversation_bridge` parse tin nhan theo **field dang thieu dau tien** (vi du `16`, `16h`, `16h30p` → `birth_hour` / `birth_minute`). Tranh vong lap INTAKE khi extractor tra `{}` cho cau tra loi ngan.
- INTAKE chi bat khi extract tra dict khong rong HOAC session da co partial birth_data. Neu extract = {} va khong co birth_data → CHAT mode, khong eo nguoi dung nhap ngay sinh.
- HAS_CHART co priority cao nhat: khi da co chart, follow-up luon duoc xu ly.

### Limitations

- Extraction NLU phu thuoc OpenAI: neu API loi thi fallback ve {} — targeted parse bu lai cho cau tra loi ngan theo dung field dang hoi.
- Dedupe in-memory: restart server xoa cache (chap nhan duoc, retry sau restart it gay hai).
- Chart chi generate 1 lan/session: neu user muon xem lai voi data khac, phai reset.

### Test results — 40/40 passed

**13 ky thuat (test_conversational_bridge.py):**

| # | Test | Ket qua |
|---|------|---------|
| 1 | webhook returns 200 immediately | PASS |
| 2 | webhook schedules background task | PASS |
| 3 | duplicate event is skipped | PASS |
| 4 | natural chat gets reply | PASS |
| 5 | birth data extraction from natural language | PASS |
| 6 | missing fields trigger targeted follow-up | PASS |
| 6b | targeted parse `16` → birth_hour, khong lap lai cau hoi gio | PASS |
| 6c | targeted parse `16h30p` → gio + phut, hoi tiep gioi tinh | PASS |
| 6d | `_parse_targeted_fields` unit | PASS |
| 7 | sufficient birth data triggers chart generation | PASS |
| 8 | follow-up after chart uses chart context | PASS |
| 9 | long messages split safely | PASS |
| 10 | background failures are logged | PASS |

**4 tieu chi san pham (P1-P4) — xac nhan qua test 4, 6, 8:**

| # | Scenario | Expected | Status |
|---|----------|----------|--------|
| P1 | User hoi tu vi chung, khong co birth data | Tra loi tu nhien, KHONG hoi ngay sinh | PASS (test 4) |
| P2 | User noi "sinh ngay 5 thang 6 nam 1990" | Trich duoc birth_day/month/year, hoi phan con lai | PASS (test 5+6) |
| P3 | Thieu gender, cac field khac da co | Hoi dung gender, khong hoi lai field co roi | PASS (test 6) |
| P4 | Co chart, hoi tiep "menh toi la gi?" | Tra loi dua tren chart, khong bao "phien hoan tat" | PASS (test 8) |
