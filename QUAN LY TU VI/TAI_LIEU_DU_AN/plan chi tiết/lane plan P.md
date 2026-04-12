## PRODUCT LANE PLAN
Từ: Product
Gửi: COO
Ngày: 2026-04-10
Phase: Phase 1
---
1. Vấn đề đang giải

Dự án hiện vẫn là MVP kỹ thuật, chưa phải MVP kinh doanh cho Messenger. Lane Product cần chuyển bot từ flow hỏi-thông-tin-rồi-trả-text sang sản phẩm có khả năng:
- đón đúng ý định theo source vào bot
- intake dữ liệu sinh thông minh nhưng có xác nhận trước khi lập chart
- tạo free result đủ trust nhưng không nuốt mất lý do mua tiếp
- giữ được cảm giác trợ lý hội thoại, không biến bot thành menu
- có ít nhất 1 đường upsell đo được
- có trust/safety tối thiểu ngay từ release đầu
- có logic admin governance đủ để vận hành content thường ngày mà không phải sửa code
- có metric pack đủ rõ để COO/QA/CEO review release đầu theo đúng outcome đã khóa

2. Người dùng / đối tượng

Đối tượng ưu tiên của release đầu:
- người dùng mới vào Messenger từ click-to-Messenger ads hoặc bài post với 3 source launch:
  - love
  - career
  - organic_general
- người dùng quay lại nhưng chưa mua
- người dùng đã bỏ dở intake
- người dùng đã mua 1 lần và quay lại

Người dùng nội bộ vận hành:
- operator/admin không kỹ thuật cần sửa content vận hành thường ngày qua admin
- operator follow-up lead premium/handoff ở mức tối thiểu
- owner campaign cần bật/tắt campaign, gán greeting tương ứng, và chọn flow mặc định từ admin

3. Phạm vi MVP

Phạm vi lane Product của release đầu:
- khóa 3 source launch:
  - love
  - career
  - organic_general
- không mở campaign riêng cho time_window; time_window chỉ là nhánh interest trong general
- khóa 6 flow tối thiểu:
  - new_user_love
  - new_user_career
  - new_user_general
  - returning_unpaid
  - intake_abandoned_resume
  - paid_once_repeat
- intake text-first với suy đoán tạm từ text tự nhiên nhưng bắt buộc xác nhận field mơ hồ ảnh hưởng lớn trước chart
- free result release đầu vẫn là 1 bài luận giải trọn vẹn, không phải bài chỉ nói 1 lát chủ đề
- offer entry duy nhất của release đầu:
  - 1 chủ đề sâu
- map offer theo source:
  - love -> gói tình duyên sâu
  - career -> gói công việc sâu
  - organic_general -> gói chủ đề sâu theo mối quan tâm vừa nêu
- paid path mặc định:
  - payment link + manual close
- premium/human handoff:
  - intent capture / chuyển thủ công
  - chưa mở queue engine hoàn chỉnh
- reactivation release đầu chỉ gồm:
  - in-window follow-up
  - return hooks trong hội thoại
  - remarketing-ready
- trust/safety bắt buộc:
  - micro disclaimer
  - privacy/data notice
  - trust bridge trước upsell
  - guardrail wording thay CTA bán hàng trong tình huống nhạy cảm
- admin governance cho static content + campaign config cơ bản
- A/B scope release đầu:
  - chỉ tối đa 3 test copy-level, chạy tuần tự
  - greeting/opening angle
  - trust bridge copy
  - primary upsell CTA

Ngoài phạm vi lane Product release đầu:
- campaign riêng cho time_window
- booking flow premium hoàn chỉnh
- queue engine đầy đủ cho handoff
- preview runtime cho dynamic free result
- automation outside-window làm trụ chính
- multi-profile như trụ UX chính
- A/B test logic-level hoặc entitlement-level

4. User flow chính

A. new_user_love
- greeting text nối mạch với source tình duyên, không mở bằng menu nút
- hỏi pain point tình cảm bằng 1 câu ngắn
- sau khi có tín hiệu từ user mới gợi ý hướng tiếp theo nếu cần
- mời vào intake và chốt vài thông tin để nhìn đúng hơn
- xác nhận field mơ hồ trước chart
- trả free result trọn vẹn, trong đó phần tình duyên được nhấn là campaign-intent slice
- trust bridge
- CTA chính: mở phần tình duyên sâu
- CTA phụ: hỏi tiếp điều bạn lo nhất

