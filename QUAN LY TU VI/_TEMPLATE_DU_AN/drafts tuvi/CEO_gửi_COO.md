## CEO BRIEF
Từ: CEO
Gửi: COO (chính) + QA (nắm) + Deputy (nắm)
Ngày: 2026-04-08
---

## Dự án: TuVi Bot — Từ MVP Kỹ Thuật sang Hệ Thống Kinh Doanh Hoàn Chỉnh

### Bối cảnh

Hai dự án trước đã đóng: TuVi Bot core (Gate Output 2026-04-07) và Admin Panel cục bộ (Gate Output 2026-04-08). Khách đã nhận bàn giao và gửi brief phản hồi chi tiết 22 mục (`TAI_LIEU_DU_AN/brief_khach_hang_chi_tiet_bot_tuvi_final.txt`).

Nhận xét của khách: sản phẩm hiện tại là **MVP kỹ thuật, chưa phải MVP kinh doanh**. Sản phẩm đã có webhook Messenger, flow nhập dữ liệu sinh, engine tử vi, generate reading, donation CTA và admin local — nhưng thiếu toàn bộ chiều kinh doanh: trải nghiệm, bán hàng, nuôi khách, analytics, vận hành online, bảo mật, quản trị nội dung.

---

### Vision sản phẩm

Khách muốn bot trở thành **trợ lý tử vi cá nhân hóa trên Messenger cho người Việt** — như một ChatGPT trong Messenger nhưng chuyên tử vi. Bot phải:
- Nhớ người dùng, nhận ra người quay lại, phản hồi có ngữ cảnh từ lịch sử
- Là máy lấy khách + máy nuôi khách + máy bán hàng, không phải máy sinh text một lần
- Tạo cảm giác có chiều sâu cá nhân hóa, ấm, hiểu người dùng

Bot **không được** bị cảm giác như: bot spam, tool bói vui sơ sài, bài văn AI dài nhưng rỗng, phần mềm quá kỹ thuật khó hiểu.

Định vị: *"Trợ lý tử vi cá nhân hóa trên Messenger cho người Việt — vừa dễ dùng, vừa đủ sâu, vừa có thể giúp tôi hiểu bản thân, tình cảm, công việc và quyết định sắp tới."*

---

### 4 mục tiêu kinh doanh đồng thời

1. **Lấy lead**: người dùng từ quảng cáo/bài đăng → Messenger → nói chuyện ngay
2. **Tạo niềm tin**: luận giải free đủ đúng, đủ riêng, đủ trúng để người dùng tin
3. **Kiếm tiền**: có cấu trúc offer và đường đi đủ để triển khai ít nhất 4 dòng doanh thu khách mong muốn — bài sâu/chủ đề, dự báo theo thời gian, compatibility, tư vấn người thật; donation chỉ là phụ
4. **Nuôi lại khách**: người cũ quay lại xem vận hạn mới, chủ đề mới, xem cho người thân, xem theo tháng/quý/năm, nhận nội dung tái kích hoạt

---

### TOÀN BỘ YÊU CẦU KHÁCH — COO phải nắm trọn bộ trước khi đề xuất phân kỳ

CEO liệt kê dưới đây **toàn bộ yêu cầu** đã bóc tách từ brief khách. COO căn cứ đây để lập master plan và đề xuất phân kỳ triển khai — CEO **không áp phase cứng**, COO tự đề xuất nhưng phải cover hết.

---

#### A. TRẢI NGHIỆM MESSENGER (brief khách mục 5)

**A1. Lời chào và entry point**
- Lời chào phải ăn khớp với nguồn vào (quảng cáo tình duyên → flow tình duyên, quảng cáo công việc → flow công việc)
- Mỗi chiến dịch quảng cáo có thể đi vào flow riêng (click-to-Messenger ads)
- Sau câu chào: **không hiện nút bấm ngay** — tránh phản cảm. Để khách tương tác tự nhiên, trả lời bằng text trước. Sau đó tùy ngữ cảnh hội thoại, bot mới gợi ý hành động hoặc chủ đề tiếp theo bằng nút bấm khi phù hợp
- Flow khác nhau giữa người mới và người đã từng dùng — người quay lại phải được nhận ra, không hỏi lại từ đầu

