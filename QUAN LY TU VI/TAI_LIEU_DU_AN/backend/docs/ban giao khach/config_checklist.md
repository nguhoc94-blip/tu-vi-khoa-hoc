# Checklist cấu hình (backend)

Đánh dấu từng mục trước khi lên production hoặc bàn giao.

## Bắt buộc tối thiểu

| Mục | Ghi chú |
|-----|---------|
| `DATABASE_URL` hoặc tương đương theo `app/db.py` | Kết nối PostgreSQL cho session + readings |
| OpenAI API key (nếu dùng GPT thật) | Thiếu key → teaser/reading fallback theo code hiện tại |

## Tùy chọn / hành vi

| Biến / cấu hình | Ý nghĩa |
|-----------------|--------|
| `USE_MOCK_CHART` | Khi bật (tuỳ convention trong `chart_builder.py`): bỏ qua engine tử vi thật, dùng chart mock để test pipeline |
| Donation CTA (theo `messenger_handler`) | Nếu được cấu hình qua env (xem mã nguồn), chuỗi CTA nối sau luận giải |

## Messenger Meta

- Verify token, app secret, page access token (theo quy trình Meta).
- URL callback HTTPS công khai cho `GET/POST /webhook`.

## Không đổi nếu không có quyết định COO/Engineering

- Literal ngân hàng và CEO note trong `app/services/final_message_builder.py`.
- Công thức ngày can chi (epoch `1911-01-01` → Tân Mùi) trong `tuvi_can_chi_engine.py`.

## Ranh giới cấu hình: ai làm việc gì

| Hạng mục | Khách / vận hành không chuyên | Engineering |
|----------|------------------------------|-------------|
| Đánh dấu checklist env đã đủ theo bảng trên | Có | Xác minh nếu nghi ngờ thiếu |
| Lấy OpenAI key, tạo Meta App, Page token | Không (bí mật) | Có |
| Điền `DATABASE_URL`, chạy migrate/SQL trên Postgres | Không | Có |
| Bật/tắt `USE_MOCK_CHART` trên staging để test | Chỉ khi được hướng dẫn | Khuyến nghị Engineering thao tác |

Chi tiết tình huống bàn giao: xem `docs/handoff_checklist.md` (mục ranh giới).