B. new_user_career
- greeting text nối mạch với source công việc
- hỏi bận tâm chính: đổi việc / thăng tiến / tiền bạc
- mời vào intake
- xác nhận field mơ hồ trước chart
- trả free result trọn vẹn, trong đó phần công việc được nhấn là campaign-intent slice
- trust bridge
- CTA chính: mở phần công việc sâu
- CTA phụ: hỏi tiếp hướng đi phù hợp

C. new_user_general
- greeting text tổng quan cá nhân hóa nhẹ
- hỏi user muốn hiểu tình cảm, công việc hay hướng đi chung
- nếu user tự nêu 30/90 ngày hoặc năm nay thì lưu time_window là interest branch, không mở flow campaign riêng
- mời vào intake
- xác nhận field mơ hồ trước chart
- trả free result trọn vẹn rồi bridge sang chủ đề sâu
- CTA chính: xem sâu phần bạn đang quan tâm nhất
- CTA phụ: xem nhịp 30–90 ngày tới

D. returning_unpaid
- nhận diện user cũ và nhắc rất ngắn đã xem gì trước đó
- không hỏi lại từ đầu nếu active profile và chart còn hợp lệ
- hỏi tiếp lần này muốn đào sâu chuyện nào
- nếu đổi hồ sơ hoặc dữ liệu mơ hồ mới quay lại intake xác nhận
- CTA chính: đi tiếp phần còn dang dở
- CTA phụ: xem sâu chủ đề này

E. intake_abandoned_resume
- nhắc ngắn còn thiếu field nào
- cho user tiếp tục đúng bước dở
- xác nhận lại nếu field mơ hồ
- đủ dữ liệu thì chạy free result ngay
- CTA chính: tiếp tục lập lá số
- CTA phụ: sửa thông tin trước khi xem

F. paid_once_repeat
- nhận diện paid status
- hỏi muốn đào sâu chủ đề khác, nhịp thời gian, hay người thật hỗ trợ
- nếu cần ngữ cảnh mới thì hỏi ngắn
- show next-best-offer hoặc premium intent capture
- CTA chính: mở gói tiếp theo phù hợp
- CTA phụ: để chuyên gia hỗ trợ tiếp

4A. Cấu trúc free result release đầu

Free result release đầu phải là 1 bài luận giải trọn vẹn với baseline sections tối thiểu luôn có:
1. mở bài / tổng quan ngắn cá nhân hóa
2. 3 điểm nổi bật
3. tình cảm ở mức đủ trust
4. công việc / sự nghiệp ở mức đủ trust
5. tài lộc / nhịp tài chính ở mức đủ trust
6. điều cần cẩn trọng
7. gợi ý hành động tiếp / điều nên lưu ý tiếp theo

Cách đặt campaign-intent slice:
- không thay thế cấu trúc bài
- được đặt như phần nhấn mạnh chính trong bài, thường nằm ở:
  - love -> nhấn sâu hơn ở phần tình cảm + trust bridge
  - career -> nhấn sâu hơn ở phần công việc + trust bridge
  - organic_general -> nhấn theo mối quan tâm user vừa nêu
- nghĩa là free result vẫn đủ cảm giác “đọc lá số tổng thể”, nhưng có một lát nhấn đúng pain point đầu vào để tăng trust và kéo upsell tự nhiên

Ranh giới free vs paid:
- free phải chạm đủ trust, nhưng không trả full timeline cụ thể, phân tích nhiều lớp cho bối cảnh đời thực, so sánh lựa chọn, kế hoạch 30/90 ngày chi tiết, compatibility đủ sâu, hoặc deep dive hoàn chỉnh cho 1 chủ đề
- follow-up miễn phí vẫn được phép để giữ cảm giác trợ lý hội thoại, nhưng chỉ ở mức giải thích bề mặt ngắn; khi user kéo sang timeline cụ thể, nhiều lớp, hoặc bối cảnh quyết định thật thì phải bridge sang paid/premium

5. Input/output chính của sản phẩm

Input sản phẩm:
- source/campaign/entry point hiện tại
- lịch sử hội thoại và trạng thái user
- birth data do user cung cấp bằng text tự nhiên hoặc qua quick replies hỗ trợ
- field xác nhận cuối trước chart
- active profile hiện tại
- topic interest
- funnel stage
- paid status / handoff intent
- static content blocks từ admin:
  - greeting
  - quick replies labels/copy
  - CTA copy
  - offer label
  - disclaimer
  - footer
  - payment link label/url
  - social proof
  - privacy notice
  - reactivation copy
  - campaign config cơ bản

