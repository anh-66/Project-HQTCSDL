# HƯỚNG DẪN DEMO 4 VẤN ĐỀ ĐỒNG THỜI (CONCURRENCY CONTROL)
## DỰ ÁN: HỆ THỐNG QUẢN LÝ KHÁCH SẠN (HQTCSDL)

> **Lưu ý:** Hiện tại bạn đang ở **Branch Demo Lỗi** (chưa khắc phục hoặc đã tháo gỡ các cơ chế khóa/hạ mức cô lập và thêm độ trễ `SLEEP` để quan sát rõ hiện tượng trực tiếp trên giao diện người dùng).

---

## I. CHUẨN BỊ MÔI TRƯỜNG & TÀI KHOẢN THỬ NGHIỆM

### 1. Khởi động Web & CSDL
1. Đảm bảo MySQL Server đang chạy và database `hotel_management` đã nạp file `sql/03_procedures.sql`.
2. Chạy ứng dụng web:
   ```bash
   venv\Scripts\python app.py
   ```
   Truy cập website tại: `http://127.0.0.1:5000`

### 2. Chuẩn bị 2 trình duyệt để đóng vai 2 người dùng đồng thời
- **Cửa sổ 1 (Trình duyệt thường):** Đại diện cho **Người dùng A** (Khách hàng hoặc Lễ tân).
- **Cửa sổ 2 (Trình duyệt ẩn danh - Incognito):** Đại diện cho **Người dùng B** (Admin hoặc Lễ tân 2).

### 3. Danh sách tài khoản mẫu (Mật khẩu tất cả đều là `123456`)
| Tài khoản | Mật khẩu | Vai trò | Họ tên | Mục đích sử dụng |
| :--- | :--- | :--- | :--- | :--- |
| `admin` | `123456` | **Admin** | Nguyen Van Admin | Quản trị hệ thống, sửa giá, thêm phòng |
| `letan01` | `123456` | **LeTan** | Tran Thi Le Tan | Lễ tân thực hiện walk-in, xem dịch vụ |
| `khach01` | `123456` | **KhachHang** | Le Van Khach | Khách hàng tìm & đặt phòng trực tuyến |

---

## II. KỊCH BẢN CHI TIẾT DEMO 4 VẤN ĐỀ

---

### VẤN ĐỀ 1: MẤT DỮ LIỆU CẬP NHẬT (LOST UPDATE / TRÙNG ĐẶT PHÒNG)

#### 1. Bản chất & Nguyên nhân
- **Bản chất:** Hai giao dịch $T_1$ và $T_2$ cùng đọc trạng thái phòng trống tại cùng một thời điểm. Cả hai cùng ghi nhận đặt phòng mà không khóa dòng (`SELECT ... FOR UPDATE`), dẫn đến cùng một phòng bị đặt trùng lặp (Overbooking) cho 2 người khác nhau trong cùng khoảng thời gian.
- **Vị trí code demo:** Trong Stored Procedure `sp_TaoDatPhong` (`sql/03_procedures.sql`), đã **bỏ** khóa `FOR UPDATE` và thêm độ trễ `DO SLEEP(6);` sau khi kiểm tra phòng trống.

#### 2. Các bước demo trên giao diện UI
1. **Cửa sổ 1 (Khách hàng `khach01`):**
   - Đăng nhập tài khoản `khach01`.
   - Vào menu **"Tìm & Đặt phòng"** (`/tim-phong`).
   - Tìm phòng từ ngày `2026-09-01` đến `2026-09-05`.
   - Nhấn nút **"Đặt ngay"** tại **Phòng P101** để vào trang xác nhận đặt phòng.
2. **Cửa sổ 2 (Lễ tân `letan01` - Trình duyệt ẩn danh):**
   - Đăng nhập tài khoản `letan01`.
   - Vào menu **"Walk-in"** (`/dat-phong/walk-in`).
   - Chọn **Phòng P101**, nhập ngày nhận `2026-09-01`, ngày trả `2026-09-05`, nhập tên khách vãng lai `Nguyễn Văn Thử Nghiệm`.
3. **Thực hiện thao tác đồng thời:**
   - Tại **Cửa sổ 1**, bấm nút **"Xác nhận đặt phòng"** $\rightarrow$ Hệ thống đang xử lý và chờ 6 giây.
   - Trong vòng 6 giây đó, nhanh tay chuyển sang **Cửa sổ 2**, bấm nút **"Tạo phiếu đặt phòng"**.
