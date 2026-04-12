## SPECIALIST REPORT
Từ: Marketing/Funnel Specialist
Gửi: Product
Ngày: 2026-04-10
Phase: Phase 2 execution round 1
---
A. Campaign-to-flow mapping pack v1

### A1. Source / state -> flow map baseline
| Source hiện tại | User state ưu tiên | Flow được gọi | Ghi chú |
|---|---|---|---|
| love | new user, chưa có active chart/session dở | new_user_love | Source-driven flow cho entry đầu |
| career | new user, chưa có active chart/session dở | new_user_career | Source-driven flow cho entry đầu |
| organic_general | new user, chưa có active chart/session dở | new_user_general | General entry; time-window chỉ là nhánh quan tâm bên trong |
| bất kỳ | intake đang dở, còn missing field | intake_abandoned_resume | State-driven flow, ưu tiên cao hơn source |
| bất kỳ | đã xem free, chưa trả tiền | returning_unpaid | State-driven flow, ưu tiên cao hơn source |
| bất kỳ | đã có paid status tối thiểu 1 lần | paid_once_repeat | State-driven flow, ưu tiên cao hơn source |

### A2. Flow priority rule baseline
1. Nếu user có intake dở và còn missing field -> vào `intake_abandoned_resume`
2. Nếu user đã paid ít nhất 1 lần -> vào `paid_once_repeat`
3. Nếu user đã xem free nhưng chưa paid -> vào `returning_unpaid`
4. Chỉ khi không rơi vào 3 trạng thái trên mới route theo source entry:
   - `love` -> `new_user_love`
   - `career` -> `new_user_career`
   - `organic_general` -> `new_user_general`

### A3. Flow matrix v1
| Flow name | Opening intent | Opening question baseline | CTA chính baseline | CTA phụ baseline | Rule chuyển flow | Event touchpoint (business) | Text-first / quick replies |
|---|---|---|---|---|---|---|---|
| new_user_love | Nối mạch đúng ngữ cảnh tình duyên, kéo user nói pain point trước khi intake | “Hiện tại chuyện tình cảm làm bạn bận tâm nhất là điều gì?” | “Để mình nhìn kỹ cho bạn” | “Nói ngắn điều bạn lo nhất” | Sau 1 lượt user trả lời hoặc không trả lời nhưng vẫn muốn tiếp -> vào intake; nếu thiếu field lớn thì sang confirm step trước chart; sau free result -> giữ trong flow để upsell/hỏi tiếp | conversation_started, source_identified, topic_inferred_or_selected, intake_started, birthdata_confirmation_requested, birthdata_confirmed, free_result_sent, upsell_offer_shown, upsell_primary_clicked / upsell_secondary_clicked | Opening giữ text-first; quick replies chỉ dùng ở bước confirm, resume, CTA sau free |
| new_user_career | Nối mạch đúng ngữ cảnh công việc/sự nghiệp, xác định pain point nghề nghiệp | “Lúc này bạn đang bận tâm nhất về công việc, hướng đi hay tiền bạc?” | “Để mình nhìn kỹ cho bạn” | “Nói ngắn điều bạn đang phân vân” | Tương tự love flow; nếu user nêu đổi việc/thăng tiến/tài chính thì lưu topic interest nhưng không tách source mới | conversation_started, source_identified, topic_inferred_or_selected, intake_started, birthdata_confirmation_requested, birthdata_confirmed, free_result_sent, upsell_offer_shown, upsell_primary_clicked / upsell_secondary_clicked | Opening giữ text-first; quick replies chỉ dùng khi cần rescue/disambiguation và ở bước confirm + CTA |
| new_user_general | Mở tự nhiên, xác định user muốn hiểu tình cảm, công việc hay hướng đi chung | “Bạn muốn mình nhìn trước về tình cảm, công việc hay bức tranh chung của bạn?” | “Bắt đầu xem cho tôi” | “Chọn điều tôi đang quan tâm” | Nếu user nói time-window thì chỉ lưu interest branch trong general, không mở flow/source riêng; sau khi đã có intent đủ rõ -> vào intake | conversation_started, source_identified, topic_inferred_or_selected, intake_started, birthdata_confirmation_requested, birthdata_confirmed, free_result_sent, upsell_offer_shown, upsell_primary_clicked / upsell_secondary_clicked | Opening ưu tiên text-first; quick replies được phép như rescue để chọn interest nếu user im lặng / trả lời quá mơ hồ |
| returning_unpaid | Nhận diện user cũ, nhắc rất ngắn họ đã xem gì và kéo quay lại phần còn dang dở / chủ đề đang quan tâm | “Lần trước mình đã xem tổng quan cho bạn rồi — lần này bạn muốn đào sâu phần nào nhất?” | “Xem tiếp phần đang dở” | “Xem sâu chủ đề này” | Nếu user đổi hồ sơ hoặc birth data có khả năng sai/mơ hồ -> quay về confirm/intake; nếu user đi tiếp bình thường -> giữ flow returning cho free follow-up ngắn rồi bridge paid | conversation_started, source_identified, topic_inferred_or_selected, intake_resumed hoặc upsell_offer_shown, upsell_primary_clicked / upsell_secondary_clicked, return_7d / return_30d | Opening giữ text-first; quick replies dùng cho 2 lựa chọn tiếp tục / đào sâu |
| intake_abandoned_resume | Kéo user quay lại đúng bước đang dở, giảm ma sát và hoàn tất confirm trước chart | “Bạn còn thiếu một vài thông tin để mình xem chính xác hơn — mình đi tiếp từ bước đang dở nhé?” | “Tiếp tục lập lá số” | “Sửa thông tin trước khi xem” | Nếu user chọn tiếp tục -> quay về step còn thiếu; nếu chọn sửa -> mở lại step confirm tương ứng; đủ dữ liệu -> chạy free result ngay | conversation_started, source_identified, intake_resumed, birthdata_confirmation_requested, birthdata_confirmed, free_generated_success / free_generated_failed, free_result_sent | Step mở đầu có thể text-first + quick replies ngay sau đó; quick replies là baseline bắt buộc cho resume/edit |
| paid_once_repeat | Nhận diện user đã mua, dẫn sang next-best paid path hoặc human handoff tối thiểu | “Bạn muốn đào sâu chủ đề khác, đi tiếp phần thời điểm này hay để mình ghi nhận nhu cầu gặp chuyên gia?” | “Mở gói tiếp theo phù hợp” | “Để chuyên gia hỗ trợ tiếp” | Nếu user muốn đào sâu chủ đề khác -> route trong flow paid repeat; nếu muốn human handoff -> intent capture; nếu thiếu ngữ cảnh/hồ sơ -> hỏi ngắn rồi tiếp tục | conversation_started, source_identified, topic_inferred_or_selected, upsell_offer_shown, upsell_primary_clicked / upsell_secondary_clicked, paid_intent_submitted | Opening giữ text-first; quick replies dùng ở bước chọn next action và human handoff |