Output sản phẩm:
- opening hội thoại theo source
- intake UX với xác nhận KB-2
- free result trọn vẹn theo baseline sections
- trust bridge trước upsell
- CTA chính + CTA phụ đúng ngữ cảnh
- premium intent capture nếu phù hợp
- event/business semantics thống nhất cho dashboard:
  - conversation_started
  - source_identified
  - topic_inferred_or_selected
  - intake_started
  - intake_resumed
  - birthdata_confirmation_requested
  - birthdata_confirmed
  - free_generated_success
  - free_generated_failed
  - free_result_sent
  - upsell_offer_shown
  - upsell_primary_clicked
  - upsell_secondary_clicked
  - payment_link_clicked
  - paid_intent_submitted
  - manual_paid_marked
  - return_1d
  - return_7d
  - return_30d
  - guardrail_triggered
  - fallback_response_sent

5A. Metric pack release đầu — business semantics

1. completion rate
- business meaning: tỷ lệ user vào intake và đi đến mốc hoàn tất đủ dữ liệu để bot có thể tiếp tục an toàn
- admin release đầu hiển thị 2 lớp:
  - intake_completion_rate = birthdata_confirmed / intake_started
  - free_delivery_rate = free_generated_success / intake_started
- lý do: tách rõ “đã chốt dữ liệu” và “đã giao free result”

2. upsell click
- business meaning: tỷ lệ user đã được show offer và có hành động click CTA mua tiếp
- metric:
  - upsell_click_rate = upsell_primary_clicked / upsell_offer_shown
- metric phụ:
  - secondary_engagement_rate = upsell_secondary_clicked / upsell_offer_shown

3. paid intent / conversion
- business meaning:
  - paid intent = user đã sang bước có ý định mua thật
  - conversion = lead đã được đánh dấu paid thành công theo cơ chế release đầu
- metric:
  - paid_intent_rate = paid_intent_submitted / free_result_sent
  - paid_conversion_rate = manual_paid_marked / paid_intent_submitted
- ghi chú semantics:
  - release đầu là manual-paid mapped, không phải gateway-confirmed auto payment

4. return rate
- business meaning: tỷ lệ user quay lại sau khi đã được giao free result hoặc sau nhịp mua/hỏi tiếp
- metric tối thiểu:
  - return_7d_rate = return_7d / free_result_sent
  - return_30d_rate = return_30d / free_result_sent

5. fallback/error rate
- business meaning: tỷ lệ hội thoại rơi vào lỗi generate hoặc fallback UX/content thay vì đi đúng luồng giá trị
- metric:
  - fallback_error_rate = (free_generated_failed + fallback_response_sent + guardrail_triggered) / conversation_started
- ghi chú:
  - guardrail là một loại fallback an toàn, không phải bug kỹ thuật, nhưng vẫn phải hiện trong metric pack để QA/CEO nhìn thấy tỷ lệ bot phải rời luồng bình thường

6. visibility funnel trong admin
- business meaning: admin nhìn được các mốc chính của funnel theo source/campaign và biết user rơi ở đâu
- tối thiểu phải thấy:
  - conversation_started
  - intake_started
  - birthdata_confirmed
  - free_generated_success
  - upsell_offer_shown
  - upsell_primary_clicked
  - paid_intent_submitted
  - manual_paid_marked
  - return_7d / return_30d
  - free_generated_failed / fallback_response_sent / guardrail_triggered
- breakdown tối thiểu:
  - theo source/campaign
  - theo funnel stage
  - theo offer chính

5B. Định nghĩa fallback từ góc UX/content

Một hội thoại bị coi là fallback về mặt UX/content khi rơi vào một trong các nhóm sau:
1. bot không xác định được ý định đủ rõ sau số lượt hỏi mở cho phép và phải trả lời bằng mẫu an toàn/chung để kéo user về flow
2. bot không trích xuất hoặc không chốt được birth data đủ chắc sau các lượt confirm hợp lý và phải chuyển sang mẫu hướng dẫn nhập lại/rút gọn
3. bot không tạo được free result do lỗi generate hoặc lỗi route và phải trả về mẫu xin lỗi / thử lại / chuyển hướng
4. user hỏi ngoài scope hiện tại của release đầu và bot phải trả lời bằng mẫu giới hạn năng lực thay vì tiếp tục flow giá trị bình thường
5. bot chạm tình huống nhạy cảm và phải chuyển sang guardrail wording thay CTA thường

