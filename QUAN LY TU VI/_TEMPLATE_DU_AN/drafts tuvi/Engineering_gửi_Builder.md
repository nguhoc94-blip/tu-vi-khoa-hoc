## GIAO TASK
Từ: Engineering
Gửi: Builder
Ngày: 2026-04-11
Phase: Phase 2
---
Task cần làm:
Engineering **phê duyệt plan chi tiết Nhịp 3** và cho phép Builder **bắt đầu thi công Nhịp 3** theo đúng phạm vi đã nộp, với các khóa triển khai bổ sung dưới đây. Đây là lệnh mở thi công thực tế sau vòng plan-only.

Phạm vi giữ nguyên:
1. Ops / Online readiness
2. Observability
3. Trust / Safety
4. Regression / smoke / evidence để Engineering tổng hợp lane completion cuối lane

Input đã có:
- `COO_gửi_Engineering.md` (Phase 2 — chỉ báo COO khi lane hoàn tất hoặc có blocker/escalation)
- lane plan Engineering đã khóa
- Nhịp 1 và Nhịp 2 đã duyệt xong
- codebase chuẩn `QUAN LY TU VI/TAI_LIEU_DU_AN/backend/`
- `Builder_gửi_Engineering.md` (plan chi tiết Nhịp 3)

Output mong muốn:
1. Thi công xong Nhịp 3 trên codebase chuẩn
2. Gửi lại `Builder_gửi_Engineering.md` theo format BUILDER REPORT với:
   - việc đã làm
   - file đã sửa
   - build/test đã chạy
   - kết quả pass/fail
   - lỗi còn lại
   - vượt scope hay không
   - bằng chứng cụ thể
3. Không gửi COO trực tiếp

Điều kiện done:
- Có deploy path Render baseline + runbook deploy/redeploy/restart/rollback/verify webhook
- `/health` và `/readiness` usable cho vận hành
- Log redact / trust-safety baseline / anonymization baseline hoạt động
- Có procedure cleanup `webhook_dedupe`
- Full pytest pass hoặc nêu rõ fail nào
- Có smoke evidence đủ để Engineering khóa lane completion report

Khóa triển khai bổ sung từ Engineering:
1. **Render health check path chốt luôn**
   - platform health check dùng **`/health`** làm liveness
   - `/readiness` dùng cho verify DB/readiness trong runbook và smoke
   - không dùng `/readiness` làm platform liveness mặc định để tránh restart sai khi DB transient fail

2. **Retention `webhook_dedupe` chốt theo lane đã khóa trước đó**
   - cleanup giữ đúng **24 giờ**
   - không tự nâng lên N ngày khác nếu không có blocker thật sự
   - nếu implementation cần batching để tránh lock, được phép làm nhưng không đổi semantics 24h

3. **Trust/Safety baseline chốt theo hướng release đầu**
   - ưu tiên **anonymization baseline** có audit hơn hard delete toàn phần nếu không bắt buộc xóa vật lý
   - nếu có route admin cho anonymize/delete phải nằm sau auth + RBAC + audit đã có từ Nhịp 2

4. **Không kéo scope ngoài Nhịp 3**
   - không mở dashboard platform mới
   - không thêm monitoring stack riêng
   - không sửa logic bridge 4 lát trừ hook/log tối thiểu thật sự cần

5. **Evidence cho lane completion bắt buộc**
   - commit SHA / artifact deploy
   - output pytest
   - smoke checklist
   - runbook
   - ghi rõ những gì mới chỉ verified ở staging, chưa phải production thật

Ràng buộc:
- không mở scope ngoài Nhịp 3
- không đổi logic release đầu
- không gộp lại các lát bridge đã khóa
- migration nếu có vẫn additive-only
- không tự báo COO
- nếu phát sinh blocker làm lane không thể đóng đúng plan, báo Engineering ngay

Deadline/Timebox:
- bám khung Nhịp 3 đã khóa: 8–10 ngày lane thực tế
- khi có build report sạch, Engineering sẽ review để quyết định gửi COO LANE COMPLETION REPORT hay yêu cầu fix cuối lane

---

## Phụ lục — Trạng thái Builder (đóng nhiệm vụ theo memo này)

**Ngày cập nhật:** 2026-04-12  
**Không gửi COO từ Builder** (đúng ràng buộc memo).

- **Báo cáo chính thức:** `drafts tuvi/Builder_gửi_Engineering.md` — có mục **Đối chiếu `Engineering_gửi_Builder.md`** (output, điều kiện done, khóa triển khai, lỗi, scope).
- **Evidence:** `QUAN LY TU VI/TAI_LIEU_DU_AN/backend/docs/pytest_last_run.txt`, `docs/git_sha_for_evidence.txt`, `docs/smoke_checklist_nhip3.md`, `docs/runbook_deploy.md`, `docs/builder_evidence_nhip3.md`.
- **Pytest:** 66/66 passed (lần chạy evidence gần nhất ghi trong `pytest_last_run.txt`).
- **Deploy Render:** ✅ **Production live** 2026-04-12 — `https://tuvi-backend-ocgd.onrender.com` (chi tiết + evidence `/health` + `/readiness` trong `Builder_gửi_Engineering.md` § *BÁO CÁO E*). Cần team cập nhật webhook Facebook + tick smoke prod.
- **Phần bổ sung sau Nhịp 3 (CEO):** nằm trong `Builder_gửi_Engineering.md` § *BỔ SUNG SAU TRIỂN KHAI* — ngoài scope Engineering ban đầu, đã ghi rõ nguồn chỉ đạo.
