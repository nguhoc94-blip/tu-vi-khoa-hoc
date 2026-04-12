-- CP3 wording/policy seed (Nhịp 2). Published content in config_value; runtime reads published only.
-- payment_link_placeholder_final: NEED_PRODUCT_FINAL; payment_link_label_final: publish-ready label text.

INSERT INTO app_config (config_key, config_value) VALUES
('confirmation_birthdata_summary', jsonb_build_object(
    'text', 'Mình chốt lại thông tin để xem cho bạn chính xác hơn nhé: [tóm tắt dữ liệu]. Nếu đúng rồi mình xem tiếp, còn nếu chưa đúng bạn sửa lại giúp mình ở đây.',
    'cp3', true)),
('confirmation_birthdata_yes', jsonb_build_object('text', 'Đúng rồi', 'cp3', true)),
('confirmation_birthdata_edit', jsonb_build_object('text', 'Sửa lại thông tin', 'cp3', true)),
('confirmation_calendar_prompt', jsonb_build_object(
    'text', 'Ngày sinh này là âm lịch hay dương lịch vậy bạn?', 'cp3', true)),
('confirmation_calendar_solar', jsonb_build_object('text', 'Dương lịch', 'cp3', true)),
('confirmation_calendar_lunar', jsonb_build_object('text', 'Âm lịch', 'cp3', true)),
('confirmation_gender_prompt', jsonb_build_object(
    'text', 'Để mình chốt đúng lá số, bạn cho mình xác nhận giới tính nhé.', 'cp3', true)),
('confirmation_gender_male', jsonb_build_object('text', 'Nam', 'cp3', true)),
('confirmation_gender_female', jsonb_build_object('text', 'Nữ', 'cp3', true)),
('confirmation_birthhour_prompt', jsonb_build_object(
    'text', 'Nếu nhớ gần đúng giờ sinh, bạn cứ chọn mốc gần nhất để mình nhìn sát hơn nhé.', 'cp3', true)),
('confirmation_missing_field_resume', jsonb_build_object(
    'text', 'Bạn còn thiếu một chút thông tin để mình xem tiếp chính xác hơn. Mình đi tiếp từ phần còn thiếu nhé?', 'cp3', true)),
('confirmation_missing_field_retry', jsonb_build_object(
    'text', 'Không sao, bạn nhập lại giúp mình theo cách bạn nhớ rõ nhất, mình sẽ chốt lại với bạn trước khi xem.', 'cp3', true)),
('confirmation_profile_switch_check', jsonb_build_object(
    'text', 'Mình đang hiểu là bạn muốn xem cho hồ sơ hiện tại. Nếu bạn đang hỏi cho người khác, nói mình biết để mình đổi đúng người nhé.', 'cp3', true)),
('confirmation_pre_chart_safe_close', jsonb_build_object('text', 'Ổn rồi, mình xem tiếp cho bạn ngay đây.', 'cp3', true)),

('trust_bridge_final_love', jsonb_build_object(
    'text', 'Phần mình vừa nhìn là lớp tổng quan để bạn thấy đúng nhịp tình cảm của mình. Nếu muốn đi sâu hơn, mình có thể mở riêng phần tình duyên để nhìn rõ điều dễ lặp lại và cách ứng xử phù hợp hơn với hoàn cảnh hiện tại của bạn.',
    'cp3', true)),
('trust_bridge_final_career', jsonb_build_object(
    'text', 'Phần vừa rồi giúp bạn thấy nhịp chung về công việc và hướng đi. Nếu bạn cần nhìn kỹ hơn phần sự nghiệp, mình có thể mở sâu riêng chủ đề này để tách rõ điểm mạnh, điểm nghẽn và hướng nên ưu tiên trước.',
    'cp3', true)),
('trust_bridge_final_general', jsonb_build_object(
    'text', 'Mình đã chạm vào bức tranh tổng thể để bạn có cảm giác đúng người đúng chuyện. Nếu bạn muốn, mình có thể đi sâu riêng phần đang làm bạn băn khoăn nhất để không phải nói dàn trải.',
    'cp3', true)),
('trust_bridge_final_returning_unpaid', jsonb_build_object(
    'text', 'Lần trước mình đã mở tổng quan cho bạn rồi, nên bây giờ mình có thể đi nhanh hơn vào phần còn dang dở hoặc phần bạn đang muốn hiểu kỹ hơn.',
    'cp3', true)),
('trust_bridge_final_intake_resume', jsonb_build_object(
    'text', 'Giờ dữ liệu của bạn đã đủ chắc để mình nhìn tiếp. Nếu muốn, mình có thể đi sâu luôn vào phần bạn cần nhất thay vì dừng ở mức tổng quan.',
    'cp3', true)),
('trust_bridge_final_paid_repeat', jsonb_build_object(
    'text', 'Bạn đã có một lớp nhìn trước đó rồi, nên lần này mình không cần quay lại từ đầu. Mình có thể mở tiếp phần phù hợp hơn với nhu cầu hiện tại của bạn.',
    'cp3', true)),

