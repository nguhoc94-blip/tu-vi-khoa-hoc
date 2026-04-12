GỬI: Product / Engineering
TỪ: TuVi Fortune Specialist
LOẠI: rulebook
NGÀY: 2026-04-06

# RUILE NỘI BỘ — TUVI_MVP_V1
Trạng thái: CHỐT GỬI PRODUCT
Rule set id: tuvi_mvp_v1
Timezone mặc định: Asia/Bangkok

## 0. Mục đích
Tài liệu này khóa cứng rule domain nội bộ cho engine lá số tử vi MVP v1 trong phạm vi:
- Mệnh
- Thân
- Cục
- 12 houses
- 14 chính tinh
- đại vận

Tài liệu này dùng để:
- Product khóa spec
- Engineering thi công
- QA đối chiếu output domain

## 1. Nguồn căn cứ
1. `ruile.txt`
2. `bang an sao, menh cuc.txt`
3. `image.png`
4. `Product_gửi_SpecialistNV.md`
5. `TuVi_Fortune_Specialist_Prompt.md`
6. `Văn bản đã dán (1).txt` — bản chốt rule bổ sung từ Product

## 2. Nguyên tắc cao nhất
- Chỉ dùng 1 rule set duy nhất: `tuvi_mvp_v1`
- Deterministic: cùng input chuẩn hóa phải ra cùng chart
- Không trộn trường phái
- Không tự đoán rule ngoài tài liệu đã chốt
- Không tự thêm sao ngoài phạm vi MVP
- Field chưa support phải để rỗng có chủ đích hoặc `[]`
- Không gọi API ngoài để lấy rule sống
- Nếu có dùng thư viện ngoài thì phải vendor/fork vào repo và output vẫn phải theo contract nội bộ

## 3. Phạm vi MVP v1
### 3.1. Có trong MVP
- normalize input
- solar/lunar conversion
- can chi
- mệnh
- thân
- cục
- 12 houses
- 14 chính tinh
- major fortunes

### 3.2. Ngoài phạm vi MVP
- phụ tinh
- hóa lộc/quyền/khoa/kỵ
- trường sinh
- tiểu hạn
- lưu niên
- text luận giải
- chấm điểm

## 4. Input contract
Engine nhận đúng các field user-facing sau:
- `full_name`
- `birth_day`
- `birth_month`
- `birth_year`
- `birth_hour`
- `birth_minute`
- `gender`
- `calendar_type`
- `is_leap_lunar_month`

System gán cứng:
- `timezone = Asia/Bangkok`
- `rule_set_id = tuvi_mvp_v1`

## 5. Calendar engine
Tên chuẩn nội bộ:
- `tuvi_calendar_engine_v1`
- `calendar_engine_version = 1.0.0`

Nhiệm vụ:
- `solar -> lunar`
- `lunar -> solar`
- support `is_leap_lunar_month`
- cùng input phải ra cùng output

Ràng buộc:
- không gọi API ngoài
- không đổi package theo môi trường
- nếu dùng thư viện ngoài thì phải vendor/fork vào repo
- toàn bộ output vẫn mang contract của `tuvi_calendar_engine_v1`

## 6. Rule giờ sinh
Dùng giờ dân dụng hiện đại, chia theo 12 địa chi, mỗi chi 2 giờ:

- `ty = 23:00–00:59`
- `suu = 01:00–02:59`
- `dan = 03:00–04:59`
- `mao = 05:00–06:59`
- `thin = 07:00–08:59`
- `ti = 09:00–10:59`
- `ngo = 11:00–12:59`
- `mui = 13:00–14:59`
- `than = 15:00–16:59`
- `dau = 17:00–18:59`
- `tuat = 19:00–20:59`
- `hoi = 21:00–22:59`

Cấm:
- không dùng giờ Mặt Trời trong MVP v1

## 7. Rule ngày sinh
- Giữ nguyên ngày dân dụng user nhập
- Không tự đổi ngày ở khung 23:00–23:59
- Nếu sinh lúc 23:30 thì chỉ map giờ sang `ty`, không đẩy ngày sang hôm sau

