## COO MASTER PLAN
Từ: COO
Gửi: QA + Deputy
Ngày: 2026-04-10
Phase: Phase 1
---
1. Mục tiêu dự án

Chuyển TuVi Bot từ MVP kỹ thuật sang hệ thống kinh doanh hoàn chỉnh trên Messenger, vẫn giữ engine lá số deterministic là nguồn sự thật và dùng AI cho diễn giải/cá nhân hóa/hỗ trợ bán hàng.

Mục tiêu Gate Plan của bản này là khóa kế hoạch đủ để triển khai release đầu đáp ứng outcome bắt buộc KB-1 và giữ đúng hướng full-scope A→L theo CEO brief:
- bot chạy online thật, không local/ngrok production
- flow Messenger mới theo source vào bot
- intake dữ liệu sinh thông minh có xác nhận trước khi lập chart
- free result đủ trust nhưng vẫn giữ lý do mua tiếp
- có ít nhất 1 đường upsell đo được
- admin cơ bản đủ vận hành thường ngày
- funnel analytics cơ bản + metric pack release đầu
- trust/safety tối thiểu ngay từ release đầu
- mở đường cho các scope còn lại của full brief mà không làm lệch outcome khách đã khóa

2. Phạm vi bản này

Bản này là master plan Phase 1 để xin Gate Plan cho hướng triển khai full-scope theo cấu trúc release có kiểm soát, trong đó:
- Release đầu là release bắt buộc phải đạt outcome KB-1 + KB-8 + KB-9
- Các scope full A→L chưa an toàn để nhồi vào release đầu sẽ được giữ trong roadmap triển khai sau release đầu, nhưng kiến trúc/schema/event/admin surface phải mở đường ngay từ release đầu để không phải làm lại

Phạm vi release đầu được khóa ở mức master plan:
- 3 source launch đầu: love, career, organic_general
- 6 flow tối thiểu: new_user_love, new_user_career, new_user_general, returning_unpaid, intake_abandoned_resume, paid_once_repeat
- intake text-first với suy đoán tạm nhưng bắt buộc confirm các field lớn trước chart theo KB-2
- free result là 1 bài luận giải trọn vẹn với các baseline sections tối thiểu: tổng quan ngắn, 3 điểm nổi bật, tình cảm, công việc/sự nghiệp, tài lộc/nhịp tài chính, điều cần cẩn trọng, gợi ý hành động tiếp; campaign-intent slice chỉ là phần nhấn trong bài
- 1 entry offer shape cho lần upsell đầu: 1 chủ đề sâu, map theo source
- paid path release đầu: payment link + manual close
- premium release đầu: intent capture + handoff thủ công tối thiểu
- reactivation release đầu: in-window follow-up, return hooks trong hội thoại, remarketing-ready
- trust/safety release đầu: micro disclaimer, privacy/data notice, trust bridge trước upsell, guardrail wording trong tình huống nhạy cảm
- admin release đầu: campaign config cơ bản, static content governance, funnel dashboard, health/errors surface, lead detail/transcript, auth/RBAC, audit log
- deploy/vận hành release đầu: Render ưu tiên, Railway fallback; dashboard hosting + runbook đủ để người vận hành ít phụ thuộc terminal

Đề xuất phân kỳ để CEO quyết tại Gate Plan:
- Phương án khuyến nghị: chia release nội bộ có kiểm soát
  - Release 1: toàn bộ hard scope bắt buộc theo KB-1/KB-8/KB-9
  - Release sau: payment tự động thật, compatibility sâu, queue engine handoff đầy đủ, time_window campaign riêng, outside-window automation làm trụ chính, runtime preview cho dynamic free result, membership/CRM sâu
- Trade-off:
  - Nếu ép full A→L vào một release triển khai duy nhất: rủi ro trễ, acceptance loãng, khó khóa đồng thời UX + production + admin + analytics + safety
  - Nếu duyệt phương án chia release nhưng khóa đủ Release 1 như trên: rủi ro điều phối giảm, QA review rõ hơn, vẫn không lệch outcome khách vì release đầu đã giữ đủ các điều kiện cứng của brief

3. Ngoài phạm vi

Ngoài phạm vi của Release 1 nhưng đã được giữ chỗ trong định hướng full-scope:
- campaign riêng cho time_window
- booking flow premium hoàn chỉnh
- queue engine đầy đủ cho human handoff
- payment gateway tự động và auto-confirm payment
- compatibility đủ sâu như một product line riêng
- automation outside-window làm trụ chính
- multi-profile như trụ UX chính
- A/B test logic-level hoặc entitlement-level
- runtime preview cho dynamic free result
- membership / gói theo dõi định kỳ / CRM sâu

Ngoài phạm vi tuyệt đối của dự án theo brief và nguyên tắc lõi:
- không để AI bịa chart
- không dùng ngrok hoặc tunnel tạm cho production
- không để bot biến thành menu đóng thay cho trợ lý hội thoại
- không bỏ trust/safety sang release sau

4. Tuyến xử lý

