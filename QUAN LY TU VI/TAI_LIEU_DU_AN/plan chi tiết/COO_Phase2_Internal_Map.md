## COO PHASE 2 — KẾ HOẠCH ĐIỀU PHỐI NỘI BỘ
Từ: COO
Gửi: Nội bộ điều phối COO
Ngày: 2026-04-10
Phase: Phase 2
---
1. Mục tiêu điều phối

Triển khai Release 1 đúng Gate Plan đã được CEO duyệt có điều kiện:
- giữ hard scope KB-1 / KB-8 / KB-9
- Product giao đúng CP1 + CP2 trong Nhịp 1; CP3 chậm nhất đầu Nhịp 2
- Engineering thi công đúng 3 nhịp, giữ conversation_bridge theo 4 lát và migration additive-only
- chỉ nhận báo cáo lane khi lane hoàn tất; không nhận báo cáo giữa chừng
- theo yêu cầu hiện tại: không phát hành báo cáo cấp trên/Reporter giữa các loop thường; chỉ escalate khi có blocker hoặc trượt điều kiện CEO đã khóa

2. Khung nhịp Phase 2

Nhịp 1 — Foundation baseline
- Timebox điều phối: 10–13 ngày lane thực tế
- Product:
  - bàn giao CP1: payload spec quick replies/postbacks cho 6 flow
  - bàn giao CP2: seed content mặc định cho app_config
  - mở quản lý trực tiếp Marketing Specialist nếu cần để khóa campaign-to-flow, CTA tone, trust bridge, social proof governance
- Engineering:
  - Foundation + Data/Migration + Webhook hardening + bridge lát 1–2
- Điều kiện dừng Nhịp 1:
  - Product đã giao đủ CP1 + CP2
  - Engineering có schema additive + webhook production-safe baseline + event/source/return baseline

Nhịp 2 — Admin usable + confirm/multi-profile baseline
- Timebox điều phối: 10–12 ngày lane thực tế
- Product:
  - khóa CP3 chậm nhất đầu Nhịp 2: wording final confirmation / trust / CTA / footer / social proof / campaign labels
  - hỗ trợ fix điểm P↔E nếu admin/config surface cần map lại content
- Engineering:
  - Admin API/views + bridge lát 3–4
- Điều kiện dừng Nhịp 2:
  - Admin usable cho vận hành cơ bản
  - KB-2 confirm flow chạy đúng
  - multi-profile baseline chạy ở mức release đầu
  - CP3 đã khóa xong

Nhịp 3 — Online readiness + regression
- Timebox điều phối: 8–10 ngày lane thực tế
- Product:
  - chỉ hỗ trợ polish copy/fallback/trust wording trong phạm vi đã khóa
- Engineering:
  - Ops/Observability + Trust/Safety + Regression
- Điều kiện dừng Nhịp 3:
  - deploy online bước đầu
  - health/errors/runbook/rollback rõ
  - metric pack đo và trace được
  - regression confidence trước Gate Output

3. Quy tắc điều phối trong Phase 2

- COO không nhận báo cáo giữa chừng từ P/E; chỉ nhận khi lane hoàn tất theo manual
- P/E được mở loop nội bộ với cấp dưới theo lane của mình
- Builder luôn dưới Engineering
- Marketing Specialist dưới Product
- Không mở rộng scope release đầu
- Không thay đổi 3 source / 6 flow / free result structure / free-vs-paid boundary / metric pack đã khóa ở Gate Plan

4. Điều kiện escalation bắt buộc dù chưa hết Phase 2

COO phải báo CEO ngay nếu xảy ra một trong các tình huống sau:
- Product trượt CP1 hoặc CP2 trong Nhịp 1
- Product chưa khóa CP3 ở đầu Nhịp 2
- Engineering có dấu hiệu gộp lát / nhảy lát ở conversation_bridge
- Migration có nguy cơ phá schema cũ hoặc mất dữ liệu
- Xuất hiện blocker P0 làm lệch Gate Output target

5. Kết thúc Phase 2

Chỉ khi cả Product và Engineering đều gửi LANE COMPLETION REPORT sạch hoặc có blocker được khai báo rõ,
COO mới:
- đánh giá toàn phase
- nếu đạt: khóa output phase
- gửi QA + Deputy cho Gate Output
- sau CEO quyết mới gửi Reporter theo đúng manual
