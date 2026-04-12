## SPECIALIST REPORT
Từ: Marketing/Funnel Specialist
Gửi: Product
Ngày: 2026-04-10
Phase: Phase 2 execution round 2
---
A. Seed content v1 cho app_config

Ghi chú chung:
- Đây là seed baseline phục vụ CP2 và smoke test; không phải wording final CP3.
- Placeholder được đánh dấu rõ `NEED_PRODUCT_FINAL` khi chưa có dữ liệu thật.
- Không có social proof block trong vòng này theo chỉ thị Product.

| Block name | Source/flow áp dụng | Text baseline | Placeholder / NEED_PRODUCT_FINAL | CP2 critical |
|---|---|---|---|---|
| greeting_love | source `love` / `new_user_love` | “Mình ở đây để nhìn chuyện tình cảm của bạn theo cách rõ và dễ hiểu hơn, không phán cứng.” | Không | Có |
| greeting_career | source `career` / `new_user_career` | “Mình sẽ giúp bạn nhìn rõ hơn nhịp công việc, hướng đi và điều đang làm bạn lăn tăn lúc này.” | Không | Có |
| greeting_general | source `organic_general` / `new_user_general` | “Mình có thể nhìn cùng bạn bức tranh tổng thể trước, rồi đi sâu vào điều bạn đang quan tâm nhất.” | Không | Có |
| opening_question_love | `new_user_love` | “Hiện tại chuyện tình cảm làm bạn bận tâm nhất là điều gì?” | Không | Có |
| opening_question_career | `new_user_career` | “Lúc này bạn đang bận tâm nhất về công việc, hướng đi hay tiền bạc?” | Không | Có |
| opening_question_general | `new_user_general` | “Bạn muốn mình nhìn trước về tình cảm, công việc hay bức tranh chung của bạn?” | Không | Có |
| opening_question_returning_unpaid | `returning_unpaid` | “Lần trước mình đã xem tổng quan cho bạn rồi — lần này bạn muốn đào sâu phần nào nhất?” | Không | Có |
| opening_question_intake_resume | `intake_abandoned_resume` | “Bạn còn thiếu một vài thông tin để mình xem chính xác hơn — mình đi tiếp từ bước đang dở nhé?” | Không | Có |
| opening_question_paid_repeat | `paid_once_repeat` | “Bạn muốn đào sâu chủ đề khác, đi tiếp phần thời điểm này hay để mình ghi nhận nhu cầu gặp chuyên gia?” | Không | Không |
| cta_after_free_primary_love | `new_user_love` sau free | “Xem sâu tình duyên” | Không | Có |
| cta_after_free_secondary_love | `new_user_love` sau free | “Hỏi tiếp điều tôi lo nhất” | Không | Có |
| cta_after_free_primary_career | `new_user_career` sau free | “Xem sâu công việc” | Không | Có |
| cta_after_free_secondary_career | `new_user_career` sau free | “Hỏi tiếp hướng đi phù hợp” | Không | Có |
| cta_after_free_primary_general | `new_user_general` sau free | “Xem sâu phần tôi quan tâm nhất” | Không | Có |
| cta_after_free_secondary_general | `new_user_general` sau free | “Nói rõ điều tôi đang phân vân” | Không | Có |
| cta_after_free_primary_returning | `returning_unpaid` | “Xem tiếp phần đang dở” | Không | Có |
| cta_after_free_secondary_returning | `returning_unpaid` | “Xem sâu chủ đề này” | Không | Có |
| cta_after_free_primary_paid_repeat | `paid_once_repeat` | “Mở gói tiếp theo phù hợp” | Không | Không |
| cta_after_free_secondary_paid_repeat | `paid_once_repeat` | “Để chuyên gia hỗ trợ tiếp” | Không | Không |
| offer_label_love_deep | map cho source/flow love | “Gói tình duyên sâu” | Không | Có |
| offer_label_career_deep | map cho source/flow career | “Gói công việc sâu” | Không | Có |
| offer_label_general_deep | map cho source/flow general theo interest | “Gói xem sâu theo điều bạn đang quan tâm” | Không | Có |
| disclaimer_snippet_intake | tất cả flow có intake / trước hoặc tại lúc bắt đầu intake | “Thông tin này giúp mình nhìn lá số sát hơn. Nội dung mang tính tham khảo định hướng, không thay thế tư vấn y tế, pháp lý hay tài chính chuyên môn.” | Không | Có |
| privacy_notice_snippet | tất cả flow thu dữ liệu sinh | “Mình dùng dữ liệu bạn cung cấp để lập lá số, trả kết quả và ghi nhớ ngữ cảnh cho lần quay lại. Bạn có thể yêu cầu sửa lại thông tin trước khi xem.” | Không | Có |
| footer_baseline | tất cả flow sau free / sau CTA | “Nếu bạn muốn, mình có thể đi tiếp phần đang cần nhất thay vì nói lan man.” | Không | Có |
| payment_link_label | tất cả flow mở paid path | “Mở link thanh toán” | Có — `NEED_PRODUCT_FINAL` nếu chưa có link thật | Có |
| reactivation_in_window_resume | `intake_abandoned_resume` / in-window | “Mình đang giữ chỗ bước bạn vừa dừng. Nếu muốn, mình đi tiếp luôn từ đây.” | Không | Có |
| reactivation_in_window_returning | `returning_unpaid` / in-window | “Mình vẫn nhớ phần bạn đang quan tâm. Bạn muốn đi tiếp chỗ cũ hay đào sâu thêm?” | Không | Có |
| reactivation_in_window_paid_repeat | `paid_once_repeat` / in-window | “Nếu bạn muốn đi tiếp, mình có thể mở phần phù hợp tiếp theo hoặc ghi nhận nhu cầu hỗ trợ thêm.” | Không | Không |
| campaign_label_love | campaign/source baseline | “Tình duyên” | Không | Có |
| campaign_label_career | campaign/source baseline | “Công việc” | Không | Có |
| campaign_label_organic_general | campaign/source baseline | “Tổng quan” | Không | Có |