Tuyến xử lý: P+E + Marketing Specialist (dưới Product)

Owner lane Product:
- Messenger UX theo source
- conversation design, progress/confirmation policy
- free result structure, ranh giới free-vs-paid
- CTA/upsell, offer mapping, trust wording
- fallback UX/content definition
- admin governance matrix cho content/campaign surfaces
- metric pack business semantics để COO/QA/CEO review

Owner lane Engineering:
- target architecture release đầu
- migration/schema/data model additive từ nền hiện tại
- webhook hardening, dedupe shared-store, retry, observability
- event pipeline, business-to-technical event mapping
- admin backend/views, auth/RBAC/audit, export, transcript surface
- deploy/runbook/health/readiness/rollback
- conversation bridge slicing 4 lát để thi công an toàn

Marketing Specialist dưới Product:
- đã được hấp thụ vào lane Product cho phần campaign-to-flow mapping, CTA tone, trust bridge, offer ladder, reactivation logic và social proof governance; không mở thêm lane riêng ở master plan này

5. Lane plan tóm tắt

Nguồn tổng hợp:
- Product_gửi_COO.md (bản chỉnh timebox 2026-04-10)
- Engineering_gửi_COO.md (bản chỉnh timebox 2026-04-10)

Tóm tắt lane Product:
- khóa 3 source đầu + 6 flow tối thiểu cho release đầu
- khóa free result là bài luận giải trọn vẹn, không phải bài chỉ nói 1 lát chủ đề
- khóa 1 entry offer đầu là “1 chủ đề sâu”, map theo source
- khóa reactivation/handoff/trust surfaces ở mức release đầu
- khóa metric pack business semantics: completion rate, upsell click, paid intent/conversion, return rate, fallback/error rate, visibility funnel trong admin
- khóa fallback definition từ góc UX/content để Engineering map event/log
- khóa admin governance matrix cho static content + campaign config cơ bản
- đã chuẩn hóa timebox lane Product và critical path đầu vào cho Phase 2

Tóm tắt lane Engineering:
- giữ stack FastAPI + PostgreSQL + OpenAI; refactor incremental, không rewrite
- khóa Render là platform ưu tiên, Railway là fallback gần nhất
- khóa target architecture: 1 FastAPI service + managed PostgreSQL + admin cùng service
- khóa data model additive gồm: messenger_sessions, user_profiles, profile_entities, conversation_history, funnel_events, orders, campaigns, app_config, admin_users, admin_audit_log
- khóa webhook hardening, signature verify, DB dedupe, attribution capture, token/fallback logging
- khóa event mapping business → technical để QA trace metric pack release đầu
- khóa admin surface release đầu: dashboard funnel/health/errors, campaign/config CRUD, lead detail/transcript, RBAC 4 nhóm quyền
- khóa conversation_bridge thi công theo 4 lát: funnel/token, campaign/return, KB-2 confirm, multi-profile awareness
- khóa test strategy, smoke deploy online, rollback/readiness/runbook
- đã chuẩn hóa timebox lane Engineering, 3 nhịp điều phối, critical path và phần chạy song song

5A. Timebox tổng hợp cấp master plan

5A.1. Timebox Phase 1 còn lại để chốt Gate Plan sạch
- Loop bổ sung do QA yêu cầu được giới hạn ở phạm vi timebox-only.
- Cả Product và Engineering đều xác nhận phần chuẩn hóa này nằm trong 0.5 ngày làm việc còn lại của Phase 1 và đã được hấp thụ xong trong ngày 2026-04-10.
- Kết luận điều phối Phase 1: không cần mở thêm loop cấp dưới chỉ để khóa timebox.

5A.2. Timebox tổng hợp cho Phase 2 / Release 1
- Timebox điều phối tổng hợp của Release 1: 28–35 ngày lane thực tế.
- Cơ sở điều phối:
  - Engineering là critical path tổng thể của release với 28–35 ngày lane thực tế, trong đó 20–24 ngày là code-only.
  - Product có lane bắt buộc 7–9 ngày làm việc, nhưng phần lớn chạy song song với Engineering; chỉ 3 nhóm CP1–CP3 là có thể làm trượt timebox nếu bàn giao muộn.
- Suy luận điều phối của COO:
  - nếu Product bàn giao đúng CP1 + CP2 trong nhịp đầu và khóa CP3 chậm nhất ở đầu nhịp 2, timebox tổng thể của dự án vẫn bám 28–35 ngày;
  - nếu Product bàn giao chậm các đầu vào critical path này, nhịp 2 hoặc đầu nhịp 3 của Engineering có thể bị trượt dù không làm sập master plan.

5A.3. Mapping phase/sprint cấp master plan
- Nhịp 0 — Closure Gate Plan:
  - 0.5 ngày làm việc
  - mục tiêu: chuẩn hóa timebox, critical path, dependency risk để vá master plan theo điều kiện QA
  - trạng thái: đã hoàn tất trong ngày