**A2. Luồng nhập dữ liệu sinh**
- **Không nhất thiết ưu tiên nút bấm** — bot phải trích xuất thông minh và linh hoạt từ dữ kiện khách đưa bằng text tự nhiên. Ví dụ: khách nói "giữa tháng 6" → bot ước đoán tạm 15/6 rồi hỏi xác nhận lại; khách nói "sinh năm con rồng" → bot ước đoán tạm năm tương ứng rồi hỏi xác nhận; khách nói "khoảng 9h sáng" → bot ước đoán tạm giờ Tỵ rồi hỏi xác nhận. Nút bấm / quick replies chỉ dùng khi thật sự hợp lý (ví dụ: xác nhận giới tính, âm/dương lịch)
- **Xác nhận trước khi lập chart** (KB-2): bot được suy đoán tạm, nhưng trước khi chạy engine phải xác nhận lại các trường mơ hồ ảnh hưởng lớn — ngày sinh, âm/dương lịch, tháng nhuận, giờ sinh, năm sinh, giới tính. Không được giả vờ chắc chắn khi dữ liệu chưa chắc
- Progress indicator rõ (bước X/N, còn thiếu gì, có thể sửa lại bước trước)
- Chỉ hỏi tháng nhuận khi thật sự cần

**A3. Hiển thị kết quả (kết quả A)**
- Kết quả phải **đầy đủ và có chiều sâu** — tương đương mức một người gửi lá số của mình cho ChatGPT kèm câu "bạn thấy lá số của tôi thế nào?" và nhận được bài phân tích nghiêm túc
- Chia thành các khối dễ đọc: tổng quan ngắn, 3 điểm nổi bật, tình duyên, công việc, tiền bạc, điều cần cẩn trọng, gợi ý hành động tiếp — nhưng tổng thể vẫn phải là một bài luận giải trọn vẹn, không cắt cụt

**A4. Sau kết quả A — hội thoại tiếp tục**
- Bot phải **tiếp tục trò chuyện được** như ChatGPT — khách hỏi tiếp về tình duyên, hỏi sâu về công việc, hỏi về người thân, hỏi so sánh với người yêu → bot phải trả lời được dựa trên lá số đã lập, không phải chỉ cho bấm nút rồi hết
- Nút gợi ý hành động tiếp (xem sâu hơn, xem chủ đề khác, gặp chuyên gia, xem lại) có thể hiện khi phù hợp nhưng **không thay thế khả năng hội thoại tự do** — đây là trợ lý cá nhân, không phải menu chọn

**A5. Giọng điệu và tâm lý hội thoại**
- Xuyên suốt hội thoại phải tạo cảm giác bot hiểu người dùng — ấm, cá nhân, nói đúng trọng tâm
- Không phải văn mẫu chung; AI phải tạo cảm giác cá nhân hóa thật, không trả template rồi ghép tên/ngày sinh vào
- Khách nói rõ: *"tạo ra cảm giác bot hiểu tôi"*, *"nội dung phải có cảm giác đúng người, đúng bối cảnh"*

---

#### B. CHẤT LƯỢNG NỘI DUNG LUẬN GIẢI (brief khách mục 6)

**B1. Cá nhân hóa thật**
- Nội dung phải nhắc tới các điểm nổi bật từ lá số cụ thể của người dùng, phân tích theo chủ đề thực tế
- Không chấp nhận kiểu văn bản AI chung chung

**B2. 3 tầng nội dung** (KB-3)
- **Free**: đủ hay để tạo niềm tin nhưng **không nuốt mất lý do mua tiếp** — phải để lại điểm kích thích muốn xem sâu hơn
- **Standard / low-ticket**: sâu theo **1 chủ đề hoặc khoảng thời gian rõ ràng** — đáng trả tiền nhỏ
- **Premium**: khác biệt ở **chiều sâu bối cảnh** hoặc chuyển qua người thật — không phải chỉ dài hơn mà phải sâu hơn

**B3. Không định mệnh hóa**
- Không khẳng định tuyệt đối: "chắc chắn ly hôn", "chắc chắn phá sản", "chắc chắn bệnh", "chắc chắn tai nạn"
- Dùng cách diễn đạt xu hướng, điểm mạnh/yếu, gợi ý lưu ý

