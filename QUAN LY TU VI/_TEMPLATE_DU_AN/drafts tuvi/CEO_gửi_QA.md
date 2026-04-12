## CEO INFORM QA
Từ: CEO
Gửi: QA
Ngày: 2026-04-10
Gate vừa chốt: Gate Plan (TuVi Bot MVP Kinh Doanh — Release 1)
---

**Quyết định CEO: DUYỆT CÓ ĐIỀU KIỆN — Mở Phase 2**

**Scope Phase 2 — Release 1:**
Bot chạy online thật, flow Messenger mới (3 source + 6 flow tối thiểu), intake thông minh có confirm KB-2, free result trọn vẹn, 1 entry offer + 1 đường upsell đo được, admin cơ bản, funnel analytics + metric pack, trust/safety, RBAC/audit, deploy online + rollback/readiness.

**QA review focus cho Gate Output:**

1. **conversation_bridge**: kiểm tra 4 lát thi công được giữ đúng, không gộp, không nhảy lát
2. **Migration additive-only**: schema mới không phá dữ liệu cũ
3. **KB-2 confirm flow**: bot phải xác nhận lại các trường mơ hồ trước khi lập chart — không giả vờ chắc chắn
4. **Bộ chỉ số release đầu (KB-8)**: QA phải trace được từ event mapping → metric pack đã khóa: completion rate, upsell click, paid intent/conversion, return rate, fallback/error rate, visibility funnel trong admin
5. **Trust/safety (KB-9)**: disclaimer hiển thị trong flow, guardrail tình huống nhạy cảm, log không lộ thô, RBAC hoạt động
6. **Free-vs-paid boundary (KB-3)**: free đủ hay nhưng không nuốt mất lý do mua tiếp
7. **Deploy online**: không dùng ngrok/tunnel tạm (KB-11), webhook ổn định, rollback hoạt động
8. **Scope không vượt**: Release 1 không đụng vào scope Release sau đã liệt kê trong master plan mục 3