- Nhịp 1 — Foundation baseline:
  - 10–13 ngày lane thực tế
  - owner kỹ thuật: Engineering
  - owner đầu vào critical: Product front-load 2–3 ngày đầu
  - output mốc: schema additive + webhook production-safe baseline + funnel/event/source baseline
- Nhịp 2 — Admin usable + confirm/multi-profile baseline:
  - 10–12 ngày lane thực tế
  - owner kỹ thuật: Engineering
  - owner đầu vào critical: Product phải khóa CP3 chậm nhất đầu nhịp này
  - output mốc: admin usable, config/campaign surfaces, KB-2 confirm flow, multi-profile baseline
- Nhịp 3 — Online readiness + regression:
  - 8–10 ngày lane thực tế
  - owner kỹ thuật: Engineering
  - owner Product: hỗ trợ polish/fallback/trust wording trong phạm vi đã khóa nếu thật sự cần
  - output mốc: deploy online bước đầu, health/errors/runbook, trust/safety hoàn chỉnh, regression confidence

5B. Critical path và dependency tổng hợp ở cấp COO

Critical path tổng thể của Release 1:
1. Foundation (`db.py`, `db_init.py`, logging, health/readiness)
2. Data migrations 001-011
3. Webhook hardening baseline
4. Bridge lát 1-2
5. Admin API nền
6. Bridge lát 3-4
7. Ops/Observability + Regression cuối

Critical input từ Product có thể làm trượt timebox nhưng không làm sập plan:
- CP1: payload spec quick replies/postbacks cho 6 flow tối thiểu
- CP2: seed content mặc định cho `app_config`
- CP3: wording final cho confirmation / trust / CTA / footer / social proof / campaign labels

Phần có thể đi song song:
- admin API và HTML views song song với một phần webhook polish sau khi có nền Foundation/Data
- campaign/config CRUD song song với dashboard queries
- trust/safety redact/anonymization song song với một phần admin lead/transcript
- Product có thể bàn giao seed content và wording final song song với thi công admin surfaces

Điểm thống nhất P↔E đã được khóa ở master plan:
- canonical semantics dùng chung: conversation_started, free_result_sent, manual_paid_marked, fallback/error pack
- admin preview chỉ áp cho static content blocks, không áp cho dynamic free result runtime
- human handoff release đầu chỉ ở mức minimal surface
- completion metrics hiển thị song song: intake_completion_rate và free_delivery_rate
- multi-profile mở đường ở schema/state từ release đầu nhưng chưa là trụ UX chính
- dynamic UX/content chi tiết của Product không chặn việc khóa plan kỹ thuật

Acceptance pack ở cấp master plan để QA review:
- scope release đầu bám đúng KB-1, KB-8, KB-9
- 3 source đầu + 6 flow tối thiểu đã được khóa
- KB-2 confirmation được khóa ở cả Product lẫn Engineering
- free result structure đã khóa đủ để không bị hiểu sai
- free-vs-paid boundary và 1 entry offer đầu đã khóa
- admin governance matrix + campaign config + metric pack + fallback definition đã khóa
- event mapping business → technical đủ để QA trace và admin hiển thị đúng
- trust/safety, deploy online, rollback/readiness, RBAC, audit đều có mặt trong release đầu
- timebox tổng hợp cấp phase/release đã được nâng lên master plan
- release strategy đã nêu rõ trade-off để CEO quyết, không tự ý cắt release

Rủi ro chính ở cấp master plan:
- conversation_bridge là điểm gãy P0 kỹ thuật nếu không giữ đúng 4 lát thi công
- migration/backfill có nguy cơ bẩn dữ liệu cũ nếu làm không additive
- nếu cố nhồi full A→L vào một release triển khai duy nhất sẽ làm loãng acceptance và tăng xác suất trễ
- admin hữu dụng phụ thuộc cả backend, views và content governance đồng bộ giữa P↔E
- timebox có thể trượt nếu Product bàn giao muộn CP1–CP3, dù đây không còn là blocker plan

6. Lệnh đầu tiên nên gửi

Nếu CEO duyệt Gate Plan:
1. COO nhận CEO CHỈ THỊ mở Phase 2
2. COO gửi kế hoạch đã duyệt cho Product và Engineering theo đúng lane owner
3. Engineering mở thi công theo 3 nhịp:
   - Nhịp 1: Foundation → Data/Migration → Webhook hardening → bridge lát 1–2
   - Nhịp 2: Admin API/views → bridge lát 3–4
   - Nhịp 3: Ops/Observability → Trust/Safety → Regression
4. Product bàn giao gói triển khai Phase 2 theo nguyên tắc timebox:
   - Nhịp 1: payload spec quick replies/postbacks + seed content v1 + wording baseline
   - Đầu Nhịp 2: khóa CP3 gồm confirmation/trust/CTA/footer/social proof/campaign labels
   - Cuối Nhịp 2 / đầu Nhịp 3 nếu cần: polish copy/fallback/trust wording trong phạm vi đã khóa
5. P/E chỉ báo COO khi lane hoàn tất; COO không nhận báo cáo giữa chừng
