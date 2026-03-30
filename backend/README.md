# TuVi Messenger Bot Backend

## Bao cao tong hop hien trang MVP

### Muc tieu da dat duoc
- Hoan tat local MVP cho backend bot TuVi tren FastAPI.
- Co API noi bo `POST /generate-reading` de validate + normalize input va tra:
  - `normalized_input`
  - `chart_json` mock
  - `teaser` (OpenAI neu co key, fallback mock neu loi/thieu key)
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
  - gui full reading
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

### Buoc tiep theo de xuat
1. Step 5: paid generation flow + payment gating.
2. Step 6: production hardening webhook (retry strategy, signature verify, rate limit).
3. Step 7: bo sung dashboard/ops monitoring cho luong chat.

---

## Environment

| Bien | Bat buoc | Mo ta |
|------|----------|-------|
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
