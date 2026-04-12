# Thư mục drafts/ — File nháp giao tiếp giữa agent (v8)

Mọi giao tiếp chính thức giữa agent **bắt buộc** tạo file .md trong thư mục này.

## Quy tắc

- Format tên: `[Agent_gửi]_gửi_[Agent_nhận].md`
- Ghi đè khi cùng cặp agent giao tiếp lại trong cùng phase
- File nháp KHÔNG thay thế 5 file chính thức — chỉ là trace giao tiếp
- Reporter đối chiếu file nháp khi cập nhật file chính thức
- Mỗi file nháp phải có header tối thiểu: `Từ / Gửi / Ngày / Phase / Nội dung`
- **Mỗi file chỉ chứa đúng 1 form**
- **Tránh dài dòng**: chỉ điền đúng trường trong form

## Danh sách file cho 1 vòng dự án đầy đủ

### Phase 1 — Lập kế hoạch

| File | Form | Mô tả |
|---|---|---|
| `CEO_gửi_COO.md` | CEO BRIEF | CEO giao brief cho COO (+ inform QA, Deputy) |
| `CEO_gửi_QA.md` | CEO INFORM QA | CEO inform QA nắm context từ đầu |
| `COO_gửi_Product.md` | COO GỬI PRODUCT | COO giao lane cho Product |
| `COO_gửi_Engineering.md` | COO GỬI ENGINEERING | COO giao lane cho Engineering |
| `Product_gửi_Engineering.md` | PRODUCT GỬI ENGINEERING | Handoff spec P→E (loop nội bộ) |
| `Engineering_gửi_Product.md` | ENGINEERING GỬI PRODUCT | Phản biện kỹ thuật E→P (loop nội bộ) |
| `Builder_gửi_Engineering.md` | BUILDER REPORT | Builder gửi sub-plan về Engineering (nếu E giao) |
| `Specialist_gửi_Engineering.md` | SPECIALIST REPORT | Specialist KT gửi sub-plan về Engineering (nếu có) |
| `Specialist_gửi_Product.md` | SPECIALIST REPORT | Specialist NV gửi sub-plan về Product (nếu có) |
| `AgentBatKy_gửi_CapTren_SkillGap.md` | FORM 11E-1 | Agent báo skill gap về P/E (khi bị kẹt) |
| `PE_gửi_COO_LearningProposal.md` | FORM 11E-2 | P/E đề xuất xử lý skill gap lên COO |
| `COO_gửi_CEO_SpecialistForm_SkillGap.md` | FORM 11E-3 | COO đề xuất Specialist mới (Đường B) lên CEO |
| `Engineering_gửi_COO.md` | ENGINEERING LANE PLAN | Engineering lane plan kỹ thuật → COO |
| `Product_gửi_COO.md` | PRODUCT LANE PLAN | Product lane plan sản phẩm → COO |
| `COO_gửi_QA.md` | COO GỬI QA REVIEW | COO gửi master plan cho QA review |
| `QA_gửi_Deputy_PlanReview.md` | QA PLAN REVIEW | QA Plan Review → Deputy |
| `Deputy_gửi_CEO.md` | EXECUTIVE REVIEW | Executive Review → CEO |
| `Deputy_gửi_Reporter.md` | GÓI CHỐT | GÓI CHỐT sau CEO duyệt Gate Plan |
| `COO_gửi_Reporter.md` | GÓI TRẠNG THÁI | GÓI TRẠNG THÁI |

> Nếu cần kích hoạt Specialist mới thông thường: `COO_gửi_CEO_SpecialistForm.md` → CEO duyệt trước
> Nếu Specialist được trigger bởi skill gap: dùng `COO_gửi_CEO_SpecialistForm_SkillGap.md` (FORM 11E-3)

### Phase 2 — Triển khai

| File | Form | Mô tả |
|---|---|---|
| `COO_gửi_Product.md` | COO GỬI PRODUCT | COO giao triển khai cho Product |
| `COO_gửi_Engineering.md` | COO GỬI ENGINEERING | COO giao triển khai cho Engineering |
| `Engineering_gửi_Builder.md` | GIAO TASK | Engineering giao task cho Builder |
| `Builder_gửi_Engineering.md` | BUILDER REPORT | Builder build report → Engineering |
| `Engineering_gửi_SpecialistKT.md` | GIAO TASK | Engineering giao task cho Specialist KT (nếu có) |
| `Specialist_gửi_Engineering.md` | SPECIALIST REPORT | Specialist KT output → Engineering |
| `Product_gửi_SpecialistNV.md` | GIAO TASK | Product giao task cho Specialist NV (nếu có) |
| `Specialist_gửi_Product.md` | SPECIALIST REPORT | Specialist NV output → Product |
| `Engineering_gửi_COO.md` | ENGINEERING LANE PLAN *(Phase 1)* / LANE COMPLETION REPORT *(Phase 2)* | Engineering gửi lane plan (Phase 1) hoặc báo hoàn thành lane (Phase 2) → COO |
| `Product_gửi_COO.md` | PRODUCT LANE PLAN *(Phase 1)* / LANE COMPLETION REPORT *(Phase 2)* | Product gửi lane plan (Phase 1) hoặc báo hoàn thành lane (Phase 2) → COO |
| `AgentBatKy_gửi_CapTren_SkillGap.md` | FORM 11E-1 | Agent báo skill gap về P/E (khi bị kẹt) |
| `PE_gửi_COO_LearningProposal.md` | FORM 11E-2 | P/E đề xuất xử lý skill gap lên COO |
| `COO_gửi_CEO_SpecialistForm_SkillGap.md` | FORM 11E-3 | COO đề xuất Specialist mới (Đường B) lên CEO |
| `COO_gửi_QA.md` | COO GỬI QA REVIEW | COO gửi output phase cho QA review |
| `QA_gửi_Deputy_Report.md` | QA REPORT | QA Report → Deputy |
| `Deputy_gửi_CEO.md` | EXECUTIVE REVIEW | Executive Review → CEO |
| `Deputy_gửi_Reporter.md` | GÓI CHỐT | GÓI CHỐT sau CEO duyệt Gate Output |
| `COO_gửi_Reporter.md` | GÓI TRẠNG THÁI | GÓI TRẠNG THÁI |

