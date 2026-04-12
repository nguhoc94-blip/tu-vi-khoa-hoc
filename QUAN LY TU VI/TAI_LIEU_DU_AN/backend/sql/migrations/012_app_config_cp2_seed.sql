-- CP2 seed baseline (Nhịp 1). disclaimer + privacy: no placeholder per Product.
-- payment_link_label: NEED_PRODUCT_FINAL allowed.

INSERT INTO app_config (config_key, config_value) VALUES
('greeting_love', jsonb_build_object(
    'text', 'Chào bạn, mình là trợ lý tử vi. Hôm nay mình đồng hành cùng bạn về chuyện tình cảm — ấm và không vội.',
    'cp2_pack', 'Nhip1')),
('greeting_career', jsonb_build_object(
    'text', 'Chào bạn, mình là trợ lý tử vi. Mình sẽ cùng bạn nhìn rõ hơn về công việc và định hướng nghề nghiệp.',
    'cp2_pack', 'Nhip1')),
('greeting_general', jsonb_build_object(
    'text', 'Chào bạn, mình là trợ lý tử vi. Bạn muốn bắt đầu từ tổng quan hay một chủ đề đang băn khoăn?',
    'cp2_pack', 'Nhip1')),
('opening_question_love', jsonb_build_object(
    'text', 'Để lập lá số, bạn cho mình họ tên và thời gian sinh (ngày, tháng, năm, giờ, phút) và giới tính nhé.',
    'cp2_pack', 'Nhip1')),
('opening_question_career', jsonb_build_object(
    'text', 'Để xem hướng công việc, mình cần họ tên và thời gian sinh đầy đủ (kể cả phút sinh nếu có).',
    'cp2_pack', 'Nhip1')),
('opening_question_general', jsonb_build_object(
    'text', 'Bạn muốn mình hỏi thêm một chút: bạn đang băn khoăn nhất về tình cảm, công việc, hay hướng đi chung?',
    'cp2_pack', 'Nhip1')),
('opening_question_returning_unpaid', jsonb_build_object(
    'text', 'Chào bạn quay lại. Lần trước bạn đã xem phần miễn phí; bạn muốn đi tiếp phần còn lại hay xem lại tóm tắt?',
    'cp2_pack', 'Nhip1')),
('opening_question_intake_resume', jsonb_build_object(
    'text', 'Mình thấy hồ sơ ngày sinh của bạn còn dang dở. Bạn muốn tiếp tục điền hay chỉnh lại thông tin?',
    'cp2_pack', 'Nhip1')),
('opening_question_paid_repeat', jsonb_build_object(
    'text', 'Chào bạn, cảm ơn bạn đã tin tưởng trước đó. Hôm nay bạn muốn xem thêm phần nào?',
    'cp2_pack', 'Nhip1')),
('cta_primary_after_free_love', jsonb_build_object(
    'text', 'Xem sâu hơn về tình cảm (1 chủ đề sâu)',
    'cp2_pack', 'Nhip1')),
('cta_secondary_after_free_love', jsonb_build_object(
    'text', 'Để sau / tôi cần suy nghĩ thêm',
    'cp2_pack', 'Nhip1')),
('cta_primary_after_free_career', jsonb_build_object(
    'text', 'Xem sâu hơn về công việc (1 chủ đề sâu)',
    'cp2_pack', 'Nhip1')),
('cta_secondary_after_free_career', jsonb_build_object(
    'text', 'Để sau / tôi cần suy nghĩ thêm',
    'cp2_pack', 'Nhip1')),
('cta_primary_after_free_general', jsonb_build_object(
    'text', 'Đi sâu chủ đề bạn đang băn khoăn',
    'cp2_pack', 'Nhip1')),
('cta_secondary_after_free_general', jsonb_build_object(
    'text', 'Để sau / tôi cần suy nghĩ thêm',
    'cp2_pack', 'Nhip1')),
('cta_primary_after_free_returning_unpaid', jsonb_build_object(
    'text', 'Mở phần nội dung đầy đủ (thanh toán thủ công)',
    'cp2_pack', 'Nhip1')),
('cta_secondary_after_free_returning_unpaid', jsonb_build_object(
    'text', 'Tôi muốn xem lại phần đã đọc',
    'cp2_pack', 'Nhip1',
    'event_baseline', 'upsell_secondary_clicked')),
('cta_primary_after_free_paid_repeat', jsonb_build_object(
    'text', 'Xem thêm luận giải / chủ đề tiếp theo',
    'cp2_pack', 'Nhip1')),
('cta_secondary_after_free_paid_repeat', jsonb_build_object(
    'text', 'Tôi cần hỗ trợ từ người',
    'cp2_pack', 'Nhip1')),