('cta_primary_final_love', jsonb_build_object('text', 'Xem sâu chuyện tình cảm này', 'cp3', true)),
('cta_secondary_final_love', jsonb_build_object('text', 'Nói tiếp điều tôi đang lo', 'cp3', true)),
('cta_primary_final_career', jsonb_build_object('text', 'Xem sâu phần công việc', 'cp3', true)),
('cta_secondary_final_career', jsonb_build_object('text', 'Hỏi tiếp hướng đi phù hợp', 'cp3', true)),
('cta_primary_final_general', jsonb_build_object('text', 'Xem sâu phần tôi quan tâm nhất', 'cp3', true)),
('cta_secondary_final_general', jsonb_build_object('text', 'Nói rõ điều tôi đang phân vân', 'cp3', true)),
('cta_primary_final_returning_unpaid', jsonb_build_object('text', 'Xem tiếp phần đang dở', 'cp3', true)),
('cta_secondary_final_returning_unpaid', jsonb_build_object('text', 'Xem sâu chủ đề này', 'cp3', true)),
('cta_primary_final_intake_resume', jsonb_build_object('text', 'Tiếp tục lập lá số', 'cp3', true)),
('cta_secondary_final_intake_resume', jsonb_build_object('text', 'Sửa thông tin trước khi xem', 'cp3', true)),
('cta_primary_final_paid_repeat', jsonb_build_object('text', 'Mở phần phù hợp tiếp theo', 'cp3', true)),
('cta_secondary_final_paid_repeat', jsonb_build_object('text', 'Để mình ghi nhận nhu cầu hỗ trợ thêm', 'cp3', true)),

('footer_final_common', jsonb_build_object(
    'text', 'Bạn có thể đi tiếp phần đang cần nhất, mình sẽ giữ cuộc trò chuyện này gọn và đúng trọng tâm.', 'cp3', true)),
('payment_pre_cta_final', jsonb_build_object(
    'text', 'Nếu bạn muốn đi sâu hơn ngay lúc này, mình để sẵn bước tiếp theo ở đây.', 'cp3', true)),
('payment_link_label_final', jsonb_build_object('text', 'Mở link thanh toán', 'cp3', true)),
('payment_link_placeholder_final', jsonb_build_object(
    'text', '[NEED_PRODUCT_FINAL] Mở link thanh toán (placeholder — thay khi có link thật)',
    'cp3', true,
    'placeholder_tag', 'NEED_PRODUCT_FINAL')),

('premium_copy_love', jsonb_build_object(
    'text', 'Bước tiếp theo phù hợp nhất lúc này là mở sâu riêng phần tình cảm để nhìn kỹ hơn điều bạn đang vướng.', 'cp3', true)),
('premium_copy_career', jsonb_build_object(
    'text', 'Bước tiếp theo phù hợp nhất lúc này là mở sâu riêng phần công việc để nhìn rõ hướng ưu tiên hơn.', 'cp3', true)),
('premium_copy_general', jsonb_build_object(
    'text', 'Mình có thể mở sâu riêng đúng phần bạn đang quan tâm nhất để không phải nói dàn trải.', 'cp3', true)),
('premium_trigger_final', jsonb_build_object(
    'text', 'Nếu bạn cần đi sâu theo hoàn cảnh rất riêng hoặc muốn có người hỗ trợ tiếp, mình có thể ghi nhận nhu cầu đó cho bạn.', 'cp3', true)),
('premium_handoff_prompt_final', jsonb_build_object(
    'text', 'Bạn để lại nhu cầu chính ở đây, mình sẽ ghi nhận để bước hỗ trợ tiếp theo bám đúng điều bạn đang cần.', 'cp3', true)),
('premium_expectation_setting_final', jsonb_build_object(
    'text', 'Ở bước này mình ghi nhận nhu cầu và ngữ cảnh của bạn trước. Nếu cần chuyển tiếp hỗ trợ, phần đó sẽ được xử lý theo khả năng vận hành hiện có, nên mình chưa hứa thời gian phản hồi cụ thể ngay tại đây.',
    'cp3', true)),
('premium_secondary_cta_final', jsonb_build_object('text', 'Để mình ghi nhận nhu cầu hỗ trợ thêm', 'cp3', true)),

('social_proof_placeholder_policy_final', jsonb_build_object(
    'text', 'Chỉ hiển thị social proof khi đã có asset thật được Product duyệt. Nếu chưa có, block này giữ ở draft/preview và không publish ra user.',
    'cp3', true)),
('social_proof_preview_label_final', jsonb_build_object(
    'text', '[NEED_PRODUCT_FINAL] Chờ asset social proof thật do Product xác nhận',
    'cp3', true,
    'placeholder_tag', 'NEED_PRODUCT_FINAL')),
('social_proof_publish_snippet_template', jsonb_build_object(
    'text', 'Phản hồi thật từ người dùng trước đó — hiển thị theo asset đã được duyệt.', 'cp3', true)),
('social_proof_placement_rule_final', jsonb_build_object(
    'text', 'Ưu tiên sau trust bridge hoặc trước CTA chính; không chen opening; không trước free result.',
    'cp3', true)),
('social_proof_blocking_rule_final', jsonb_build_object(
    'text', 'Không có asset thật thì chỉ preview trong admin, không publish user.', 'cp3', true)),

('campaign_label_final_love', jsonb_build_object('text', 'Tình duyên', 'cp3', true)),
('campaign_label_final_career', jsonb_build_object('text', 'Công việc', 'cp3', true)),
('campaign_label_final_organic_general', jsonb_build_object('text', 'Tổng quan', 'cp3', true)),

('feature_social_proof_publish_allowed', jsonb_build_object('allowed', false, 'cp3', true))
ON CONFLICT (config_key) DO UPDATE SET
    config_value = EXCLUDED.config_value,
    updated_at = NOW();