### Fast Track (khi CEO duyệt FORM FT-1)

| File | Form | Mô tả |
|---|---|---|
| `COO_gửi_CEO_FastTrack.md` | FORM FT-1 | COO đề xuất Fast Track → CEO duyệt |
| `CEO_gửi_COO_FastTrack.md` | CEO QUYẾT ĐỊNH FAST TRACK | CEO trả lời COO (duyệt / không / có điều kiện) |
| `Deputy_gửi_Reporter.md` | GÓI CHỐT | GÓI CHỐT (Fast Track Gate) → Reporter cập nhật 05 |
| `QA_gửi_COO_FastTrack.md` | FORM QA-FT | QA Lightweight Report → COO |
| `COO_gửi_Reporter.md` | GÓI TRẠNG THÁI | GÓI TRẠNG THÁI Closure — COO gửi khi FT kết thúc → Reporter cập nhật 03 |
| `Deputy_gửi_Reporter_Closure.md` | GÓI XÁC NHẬN CLOSURE FT | Lightweight — Reporter KHÔNG cập nhật 05 từ gói này |

> Nếu Fast Track thoát giữa chừng: COO gửi GÓI TRẠNG THÁI (lý do thoát) → Reporter cập nhật 03 → job về Phase 1 bình thường

### CEO giao tiếp với COO (các loại)

| File | Form | Khi nào dùng |
|---|---|---|
| `CEO_gửi_COO.md` | CEO BRIEF | Khởi động dự án mới |
| `CEO_gửi_COO_ChiThi.md` | CEO CHỈ THỊ SAU GATE | Sau khi CEO quyết định ở Gate Plan / Gate Output |
| `CEO_gửi_COO_FastTrack.md` | CEO QUYẾT ĐỊNH FAST TRACK | CEO duyệt / không duyệt đề xuất FT-1 của COO |

### Quy trình sửa prompt (Mục 12A)

| File | Form | Mô tả |
|---|---|---|
| `CEO_gửi_COO_PromptChange.md` | FORM 12A-1 (Tùy chọn) | Dùng khi muốn log yêu cầu chính thức — không bắt buộc |
| `COO_gửi_CEO_PromptChangeProposal.md` | FORM 12A-2 | COO đề xuất bản sửa prompt → CEO (+ QA/Deputy nếu cần) |
| `QADeputy_gửi_CEO_PromptImpactReview.md` | FORM 12A-3 (Optional) | QA/Deputy review tác động → CEO — bỏ qua khi sửa nhỏ cục bộ |
| `CEO_gửi_Reporter_PromptApproval.md` | FORM 12A-4 | CEO duyệt → lệnh cập nhật prompt cho Reporter (+ COO biết) |

> **Quy trình sửa prompt (v8):** CEO phát hiện lỗi → chọn 1 trong 2 đường:
> - Sửa nhỏ, không đổi vai/tuyến/rule chung: CEO sửa tay trực tiếp vào 02_prompt_library.md + ghi Prompt Changelog (không cần 12A-1, không cần 12A-2)
> - Sửa phức tạp: CEO chat COO trực tiếp → COO soạn 12A-2 → QA/Deputy review 12A-3 (nếu ảnh hưởng vai khác) → CEO duyệt/bác → CEO gửi 12A-4 → Reporter cập nhật file → ghi Prompt Changelog
> Nếu prompt sửa thay đổi vai trò hoặc tuyến báo cáo → tự động coi là sửa cấp công ty

## Quy tắc input/output cứng

| Agent | Input nhận từ | Output gửi về |
|---|---|---|
| CEO | — | COO (chính) + QA + Deputy (inform) |
| COO | CEO, P/E (FORM 11E-2 skill gap) | P/E (brief/chỉ thị), QA+Deputy (gói review), Reporter (trạng thái), CEO (FORM 11E-3 Specialist mới) |
| Product | COO, Builder/Specialist NV (FORM 11E-1) | COO (lane plan / FORM 11E-2 skill gap), Engineering (loop nội bộ) |
| Engineering | COO, Product, Builder/Specialist KT (FORM 11E-1) | COO (lane plan / FORM 11E-2 skill gap), Builder/Specialist KT (giao task) |
| Builder | Engineering | Engineering (sub-plan / build report / SKILL LEARNING REPORT / FORM 11E-1) |
| Specialist KT | Engineering | Engineering (output / SKILL LEARNING REPORT / FORM 11E-1) |
| Specialist NV | Product | Product (output / SKILL LEARNING REPORT / FORM 11E-1) |
| QA | CEO (brief), COO (gói review) | Deputy (chính), copy COO |
| Deputy | CEO (brief), QA (report) | CEO (review), Reporter (gói chốt / gói closure) |
| Reporter | Deputy (gói chốt), COO (gói trạng thái) | 5 file dự án chính thức |

> **SKILL LEARNING REPORT** (Đường A — Mục 11E): không tạo file riêng. Builder/Specialist dùng form report hiện có (`Builder_gửi_Engineering.md` / `Specialist_gửi_*.md`) với `Phase: Skill Learning Report` và 3 trường bổ sung: `Skill đã học / Evidence pass/fail / Kết luận`.
