Từ: Engineering
Gửi: Builder
Ngày: 2026-04-12
Phase: Phase 2
---
Task cần làm:
Thực hiện **vòng khắc phục bảo mật khẩn cấp cuối lane** trước khi Engineering được phép khóa `LANE COMPLETION REPORT` gửi COO.

Lý do mở vòng này:
- Artifact hiện tại cho thấy backend đã live và scope 3 nhịp cơ bản đã hoàn tất.
- Nhưng Engineering kiểm tra thấy có **rủi ro lộ secret / sai vệ sinh repo** ở mức không thể coi lane là “sạch” để báo COO.
- Đây là vòng fix hẹp, không mở scope sản phẩm mới.

Phạm vi:
1. **Xử lý secret hygiene**
   - bảo đảm file `.env` chứa secret thật **không nằm trong repo trackable** và không tiếp tục xuất hiện trong package bàn giao/code push
   - bổ sung `.gitignore` phù hợp nếu thiếu
   - rà lại các file docs/config để không còn secret thật hoặc dữ liệu nhạy cảm bị lộ trong artifact
   - không ghi lại giá trị secret thật trong report

2. **Xử lý repo/public exposure risk**
   - nếu repo đang public chỉ để phục vụ deploy, chuyển sang cấu hình an toàn hơn theo hướng Engineering đã note:
     - GitHub App / kết nối phù hợp
     - repo private nếu hạ tầng cho phép
   - nếu không thể đổi ngay do phụ thuộc quyền/owner, phải ghi rõ blocker thực tế và risk còn mở

3. **Rotate / invalidate secret khi cần**
   - nếu secret có khả năng đã từng xuất hiện trong repo/artifact/public channel:
     - rotate secret tương ứng
     - cập nhật secret mới trên môi trường deploy
     - verify lại service sau rotate
   - nếu khẳng định một secret **không hề bị lộ**, phải nêu basis rõ ràng; không được kết luận cảm tính

4. **Evidence sau fix**
   - xác nhận service còn sống sau remediation:
     - `/health`
     - `/readiness`
   - xác nhận artifact bàn giao mới không còn chứa secret thật ở các vị trí không được phép
   - nêu rõ repo hiện ở trạng thái nào: private / public tạm thời / blocker quyền

Input đã có:
- `Builder_gửi_Engineering.md` bản deploy production
- codebase chuẩn `TAI_LIEU_DU_AN/backend/`
- `backend.zip` artifact hiện tại
- runbook / render.yaml / evidence docs hiện có

Output mong muốn:
`Builder_gửi_Engineering.md` bản mới theo format **BUILDER REPORT**, bắt buộc có thêm:
- việc đã làm để xử lý secret hygiene
- file nào đã thêm/sửa/xóa khỏi tracking
- repo visibility hiện tại
- secret nào đã rotate (chỉ nêu tên key, không nêu giá trị)
- verify sau remediation
- kết luận:
  - `đủ sạch để Engineering khóa lane`, hoặc
  - `chưa đủ` + blocker còn lại

Điều kiện done:
- không còn secret thật nằm trong artifact/repo path không được phép
- có `.gitignore` hoặc cơ chế tương đương đủ rõ
- rủi ro repo public/secret exposure đã được xử lý hoặc khai báo blocker trung thực
- service vẫn hoạt động sau remediation
- evidence đủ để Engineering quyết định có gửi COO được hay chưa

Ràng buộc:
- không mở feature mới
- không đổi logic sản phẩm
- không viết lại lane plan
- không ghi secret thật vào report
- nếu gặp blocker quyền GitHub/Render/owner thì báo đúng blocker, không suy đoán

Deadline/Timebox:
- vòng khẩn cấp ngắn, chỉ để làm sạch lane trước khi đóng phase

---

## Phụ lục — Trạng thái Builder (đóng vòng bảo mật)

**Cập nhật:** 2026-04-12 — xem `Builder_gửi_Engineering.md` § **VÒNG KHẮC PHỤC BẢO MẬT (memo Engineering 2026-04-12)**.