QA PLAN REVIEW

Từ: QA
Gửi: Deputy (chính) / COO (copy) / CEO nếu có P0
Ngày: 2026-04-10

Scope hợp lý: Có. Bản master plan cập nhật tiếp tục bám đúng outcome khóa của release đầu theo KB-1/KB-8/KB-9: online thật, flow Messenger mới theo source, intake text-first có confirm KB-2, free result đủ trust nhưng không nuốt mất lý do mua tiếp, có ít nhất 1 đường upsell đo được, admin cơ bản, funnel analytics, trust/safety và vận hành ít phụ thuộc terminal. Kế hoạch cũng vẫn giữ đúng thẩm quyền: chia release là đề xuất để CEO quyết tại Gate Plan, không tự cắt scope sai quyền.

Rủi ro chính:

conversation_bridge vẫn là điểm gãy kỹ thuật lớn nhất nếu không giữ đúng 4 lát thi công.
Migration/backfill vẫn có nguy cơ bẩn dữ liệu cũ nếu không giữ additive-only.
Nếu cố nhồi full A→L vào một release triển khai duy nhất thì acceptance sẽ loãng và xác suất trễ tăng.
Timebox tổng thể không còn là blocker plan, nhưng có thể trượt nếu Product bàn giao muộn CP1/CP2/CP3; master plan đã nêu rõ đây là risk điều phối chứ không phải khoảng hở chưa được nhận diện.

Khả thi kỹ thuật: Có. Hướng kỹ thuật vẫn nhất quán và khả thi cho release đầu: FastAPI + PostgreSQL + OpenAI, refactor incremental, schema additive, signature verify, DB dedupe, event mapping business→technical, admin cùng service, RBAC/audit, smoke deploy online, rollback/readiness/runbook. Hướng này khớp brief khách về online thật, không dùng ngrok, và đủ bề mặt vận hành cơ bản.

Spec đầy đủ: Có. Spec sản phẩm ở cấp master plan tiếp tục khóa đủ 3 source launch, 6 flow tối thiểu, free result là bài luận giải trọn vẹn, free-vs-paid boundary, trust/safety, metric pack, fallback definition, admin governance matrix và campaign config cơ bản. Các điểm giao P↔E cũng đã được khóa để tránh implementation lệch nghĩa.

Acceptance criteria: Có. So với bản trước, COO đã hấp thụ điều kiện còn mở: timebox tổng hợp cấp phase/release đã được nâng lên master plan, kèm mapping phase/sprint, critical path, phần chạy song song và dependency risk ở cấp điều phối. Phần này bám lane plan thực tế: Engineering là critical path 28–35 ngày lane thực tế, 20–24 ngày code-only; Product là lane 7–9 ngày chủ yếu chạy song song, với CP1/CP2 trong nhịp 1 và CP3 chậm nhất đầu nhịp 2. QA không thấy dấu hiệu COO tự suy diễn timebox vượt dữ liệu lane plan.

Mâu thuẫn nội bộ: Không. Các điểm giao giữa Product và Engineering vẫn khớp nhau: canonical semantics dùng chung, preview chỉ áp cho static content blocks, human handoff release đầu ở mức minimal surface, completion metrics hiển thị song song, multi-profile chỉ mở đường ở schema/state chứ chưa là trụ UX chính. Cấu trúc timebox tổng hợp của COO cũng bám đúng logic “Engineering là critical path, Product front-load CP1/CP2 rồi khóa CP3 đầu nhịp 2”, nên không tạo mâu thuẫn mới ở cấp master plan.

Kết luận: Pass.
Không phát hiện P0 trong master plan cập nhật này. Điều kiện mở từ bản review trước đã được COO hấp thụ đủ ở cấp master plan, đặc biệt là phần timebox tổng hợp / phase-sprint mapping / critical path / dependency risk. Gói Gate Plan hiện đủ điều kiện để Deputy thực hiện executive review và trình CEO quyết định.

Bằng chứng:

COO yêu cầu QA kiểm riêng việc timebox tổng hợp mới thêm có bám lane plan Product/Engineering hay không, và overall release 28–35 ngày có hợp lý không.
Master plan v2 đã bổ sung mục 5A/5B: timebox tổng hợp, mapping phase/sprint, critical path, parallelization, dependency risk.
Lane Engineering xác nhận 0.5 ngày còn lại của Phase 1, 28–35 ngày lane thực tế, 20–24 ngày code-only, và dependency Product chỉ là risk trượt timebox chứ không blocker plan.
Lane Product xác nhận CP1/CP2 phải bàn giao trong nhịp 1, CP3 chậm nhất đầu nhịp 2, và phần polish không được kéo lùi baseline build.
CEO brief yêu cầu master plan phải đủ để CEO quyết Gate Plan cho release đầu bám KB-1/KB-8/KB-9 và không lệch outcome khách đã khóa.