**B4. Gói chủ đề rõ ràng**
- Tình duyên và hôn nhân
- Công việc và nghề nghiệp
- Tài lộc và tiền bạc
- Vận hạn năm nay
- 30 ngày tới, 90 ngày tới
- Compatibility với người yêu/bạn đời/đối tác
- Xem cho con cái hoặc người thân

---

#### C. KIẾM TIỀN (brief khách mục 7)

**C1.** Donation giữ lại nhưng **không phải mô hình chính**

**C2. Ít nhất 4 dòng doanh thu:**
- Mở khóa bài đầy đủ / bài sâu theo chủ đề
- Gói dự báo theo thời gian: 30 ngày, 90 ngày, 1 năm
- Gói compatibility: người yêu, vợ/chồng, đối tác, bạn bè
- Gói gặp người thật / đặt lịch tư vấn

**C3. Offer cho người mới**
- Bản đọc đầu tiên giá thấp, ưu đãi lần đầu, mở khóa 1 chủ đề giá nhỏ, combo 2 chủ đề giá tốt hơn

**C4. Đường upsell rõ ngay trong chat**
- Sau free result phải có câu mời mua **tự nhiên**, không ép, có lựa chọn rõ cho bước tiếp
- Ngôn ngữ CTA không sale cứng — Product phải định nghĩa tone mời cho từng bước

**C5. Cơ chế mua lại**
- Người đã mua → dẫn tiếp sang gói tiếp, gói cao hơn, gói theo tháng/năm, gói cho người thân

---

#### D. MARKETING VÀ FUNNEL (brief khách mục 8)

**D1. Hỗ trợ click-to-Messenger ads theo chiến dịch**
- Mỗi chiến dịch quảng cáo có thể đi vào flow riêng theo chủ đề
- **Admin phải có phần cấu hình chiến dịch**: cho phép admin tạo/sửa/bật/tắt từng chiến dịch, điền lời chào tương ứng, chọn flow mặc định, toggle on/off — tất cả từ giao diện admin, không cần deploy

**D2. Attribution nguồn lead**
- Biết người dùng đến từ chiến dịch nào, nhóm quảng cáo nào, bài viết nào, keyword nào, entry point nào

**D3. Phân loại lead tự động**
- Phân nhóm theo: chủ đề quan tâm, trạng thái nhập dữ liệu, đã xem free chưa, đã mua chưa, đã quay lại chưa, tiềm năng mua gói nào

**D4. Follow-up và nurturing** (KB-6)
- Nuôi lại khách bằng: nhắc quay lại, gợi ý chủ đề tiếp, thông báo bài mới / ưu đãi mới
- Xuất dữ liệu để remarketing
- **Phải thiết kế theo khả năng thực tế của nền tảng Messenger** — nurturing và reactivation phải là flow hợp lệ, đo được, dùng được, không phải ý tưởng trên giấy

**D5. Social proof**
- Chỗ để dùng feedback thật, case đúng, ảnh chụp hội thoại mẫu, rating/review nếu có

---

#### E. BACKEND VÀ DỮ LIỆU (brief khách mục 9)

**E1. Hồ sơ người dùng**
- Mỗi người dùng có hồ sơ riêng: thông tin sinh, loại lịch, lịch sử các lần xem, chủ đề đã hỏi, gói đã mua, trạng thái lead

**E2. Nhiều lá số trên 1 tài khoản** (KB-5)
- Xem cho mình + lưu thêm người yêu, vợ/chồng, con, đối tác
- Khi có nhiều hồ sơ, bot phải **hỏi lại ngắn gọn** để xác định đang nói về ai — không được trộn hồ sơ hoặc tự giả định

**E3. Engine lá số deterministic = nguồn sự thật**
- Tính toán cốt lõi là logic ổn định, nhất quán, AI không được bịa chart
- AI chỉ dùng để diễn giải, cá nhân hóa, gợi ý, hỗ trợ bán hàng

**E4. Event log và analytics — 8 event cốt lõi:**
- Bắt đầu hội thoại
- Hoàn thành nhập dữ liệu
- Generate free thành công / thất bại
- Bấm xem sâu hơn
- Bấm link thanh toán / đăng ký / donation
- Mua thành công hoặc bỏ dở
- Quay lại sau 1 / 7 / 30 ngày