B. CTA / trust bridge baseline pack

### B1. Tone principles dùng chung
- Ấm, bình tĩnh, cá nhân hóa vừa đủ; không sale cứng.
- Nói theo hướng “mình nhìn cùng bạn”, tránh phán tuyệt đối hay định mệnh hóa.
- CTA phải nghe như bước tiếp theo tự nhiên của hội thoại, không như ép mua.
- Trust bridge phải nối từ điều bot vừa nhìn thấy sang lý do vì sao gói sâu hơn có giá trị.
- Free follow-up vẫn cho phép ở mức bề mặt để giữ cảm giác trợ lý; nhưng không đi sang timeline cụ thể, phân tích nhiều lớp hay so sánh lựa chọn đời thực.

### B2. Trust bridge baseline theo flow
| Flow | Trust bridge baseline |
|---|---|
| new_user_love | “Phần mình vừa nói mới là lớp tổng quan để bạn nhìn đúng nhịp cảm xúc và điểm dễ vướng. Nếu bạn muốn, mình có thể đi sâu riêng chuyện tình cảm để nhìn rõ hơn điều đang lặp lại và cách ứng xử phù hợp hơn.” |
| new_user_career | “Phần vừa rồi giúp bạn thấy nhịp chung về công việc và hướng đi. Nếu cần quyết rõ hơn phần sự nghiệp, mình có thể mở sâu riêng chủ đề này để nhìn kỹ điểm mạnh, điểm nghẽn và hướng ưu tiên.” |
| new_user_general | “Mình đã chạm vào bức tranh tổng thể để bạn có cảm giác đúng người đúng chuyện. Nếu bạn muốn đi thẳng vào phần đang làm bạn băn khoăn nhất, mình có thể mở sâu riêng chủ đề đó.” |
| returning_unpaid | “Lần trước mình đã mở tổng quan cho bạn rồi, nên lần này mình có thể đi nhanh hơn vào phần còn dang dở hoặc phần bạn đang muốn hiểu kỹ hơn.” |
| intake_abandoned_resume | Không dùng trust bridge ở opening. Chỉ dùng sau khi free result đã gửi thành công: “Giờ dữ liệu đã đủ chắc, mình có thể đi tiếp phần bạn cần nhất thay vì dừng ở mức tổng quan.” |
| paid_once_repeat | “Bạn đã có một lớp nhìn trước đó rồi, nên lần này mình không cần quay lại từ đầu. Mình có thể mở tiếp phần phù hợp hơn với nhu cầu hiện tại của bạn.” |