('offer_label_love_deep', jsonb_build_object(
    'text', 'Gói nhìn sâu tình cảm (1 chủ đề)',
    'cp2_pack', 'Nhip1')),
('offer_label_career_deep', jsonb_build_object(
    'text', 'Gói nhìn sâu công việc (1 chủ đề)',
    'cp2_pack', 'Nhip1')),
('offer_label_general_deep', jsonb_build_object(
    'text', 'Gói nhìn sâu theo chủ đề bạn chọn',
    'cp2_pack', 'Nhip1')),
('disclaimer_snippet_intake', jsonb_build_object(
    'text', 'Lưu ý: nội dung chỉ mang tính tham khảo, không thay thế tư vấn y khoa, pháp lý hay quyết định cá nhân của bạn.',
    'cp2_pack', 'Nhip1')),
('privacy_notice_snippet', jsonb_build_object(
    'text', 'Dữ liệu bạn nhập trong hội thoại được dùng để lập và giải lá số trong phiên này. Bạn có thể nhắn reset để nhập lại từ đầu.',
    'cp2_pack', 'Nhip1')),
('footer_baseline', jsonb_build_object(
    'text', 'Cảm ơn bạn đã trò chuyện. Nếu cần, nhắn reset để bắt đầu lại.',
    'cp2_pack', 'Nhip1')),
('payment_link_label', jsonb_build_object(
    'text', '[NEED_PRODUCT_FINAL] Mở link thanh toán (Product sẽ cập nhật khi có link chính thức)',
    'cp2_pack', 'Nhip1',
    'placeholder_tag', 'NEED_PRODUCT_FINAL')),
('reactivation_in_window_resume', jsonb_build_object(
    'text', 'Bạn còn dang dở phần nhập ngày sinh — bạn muốn tiếp tục ngay không?',
    'cp2_pack', 'Nhip1')),
('reactivation_in_window_returning', jsonb_build_object(
    'text', 'Bạn có một bản xem miễn phí trước đó. Bạn muốn xem lại hay đi tiếp?',
    'cp2_pack', 'Nhip1')),
('reactivation_in_window_paid_repeat', jsonb_build_object(
    'text', 'Chào bạn quay lại. Bạn muốn xem thêm phần nào hôm nay?',
    'cp2_pack', 'Nhip1')),
('campaign_label_love', jsonb_build_object(
    'text', 'Chiến dịch: Tình cảm',
    'cp2_pack', 'Nhip1')),
('campaign_label_career', jsonb_build_object(
    'text', 'Chiến dịch: Công việc',
    'cp2_pack', 'Nhip1')),
('campaign_label_organic_general', jsonb_build_object(
    'text', 'Chiến dịch: Tổng quan / organic',
    'cp2_pack', 'Nhip1')),
('trust_bridge_new_user_love', jsonb_build_object(
    'text', 'Phần miễn phí giúp bạn nắm khung tổng thể; phần sâu hơn sẽ đi chi tiết vào chuyện tình cảm khi bạn sẵn sàng.',
    'cp2_pack', 'Nhip1')),
('trust_bridge_new_user_career', jsonb_build_object(
    'text', 'Phần miễn phí cho bức tranh tổng thể; phần sâu sẽ đi vào công việc và định hướng khi bạn muốn đi tiếp.',
    'cp2_pack', 'Nhip1')),
('trust_bridge_new_user_general', jsonb_build_object(
    'text', 'Mình sẽ cùng bạn làm rõ chủ đề đang băn khoăn, không ép bạn chọn gói.',
    'cp2_pack', 'Nhip1')),
('trust_bridge_returning_unpaid', jsonb_build_object(
    'text', 'Bạn đã có phần xem trước; phần còn lại giúp đi sâu hơn khi bạn cảm thấy phù hợp.',
    'cp2_pack', 'Nhip1')),
('trust_bridge_intake_resume', jsonb_build_object(
    'text', 'Sau khi có kết quả miễn phí, mình sẽ gợi ý bước tiếp phù hợp, không ép mua.',
    'cp2_pack', 'Nhip1')),
('trust_bridge_paid_repeat', jsonb_build_object(
    'text', 'Cảm ơn bạn đã đồng hành. Hôm nay mình có thể hỗ trợ thêm theo nhu cầu hiện tại của bạn.',
    'cp2_pack', 'Nhip1')),
('intake_resume_qr_resume', jsonb_build_object(
    'text', 'Tiếp tục nhập',
    'cp2_pack', 'Nhip1')),
('intake_resume_qr_edit', jsonb_build_object(
    'text', 'Sửa lại thông tin',
    'cp2_pack', 'Nhip1'))
ON CONFLICT (config_key) DO UPDATE SET
    config_value = EXCLUDED.config_value,
    updated_at = NOW();