**E5. Payment readiness**
- Dù chưa cần tích hợp payment ngay, backend phải sẵn: tạo đơn hàng, ghi nhận trạng thái thanh toán, mở khóa nội dung, log giao dịch, hỗ trợ khuyến mãi / mã giảm giá

**E6. Human handoff readiness**
- Mode gửi lead chất lượng sang nhân sự tư vấn, lưu transcript, đánh dấu lead nóng, đặt lịch / để lại thông tin liên hệ

**E7. Production-ready**
- Webhook chống duplicate
- Session không mất khi người dùng quay lại
- Log lỗi rõ, dễ dò
- Retry hợp lý khi gọi OpenAI
- Không bị treo khi có nhiều người dùng cùng lúc ở mức cơ bản
- Theo dõi chi phí model (tối thiểu log token)
- Dễ debug khi có khách thật

---

#### F. ADMIN VÀ QUẢN TRỊ NỘI DUNG (brief khách mục 10, 18)

**F1. Panel dễ dùng cho người không kỹ thuật**
- Bật/tắt offer, sửa câu chào, sửa CTA, sửa link thanh toán/hỗ trợ, sửa footer, xem health, xem số liệu chính
- Không cần sửa code cho các thay đổi nội dung thường ngày

**F2. Funnel dashboard trong admin**
- Số bắt đầu, số nhập đủ dữ liệu, số free thành công, số bấm sâu hơn, số mua, tỷ lệ conversion theo từng nguồn

**F3. Log hội thoại và lỗi**
- Log hội thoại tóm tắt, trạng thái từng lead, request lỗi, generate lỗi, cảnh báo fallback quá nhiều

**F4. A/B testing**
- Tối thiểu thay thử: lời chào A/B, CTA A/B, cấu trúc bài free A/B, offer đầu vào A/B

**F5. Quản trị nội dung qua giao diện — 9 phần:**
- Lời chào
- Quick replies
- CTA sau free result
- Offer hiện hành
- Disclaimer
- Footer
- Link thanh toán
- Social proof snippets
- Flow reactivation
- Cần xác định rõ: phần nào sửa từ admin, phần nào phải deploy, template nào có version, có cần preview trước publish không

---

#### G. TRUST, PHÁP LÝ VÀ NIỀM TIN (brief khách mục 11)

**G1. Disclaimer bản chất dịch vụ**
- Sản phẩm phải trình bày là công cụ định hướng / tự phản chiếu / tham khảo
- Không được tạo cảm giác thay thế bác sĩ, luật sư, chuyên gia tâm lý
- Hiển thị ít nhất 1 lần trong flow

**G2. Bảo vệ dữ liệu cá nhân cơ bản**
- Không lộ log thô không cần thiết
- Có cơ chế xóa hồ sơ nếu người dùng yêu cầu
- Trình bày minh bạch về dữ liệu

**G3. Guardrail tình huống nhạy cảm**
- Nếu người dùng đề cập bệnh nặng, pháp lý, tự hại, khủng hoảng tinh thần → bot chuyển sang cách nói an toàn, không phán định, gợi ý liên hệ chuyên gia thật

---

#### H. DEPLOY VÀ VẬN HÀNH ONLINE (brief khách mục 15, 21)

**H1. Môi trường online thật** (KB-7, KB-11)
- Không phụ thuộc máy local
- Có domain hoặc subdomain rõ ràng
- Webhook hoạt động ổn định không cần mở terminal thủ công
- **Không dùng ngrok hoặc bất kỳ tunnel tạm bợ nào** cho production
- Khách không ép công ty tự xây platform deploy riêng — nếu dashboard hosting (Railway, Render, Fly.io...) đáp ứng được outcome vận hành thì được dùng

**H2. GUI vận hành**
- Giao diện hoặc quy trình đơn giản để: nhập biến môi trường, kết nối database, kiểm tra webhook, deploy/redeploy/restart
- Không bắt SSH, terminal, chạy lệnh tay mỗi lần sửa nhỏ
- Tác vụ vận hành thường ngày qua admin hoặc dashboard hosting

**H3. Sau setup ban đầu, người vận hành không kỹ thuật phải có thể:**
- Xem bot online hay offline
- Xem lỗi cơ bản
- Sửa cấu hình thường gặp
- Bấm deploy lại / restart
- Xem webhook có nhận event không