### B3. CTA chính / CTA phụ baseline theo flow
| Flow | CTA chính baseline | CTA phụ baseline |
|---|---|---|
| new_user_love | Xem sâu tình duyên | Hỏi tiếp điều tôi lo nhất |
| new_user_career | Xem sâu công việc | Hỏi tiếp hướng đi phù hợp |
| new_user_general | Xem sâu phần tôi quan tâm nhất | Nói rõ điều tôi đang phân vân |
| returning_unpaid | Xem tiếp phần đang dở | Xem sâu chủ đề này |
| intake_abandoned_resume | Tiếp tục lập lá số | Sửa thông tin trước khi xem |
| paid_once_repeat | Mở gói tiếp theo phù hợp | Để chuyên gia hỗ trợ tiếp |

### B4. Rule dùng CTA thường vs guardrail wording
Dùng CTA thường khi:
- User đang ở flow bình thường, không có tín hiệu nhạy cảm.
- Bot vừa gửi free result hoặc vừa hoàn tất một bước resume/return hợp lệ.
- User hỏi tiếp trong phạm vi có thể bridge tự nhiên sang paid/premium.

Chuyển sang guardrail wording, không dùng CTA bán hàng khi:
- User nói về bệnh tật, tự hại, tai nạn, phá sản chắc chắn, ly hôn chắc chắn hoặc các kết luận cực đoan.
- User đang hoảng loạn, tìm xác nhận tuyệt đối hoặc yêu cầu bot ra quyết định thay.
- User hỏi ngoài phạm vi an toàn mà bot chỉ nên trả lời giới hạn năng lực.

Guardrail wording baseline:
- “Mình không nên kết luận tuyệt đối cho trường hợp này. Nếu bạn muốn, mình có thể giúp bạn nhìn theo hướng điều cần lưu ý và cách bình tĩnh xử lý tiếp.”
- “Phần này cần nhìn cẩn trọng hơn và không nên hiểu theo kiểu chắc chắn xảy ra. Mình có thể cùng bạn tách ra điều nào là xu hướng, điều nào nên kiểm chứng thêm.”

### B5. Rule không sale cứng / không triệt tiêu lý do mua tiếp
- Không dùng từ ép mua như “mua ngay”, “chốt ngay”, “ưu đãi sốc”.
- Không hứa kết quả chắc chắn hoặc biến paid thành “câu trả lời cuối cùng”.
- Free chỉ nên chạm đủ trust: tổng quan, điểm nổi bật, cảm xúc đúng ngữ cảnh, gợi ý bước tiếp.
- Khi user hỏi sâu quá mức free-vs-paid boundary, bridge bằng giá trị của gói sâu hơn thay vì trả lời hết miễn phí.
- CTA phụ phải giữ được nhịp hội thoại nhưng vẫn ở bề mặt; không mở thành deep reading miễn phí trá hình.

C. Governance note v1