Không coi là fallback:
- user chủ động không mua
- user chọn CTA phụ để hỏi tiếp
- user quay lại ở flow returning bình thường
- user bị route sang paid/premium đúng rule free-vs-paid

6. Definition of done

Lane Product được coi là xong ở Phase 1 khi:
- phạm vi release đầu của lane Product đã được khóa rõ, không mơ hồ và không vượt scope
- 6 flow tối thiểu đã được mô tả đủ để Engineering code routing mà không phải suy đoán scope sản phẩm
- cấu trúc free result đã được khóa là 1 bài luận giải trọn vẹn, không bị hiểu thành bài chỉ nói 1 chủ đề
- ranh giới free vs paid đã được khóa rõ
- trust/safety surface đã được xác định vị trí hiển thị và nguyên tắc wording
- admin governance matrix đã được chốt đủ cho release đầu
- metric pack business semantics đã được khóa đủ để COO/QA/CEO review release đầu
- fallback definition đã được Product khóa đủ để Engineering map vào event/log chuẩn
- semantic/event business layer đã được Product và Engineering thống nhất
- dependency sang Engineering đã ghi đủ để COO tổng hợp master plan
- timebox và critical path của lane Product đã được chuẩn hóa đủ để COO tổng hợp master plan
- không còn mâu thuẫn kế hoạch ở vòng P↔E

7. Acceptance criteria

7.1. Entry/source scope
- Pass khi lane plan chỉ giữ đúng 3 source launch đầu: love, career, organic_general; time_window chỉ là interest branch trong general
- Fail khi mở thêm campaign riêng ngoài 3 source này trong release đầu

7.2. Flow coverage
- Pass khi có đủ 6 flow tối thiểu và mỗi flow có opening intent, intake path, trust point, CTA chính, CTA phụ, exit/transition hợp lý
- Fail khi thiếu bất kỳ flow tối thiểu nào hoặc flow chỉ mô tả chung chung

7.3. Intake confirmation
- Pass khi lane plan khóa rõ: bot được suy đoán tạm từ text tự nhiên nhưng không được generate chart nếu field lớn còn mơ hồ/chưa confirm
- Fail khi intake cho phép build chart mà không có bước confirm field ảnh hưởng lớn

7.4. Free result structure
- Pass khi free result được khóa là 1 bài luận giải trọn vẹn với baseline sections tối thiểu luôn có:
  - tổng quan ngắn
  - 3 điểm nổi bật
  - tình cảm
  - công việc/sự nghiệp
  - tài lộc/nhịp tài chính
  - điều cần cẩn trọng
  - gợi ý hành động tiếp
  và campaign-intent slice chỉ là phần nhấn bên trong bài, không thay thế cấu trúc bài
- Fail khi free result bị hiểu thành bài chỉ nói 1 chủ đề hoặc chỉ có 1 slice theo campaign

7.5. Free vs paid boundary
- Pass khi free đủ trust nhưng không lấn sang timeline cụ thể, phân tích nhiều lớp cho bối cảnh thật, so sánh lựa chọn, 30/90 ngày chi tiết, compatibility đủ sâu hoặc deep dive hoàn chỉnh
- Fail khi free quá nông không đủ trust hoặc quá sâu làm mất lý do mua tiếp

7.6. Offer entry
- Pass khi release đầu chỉ có 1 entry offer shape là 1 chủ đề sâu, map đúng theo source
- Fail khi show song song nhiều entry offer ngang hàng ở lần mời mua đầu tiên

7.7. Returning flows
- Pass khi returning_unpaid, intake_abandoned_resume, paid_once_repeat đều ưu tiên continuity, không hỏi lại từ đầu nếu profile/chart còn hợp lệ
- Fail khi flow returning quay user về opening/intake từ đầu không cần thiết

7.8. Trust/safety
- Pass khi có đủ 4 surface bắt buộc:
  - micro disclaimer
  - privacy/data notice
  - trust bridge
  - guardrail wording