**H4. Hệ thống GUI cần có:**
- Giao diện setup ban đầu
- Form nhập biến cấu hình
- Nút kiểm tra kết nối
- Nút deploy / redeploy / restart
- Nút test webhook
- Nút xem health
- Nơi xem log lỗi cơ bản

*Khách chấp nhận: setup hạ tầng lần đầu do team kỹ thuật thực hiện; sau bàn giao, vận hành thường ngày phải tối thiểu phụ thuộc terminal.*

---

#### I. YÊU CẦU PHI CHỨC NĂNG (brief khách mục 16)

- Phản hồi chat thường trong vài giây
- Generate dài phải có thông báo đang xử lý
- Không mất session khi người dùng quay lại
- Duplicate webhook không gửi lặp
- Lỗi log rõ, dễ dò
- Không treo khi nhiều người dùng cơ bản
- Backup dữ liệu định kỳ
- Khôi phục được nếu deploy lỗi
- Restart service không làm hỏng dữ liệu cũ
- Khi lỗi, admin nhìn thấy nguyên nhân cơ bản

---

#### J. BẢO MẬT VÀ QUYỀN TRUY CẬP (brief khách mục 17)

- Admin có đăng nhập
- Phân quyền tối thiểu: xem số liệu, sửa nội dung, vận hành/deploy, xem lead
- Không ai ngoài người có quyền xem dữ liệu khách hàng
- Transcript và dữ liệu sinh không lộ công khai
- Log hành động admin cho các thay đổi quan trọng

---

#### K. DỮ LIỆU VÀ KẾT NỐI NGOÀI (brief khách mục 19)

- Xuất lead ra file
- Xuất đơn hàng / conversion ra file
- Lọc theo chiến dịch, nguồn, trạng thái
- Có đường kết nối sau này với CRM, sheet, công cụ quảng cáo
- Import social proof, content, offer khi cần

---

#### L. RELEASE VÀ XỬ LÝ SỰ CỐ (brief khách mục 20)

- Quy trình update bot không mất dữ liệu
- Rollback nếu bản mới lỗi
- Health check
- Cảnh báo khi webhook chết
- Biết OpenAI, Meta hay database đang lỗi ở đâu
- Nút hoặc quy trình rõ để restart dịch vụ

---

### TIÊU CHÍ NGHIỆM THU CỦA KHÁCH (brief khách mục 14)

Khách sẽ coi sản phẩm đạt khi:
1. Người dùng mới vào Messenger hiểu phải làm gì trong vài giây đầu
2. Tỷ lệ bỏ cuộc khi nhập dữ liệu giảm rõ
3. Bản free (kết quả A) tạo được cảm giác đúng và đáng xem tiếp — khi có đủ dữ liệu phù hợp, có thể kèm đối chiếu quá khứ để tăng độ tin cậy (ví dụ: khách đang đại vận 33–42, bot bổ sung phân tích đại vận 22–32 trước đó để khách tự đối chiếu với thực tế đã qua → chứng minh tính chân thực)
4. Có ít nhất 1 đường upsell rõ và đo được
5. Backend log được funnel cơ bản từ vào bot đến bấm mua
6. Admin nhìn thấy funnel và biết bot rơi ở bước nào
7. Sản phẩm có thể dùng để chạy quảng cáo click-to-Messenger có chủ đích
8. Người dùng có lý do quay lại, không chỉ xem 1 lần

---

### KHÓA BRIEF TỪ PHÍA KHÁCH HÀNG

**Các điểm dưới đây là nguồn sự thật — công ty không được tự suy diễn khác đi. COO, QA, Deputy và mọi agent phải tuân thủ.**

**KB-1. Yêu cầu release đầu tiên:**
Công ty được phép chia release nội bộ, nhưng release đầu tiên **bắt buộc** phải đủ để: bot chạy online thật, có flow Messenger mới, nhập dữ liệu sinh thông minh có xác nhận lại khi cần, kết quả free đủ tốt, ít nhất 1 đường upsell đo được, admin cơ bản, funnel analytics cơ bản, vận hành thường ngày ít phụ thuộc terminal, và trust/safety tối thiểu.