### A4. Text-first vs quick replies rule baseline
- Text-first bắt buộc ở: opening của 3 flow new user, opening của returning_unpaid, paid_once_repeat
- Quick replies baseline bắt buộc ở:
  - bước chọn hướng tiếp theo khi user cần rescue/disambiguation
  - bước confirm birth data trước chart
  - bước resume / edit trong intake_abandoned_resume
  - CTA sau free result
  - intent capture cho premium/handoff
- Postback / open-url baseline dùng cho:
  - CTA mở payment link
  - CTA gửi intent gặp chuyên gia / cần hỗ trợ thêm

### A5. Note chốt cho round 1
- Không có source mới ngoài `love`, `career`, `organic_general`
- Không có flow mới ngoài 6 flow tối thiểu
- Không có A/B, optimization copy, social proof, seed content hay wording final trong pack này
- `time_window` không là campaign riêng; chỉ là interest note trong `new_user_general`

B. Payload-spec support pack

### B1. Payload baseline bắt buộc cho CP1
| Flow name | Step name | Label hiển thị | Intent / nghĩa nghiệp vụ | Action mong muốn khi bấm | Event business mong muốn | Segment / funnel-stage update mong muốn | CP1 | Baseline / để sau |
|---|---|---|---|---|---|---|---|---|
| new_user_love | post-opening rescue | Xem cho tôi | User chấp nhận đi vào intake từ source love | Chuyển sang intake bước đầu | intake_started | funnel_stage = intake_started; topic_interest = love | critical | baseline |
| new_user_love | post-free CTA primary | Xem sâu tình duyên | User muốn mở low-ticket chủ đề sâu theo source love | Hiện paid bridge + payment path | upsell_primary_clicked | funnel_stage = paid_offer_engaged; offer_interest = love_deep | critical | baseline |
| new_user_love | post-free CTA secondary | Hỏi tiếp điều tôi lo nhất | User muốn tiếp tục hội thoại miễn phí ở mức bề mặt | Giữ conversation trong free follow-up ngắn, chưa mở payment path | upsell_secondary_clicked | funnel_stage = free_followup; topic_interest = love | critical | baseline |
| new_user_career | post-opening rescue | Xem cho tôi | User chấp nhận đi vào intake từ source career | Chuyển sang intake bước đầu | intake_started | funnel_stage = intake_started; topic_interest = career | critical | baseline |
| new_user_career | post-free CTA primary | Xem sâu công việc | User muốn mở low-ticket chủ đề sâu theo source career | Hiện paid bridge + payment path | upsell_primary_clicked | funnel_stage = paid_offer_engaged; offer_interest = career_deep | critical | baseline |
| new_user_career | post-free CTA secondary | Hỏi tiếp hướng đi phù hợp | User muốn tiếp tục hội thoại miễn phí ở mức bề mặt | Giữ conversation trong free follow-up ngắn | upsell_secondary_clicked | funnel_stage = free_followup; topic_interest = career | critical | baseline |
| new_user_general | interest rescue | Tình cảm | User chọn interest branch là tình cảm | Lưu interest = love rồi vào intake / tiếp tục hỏi mở | topic_inferred_or_selected | topic_interest = love | critical | baseline |
| new_user_general | interest rescue | Công việc | User chọn interest branch là công việc | Lưu interest = career rồi vào intake / tiếp tục hỏi mở | topic_inferred_or_selected | topic_interest = career | critical | baseline |
| new_user_general | interest rescue | Hướng đi chung | User chọn interest branch là tổng quan / general | Lưu interest = general rồi vào intake / tiếp tục hỏi mở | topic_inferred_or_selected | topic_interest = general | critical | baseline |
| new_user_general | post-opening rescue | Bắt đầu xem cho tôi | User chấp nhận đi vào intake sau khi đã rõ interest | Chuyển sang intake bước đầu | intake_started | funnel_stage = intake_started | critical | baseline |
| new_user_general | post-free CTA primary | Xem sâu phần tôi quan tâm nhất | User muốn mở low-ticket chủ đề sâu map theo interest vừa nêu | Hiện paid bridge + payment path | upsell_primary_clicked | funnel_stage = paid_offer_engaged; offer_interest = mapped_topic_deep | critical | baseline |
| new_user_general | post-free CTA secondary | Nói rõ điều tôi đang phân vân | User muốn hỏi tiếp miễn phí ở mức bề mặt | Giữ free follow-up ngắn | upsell_secondary_clicked | funnel_stage = free_followup | critical | baseline |
| returning_unpaid | returning choice | Xem tiếp phần đang dở | User quay lại phần đang dang dở / dang quan tâm | Route vào phần conversation tiếp theo hoặc paid bridge phù hợp | upsell_primary_clicked | funnel_stage = returning_reengaged | critical | baseline |
| returning_unpaid | returning choice | Xem sâu chủ đề này | User muốn đi vào low-ticket cho chủ đề đang quan tâm | Hiện paid bridge + payment path | upsell_secondary_clicked | funnel_stage = paid_offer_engaged | critical | baseline |
| intake_abandoned_resume | resume choice | Tiếp tục lập lá số | User muốn quay lại đúng bước intake còn thiếu | Resume vào missing-field step | intake_resumed | funnel_stage = intake_resumed | critical | baseline |
| intake_abandoned_resume | resume choice | Sửa thông tin trước khi xem | User muốn chỉnh lại field đã nhập | Mở lại confirm / edit step tương ứng | birthdata_confirmation_requested | funnel_stage = intake_editing | critical | baseline |
| paid_once_repeat | next action | Mở gói tiếp theo phù hợp | User muốn đi tiếp sang next-best paid path | Hiện offer phù hợp + payment path | upsell_primary_clicked | funnel_stage = repeat_paid_offer | critical | baseline |
| paid_once_repeat | next action | Để chuyên gia hỗ trợ tiếp | User muốn human handoff tối thiểu | Mở intent capture / gửi form hỏi ngắn | paid_intent_submitted | funnel_stage = premium_intent_captured | critical | baseline |
| universal_confirm | birthdata confirm | Đúng rồi | User xác nhận birth data đủ chắc để chạy chart | Khóa confirm và cho phép generate chart | birthdata_confirmed | funnel_stage = ready_for_chart | critical | baseline |
| universal_confirm | birthdata confirm | Sửa lại thông tin | User chưa xác nhận, cần chỉnh field trước chart | Quay lại step field mơ hồ tương ứng | birthdata_confirmation_requested | funnel_stage = intake_editing | critical | baseline |
| universal_confirm | calendar confirm | Dương lịch | User xác nhận lịch dương | Lưu calendar_type = solar | birthdata_confirmation_requested | calendar_type = solar | critical | baseline |
| universal_confirm | calendar confirm | Âm lịch | User xác nhận lịch âm | Lưu calendar_type = lunar | birthdata_confirmation_requested | calendar_type = lunar | critical | baseline |
| universal_confirm | gender confirm | Nam | User xác nhận giới tính nam | Lưu gender = male | birthdata_confirmation_requested | gender = male | critical | baseline |
| universal_confirm | gender confirm | Nữ | User xác nhận giới tính nữ | Lưu gender = female | birthdata_confirmation_requested | gender = female | critical | baseline |
| universal_offer | payment CTA | Mở link thanh toán | User có ý định trả tiền ở release đầu | Mở payment link placeholder / thật | payment_link_clicked | funnel_stage = payment_link_opened | critical | baseline |
| universal_offer | premium intent | Tôi cần hỗ trợ thêm | User có nhu cầu human handoff / premium intent | Ghi nhận intent + chuyển bước expectation-setting tối thiểu | paid_intent_submitted | funnel_stage = premium_intent_captured | critical | baseline |

