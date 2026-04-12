# 01 — Project Brief
<!-- Nguồn sự thật của dự án. Spec và plan chính thức đều nằm ở file này. -->
<!-- Reporter cập nhật file này từ GÓI CHỐT của Deputy sau khi CEO duyệt plan (Gate Plan). -->

## Phase hiện tại
Phase 2 — Triển khai (Release 1, duyệt có điều kiện tại Gate Plan 2026-04-10)

## Dự án là gì
TuVi Bot — chuyển từ MVP kỹ thuật sang hệ thống kinh doanh hoàn chỉnh trên Messenger: engine lá số deterministic là nguồn sự thật; AI dùng cho diễn giải, cá nhân hóa và hỗ trợ bán hàng (theo CEO brief và master plan đã chốt).

## Mục tiêu
- **Release 1 (scope hiện hành):** đạt outcome bắt buộc **KB-1, KB-8, KB-9**; bot online thật; flow Messenger theo source; intake text-first có xác nhận KB-2 trước chart; free result đủ trust nhưng giữ lý do mua tiếp; ít nhất một đường upsell đo được; admin cơ bản vận hành; funnel analytics + metric pack release đầu; trust/safety tối thiểu; mở đường roadmap full-scope A→L không làm lệch outcome khách.
- **Chiến lược phân kỳ:** chia release có kiểm soát — Release 1 khóa hard scope; phần full A→L chưa an toàn gói một lần thì để release sau (đã nêu trade-off trong master plan).

## Ai dùng
Người dùng Việt trên Messenger tìm trợ lý tử vi cá nhân hóa; vận hành nội bộ qua admin/analytics.

## Phạm vi (trong scope) — Release 1
Căn cứ chính thức: `QUAN LY TU VI/TAI_LIEU_DU_AN/plan chi tiết/COO_MASTER_PLAN.md` (ngày 2026-04-10). Tóm tắt:
- 3 source launch đầu: love, career, organic_general; 6 flow tối thiểu; intake text-first + KB-2; free result dạng bài luận trọn vẹn với baseline sections tối thiểu; 1 entry offer shape (1 chủ đề sâu, map theo source); paid path payment link + manual close; premium/handoff/reactivation/trust-safety/admin/deploy ở mức đã khóa trong master plan; conversation_bridge thi công **4 lát**; migration **additive-only**; timebox Release 1 **28–35 ngày** lane thực tế, **3 nhịp** điều phối; Product **CP1+CP2** trong Nhịp 1, **CP3** chậm nhất đầu Nhịp 2; Marketing Specialist kích hoạt dưới Product (theo chỉ thị CEO/COO).

## Ngoài phạm vi
Các mục full brief A→L chưa đưa vào Release 1 nhưng đã giữ chỗ kiến trúc — chi tiết mục 3 `COO_MASTER_PLAN.md`. Không vi phạm nguyên tắc: AI không bịa chart; không ngrok production; bot không thành menu đóng.

## Đầu ra mong muốn
Release 1 đáp ứng outcome KB-1/KB-8/KB-9, đo được metric pack tại Gate Output; nền tảng sẵn sàng mở rộng release sau theo roadmap.

## Definition of Done
Theo Gate Output Phase 2 (chưa diễn ra): acceptance và metric đã khóa trong master plan + điều kiện CEO tại Gate Plan được thể hiện trong bàn giao và QA.

---
## Spec / Plan chính thức
**Master plan đã duyệt có điều kiện (Gate Plan 2026-04-10):** `QUAN LY TU VI/TAI_LIEU_DU_AN/plan chi tiết/COO_MASTER_PLAN.md`

**Brief CEO (toàn bộ yêu cầu khách / ngữ cảnh):** `QUAN LY TU VI/_TEMPLATE_DU_AN/drafts tuvi/CEO_gửi_COO.md`

**Brief khách chi tiết:** `QUAN LY TU VI/TAI_LIEU_DU_AN/brief_khach_hang_chi_tiet_bot_tuvi_final.txt` (tham chiếu; scope triển khai Release 1 lấy master plan + Gate Plan làm chuẩn).
