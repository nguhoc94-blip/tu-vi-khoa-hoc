# Admin Panel cục bộ (Streamlit)

Chạy **trên máy local**, cùng repo backend. Không deploy public; không đăng nhập đa user.

## Hai lệnh bắt buộc (theo scope COO)

```bash
pip install streamlit
streamlit run admin.py
```

*(Trên Windows PowerShell, có thể dùng cùng hai dòng; đảm bảo đang đứng trong thư mục `backend`.)*

**Gợi ý thêm:** có thể cài toàn bộ phụ thuộc một lần:

```bash
pip install -r requirements.txt
```

Sau đó vẫn dùng **`streamlit run admin.py`** để mở panel (lệnh thứ 2 ở trên không thay đổi).

## Trước khi mở panel

1. Sao chép `.env.example` → `.env` trong thư mục `backend` (hoặc điền trực tiếp trong Wizard).
2. Bắt buộc có `MESSENGER_PART_2_BANK_BLOCK` và `MESSENGER_PART_3_CEO_NOTE` — bot ghép tin nhắn cuối đọc từ đây.
3. Backend API nên chạy ở **http://localhost:8000** (mặc định nút “Kiểm tra kết nối”). `BACKEND_BASE_URL` **không** nằm trong 6 ô Wizard; chỉ override qua `.env` nếu cần.

## Tab trong panel

- **Setup lần đầu:** 6 biến + Lưu + Kiểm tra `/health`.
- **Vận hành:** `/health`, sửa bank/CEO, banner nhắc restart, lệnh restart copy-paste, log tail (đã lọc secret).

## Smoke nhanh

1. `uvicorn app.main:app --reload --port 8000` (terminal 1, trong `backend`).
2. `streamlit run admin.py` (terminal 2).
3. Wizard → Lưu → thấy banner restart → restart uvicorn → gửi thử Messenger / kiểm tra footer.
