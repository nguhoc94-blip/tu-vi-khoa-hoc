## CEO CHỈ THỊ
Từ: CEO
Gửi: COO
Ngày: 2026-04-10
Gate vừa chốt: Gate Plan (TuVi Bot MVP Kinh Doanh — Release 1)
---

**Quyết định: DUYỆT CÓ ĐIỀU KIỆN**

### Căn cứ

- QA Plan Review: **Pass**, không P0, scope bám KB-1/KB-8/KB-9, khả thi kỹ thuật, spec đủ, acceptance criteria đủ, không mâu thuẫn nội bộ
- Deputy Executive Review: đủ điều kiện chốt Gate Plan, khuyến nghị duyệt có điều kiện
- COO Master Plan: release đầu khóa rõ outcome bắt buộc, timebox hợp lý, trade-off chia release trình rõ ràng

### Quyết định về chiến lược release

CEO **chấp thuận** phương án chia release có kiểm soát theo đề xuất COO:

- **Release 1** (bắt buộc): toàn bộ hard scope KB-1/KB-8/KB-9 — bot chạy online thật, flow Messenger mới theo 3 source + 6 flow tối thiểu, intake thông minh có confirm KB-2, free result trọn vẹn, 1 entry offer + 1 đường upsell đo được, admin cơ bản, funnel analytics + metric pack, trust/safety, RBAC/audit, deploy online + rollback/readiness
- **Release sau**: payment tự động, compatibility sâu, queue engine handoff đầy đủ, time_window campaign riêng, outside-window automation, runtime preview, membership/CRM sâu

Lý do: ép full A→L vào 1 release tăng rủi ro trễ và loãng acceptance — Deputy, QA và COO đều đồng ý điểm này. Release 1 đã đủ outcome bắt buộc của khách.

### Điều kiện CEO đặt cho Phase 2

**ĐK-1. Product phải bàn giao đúng nhịp — đây là mốc bắt buộc, không phải khuyến nghị:**
- CP1 (payload spec quick replies/postbacks cho 6 flow) + CP2 (seed content mặc định cho `app_config`): bàn giao trong Nhịp 1
- CP3 (wording final confirmation/trust/CTA/footer/social proof/campaign labels): khóa chậm nhất đầu Nhịp 2
- COO có trách nhiệm **quản nhịp** CP1/CP2/CP3 — nếu Product trượt, COO báo CEO ngay, không chờ cuối nhịp

**ĐK-2. Engineering giữ kỷ luật thi công:**
- `conversation_bridge` phải thi công theo đúng 4 lát đã khóa trong master plan — không gộp, không nhảy lát
- Migration phải additive-only — không phá schema cũ, không mất dữ liệu

**ĐK-3. Bộ chỉ số release đầu phải đo được khi Gate Output:**
- completion rate, upsell click, paid intent/conversion, return rate, fallback/error rate, visibility funnel trong admin
- QA phải trace được từng metric từ event mapping đã khóa

### Lệnh cụ thể cho COO: Mở Phase 2

1. Gửi kế hoạch đã duyệt cho Product và Engineering theo đúng lane owner
2. Engineering mở thi công theo 3 nhịp (Nhịp 1 → Foundation/Data/Webhook/Bridge 1-2; Nhịp 2 → Admin/Bridge 3-4; Nhịp 3 → Ops/Trust/Regression)
3. Product bàn giao CP1+CP2 trong Nhịp 1, khóa CP3 đầu Nhịp 2
4. COO quản nhịp Product delivery — nếu CP trượt, báo CEO trước khi nhịp bị ảnh hưởng kết thúc
5. Marketing Specialist đã được CEO chấp thuận kích hoạt — COO hoàn tất FORM + prompt theo manual, Product quản lý trực tiếp
6. P/E báo COO khi lane hoàn tất; COO tổng hợp gửi QA + Deputy cho Gate Output

### Rủi ro CEO theo dõi

1. Product giao chậm CP1/CP2/CP3 → COO phải báo sớm
2. conversation_bridge gãy nếu không giữ 4 lát → Engineering chịu trách nhiệm
3. Migration bẩn dữ liệu cũ → Engineering giữ additive-only
4. Admin không đồng bộ P↔E → COO điều phối