## 8. Rule lịch
### 8.1. Khi `calendar_type = solar`
- quy đổi sang lunar
- ép `is_leap_lunar_month = false`

### 8.2. Khi `calendar_type = lunar`
- bắt buộc có `is_leap_lunar_month = true|false`
- quy đổi sang solar để đối chiếu nội bộ

## 9. Can chi engine
Tên chuẩn nội bộ:
- `tuvi_can_chi_engine_v1`
- `can_chi_engine_version = 1.0.0`

### 9.1. Năm can chi
- lấy theo năm âm lịch sau khi normalize bằng `tuvi_calendar_engine_v1`

### 9.2. Tháng can chi
- lấy theo tháng âm lịch
- thiên can tháng khởi bằng Ngũ Hổ Độn:
  - Giáp/Kỷ -> Bính Dần
  - Ất/Canh -> Mậu Dần
  - Bính/Tân -> Canh Dần
  - Đinh/Nhâm -> Nhâm Dần
  - Mậu/Quý -> Giáp Dần
- từ Dần đếm thuận 12 tháng, can tăng tuần tự

### 9.3. Ngày can chi
- tính từ solar date normalized bằng một công thức sexagenary cố định trong `tuvi_can_chi_engine_v1`
- không để Engineering tự chọn hằng số/epoch

### 9.4. Giờ can chi
- địa chi giờ dùng mapping giờ dân dụng ở mục 6
- thiên can giờ tính theo Ngũ Thử Độn từ can ngày:
  - Giáp/Kỷ -> Giáp Tý
  - Ất/Canh -> Bính Tý
  - Bính/Tân -> Mậu Tý
  - Đinh/Nhâm -> Canh Tý
  - Mậu/Quý -> Nhâm Tý
- từ giờ Tý đếm thuận qua 12 chi giờ

## 10. Rule an Mệnh
1. Từ `Dần = tháng 1`
2. Đếm thuận đến tháng sinh âm lịch
3. Từ vị trí đó lấy `Tý` làm mốc giờ
4. Đếm nghịch đến giờ sinh
5. Vị trí dừng = `menh_position`

Output:
- `menh_position` là 1 trong 12 địa chi

## 11. Rule an Thân
1. Cùng điểm gốc với an Mệnh
2. Từ mốc `Tý`
3. Đếm thuận đến giờ sinh
4. Vị trí dừng = `than_position`

Output:
- `than_position` là 1 trong 12 địa chi

## 12. Rule âm dương + giới tính
Can dương:
- `giap`
- `binh`
- `mau`
- `canh`
- `nham`

Can âm:
- `at`
- `dinh`
- `ky`
- `tan`
- `quy`

Mapping:
- dương + nam = `duong_nam`
- âm + nữ = `am_nu`
- âm + nam = `am_nam`
- dương + nữ = `duong_nu`

Output:
- `am_duong_gender_group`

## 13. Rule Cục
Output chuẩn chỉ được phép là:
- `thuy_2`
- `moc_3`
- `kim_4`
- `tho_5`
- `hoa_6`

### 13.1. Rule khóa cứng
Cục = ngũ hành nạp âm của “can-chi cung Mệnh”, rồi map sang số Cục.

Mapping:
- Thủy -> `thuy_2`
- Mộc -> `moc_3`
- Kim -> `kim_4`
- Thổ -> `tho_5`
- Hỏa -> `hoa_6`

### 13.2. Cách tạo bảng tra Cục trong engine
1. an thiên can 12 cung bằng Ngũ Hổ Độn, lấy Dần làm gốc
2. xác định `menh_position`
3. lấy đúng cặp `stem.branch` tại cung Mệnh
4. tra nạp âm của cặp đó
5. map nạp âm sang 5 loại Cục ở trên

### 13.3. Kết luận implementation
Không đóng băng bảng 10 x 12 thủ công.
Chỉ cần đóng băng:
- quy tắc an can cung
- bảng nạp âm 60 hoa giáp
- mapping ngũ hành -> số Cục