### B2. Payload có thể để sau, không chặn CP1 baseline
| Flow name | Step name | Label hiển thị | Intent / nghĩa nghiệp vụ | Action mong muốn khi bấm | Event business mong muốn | Segment / funnel-stage update mong muốn | CP1 | Baseline / để sau |
|---|---|---|---|---|---|---|---|---|
| universal_confirm | birth hour helper | Tôi chưa nhớ giờ sinh | User chưa chắc giờ sinh | Hiện copy hướng dẫn nhập gần đúng / tiếp tục confirm mềm | birthdata_confirmation_requested | birth_hour_confidence = low | non-critical | để sau |
| paid_once_repeat | next action helper | Xem chủ đề khác | User muốn đổi chủ đề nhưng chưa chọn chủ đề mới | Mở câu hỏi text-first để lấy chủ đề mới | topic_inferred_or_selected | topic_interest = unknown_new_topic | non-critical | để sau |
| returning_unpaid | returning helper | Xem lại từ đầu | User muốn bỏ ngữ cảnh cũ và vào lại onboarding | Reset soft context rồi route source phù hợp | conversation_started | funnel_stage = restart_requested | non-critical | để sau |

### B3. Ghi chú handoff cho Engineering từ góc nghĩa nghiệp vụ
- `critical + baseline` là nhóm Product có thể handoff ngay cho Engineering để map payload/postback trước
- Label trong tài liệu này là label baseline ở góc nghĩa nghiệp vụ; wording final vẫn thuộc CP3
- `payment link` hiện cho phép placeholder nếu Product chưa có link thật; khi dùng placeholder phải gắn tag `NEED_PRODUCT_FINAL`
- `premium intent` chỉ được expectation-setting tối thiểu; không hứa SLA cụ thể khi owner handoff chưa chốt
- Với các flow text-first, Engineering không nên ép quick replies xuất hiện ngay từ câu đầu; quick replies là rescue/disambiguation hoặc CTA sau free, không thay thế hội thoại mở

NEED_PRODUCT_CONFIRM
1. Xác nhận Product muốn giữ event cho CTA secondary ở `returning_unpaid` là `upsell_secondary_clicked` hay muốn đổi sang event riêng kiểu `returning_topic_selected`; khuyến nghị của Specialist: giữ `upsell_secondary_clicked` ở baseline để không mở thêm event ngoài metric pack đã khóa.
2. Xác nhận nếu payment link thật chưa sẵn sàng ở thời điểm CP1 handoff thì Product sẽ cho dùng label placeholder có tag `NEED_PRODUCT_FINAL`; khuyến nghị: có.
3. Xác nhận Product có muốn giữ quick reply rescue cho `new_user_general` ngay sau 1 lượt hỏi mở nếu user im lặng / trả lời quá mơ hồ; khuyến nghị: có, vì không đổi logic text-first nhưng giúp giảm drop ở general source.