4. **Kết quả quan sát:**
   - Cả 2 cửa sổ đều nhận được thông báo màu xanh: **"Đặt phòng thành công!"**.
   - Tại **Cửa sổ 2**, vào menu **"Quản lý đặt phòng"** (`/dat-phong/quan-ly`):
     - Xuất hiện **2 phiếu đặt phòng khác nhau** nhưng **cùng đặt Phòng P101** trong cùng khoảng thời gian từ ngày `01/09/2026` đến `05/09/2026`!
   - $\rightarrow$ **Giải thích cho thầy:** Do không khóa dữ liệu khi đọc trạng thái phòng, cả 2 giao dịch đều thấy phòng còn trống và cùng ghi dữ liệu đè lên nhau, gây ra lỗi mất cập nhật (Lost Update).

---

### VẤN ĐỀ 2: ĐỌC DỮ LIỆU RÁC (DIRTY READ / UNCOMMITTED READ)

#### 1. Bản chất & Nguyên nhân
- **Bản chất:** Giao dịch $T_1$ cập nhật dữ liệu nhưng **chưa COMMIT** (đang trong quá trình xử lý hoặc chuẩn bị ROLLBACK). Giao dịch $T_2$ chạy ở mức cô lập `READ UNCOMMITTED` đọc dữ liệu tạm thời này. Sau đó $T_1$ bị lỗi và **ROLLBACK**, khiến dữ liệu mà $T_2$ vừa đọc được trở thành "dữ liệu rác" không có thật.
- **Vị trí code demo:**
  - `sua_dich_vu` trong `db/queries.py`: Thực hiện `UPDATE` giá dịch vụ $\rightarrow$ `time.sleep(8)` $\rightarrow$ `conn.rollback()`.
  - `lay_danh_sach_dich_vu` trong `db/queries.py`: Mở session với `SET SESSION TRANSACTION ISOLATION LEVEL READ UNCOMMITTED`.

#### 2. Các bước demo trên giao diện UI
1. **Cửa sổ 1 (Admin `admin` - Người ghi dữ liệu tạm):**
   - Đăng nhập `admin` $\rightarrow$ Vào **Quản trị** $\rightarrow$ **Quản lý danh mục dịch vụ** (`/dich-vu`).
   - Tại dịch vụ **"Ăn sáng tại phòng"** (giá gốc là `100.000 VNĐ`), bấm nút **"Sửa"**.
   - Sửa đơn giá thành **`10.000`** (giảm sốc) $\rightarrow$ Bấm nút **"Cập nhật"**.
   - *(Trang web Cửa sổ 1 sẽ quay loading trong 8 giây trước khi tự động Rollback)*.
2. **Cửa sổ 2 (Lễ tân `letan01` - Người đọc dữ liệu rác):**
   - Đăng nhập `letan01` $\rightarrow$ Vào **Dịch vụ & Thanh toán** $\rightarrow$ **Danh mục Dịch vụ** (`/dich-vu`) **trong khoảng 8 giây mà Cửa sổ 1 đang loading**.
   - **Quan sát:** Lễ tân thấy giá dịch vụ "Ăn sáng tại phòng" hiển thị là **`10.000 VNĐ`** (đây là Dirty Read!).
3. **Kết thúc giao dịch:**
   - Hết 8 giây, Cửa sổ 1 hiện thông báo đỏ: `[DEMO DIRTY READ] Giao dịch T1 đã tạm UPDATE giá thành 10,000 VNĐ, giữ trong 8s rồi ROLLBACK (không lưu vào CSDL)`.
   - Tại Cửa sổ 2, nhấn **F5** tải lại trang $\rightarrow$ Đơn giá trở về đúng giá trị ban đầu là **`100.000 VNĐ`**.
   - $\rightarrow$ **Giải thích cho thầy:** Lễ tân ở Cửa sổ 2 đã đọc phải dữ liệu chưa được commit của Admin (Dirty Read). Khi Admin rollback, dữ liệu đó biến mất.

---

### VẤN ĐỀ 3: KHÔNG ĐỌC LẠI ĐƯỢC DỮ LIỆU (NON-REPEATABLE READ)