## 14. 12 houses
Fixed order của `house_code`:
1. `menh`
2. `phu_mau`
3. `phuc_duc`
4. `dien_trach`
5. `quan_loc`
6. `no_boc`
7. `thien_di`
8. `tat_ach`
9. `tai_bach`
10. `tu_tuc`
11. `phu_the`
12. `huynh_de`

Mỗi house bắt buộc có:
- `house_index`
- `house_code`
- `branch`
- `is_menh_house`
- `is_than_house`
- `main_stars`

Optional:
- `secondary_stars`

Quy ước:
- luôn đủ 12 houses
- `main_stars` luôn là array
- `secondary_stars` mặc định là `[]`

### 14.1. Rule gán branch cho 12 houses
- `houses[0].branch = menh_position`
- từ đó đếm thuận theo vòng 12 địa chi
- mỗi house tiếp theo lấy branch kế tiếp

Pseudo-rule:
- `menh = menh_position`
- `phu_mau = menh_position + 1`
- `phuc_duc = menh_position + 2`
- ...
- `huynh_de = menh_position + 11`
- tính theo modulo 12

## 15. 14 chính tinh
Chỉ support đúng 14 chính tinh sau:
- `tu_vi`
- `thien_co`
- `thai_duong`
- `vu_khuc`
- `thien_dong`
- `liem_trinh`
- `thien_phu`
- `thai_am`
- `tham_lang`
- `cu_mon`
- `thien_tuong`
- `thien_luong`
- `that_sat`
- `pha_quan`

Quy ước:
- mọi sao ngoài danh sách trên không được đưa vào `main_stars`
- `secondary_stars = []` trong MVP

### 15.1. Bước 1: an sao Tử Vi
Dùng công thức theo ngày sinh âm lịch + số Cục:

- tìm `a` nhỏ nhất sao cho `(lunar_day + a) / cuc_number = b` là số nguyên
- từ cung `Dần = 1`, đếm thuận đến `b`
- nếu `a` là lẻ -> lùi `a` cung
- nếu `a` là chẵn -> tiến `a` cung
- cung dừng là vị trí `tu_vi`

### 15.2. Bước 2: an 5 sao còn lại của chòm Tử Vi
Từ vị trí `tu_vi`, đặt:
- `thien_co = tu_vi - 1`
- `thai_duong = tu_vi - 3`
- `vu_khuc = tu_vi - 4`
- `thien_dong = tu_vi - 5`
- `liem_trinh = tu_vi - 8`

(mod 12)

### 15.3. Bước 3: an Thiên Phủ
- `thien_phu = mirror(tu_vi, axis = Dan-Than)`

Quy ước implementation:
- mirror qua trục Dần–Thân nghĩa là lấy cung đối xứng của `tu_vi` trên trục Dần–Thân theo contract nội bộ đã chốt
- Engineering phải implement đúng 1 hàm cố định cho phép biến đổi này và dùng thống nhất trong toàn bộ engine

### 15.4. Bước 4: an 7 sao còn lại của chòm Thiên Phủ
Từ `thien_phu`, đếm thuận:
- `thai_am = thien_phu + 1`
- `tham_lang = thien_phu + 2`
- `cu_mon = thien_phu + 3`
- `thien_tuong = thien_phu + 4`
- `thien_luong = thien_phu + 5`
- `that_sat = thien_phu + 6`
- `pha_quan = thien_phu - 2`

(mod 12)

## 16. Major fortunes (Đại vận)
### 16.1. Hướng chạy
- `duong_nam`, `am_nu` -> `forward`
- `am_nam`, `duong_nu` -> `backward`

### 16.2. Tuổi mở đại vận đầu
- `age_start_first = cuc_number`
- `age_end_first = cuc_number + 9`

### 16.3. House của từng đại vận
- đại vận đầu khởi tại cung Mệnh
- nếu `forward`:
  - `index 0` ở Mệnh
  - `index 1` ở house kế tiếp
  - `index 2` ở house kế tiếp nữa
- nếu `backward`:
  - `index 0` ở Mệnh
  - `index 1` ở house liền trước
  - `index 2` ở house liền trước nữa

