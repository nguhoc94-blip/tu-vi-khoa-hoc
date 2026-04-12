## PRODUCT GỬI ENGINEERING
Từ: Product
Gửi: Engineering
Ngày: 2026-04-10
Phase: Phase 1 (loop nội bộ P↔E)
---
Spec / lane plan sản phẩm: 
Product xác nhận baseline release đầu giữ nguyên, KHÔNG reset plan nền. Product ghi nhận phản hồi Engineering rằng phạm vi hiện tại khả thi về mặt kỹ thuật nếu giữ đúng baseline đã khóa: 3 source launch (`love`, `career`, `organic_general`), 1 offer entry duy nhất, `payment link + manual close`, premium ở mức `intent capture / chuyển thủ công`, trust/safety bắt buộc, A/B chỉ ở copy-level tuần tự, admin governance chỉ preview cho static content blocks. Product dùng phản hồi này để chốt 5 điểm còn mở của vòng P↔E như dưới đây.

1. Product chốt phản hồi trên 5 điểm mở

### 1.1. M1 — Canonical event naming / semantics
Product chốt dùng canonical naming / semantics cho vòng này như sau:
- `conversation_started` = tên canonical ở layer business + spec + dashboard
- `free_result_sent` = tên canonical kỹ thuật thay cho `free_result_seen`
  - dashboard/business wording có thể hiển thị là: `free delivered`
  - release đầu KHÔNG dùng semantics “user đã thực sự đọc”
- `manual_paid_marked` = tên canonical business cho release đầu
  - state kỹ thuật map xuống: `order_marked_paid_manual`
  - metric business “paid success” ở release đầu được hiểu là manual-paid mapped success, không phải gateway-confirmed success

### 1.2. M2 — Preview semantics
Product chốt:
- `draft -> preview -> publish` chỉ áp cho **static content blocks** sau:
  - greeting theo campaign
  - opening question
  - CTA copy sau free
  - offer label
  - social proof snippet
  - disclaimer snippet
  - privacy / data notice snippet
  - reactivation copy trong window
- KHÔNG yêu cầu preview cho dynamic runtime output như free result hoàn chỉnh ghép từ chart + prompt + context ở release đầu.

### 1.3. M3 — Human handoff scope
Product chốt release đầu chỉ cần **minimal handoff surface**, chưa mở queue engine hoàn chỉnh.
Phạm vi tối thiểu chấp nhận được:
- `premium_intent_captured`
- `follow_up_owner`
- `follow_up_status`
- transcript / conversation history để operator đọc lại
- note / audit khi operator đổi trạng thái

### 1.4. M4 — Returning flow wording + KB-2 confirmation UX
Product chốt wording baseline cho 3 returning flows như sau:
- `returning_unpaid`:
  - opening text baseline: “Mình còn nhớ lần trước bạn đã xem [chủ đề gần nhất]. Lần này bạn muốn đào sâu tiếp phần đó hay chuyển sang chuyện khác?”
- `intake_abandoned_resume`:
  - opening text baseline: “Mình còn thiếu [trường còn thiếu] để chốt lá số cho bạn. Bạn muốn tiếp tục ngay hay sửa lại thông tin trước khi xem?”
- `paid_once_repeat`:
  - opening text baseline: “Lần trước bạn đã xem sâu phần [chủ đề đã mua]. Lần này bạn muốn mở tiếp chủ đề khác, xem nhịp tiếp theo, hay cần chuyên gia hỗ trợ?”

Product chốt rule xác nhận KB-2 ở mức wording baseline:
- khi bot suy đoán tạm dữ liệu có ảnh hưởng lớn, dùng mẫu: “Mình đang hiểu tạm là [giá trị suy đoán]. Bạn xác nhận giúp mình để mình lập lá số đúng nhé.”
- nếu còn từ 2 field lớn trở lên chưa chắc chắn, bot phải vào nhịp confirm trước khi generate chart
- nếu user sửa field lớn, bot reset trạng thái confirm liên quan trước khi generate

### 1.5. M5 — Completion metric definition
Product chốt admin release đầu hiển thị **2 mốc completion song song**:
- `intake_completion_rate = birthdata_confirmed / intake_started`
- `free_delivery_rate = free_generated_success / intake_started`
Không ép dùng 1 mốc duy nhất ở release đầu.

2. Product xác nhận lại baseline scope để Engineering khóa lane kỹ thuật
- 3 source launch đầu: `love`, `career`, `organic_general`
- `time_window` chỉ là nhánh interest trong `general`, không là campaign riêng
- 1 low-ticket entry duy nhất: `1 chủ đề sâu`
- paid path: `payment link + manual close`
- premium: `intent capture / chuyển thủ công`
- reactivation ngoài 24h không là trụ chính release đầu
- trust/safety là scope bắt buộc
- multi-profile chuẩn bị ở schema, chưa là trụ UX chính release đầu

3. Product xác nhận phần nào cần Engineering giữ đúng trong lane kỹ thuật
- state persistence 3 lớp theo đề xuất Engineering là baseline khả thi
- source attribution giữ được first/latest/current entry point
- confirmation flow là lát riêng của conversation bridge, không merge mơ hồ với các lát khác
- admin governance release đầu chỉ preview static content blocks
- paid success metric release đầu map từ manual-paid
- human handoff chỉ ở mức minimal surface

4. Yêu cầu Engineering phản hồi
Product đề nghị Engineering phản hồi đúng 3 phần:
1. Xác nhận đã chấp nhận toàn bộ 5 điểm Product chốt ở trên hay chưa
2. Nếu chưa chấp nhận, nêu đúng điểm nào còn xung đột kỹ thuật và phương án thay thế cụ thể
3. Nếu đã chấp nhận, Engineering khóa lane plan kỹ thuật theo baseline thống nhất này để Product hoàn thiện `Product_gửi_COO.md`

Điểm thống nhất đến nay:
- Product không đổi hướng plan nền
- Product chỉ điều chỉnh semantics / governance / metric / handoff scope cho đúng khả năng release đầu
- Mục tiêu vòng này là thống nhất P↔E trước khi Product gửi COO
