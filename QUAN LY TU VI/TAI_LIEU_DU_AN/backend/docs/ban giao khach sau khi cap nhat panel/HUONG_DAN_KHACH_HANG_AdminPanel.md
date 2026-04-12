## HƯỚNG DẪN KHÁCH HÀNG — ADMIN PANEL CỤC BỘ
Từ: COO
Gửi: Khách hàng
Ngày: 2026-04-08
Loại: handoff-guide
---

# 1. Mục đích
Anh/chị dùng **Admin Panel cục bộ** để tự cấu hình và vận hành TuVi Messenger Bot mà **không cần sửa file `.env` bằng tay**.

Admin Panel này chạy **trên chính máy của anh/chị**.

---

# 2. Anh/chị sẽ dùng để làm gì
Có 2 việc chính:

## A. Cấu hình lần đầu
Anh/chị sẽ mở giao diện web để nhập các thông tin cần thiết:
- OpenAI API Key
- Facebook Page Access Token
- Facebook Verify Token
- Database URL
- Nội dung bank block
- Nội dung lời nhắn cuối

Sau đó bấm:
- **Lưu cấu hình**
- **Kiểm tra kết nối**

## B. Vận hành hằng ngày
Anh/chị có thể:
- xem bot đang hoạt động hay không
- sửa lại **bank block**
- sửa lại **lời nhắn cuối**
- xem log cơ bản
- copy lệnh restart server khi cần

---

# 3. Bước đầu tiên anh/chị cần làm
Mở terminal trong thư mục backend của dự án, rồi chạy lần lượt **2 lệnh** sau:

```bash
pip install streamlit
streamlit run admin.py
```

Sau khi chạy xong, trình duyệt sẽ mở giao diện Admin Panel local.

---

# 4. Cách dùng Setup Wizard (lần đầu)
Trong giao diện Admin Panel:

## Bước 1
Điền đủ 6 ô:
1. `OPENAI_API_KEY`
2. `FB_PAGE_ACCESS_TOKEN`
3. `FB_VERIFY_TOKEN`
4. `DATABASE_URL`
5. **Bank block**
6. **CEO note** / lời nhắn cuối

## Bước 2
Bấm **Lưu cấu hình**

Kết quả đúng là:
- hệ thống lưu cấu hình vào file `.env`
- các giá trị mới được ghi lại thành công

## Bước 3
Bấm **Kiểm tra kết nối**

Kết quả đúng là:
- hệ thống kiểm tra kết nối tới backend local
- nếu backend đang chạy đúng, màn hình sẽ báo kết nối thành công

---

# 5. Cách dùng Admin Panel hằng ngày
Sau khi đã cấu hình lần đầu, anh/chị dùng giao diện này để:

## Xem trạng thái bot
- nhìn phần **trạng thái**
- nếu backend đang chạy đúng, panel sẽ báo bot đang hoạt động

## Sửa lời nhắn cuối
Anh/chị có thể sửa:
- **bank block**
- **CEO note**

Sau khi bấm lưu:
- màn hình sẽ hiện **nhắc restart**
- anh/chị cần restart backend để bot dùng giá trị mới

## Xem log cơ bản
- panel có phần log để anh/chị kiểm tra nhanh
- log đã được làm ở mức an toàn cơ bản để tránh lộ raw secret

## Restart server
- panel sẽ hiển thị **lệnh restart dạng copy-paste**
- anh/chị chỉ cần copy lệnh đó và chạy lại trong terminal

---

# 6. Khi nào cần restart
Anh/chị **phải restart backend** sau khi:
- đổi **bank block**
- đổi **CEO note**
- đổi các giá trị cấu hình khác trong panel

Nếu không restart, bot có thể vẫn dùng giá trị cũ.

---

# 7. Nếu anh/chị muốn kiểm tra nhanh là đã đúng chưa
Sau khi sửa cấu hình và restart:

## Kiểm tra 1
Vào lại Admin Panel → xem trạng thái bot

## Kiểm tra 2
Thử thao tác theo flow bot bình thường

## Kiểm tra 3
Xác nhận phần tin nhắn cuối đã dùng đúng:
1. nội dung chính
2. bank block mới
3. lời nhắn cuối mới

---

# 8. 3 file anh/chị cần biết
Nếu cần đọc kỹ hơn, dùng 3 file này theo đúng thứ tự:

1. `docs/admin_panel_local.md`
2. `docs/config_checklist.md` hoặc `.env.example` để đối chiếu cấu hình
3. `docs/runbook_basic.md`

---

# 9. Những gì anh/chị KHÔNG cần làm
Anh/chị không cần:
- sửa code
- sửa engine tử vi
- chỉnh DB schema
- chỉnh route HTTP
- deploy lên server public
- cấu hình multi-user

---

# 10. Khi nào nên nhờ Engineering hỗ trợ
Anh/chị nên nhờ hỗ trợ nếu gặp một trong các trường hợp sau:
- đã bấm **Lưu cấu hình** nhưng không lưu được
- bấm **Kiểm tra kết nối** mà backend không phản hồi
- restart xong nhưng bot vẫn dùng giá trị cũ
- không mở được Admin Panel bằng 2 lệnh ở trên
- log báo lỗi mà anh/chị không hiểu cách xử lý

---

# 11. Tóm tắt siêu ngắn
Anh/chị chỉ cần nhớ:

1. Mở terminal trong thư mục backend
2. Chạy:
   - `pip install streamlit`
   - `streamlit run admin.py`
3. Điền cấu hình
4. Bấm **Lưu cấu hình**
5. Bấm **Kiểm tra kết nối**
6. Khi đổi nội dung trong panel → **restart backend**