**KB-2. Xác nhận dữ liệu trước khi lập chart:**
Bot được phép suy đoán tạm thời từ text tự nhiên, nhưng **trước khi lập chart cuối cùng phải xác nhận lại các trường mơ hồ ảnh hưởng lớn**: ngày sinh, âm/dương lịch, tháng nhuận, giờ sinh, năm sinh, giới tính. Không được giả vờ chắc chắn khi dữ liệu chưa chắc.

**KB-3. Phân tầng nội dung:**
Free phải đủ hay để tạo niềm tin nhưng **không được nuốt mất lý do mua tiếp**. Low-ticket phải là chủ đề hoặc khoảng thời gian rõ ràng. Premium phải khác biệt ở chiều sâu bối cảnh hoặc chuyển qua người thật.

**KB-4. Bot là trợ lý hội thoại, không phải bot menu:**
Quick replies và CTA chỉ hỗ trợ, **không thay thế** khả năng hỏi tiếp tự do dựa trên ngữ cảnh lá số đã lập.

**KB-5. Nhớ người dùng và quản lý hồ sơ:**
Bot phải nhớ người dùng theo tài khoản Messenger. Khi có nhiều hồ sơ thì phải **hỏi lại ngắn gọn để xác định đang nói về ai**, không được trộn hồ sơ.

**KB-6. Funnel và nurturing phải khả thi trên nền tảng:**
Funnel Messenger phải được thiết kế theo khả năng thực tế của nền tảng. Nurturing và reactivation phải là flow hợp lệ, đo được, dùng được — không phải ý tưởng trên giấy.

**KB-7. Vận hành online, không ép tự xây platform:**
Khách không muốn dùng local hay terminal hằng ngày, nhưng không ép công ty phải tự xây nền tảng deploy riêng nếu dashboard hosting đáp ứng được outcome vận hành.

**KB-8. Bộ chỉ số release đầu:**
Release đầu phải có bộ chỉ số đánh giá rõ để QA và CEO review: completion rate, upsell click, paid intent/conversion, return rate, fallback/error rate, và visibility của funnel trong admin.

**KB-9. Trust/safety bắt buộc từ release đầu:**
Disclaimer, guardrail và bảo vệ dữ liệu là scope bắt buộc ngay từ release đầu, không để sau.

**KB-10. Tự do giải pháp, không lệch outcome:**
Công ty được tự do chọn cách chia phase và giải pháp kỹ thuật, nhưng **không được làm lệch** các outcome khách hàng đã khóa ở trên.

**KB-11. Không dùng ngrok hoặc tunnel tạm bợ:**
Webhook phải chạy trên môi trường online thật, ổn định. Không dùng ngrok hay bất kỳ tunnel tạm bợ nào cho production.

---

### NGUYÊN TẮC CỐT LÕI (không thay đổi)

- Engine lá số deterministic là nguồn sự thật — không để AI bịa chart
- AI chỉ dùng để diễn giải, cá nhân hóa, gợi ý và hỗ trợ bán hàng
- AI phải tạo cảm giác cá nhân hóa thật — không trả template chung rồi ghép tên hoặc ngày sinh vào
- Không lộ transcript hay dữ liệu sinh ra công khai

---

### TÀI LIỆU NGUỒN

- Brief khách hàng chi tiết: `TAI_LIEU_DU_AN/brief_khach_hang_chi_tiet_bot_tuvi_final.txt`
- Codebase hiện tại: `TAI_LIEU_DU_AN/backend/` (FastAPI backend, engine tử vi, Messenger handler, admin Streamlit, prompts, SQL)
- Tiêu chí nghiệm thu khách: brief khách mục 14 (đã trích ở phần TIÊU CHÍ NGHIỆM THU bên trên)

---

### LỆNH CHO COO

1. **Nắm trọn bộ yêu cầu A → L**: CEO đã bóc tách toàn bộ brief khách theo 12 nhóm. COO phải hiểu hết trước khi lên plan.