### 16.4. Schema mỗi đại vận
Mỗi record bắt buộc có:
- `index`
- `age_start`
- `age_end`
- `house_index`
- `house_code`
- `branch`
- `main_stars_snapshot`

### 16.5. Công thức tuổi
- `age_start(i) = cuc_number + i*10`
- `age_end(i) = age_start(i) + 9`

### 16.6. Current major fortune index
- nếu không có `current_age_override` -> `null`
- nếu có:
  - nếu `current_age < cuc_number` -> `null`
  - ngược lại:
    - `idx = floor((current_age - cuc_number)/10)`
    - clamp vào khoảng `0..11`

## 17. Chart JSON thật cần trả ra
### 17.1. Nhóm bắt buộc
- `schema_version`
- `rule_set_id`
- `timezone`
- `input_normalized`
- `conversion`
- `chart_metadata`
- `houses`
- `major_fortunes`
- `validation`

### 17.2. current_context nên có
- `as_of_date`
- `current_age`
- `current_major_fortune_index`

## 18. Acceptance outputs tối thiểu
### 18.1. Input normalized
Phải có:
- input gốc
- input chuẩn hóa
- timezone
- rule_set_id
- kết quả quy đổi lịch dùng cho tính toán

### 18.2. Houses
- đủ 12 houses
- đúng fixed order
- mỗi house có đủ field bắt buộc
- `secondary_stars = []`

### 18.3. Main stars
- chỉ chứa sao thuộc danh sách 14 chính tinh
- không tự thêm phụ tinh
- cùng input chuẩn hóa phải ra cùng vị trí sao

### 18.4. Major fortunes
- đủ 12 record
- tuổi bắt đầu đúng theo số Cục
- chiều chạy đúng theo `am_duong_gender_group`
- house và branch của từng record khớp direction đã chốt

### 18.5. Determinism
- cùng input chuẩn hóa phải ra cùng chart JSON
- không đổi output giữa các môi trường chỉ vì khác package hay API ngoài

## 19. Thứ tự xử lý chuẩn trong engine
1. nhận input user-facing
2. validate required fields
3. normalize types và values
4. gán timezone, rule_set_id
5. validate chéo calendar_type và leap month
6. quy đổi solar/lunar
7. tính can chi năm/tháng/ngày/giờ
8. tính `menh_position`
9. tính `than_position`
10. an can 12 cung
11. tính `cuc`
12. tính `am_duong_gender_group`
13. tính `major_fortune_direction`
14. khởi tạo 12 houses
15. gắn `branch` cho 12 houses
16. an 14 chính tinh
17. gắn `is_menh_house`, `is_than_house`
18. sinh `major_fortunes`
19. tính `current_major_fortune_index` nếu có override
20. chạy validation cuối
21. trả chart JSON thật

## 20. Validation bắt buộc
- đủ required input fields
- calendar_type và leap month hợp lệ
- luôn đủ 12 houses
- mỗi house có `main_stars` dạng array
- `secondary_stars` luôn là `[]` trong MVP
- `cuc` phải thuộc 1 trong 5 output chuẩn
- chỉ được có 14 chính tinh trong `main_stars`
- cùng input chuẩn hóa phải ra cùng output

## 21. Các nguyên tắc cấm
Không được:
- trộn nhiều trường phái trong một chart
- tự đổi ngày ở 23:00–23:59
- dùng giờ Mặt Trời trong v1
- tự thêm sao ngoài phạm vi đã chốt
- sinh text luận giải trong engine
- gọi API ngoài làm thay đổi kết quả domain

## 22. Golden sample usage
`bang an sao, menh cuc.txt` và `image.png` dùng làm:
- tài liệu tham chiếu output
- dữ liệu test đối chiếu acceptance

Không dùng làm:
- nguồn tự suy diễn thêm rule ngoài rulebook này

## 23. Kết luận cho Engineering
Engineering được code theo đúng rulebook này cho phần:
- normalize input
- lịch
- can chi
- Mệnh
- Thân
- Cục
- 12 houses
- 14 chính tinh
- đại vận

Ngoài phạm vi đã khóa:
- không tự thêm
- không tự suy diễn
- không mở rộng MVP