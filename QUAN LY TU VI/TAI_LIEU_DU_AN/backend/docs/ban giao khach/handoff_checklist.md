# Checklist bàn giao (Builder → Engineering / vận hành)

## Ranh giới: khách tự làm được gì / khi nào cần Engineering

| Nội dung | Khách / không IT (có hướng dẫn) | Cần Engineering / quyền hạ tầng |
|----------|----------------------------------|----------------------------------|
| Đọc checklist, đối chiếu bot có trả đúng thứ tự tin nhắn (luận giải → bank → CEO) | Có | Không |
| Chạy thử conversation Messenger sau khi server đã chạy | Có (nếu được cấp Page test) | Cần Engineering nếu webhook/token lỗi |
| Cài Python, tạo venv, `pip install` trên máy cá nhân (demo) | Có thể (theo `deployment_guide`) | Cần hỗ trợ nếu lỗi môi trường / quyền máy |
| Tạo / sửa **Meta App**, Webhook URL, Verify token, Page Access Token | Thường **không** (cần tài khoản Developer & quyền App) | **Engineering** hoặc người được ủy quyền Meta |
| Tạo tunnel HTTPS (ngrok, v.v.) để Meta gọi webhook | Có thể làm theo hướng dẫn | Cần Engineering nếu firewall / DNS / SSL production |
| Tạo DB PostgreSQL, chạy `sql/init_*.sql`, cấu hình `DATABASE_URL` | Không nên tự làm nếu không quen DB | **Engineering** / DBA |
| Sửa `.env` production (OpenAI, DB, FB token) trên server | Không (PII / bí mật) | **Engineering** |
| Đổi code engine, can chi, literal bank/CEO, schema SQL | Không | **Engineering** + duyệt COO nếu SoT |

**Chuẩn bị trước khi nhờ Engineering:** có sẵn mô tả lỗi, thời điểm, `request_id` / log được phép (không gửi full PII sinh).

## Checklist boundary (P1)

- [ ] Đã đọc bảng ranh giới trên và xác định được bước nào mình tự verify được.
- [ ] Các bước Meta / DB / `.env` production đã giao đúng người (Engineering), không giả định khách tự làm.

## Mã nguồn & phụ thuộc

- [ ] `requirements.txt` cài đủ trên môi trường sạch (`lunar-vn`, `pytest` cho CI).
- [ ] Không có thay đổi SQL / state machine ngoài phạm vi đã duyệt (theo master plan).

## Kiểm thử

- [ ] `python -m pytest tests/test_tuvi_engine.py -v` pass (8 test: anchor, lunar, determinism, thứ tự tin nhắn, golden sample A/B).
- [ ] `POST /generate-reading` trả `chart_json` có `houses`, `major_fortunes`, `menh`, `can_chi` khi không mock.

## Hành vi nghiệp vụ

- [ ] Input **âm lịch** được quy đổi sang solar trước khi tính can chi ngày.
- [ ] **Không** đổi ngày dương theo giờ sinh (23:xx vẫn cùng ngày dương đã nhập).
- [ ] Tin nhắn sau luận giải: **reading → block ngân hàng → ghi chú CEO** (xem `final_message_builder.py`).
- [ ] Dòng gợi ý `start` và donation CTA (nếu bật) vẫn đúng thứ tự trong `messenger_handler.py`.

## Tài liệu

- [ ] Đã đọc `docs/deployment_guide_step_by_step.md`, `config_checklist.md`, `runbook_basic.md`.
- [ ] `expected_result_examples.md` dùng để đối chiếu JSON/UI log nội bộ.

## Bàn giao

- [ ] Ghi rõ commit/tag và môi trường đã chạy pytest.
- [ ] Ghi các giả định (timezone mặc định, rule `tuvi_mvp_v1`) nếu khác production.