- Fail khi thiếu bất kỳ surface nào hoặc guardrail vẫn giữ CTA bán hàng bình thường trong tình huống nhạy cảm

7.9. Admin governance
- Pass khi release đầu có ma trận rõ cho từng nhóm:
  - greeting
  - quick replies
  - CTA sau free result
  - offer hiện hành
  - disclaimer
  - footer
  - link thanh toán
  - social proof snippets
  - flow reactivation
  - campaign config cơ bản
  với phân loại rõ admin-editable hay deploy-only, có/không preview, có/không version
- Fail khi còn mục mơ hồ không rõ chỉnh qua admin hay phải deploy

7.10. Event/business semantics
- Pass khi Product và Engineering đã thống nhất canonical business/technical semantics ở release đầu:
  - conversation_started
  - free_result_sent
  - manual_paid_marked
  - fallback_response_sent
- Fail khi semantic còn mâu thuẫn khiến dashboard/spec/test có thể lệch nhau

7.11. Human handoff
- Pass khi release đầu chỉ yêu cầu minimal handoff surface: premium intent, owner, status, transcript/note tối thiểu
- Fail khi lane plan ngầm mở queue engine hoàn chỉnh

7.12. Metric pack
- Pass khi lane plan định nghĩa rõ business meaning và mốc funnel cho:
  - completion rate
  - upsell click
  - paid intent/conversion
  - return rate
  - fallback/error rate
  - visibility funnel trong admin
- Fail khi metric pack chỉ còn là danh sách tên chỉ số mà không có meaning/mốc đo

7.13. Completion metrics
- Pass khi admin release đầu dự kiến nhìn song song 2 chỉ số:
  - intake_completion_rate = birthdata_confirmed / intake_started
  - free_delivery_rate = free_generated_success / intake_started
- Fail khi completion metric còn mơ hồ, Product và Engineering không thống nhất mốc đo

7.14. Fallback definition
- Pass khi fallback từ góc UX/content được khóa rõ thành các nhóm cụ thể để Engineering map log/event
- Fail khi fallback chỉ được hiểu như “lỗi kỹ thuật” và bỏ sót fallback hội thoại/nội dung

8. Dependency

8.1. Dependency cần Engineering xử lý
- state persistence 3 lớp:
  - user_profiles
  - messenger_sessions
  - conversation_history
- source attribution capture:
  - first source
  - latest source
  - current entry point
- confirmation flow là lát riêng của conversation_bridge
- event firing architecture và dashboard data model
- preview/publish support cho static content blocks
- payment/manual-close logging:
  - payment_link_clicked
  - paid_intent_submitted
  - manual_paid_marked
- minimal human handoff surface
- guardrail route ở lớp policy hiện có
- schema chuẩn bị cho profile_entities + active_profile_id
- admin metrics visibility theo source/campaign
- campaign config cơ bản trong admin:
  - create/edit/on-off
  - gắn greeting tương ứng
  - chọn flow mặc định trong baseline release đầu
- quick replies payload routing ở lớp kỹ thuật

8.2. Dependency Product phải bàn giao ở Phase 2 cho Engineering/Builder
- bảng payload spec cho quick replies / postbacks theo từng flow
- gói seed content mặc định cho static content blocks trong app_config
- wording final cho returning flows
- wording final cho KB-2 confirmation prompts
- trust wording final
- CTA copy final
- quick replies labels/fallback copy final
- footer final
- social proof snippets thật được phép publish
- campaign labels/default settings final

8.3. Dependency external / vận hành
- social proof asset thật
- owner nhận premium handoff
- SLA follow-up tối thiểu cho premium/human handoff
- payment link thật nếu dùng manual close path ở release đầu

8.4. Critical path của lane Product ảnh hưởng timebox toàn dự án
Các đầu vào dưới đây là critical path vì nếu Product bàn giao muộn, Builder/Engineering sẽ bị chặn ở các phần flow runtime, config runtime hoặc publish-ready content:

- CP1. Payload spec quick replies / postbacks theo từng flow
  - ảnh hưởng trực tiếp tới routing hội thoại, event mapping và wiring các CTA/quick replies
  - phải có đủ cho 6 flow tối thiểu trước khi Builder khóa phần payload/runtime liên quan

- CP2. Seed content mặc định cho `app_config`
  - tối thiểu phải có cho greeting, opening question, CTA sau free, offer label, disclaimer, privacy/data notice, footer, payment link label, reactivation copy
  - nếu thiếu gói seed v1, admin/content surface có thể build khung nhưng không thể smoke test đúng luồng Product