#### 1. Bản chất & Nguyên nhân
- **Bản chất:** Trong cùng một giao dịch $T_1$ (ở mức cô lập `READ COMMITTED`), $T_1$ đọc một dòng dữ liệu lần 1. Giao dịch $T_2$ cập nhật dòng dữ liệu đó và `COMMIT`. Khi $T_1$ đọc lại lần 2 trong cùng giao dịch của mình thì thấy giá trị đã bị thay đổi, không lặp lại được kết quả ban đầu.
- **Vị trí code demo:**
  - `lay_phong_theo_id` trong `db/queries.py`: Mở transaction `READ COMMITTED`, đọc lần 1 (giá phòng $G_1$), delay `time.sleep(7)`, đọc lại lần 2 (giá phòng $G_2$), sau đó `COMMIT` và bắn thông báo Flash cảnh báo lên màn hình.

#### 2. Các bước demo trên giao diện UI
1. **Cửa sổ 1 (Khách hàng `khach01` - Giao dịch đọc 2 lần):**
   - Đăng nhập `khach01` $\rightarrow$ Vào **Tìm & Đặt phòng** (`/tim-phong`).
   - Nhấn **"Đặt ngay"** tại **Phòng P201** (Loại phòng Deluxe, đơn giá ban đầu là `800.000 VNĐ/ngày`).
   - *(Trang web Cửa sổ 1 sẽ bắt đầu mở giao dịch, đọc lần 1 thấy 800.000đ và đang đếm lùi 7 giây trước khi đọc lần 2)*.
2. **Cửa sổ 2 (Admin `admin` - Giao dịch sửa và Commit giữa chừng):**
   - Đăng nhập `admin` $\rightarrow$ Vào **Quản trị** $\rightarrow$ **Quản lý phòng** $\rightarrow$ Chuyển sang tab **"Loại phòng"** (`/phong/loai-phong`).
   - Tại loại phòng **"Deluxe"**, bấm **"Sửa"** $\rightarrow$ Đổi đơn giá từ `800.000` thành **`1.200.000`** $\rightarrow$ Bấm **"Cập nhật"** (Giao dịch $T_2$ đã COMMIT thành công).
3. **Kết quả quan sát tại Cửa sổ 1:**
   - Sau khi hết 7 giây, trang Đặt phòng của Khách hàng hiển thị với thông báo cảnh báo màu vàng nổi bật trên đỉnh trang:
     > **[DEMO NON-REPEATABLE READ] Phát hiện dữ liệu bị thay đổi trong cùng 1 Giao dịch! Lần 1 đọc: 800,000 VNĐ | Lần 2 đọc: 1,200,000 VNĐ do giao dịch khác đã UPDATE & COMMIT trong lúc đang đọc!**
   - $\rightarrow$ **Giải thích cho thầy:** Do mức cô lập `READ COMMITTED` không khóa dòng sau khi đọc, giao dịch của Khách hàng đọc 2 lần trong cùng một phiên lại cho ra 2 giá tiền khác nhau (Non-repeatable Read).

---

### VẤN ĐỀ 4: BÓNG MA (PHANTOM READ)

#### 1. Bản chất & Nguyên nhân
- **Bản chất:** Trong cùng một giao dịch $T_1$ (ở mức cô lập `READ COMMITTED`), $T_1$ truy vấn một tập hợp các dòng thỏa mãn điều kiện (ví dụ: các phòng thuộc Tầng 3). Giao dịch $T_2$ chèn thêm một dòng mới thỏa mãn điều kiện đó (`INSERT` thêm phòng ở Tầng 3) và `COMMIT`. Khi $T_1$ thực hiện lại câu truy vấn ban đầu thì tập kết quả xuất hiện thêm dòng mới ("bản ghi bóng ma" - Phantom row).
- **Vị trí code demo:**
  - `lay_danh_sach_phong` trong `db/queries.py`: Khi có tham số `tang` (ví dụ `tang=3`), hàm mở transaction `READ COMMITTED`, `SELECT` lần 1 (đếm số lượng phòng), delay `time.sleep(8)`, `SELECT` lần 2, so sánh số lượng phòng và bắn cảnh báo Flash lên UI.

#### 2. Các bước demo trên giao diện UI
1. **Cửa sổ 1 (Lễ tân/Admin - Giao dịch tra cứu danh sách phòng):**
   - Vào menu **"Tra cứu phòng"** / **"Quản lý phòng"** (`/phong`).
   - Tại bộ lọc **"Tầng"**, chọn **"Tầng 3"** $\rightarrow$ Bấm nút **"Lọc"**.
   - *(Trang web Cửa sổ 1 sẽ bắt đầu mở giao dịch, truy vấn lần 1 tìm thấy 1 phòng P301, và chờ 8 giây trước khi truy vấn lần 2)*.