2. **Lập master plan theo hướng full-scope release bám đủ 12 nhóm A → L.**
   - COO **không được tự động** dùng roadmap gợi ý của khách để cắt sản phẩm thành nhiều release.
   - Nếu COO đánh giá cần cắt release vì timebox / rủi ro / dependency, phải trình rõ trade-off và phương án cắt để **CEO quyết**, không tự chia.
   - **Ràng buộc cứng (KB-1):** dù chia release thế nào, release đầu tiên bắt buộc phải đủ: bot chạy online thật, flow Messenger mới, nhập dữ liệu sinh thông minh có xác nhận, kết quả free đủ tốt, ít nhất 1 đường upsell đo được, admin cơ bản, funnel analytics cơ bản, vận hành ít phụ thuộc terminal, trust/safety tối thiểu.
   - **Bộ chỉ số release đầu (KB-8):** release đầu phải có metric đánh giá rõ: completion rate, upsell click, paid intent/conversion, return rate, fallback/error rate, visibility funnel trong admin — để QA và CEO review được.

3. **Đánh giá codebase hiện tại**: xác định phần nào tái sử dụng, phần nào refactor, phần nào xây mới

4. **Đề xuất deploy platform** với trade-off rõ ràng:
   - Khách muốn: online thật, GUI deploy/restart, không SSH hàng ngày, setup lần đầu do kỹ thuật
   - COO đề xuất platform cụ thể (Railway, Render, Fly.io, VPS + Coolify...) với trade-off chi phí, độ phức tạp, khả năng vận hành không kỹ thuật
   - CEO chọn sau khi có đề xuất

5. **Đánh giá schema database**: hiện tại schema đơn giản (sessions, readings). Cần thêm: hồ sơ người dùng, lịch sử hội thoại, funnel events, lead classification, attribution, payment readiness, multi-profile. COO đánh giá mở rộng hay thiết kế lại — phải không mất dữ liệu cũ.

6. **Phân loại lane**: scope bao gồm cả Messenger UX, tone/tâm lý, CTA copy, nội dung luận giải, funnel design, marketing logic, admin, deploy, backend. COO phân rõ: phần nào Product, phần nào Engineering, phần nào cả hai.

7. **Marketing Specialist (thuộc Product) — CEO chấp thuận chủ trương kích hoạt ngay trong brief này.**
   - Dự án có tỷ trọng marketing nặng: click-to-Messenger ads, attribution, lead classification, funnel conversion, CTA tone, nurturing flow, social proof, A/B test.
   - CEO đánh giá Product hiện tại không đủ domain marketing để tự xử lý toàn bộ.
   - CEO chấp thuận chủ trương kích hoạt Marketing Specialist ngay trong brief này.
   - COO có trách nhiệm hoàn tất FORM ĐỀ XUẤT SPECIALIST và prompt định nghĩa specialist theo đúng manual để triển khai ngay trong Phase 1.
   - Product sẽ trực tiếp quản lý Marketing Specialist sau khi hồ sơ kích hoạt được hoàn tất đúng quy trình.

8. **Soạn master plan** bao gồm: phase/sprint phân kỳ, lane phân công, task, acceptance criteria từng hạng mục, timebox. Gửi master plan cho QA + Deputy nắm trước Gate Plan.

---

### LƯU Ý TỪ CEO

- Đây là dự án tạo doanh thu thật cho khách — chất lượng UX, tâm lý hội thoại và độ ổn định production quan trọng ngang nhau
- **Phần KHÓA BRIEF (KB-1 → KB-11) là ràng buộc cứng** — COO, QA, Deputy và mọi agent phải tuân thủ, không được suy diễn khác đi
- COO phải đề xuất timebox thực tế, không overpromise — nếu cần cắt release, phải trình CEO quyết (xem mục 2 Lệnh cho COO)
- Trust/safety (nhóm G, KB-9) là scope bắt buộc ngay từ release đầu, không phải "để sau" — COO phân bổ: disclaimer + guardrail là bài Product, bảo vệ dữ liệu là bài Engineering
- Hồ sơ người dùng + lịch sử hội thoại (nhóm E1) là nền tảng cho nuôi khách và upsell — COO đánh giá nên có từ kỳ nào, ảnh hưởng dependency ra sao
- Công ty được tự do chọn giải pháp kỹ thuật nhưng **không được làm lệch các outcome khách đã khóa** (KB-10)
- Brief gốc đầy đủ tại: `TAI_LIEU_DU_AN/brief_khach_hang_chi_tiet_bot_tuvi_final.txt`
