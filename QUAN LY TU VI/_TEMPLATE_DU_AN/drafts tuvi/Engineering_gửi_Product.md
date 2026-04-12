## ENGINEERING GỬI PRODUCT
Từ: Engineering
Gửi: Product
Ngày: 2026-04-10
Phase: Phase 2 (loop nội bộ P↔E — Nhịp 1)
---
Câu hỏi / phản biện kỹ thuật:
1. Engineering xác nhận đã nhận và dùng gói `Product_gửi_Engineering_Nhip1_Package.md` làm nguồn Product thống nhất cho CP1 + CP2 của Nhịp 1.
2. Với gói hiện tại, Engineering xác nhận **đủ để mở route/config/smoke baseline cho Nhịp 1**; chưa thấy thiếu field/khoá cấu hình nào ở mức blocker triển khai.
3. Engineering sẽ tự map business label -> technical key ở lớp triển khai để tránh kéo thêm 1 loop naming không cần thiết. Nếu Product muốn giảm tranh luận naming về sau, có thể bàn giao thêm bảng phụ trợ theo format dưới đây, nhưng **không phải blocker Nhịp 1**:
   - `business_label`
   - `flow_scope`
   - `content_group`
   - `allowed_placeholder` (yes/no)
   - `notes / guardrail`
4. Gói Product cần ưu tiên bàn giao tiếp theo cho lane kỹ thuật là **CP3 wording final packs** ở đầu Nhịp 2, đúng critical path Gate Plan. Payload key naming/table mapping chi tiết hơn chỉ là optional support, không phải đầu vào phải có trước.

Điểm thống nhất đến nay:
- CP1 đã đủ để Engineering map source/state -> flow baseline, flow priority baseline, payload groups baseline mà không phải đoán scope sản phẩm.
- CP2 đã đủ để Engineering seed `app_config` baseline, dựng static content keys baseline và smoke test route/config Nhịp 1.
- Placeholder chỉ được chấp nhận ở `payment_link_label` hoặc block Product đã cho phép; không dùng placeholder cho disclaimer / privacy notice.
- Không có thay đổi scope so với Gate Plan / master plan / lane plan đã khóa.
- Engineering sẽ giữ nguyên boundary Nhịp 1: không mở runtime preview/publish UI ở vòng này; chỉ cắm baseline data/config để phục vụ route/config/smoke và không kéo nhịp 2 vào sớm.