2. **Cửa sổ 2 (Admin - Giao dịch thêm phòng mới vào Tầng 3):**
   - Đăng nhập `admin` $\rightarrow$ Vào **Quản trị** $\rightarrow$ **Quản lý phòng** $\rightarrow$ Bấm nút **"Thêm phòng mới"** (`/phong/them`).
   - Nhập thông tin:
     - Số phòng: **`P302`** (hoặc `P303` nếu đã có P302)
     - Loại phòng: **Suite**
     - Tầng: **`3`**
   - Bấm nút **"Thêm phòng"** (Giao dịch $T_2$ đã `INSERT` và `COMMIT` thành công).
3. **Kết quả quan sát tại Cửa sổ 1:**
   - Sau khi hết 8 giây, trang danh sách phòng tải xong kèm theo thông báo màu vàng:
     > **[DEMO PHANTOM READ] Trong cùng 1 Giao dịch lọc Tầng 3: Lần 1 tìm thấy 1 phòng | Lần 2 tìm thấy 2 phòng -> Xuất hiện bản ghi 'Bóng ma' (Phantom) mới được thêm từ giao dịch khác và COMMIT!**
   - Bảng danh sách phòng hiển thị cả phòng mới `P302` mà ở lần đọc 1 của giao dịch chưa hề có.
   - $\rightarrow$ **Giải thích cho thầy:** Do chỉ sử dụng `READ COMMITTED` mà không dùng phạm vi khóa (Predicate Lock / Gap Lock của `SERIALIZABLE`), giao dịch $T_1$ bị chèn thêm dữ liệu bóng ma.

---

## III. BẢNG TỔNG KẾT MỨC ĐỘ CÔ LẬP VÀ 4 VẤN ĐỀ TRONG HỆ CSDL

| Mức độ cô lập (Isolation Level) | Lost Update | Dirty Read | Non-repeatable Read | Phantom Read |
| :--- | :---: | :---: | :---: | :---: |
| **READ UNCOMMITTED** *(Demo Vấn đề 2)* | ❌ Xảy ra | ❌ Xảy ra | ❌ Xảy ra | ❌ Xảy ra |
| **READ COMMITTED** *(Demo Vấn đề 3, 4)* | ❌ Xảy ra (nếu ko khóa) |  Khắc phục | ❌ Xảy ra | ❌ Xảy ra |
| **REPEATABLE READ** *(Mặc định MySQL)* | ❌ Xảy ra (nếu ko FOR UPDATE) |  Khắc phục |  Khắc phục |  Khắc phục (nhờ MVCC) |
| **SERIALIZABLE / PESSIMISTIC LOCK** |  Khắc phục |  Khắc phục |  Khắc phục |  Khắc phục |

---

## IV. GIẢI PHÁP ĐÃ KHẮC PHỤC (CHO BRANCH THỨ 2)

Khi chuyển sang **Branch Khắc phục**:
1. **Khắc phục Lost Update:** Sử dụng `SELECT ... FOR UPDATE` (Pessimistic Locking) trong Stored Procedure `sp_TaoDatPhong` để khóa độc quyền dòng dữ liệu phòng trong suốt thời gian giao dịch diễn ra, bắt các giao dịch khác phải chờ.
2. **Khắc phục Dirty Read:** Đặt mức cô lập tối thiểu là `READ COMMITTED` (hoặc giữ nguyên mặc định `REPEATABLE READ`), không cho phép đọc dữ liệu Uncommitted.
3. **Khắc phục Non-repeatable Read:** Sử dụng mức cô lập `REPEATABLE READ` kết hợp cơ chế MVCC (Multi-Version Concurrency Control) của InnoDB để đảm bảo các lần đọc trong cùng một giao dịch luôn nhìn thấy cùng một snapshot dữ liệu.
4. **Khắc phục Phantom Read:** Sử dụng `SERIALIZABLE` hoặc Next-Key Locking (Record Lock + Gap Lock) để khóa khoảng giá trị, ngăn chặn việc chèn bản ghi mới thỏa mãn điều kiện truy vấn.