- CP3. Wording final cho confirmation / trust / CTA / footer / social proof / campaign labels
  - ảnh hưởng trực tiếp đến bản publish-ready của release đầu
  - có thể đi sau CP1/CP2 một nhịp ngắn, nhưng phải chốt đủ sớm để không kéo dài vòng tích hợp, smoke test và QA copy

9. Timebox ước lượng

9.1. Kết luận timebox của lane Product
- Product đánh giá timebox hiện tại của lane mình **đủ** để giữ nguyên scope release đầu; không cần đổi scope, không cần mở thêm specialist, không cần mở lại loop P↔E chỉ để khóa timebox.
- Loop hiện tại là loop timebox-only theo yêu cầu COO; các phần scope/flow/acceptance đã giữ nguyên.

9.2. Timebox Phase 1 còn lại để chốt plan sạch cho Gate Plan
- Timebox còn lại của lane Product ở Phase 1: **0.5 ngày / 1 loop nội bộ ngắn trong ngày**
- Trạng thái tại thời điểm gửi bản này: **đã dùng xong loop đó để chuẩn hóa timebox + critical path**, không còn yêu cầu Product mở thêm loop nếu COO chấp nhận bản chuẩn hóa này

9.3. Timebox Phase 2 / Release 1 cho phần Product bắt buộc
- Ước lượng lane Product bắt buộc cho Release 1: **7–9 ngày làm việc**
- Đây là lane timebox thực tế cho Product, không bao gồm thời gian code-only của Engineering
- Timebox này giả định:
  - baseline scope release đầu giữ nguyên như đã khóa
  - không mở thêm source/campaign mới
  - không nâng human handoff lên queue engine
  - social proof dùng asset có sẵn hoặc placeholder được Product chấp thuận cho sprint đầu
  - payload spec và seed content được ưu tiên front-load ngay đầu Phase 2

9.4. Chia sprint/nhịp nội bộ tối đa 3 nhịp

- Sprint/nhịp 1: **2–3 ngày làm việc**
  - khóa payload spec quick replies/postbacks cho 6 flow tối thiểu
  - khóa seed content v1 cho `app_config`
  - khóa wording baseline cho KB-2 confirmation, trust bridge, CTA chính/phụ, footer, campaign labels
  - đây là nhịp **critical path mạnh nhất**

- Sprint/nhịp 2: **3 ngày làm việc**
  - hoàn thiện content package publish-ready cho greeting/opening/CTA/offer/disclaimer/privacy/reactivation
  - hoàn thiện social proof placement + snippet rule
  - hoàn thiện campaign config defaults và fallback copy
  - review integrated flow với Engineering trên staging/build nội bộ

- Sprint/nhịp 3: **2–3 ngày làm việc, chỉ dùng khi cần**
  - chỉnh copy/fallback/trust wording theo smoke test, staging test hoặc QA/content feedback
  - khóa bản publish-ready cuối cho release đầu
  - không mở scope mới; chỉ hấp thụ fix và polish trong phạm vi đã khóa

9.5. Điều phối critical path so với toàn dự án
- Product không chặn Engineering ở các nhóm Foundation / Data / Webhook / Auth / Admin khung.
- Product **có thể chặn** phần Builder/Engineering liên quan runtime UX/content nếu CP1–CP3 bàn giao muộn.
- Vì vậy Product đề xuất nguyên tắc điều phối:
  - CP1 + CP2 phải được bàn giao trong nhịp 1
  - CP3 phải được khóa chậm nhất trong đầu nhịp 2
  - phần polish/content không-critical phải đi sau, không được kéo lùi baseline build

9.6. Phần nào không phải critical path của lane Product
- tinh chỉnh social proof cuối nếu chưa có asset thật
- tối ưu microcopy vòng sau khi đã có baseline publish-ready
- mở rộng A/B beyond 3 test copy-level đã khóa
- time_window campaign riêng, compatibility sâu, membership, outside-window automation

9.7. Kết luận timebox gửi COO
- Lane Product hiện **đã đủ điều kiện gửi lại COO** ở dạng timebox+critical-path chuẩn hóa.
- Không cần mở thêm loop với Engineering hoặc Specialist chỉ để chỉnh phần timebox này.
