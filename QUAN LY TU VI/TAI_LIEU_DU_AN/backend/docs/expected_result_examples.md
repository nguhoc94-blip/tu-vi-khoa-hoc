# Ví dụ kết quả mong đợi (tham chiếu nội bộ)

**Ranh giới:** tài liệu này dùng để **đối chiếu** output (JSON, thứ tự tin nhắn). Khách có thể đối chiếu hành vi bot với mục 3–4 nếu được hướng dẫn; không yêu cầu khách đọc code. Sửa engine hoặc prompt — Engineering.

## 1. Anchor ngày can chi (SoT)

- Ngày dương **1911-01-01** → cột ngày **Tân Mùi** (`tan` + `mui`), index chu kỳ 60 = **7** (0-based, `tan_mui`).

## 2. `chart_json` (tóm tắt cấu trúc)

Khi `USE_MOCK_CHART` tắt và normalize hợp lệ, `chart_json` gồm (tên field có thể mở rộng nhưng các khối sau là chính):

- `houses`: 12 cung, mỗi phần tử có mã cung, các sao chính gán vào cung, v.v. (theo `tuvi_core_engine`).
- `major_fortunes`: 12 đại vận (tuổi khởi, chiều, cung).
- `menh`: thông tin mệnh/cục dùng cho adapter.
- `can_chi`: năm/tháng/ngày/giờ (mã hóa) phục vụ prompt/context.

`prompt_adapter` map `houses` → `palaces` trong envelope gửi model (`adapter_version` `"2"`).

## 3. Tin nhắn Messenger (sau khi có bài luận giải)

Thứ tự chuỗi (không xen kẽ):

1. Nội dung luận giải đầy đủ (GPT).
2. Một dòng trống, rồi block ngân hàng cố định:  
   `VPBank — 0968433571 — Nguyễn Mạnh Linh`
3. Một dòng trống, rồi ghi chú CEO (đúng literal trong `final_message_builder.py`).
4. (Tuỳ cấu hình) thêm donation CTA và dòng gợi ý `start` — xem `messenger_handler.py`.

## 4. Test tự động

`tests/test_tuvi_engine.py` kiểm tra: anchor, không đổi cột ngày theo giờ, lunar → solar, deterministic hash chart, thứ tự part trong outbound, golden sample A/B (tuvi.vn).
