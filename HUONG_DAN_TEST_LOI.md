# BÁO CÁO CẬP NHẬT CSDL & HƯỚNG DẪN DEMO TRANH CHẤP TRÊN WEB UI

## 1. CẤU TRÚC THƯ MỤC `test_loi/`

Thư mục `test_loi/` lưu trữ các file được chỉnh sửa để mô phỏng 4 hiện tượng tranh chấp dữ liệu trên Giao diện Web:

```text
test_loi/
├── HUONG_DAN_TEST_LOI.md     (File tài liệu hướng dẫn)
├── sql/
│   └── 03_procedures.sql     (Mô phỏng Lỗi 1: Lost Update & Lỗi 2: Dirty Read)
├── db/
│   └── queries.py            (Mô phỏng Lỗi 3: Non-repeatable Read & Helper Dirty Read)
└── routes/
    └── dat_phong_routes.py   (Mô phỏng Lỗi 4: Phantom Read)
```

---

## 2. QUY TRÌNH TEST 4 HỆN TƯỢNG TRANH CHẤP TRÊN WEB UI

### 3.1. Lỗi 1: Mất dữ liệu cập nhật (Lost Update)
- **Thực thi**: Copy `test_loi/sql/03_procedures.sql` đè vào `sql/03_procedures.sql` gốc và thực thi lại trên MySQL.
- **Thao tác trên Web**:
  1. Mở 2 tab trình duyệt riêng biệt (Tab 1: Khách A, Tab 2: Khách B).
  2. Cả 2 tab truy cập `/tim-phong`, chọn cùng **Phòng 101** và cùng khoảng ngày (ví dụ `01/12/2026` -> `05/12/2026`).
  3. Tab 1 bấm **"Xác nhận đặt phòng"**.
  4. Trong vòng 5 giây, Tab 2 bấm **"Xác nhận đặt phòng"**.
- **Kết quả**: Cả 2 Tab đều thông báo *"Đặt phòng thành công!"*, tạo ra 2 phiếu đặt trùng cho 1 phòng ở cùng khung giờ (Mất dữ liệu cập nhật).

---

### 2.2. Lỗi 2: Đọc dữ liệu rác (Dirty Read)
- **Thực thi**: Copy `test_loi/sql/03_procedures.sql` và `test_loi/db/queries.py` đè vào dự án gốc.
- **Thao tác trên Web**:
  1. Tab 1 (Admin): Chạy cập nhật giá phòng 101 thành `9.999.999 VNĐ` (giao dịch tạm dừng 8s rồi `ROLLBACK`).
  2. Tab 2 (Khách hàng): Truy cập xem chi tiết hoặc danh sách phòng.
- **Kết quả**: Tab 2 hiển thị đơn giá `9.999.999 VNĐ` (Đọc dữ liệu rác uncommitted). Sau khi Tab 1 rollback, làm mới trang ở Tab 2 giá phòng quay về mức ban đầu.

---

### 2.3. Lỗi 3: Không đọc lại được dữ liệu (Non-repeatable Read)
- **Thực thi**: Copy `test_loi/db/queries.py` đè vào `db/queries.py` dự án gốc.
- **Thao tác trên Web**:
  1. Tab 1 (Lễ tân A): Mở màn hình Check-out Phòng 101 (Tiền dịch vụ ban đầu = `0 VNĐ`), bấm **Check-out & Lập hóa đơn** (Hệ thống dừng 6s trước khi lưu).
  2. Trong vòng 6s đó, Tab 2 (Lễ tân B): Thêm dịch vụ "Nước ngọt" (`50.000 VNĐ`) cho Phòng 101 và lưu lại.
- **Kết quả**: Hóa đơn tạo ra tại Tab 1 hiển thị tiền dịch vụ = `50.000 VNĐ` thay vì `0 VNĐ` như ban đầu Lễ tân A nhìn thấy khi bấm nút (Dữ liệu bị thay đổi giữa 2 lần đọc trong cùng một xử lý).

---

### 2.4. Lỗi 4: Bóng ma (Phantom Read)
- **Thực thi**: Copy `test_loi/routes/dat_phong_routes.py` đè vào `routes/dat_phong_routes.py` dự án gốc.
- **Thao tác trên Web**:
  1. Tab 1 (Khách A): Chọn ngày và bấm **"Tìm phòng"** (Hệ thống chờ 5s).
  2. Trong 5s đó, Tab 2 (Khách B): Hoàn tất 1 đơn Đặt phòng cho Phòng 101.
- **Kết quả**: Tab 1 hiển thị thông báo:
  `"[DEMO PHANTOM READ] Kết quả thống kê ban đầu: Tìm thấy 5 phòng trống. (Thực tế danh sách bên dưới hiện có 4 phòng)!"`
  (Bản ghi bóng ma làm lệch số lượng thống kê đếm được ban đầu và danh sách hiển thị thực tế).