### C1. Governance table cho static content blocks baseline
| Nhóm block | Admin-editable / deploy-only | Preview | Version / publish rule | Cho phép placeholder publish? | Usable cho smoke test khi nào | Note publish thật |
|---|---|---|---|---|---|---|
| greeting theo source/campaign | Admin-editable | Có | Draft -> Preview -> Publish; sửa text phải tạo version mới | Có | Khi đủ 3 greeting source và route map đúng source | Publish thật được ngay nếu không trái tone chung |
| opening question | Admin-editable | Có | Draft -> Preview -> Publish; version theo flow | Có | Khi mỗi flow có opening question baseline và hiển thị đúng flow | Publish thật được ngay |
| CTA sau free | Admin-editable | Có | Draft -> Preview -> Publish; version theo flow + CTA slot | Có | Khi CTA primary/secondary render đúng flow và không gãy route | Publish thật được ngay |
| offer label | Admin-editable | Có | Draft -> Preview -> Publish; version theo offer mapping | Có | Khi 3 label baseline map đúng source/interest | Publish thật được ngay |
| disclaimer snippet | Admin-editable | Có | Draft -> Preview -> Publish; thay đổi phải giữ intent safety | Không nên | Khi snippet hiện đúng tại intake/opening point được chọn | Nên publish thật, không để placeholder |
| privacy/data notice snippet | Admin-editable | Có | Draft -> Preview -> Publish; thay đổi phải giữ intent privacy | Không nên | Khi snippet hiện đúng ở bước thu dữ liệu sinh | Nên publish thật, không để placeholder |
| footer | Admin-editable | Có | Draft -> Preview -> Publish; version theo template chung | Có | Khi footer xuất hiện đúng sau free/CTA | Publish thật được ngay |
| payment link label | Admin-editable | Có | Draft -> Preview -> Publish; text và link là 2 trường khác nhau | Có — chỉ label/placeholder, phải gắn `NEED_PRODUCT_FINAL` nếu link chưa final | Smoke test được nếu label render và action route đúng, dù link là placeholder rõ ràng | Publish thật chỉ khi Product final link thật |
| reactivation copy trong window | Admin-editable | Có | Draft -> Preview -> Publish; version theo use-case returning/resume/paid_repeat | Có | Khi copy gọi đúng flow/state trong cửa sổ cho phép | Publish thật được ngay nếu không hứa SLA |
| campaign labels baseline | Admin-editable | Có | Draft -> Preview -> Publish; version theo source list | Không cần | Khi label hiển thị đúng trong admin/config | Publish thật được ngay |

### C2. Rule dùng placeholder
- Chỉ cho placeholder ở block không làm sai sự thật về trải nghiệm cốt lõi.
- `payment link label` có thể publish placeholder cho smoke test nếu gắn rõ `NEED_PRODUCT_FINAL`.
- Không dùng placeholder cho disclaimer hoặc privacy notice vì đây là block trust/safety bắt buộc.
- Không placeholder kiểu giả review, giả feedback, giả SLA, giả asset social proof trong vòng này.

### C3. Rule usable cho smoke test
Một block được coi là usable cho smoke test khi:
1. render đúng flow/source/state đã map
2. không tạo hiểu sai nghiệp vụ
3. không vi phạm trust/safety structure đã khóa
4. nếu là placeholder thì đã được đánh dấu rõ và không giả lập dữ kiện thật
5. Product có thể dùng block đó để test route/config mà không cần wording final CP3

NEED_PRODUCT_CONFIRM
1. Xác nhận Product muốn đặt `footer_baseline` là block chung cho mọi flow sau free, hay chỉ áp dụng cho 3 flow new-user + `returning_unpaid`; khuyến nghị: dùng chung cho mọi flow sau free, trừ `intake_abandoned_resume` trước khi có free result.
2. Xác nhận Product có muốn `opening_question_paid_repeat` được seed luôn ở CP2 dù flow này không ưu tiên bằng `returning_unpaid` và `intake_abandoned_resume`; khuyến nghị: có, nhưng đánh dấu non-critical để không kéo chậm CP2 baseline.
3. Xác nhận vị trí publish mặc định của `disclaimer_snippet_intake`: trước câu hỏi intake đầu tiên hay gắn ngay tại bước bắt đầu thu birth data; khuyến nghị: gắn tại bước bắt đầu thu birth data để bớt làm opening nặng, nhưng vẫn đúng trust/safety.
