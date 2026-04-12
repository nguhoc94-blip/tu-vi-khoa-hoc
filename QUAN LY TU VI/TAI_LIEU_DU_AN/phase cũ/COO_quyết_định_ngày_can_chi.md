## COO QUYẾT ĐỊNH NỘI BỘ — CHỐT SOURCE OF TRUTH NGÀY CAN CHI
Từ: COO
Gửi: Product + Engineering + QA + Deputy
Ngày: 2026-04-07
Loại: decision / scope-closure
---
Quyết định:
COO tự chốt dependency còn mở của `ngày can chi` ở cấp Phase 1, không đẩy ngược lên CEO và không mở lại Product loop chỉ để xin thêm scope.

## 1. Kết luận chốt
Source of truth cho `ngày can chi` dùng trong `tuvi_can_chi_engine_v1` được khóa như sau:

### 1.1. Nguồn ngày đầu vào
- Luôn dùng `solar date normalized` dạng Gregorian dân dụng: `year-month-day`
- Nếu input ban đầu là lunar:
  - phải quy đổi ra solar trước bằng `tuvi_calendar_engine_v1`
  - sau đó mới tính `ngày can chi`
- Không dùng giờ để đổi ngày
- Giữ nguyên rule đã khóa:
  - không tự đổi ngày ở khung 23:00–23:59
  - chỉ map giờ sang địa chi giờ

### 1.2. Công thức chuẩn nội bộ
- Tính `JDN` (Julian Day Number dạng số nguyên cho civil date Gregorian) từ `solar date normalized`
- Định nghĩa vòng 60 hoa giáp theo index 0-based:
  - `0 = giap_ty`
  - ...
  - `7 = tan_mui`
  - ...
  - `59 = quy_hoi`
- Công thức cố định cho `day_can_chi_index`:
  - `day_can_chi_index = (JDN + 49) mod 60`

### 1.3. Anchor calibration khóa cứng
Anchor dùng để khóa hằng số `49`:
- `solar date = 1911-01-01`
- `day_can_chi = tan_mui`

Anchor này lấy từ golden sample trong nguồn dự án:
- file `bang an sao, menh cuc.txt` thể hiện:
  - năm dương lịch 1911
  - tháng 1
  - ngày 1
  - ngày can chi là `Tân Mùi`

## 2. Lý do COO chốt theo hướng này
- Rulebook đã khóa nguyên tắc:
  - ngày can chi phải tính từ `solar date normalized`
  - phải dùng một công thức sexagenary cố định
  - không để Engineering tự chọn epoch/hằng số
- Product đã giữ ownership đúng và nêu rõ đây là điểm cần COO chốt
- Engineering đã giữ đúng tuyến, chưa tự vượt quyền và chỉ treo dependency
- Golden sample hiện có đủ để COO khóa anchor nội bộ mà không cần mở thêm dependency vendor/fork

## 3. Hệ quả triển khai
### 3.1. Với Engineering
- Không còn dependency mở về source of truth ngày can chi
- Engineering phải implement đúng công thức nội bộ trên
- Không được thay bằng thư viện ngoài làm nguồn chuẩn cuối
- Có thể vẫn dùng helper code nội bộ cho JDN, nhưng output phải do công thức này quyết định

### 3.2. Với Product
- Không cần mở lại scope loop cho ngày can chi
- Lane Product được coi là đã đủ scope ở điểm này

### 3.3. Với QA
- QA review theo công thức đã khóa:
  - cùng `solar date normalized` phải ra cùng `day_can_chi`
  - sample 1911-01-01 phải ra `tan_mui`

## 4. Test bắt buộc bổ sung
Engineering phải thêm ít nhất các check sau trong plan/test:
1. Anchor test:
   - `1911-01-01 -> tan_mui`
2. Determinism test:
   - cùng input normalized -> cùng `day_can_chi_index`
3. No-day-shift test:
   - input `23:30` không làm đổi ngày; chỉ đổi địa chi giờ
4. Lunar-input path test:
   - lunar input -> convert ra solar -> tính `day_can_chi` từ solar normalized

## 5. Trạng thái dependency
- `ceo_note` literal text: đã đóng
- `ngày can chi` source of truth: đã đóng bởi quyết định COO này

## 6. Lệnh tiếp theo
- Dùng quyết định này để cập nhật master plan Phase 1
- QA + Deputy review bản master plan đã cập nhật
- Chưa mở Phase 2 khi chưa có Gate Plan của CEO
