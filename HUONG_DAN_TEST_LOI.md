# HƯỚNG DẪN DEMO 4 TRANH CHẤP TRỰC TIẾP TRÊN GIAO DIỆN WEB UI (BẤM NÚT CÓ SẴN)

## 1. CẤU TRÚC THƯ MỤC `test_loi/`

```text
test_loi/
├── HUONG_DAN_TEST_LOI.md     (File tài liệu hướng dẫn)
├── db/
│   └── queries.py            (Mô phỏng Lỗi 1: Lost Update, Lỗi 2: Dirty Read, Lỗi 3: Non-repeatable Read)
└── routes/
    └── dat_phong_routes.py   (Mô phỏng Lỗi 4: Phantom Read)
```

---

## 2. QUY TRÌNH DEMO 4 TRANH CHẤP TRÊN WEB (100% BẤM NÚT CÓ SẴN TRÊN GIAO DIỆN)

### 2.1. Lỗi 1: Mất dữ liệu cập nhật (Lost Update) — *Đã test thành công*
- **File đè**: Copy `test_loi/db/queries.py` đè vào `db/queries.py` dự án gốc. Khởi động app (`python app.py`).
- **Thao tác trên Web**:
  1. Mở 2 Tab trình duyệt (Tab 1: Khách A, Tab 2: Khách B).
  2. Cả 2 Tab cùng vào giao diện **"Tìm & Đặt phòng"** (`/tim-phong`), chọn cùng **Phòng P123** cho cùng khoảng ngày.
  3. Tab 1 bấm nút **"Xác nhận đặt phòng"** -> Ngay lập tức sang Tab 2 bấm nút **"Xác nhận đặt phòng"**.
- **Kết quả trên UI**: Cả 2 Tab đều quay 5s và **CẢ 2 TAB ĐỀU BÁO XANH: `[DEMO LOST UPDATE] Đặt phòng thành công!`**, tạo ra 2 phiếu đặt bị trùng lịch cho cùng 1 phòng.

---

### 2.2. Lỗi 2: Đọc dữ liệu rác (Dirty Read) — *Dùng đúng Form Sửa phòng của bạn*
- **File đè**: Copy `test_loi/db/queries.py` đè vào `db/queries.py` dự án gốc. Khởi động app (`python app.py`).
- **Thao tác trên Web**:
  1. Tab 1 (Admin/Lễ tân): Mở giao diện **"Sửa phòng P123"** (`/phong/sua/1`). Đổi ô **Loại phòng** từ *Phòng Đơn Standard* sang ***Phòng VIP Suite (1,500,000 đ/ngày)*** -> Bấm nút **"Cập nhật"** (Web sẽ xoay 8s rồi tự Rollback).
  2. Tab 2 (Khách hàng / Lễ tân): Nhanh tay sang menu **"Quản lý phòng"** (`/phong`) hoặc **"Tìm & Đặt phòng"** trong 8 giây đó.
- **Kết quả trên UI**: Tab 2 nhìn thấy Phòng P123 đã biến thành **`Phòng VIP Suite (1,500,000 đ/ngày)`** (Đọc dữ liệu rác uncommitted). Hết 8s Tab 1 thông báo Rollback, F5 lại Tab 2 phòng P123 tự quay trở lại thành **`Phòng Đơn Standard`**.

---

### 2.3. Lỗi 3: Không đọc lại được dữ liệu (Non-repeatable Read)
- **File đè**: Copy `test_loi/db/queries.py` đè vào `db/queries.py` dự án gốc. Khởi động app (`python app.py`).
- **Thao tác trên Web**:
  1. Tab 1 (Lễ tân A): Vào màn hình **Check-out** phòng đang ở . Bấm nút **"Check-out & Lập hóa đơn"** (Hệ thống chờ 6s).
  2. Trong 6s đó, Tab 2 (Lễ tân B): Vào menu **"Sử dụng dịch vụ"** (`/luu-tru/dichvu`), chọn phòng đó, chọn dịch vụ "Nước uống đóng chai" (`15.000 đ`) và bấm nút **"Thêm dịch vụ"**.
- **Kết quả trên UI**: Màn hình Hóa đơn tạo ra tại Tab 1 sau khi load xong lại hiển thị Tiền dịch vụ = `15.000 đ` thay vì `0 đ` như lúc Lễ tân A bấm nút ban đầu.

---

### 2.4. Lỗi 4: Bóng ma (Phantom Read) — *Đã test thành công*
- **File đè**: Copy `test_loi/routes/dat_phong_routes.py` đè vào `routes/dat_phong_routes.py` dự án gốc. Khởi động app (`python app.py`).
- **Thao tác trên Web**:
  1. Tab 1 (Khách A): Chọn ngày và bấm nút **"Tìm phòng"** (Web xoay 5s).
  2. Trong 5s đó, Tab 2 (Khách B): Hoàn tất 1 đơn Đặt phòng thành công.
- **Kết quả trên UI**: Tab 1 hiển thị thông báo flash màu xanh:
  `"[DEMO PHANTOM READ] Kết quả thống kê ban đầu: Tìm thấy 5 phòng trống. (Thực tế danh sách bên dưới hiện có 4 phòng)!"`
