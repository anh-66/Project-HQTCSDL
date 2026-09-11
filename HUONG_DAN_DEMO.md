# HƯỚNG DẪN DEMO 4 VẤN ĐỀ ĐỒNG THỜI (CONCURRENCY CONTROL)
## DỰ ÁN: HỆ THỐNG QUẢN LÝ KHÁCH SẠN (HQTCSDL)

> **Lưu ý quan trọng:** Bạn đang ở **Branch Demo Lỗi** (chưa khắc phục). Toàn bộ cơ chế khóa `FOR UPDATE` đã được tháo gỡ và thêm các khoảng trễ (`SLEEP` / `time.sleep`) để có thể quan sát trực tiếp 4 hiện tượng bất thường trên giao diện Web UI (Chrome vs Edge Incognito).

---

## I. GIẢI THÍCH NGUYÊN NHÂN LẦN TEST ĐẦU BỊ THẤT BẠI (VẤN ĐỀ 1)

Khi bạn test Vấn đề 1 trước đó và gặp thông báo *"Đặt phòng thất bại, phòng đã có người đặt"*, nguyên nhân chính là:
1. **Stored Procedure trong MySQL Database chưa được nạp lại:** File `sql/03_procedures.sql` trên ổ đĩa đã được sửa, nhưng Stored Procedure `sp_TaoDatPhong` trong hệ quản trị MySQL Server thực tế vẫn giữ code phiên bản cũ (vẫn còn lệnh khóa `SELECT ... FOR UPDATE` và chưa có `DO SLEEP(6)`). Do đó MySQL vẫn khóa dòng phòng và chặn giao dịch thứ 2.
2. **Quyền hạn của tài khoản ứng dụng `app_user`:** Tài khoản Flask `app_user` không có quyền `ALTER/DROP ROUTINE` trong CSDL, nên việc sửa file `.sql` không tự nạp vào CSDL được nếu không nạp qua quyền `admin_user`.
3. **Phòng P101 chưa ở trạng thái 'Trong' hoặc thiếu bản ghi:** Dữ liệu phòng thử nghiệm cần đảm bảo tồn tại và chưa bị trùng lịch cũ.

**ĐÃ XỬ LÝ SẴN CHO BẠN:**
- Đã nạp lại thành công Stored Procedure `sp_TaoDatPhong` phiên bản **Demo Lỗi** vào MySQL bằng tài khoản `admin_user` (mật khẩu `Admin@123`).
- Đã kiểm tra và khôi phục phòng **P101** sẵn sàng ở trạng thái `Trong`.
- Đã bật `threaded=True` trong `app.run()` để Flask xử lý 2 trình duyệt đồng thời mượt mà.

---

## II. CHUẨN BỊ MÔI TRƯỜNG & TÀI KHOẢN THỬ NGHIỆM

### 1. Khởi động Web & CSDL
1. Đảm bảo MySQL Server đang chạy (Database `hotel_management`).
2. Chạy ứng dụng web Flask:
   ```bash
   python app.py
   ```
   Truy cập website tại: `http://127.0.0.1:5000`

### 2. Chuẩn bị 2 trình duyệt song song để mô phỏng 2 người dùng đồng thời
- **Cửa sổ 1 (Trình duyệt Chrome):** Đại diện cho **Khách hàng** (`khach01`).
- **Cửa sổ 2 (Trình duyệt Edge - Incognito / Ẩn danh):** Đại diện cho **Lễ tân** (`letan01`) hoặc **Admin** (`admin`).

### 3. Danh sách tài khoản mẫu (Mật khẩu tất cả đều là `123456`)
| Tài khoản | Mật khẩu | Vai trò | Họ tên | Mục đích sử dụng |
| :--- | :--- | :--- | :--- | :--- |
| `admin` | `123456` | **Admin** | Nguyen Van Admin | Quản trị hệ thống, sửa giá loại phòng, thêm phòng |
| `letan01` | `123456` | **LeTan** | Tran Thi Le Tan | Lễ tân lập phiếu walk-in, xem dịch vụ |
| `khach01` | `123456` | **KhachHang** | Le Van Khach | Khách hàng tìm & đặt phòng trực tuyến |

---

## III. KỊCH BẢN CHI TIẾT DEMO 4 VẤN ĐỀ TRÊN GIAO DIỆN UI

---

### VẤN ĐỀ 1: MẤT DỮ LIỆU CẬP NHẬT (LOST UPDATE)

#### 1. Bản chất & Nguyên nhân
- **Bản chất:** Hai giao dịch $T_1$ và $T_2$ cùng thực hiện chu trình **Đọc → Tính → Ghi** trên cùng một bản ghi (giá loại phòng) mà **không có cơ chế khóa**. $T_1$ đọc giá cũ, rồi bị trì hoãn 7 giây. Trong lúc đó $T_2$ cũng đọc cùng giá cũ đó, tính giá mới và ghi vào DB (COMMIT). Khi $T_1$ hết trì hoãn, nó ghi giá mới của mình lên, **đè lên thay đổi của $T_2$** như thể $T_2$ chưa từng cập nhật.
- **Code demo:** Hàm `sua_loai_phong` (`db/queries.py`): SELECT giá cũ → `time.sleep(7)` → UPDATE giá mới → COMMIT. Không dùng `SELECT ... FOR UPDATE` nên không có khóa bi quan ngăn T2 đọc và ghi trong lúc T1 đang chờ.

#### 2. Các bước demo từng bước trên giao diện UI
1. **Chuẩn bị:** Đảm bảo loại phòng **"Standard"** đang có giá gốc là `500.000 VNĐ` (kiểm tra tại `/phong/loai-phong`). Nếu giá khác, sửa lại về `500.000` trước.
2. **Cửa sổ 1 (Trình duyệt Chrome - Admin `admin` - đóng vai Giao dịch T1):**
   - Đăng nhập `admin` → Vào **Quản lý phòng** → Tab **"Loại phòng"** (`/phong/loai-phong`).
   - Tại loại phòng **"Standard"**, bấm nút **"Sửa"** → Đổi giá thành **`550.000`** (tăng 10%) → Bấm **"Lưu thay đổi"**.
   - *(Cửa sổ 1 bắt đầu loading 7 giây — T1 đã đọc giá 500.000, đang chờ rồi mới ghi 550.000).*
3. **Cửa sổ 2 (Trình duyệt Edge Ẩn danh - Admin `admin` - đóng vai Giao dịch T2):**
   - **Nhanh tay trong 7 giây đó**, đăng nhập `admin` ở Edge → Vào **Quản lý phòng** → Tab **"Loại phòng"**.
   - Tại loại phòng **"Standard"**, bấm **"Sửa"** → Đổi giá thành **`600.000`** (tăng 20%) → Bấm **"Lưu thay đổi"**.
   - *(T2 cũng đọc giá cũ 500.000, tính 600.000 và COMMIT ngay — hoàn thành trước T1).*
4. **Kết quả quan sát & Giải thích với Thầy:**
   - **Kết quả:** Cả 2 cửa sổ đều báo **"Cập nhật loại phòng thành công!"**.
   - **Thông báo cảnh báo màu vàng** xuất hiện ở Cửa sổ 1 sau khi hết 7 giây: `[DEMO LOST UPDATE] Giao dịch T1 đã đọc giá cũ = 500,000 VNĐ, chờ 7 giây rồi ghi đè thành 550,000 VNĐ. Nếu trong 7 giây đó T2 cũng sửa giá → thay đổi của T2 đã bị T1 ghi đè mất!`
   - **Kiểm tra UI:** Reload tab **"Loại phòng"** → Giá "Standard" hiển thị **`550.000 VNĐ`** (giá của T1), **KHÔNG phải** `600.000 VNĐ` (giá T2 đã commit trước).
   - **Giải thích:** T2 đã cập nhật thành công 600.000 VNĐ và COMMIT. Nhưng T1 do đọc giá cũ 500.000 trước khi T2 ghi, tiếp tục UPDATE đè lên thành 550.000 VNĐ. **Thay đổi hợp lệ của T2 bị mất hoàn toàn** — đây chính là **Lost Update**.

---

### VẤN ĐỀ 2: ĐỌC DỮ LIỆU RÁC (DIRTY READ / UNCOMMITTED READ)

#### 1. Bản chất & Nguyên nhân
- **Bản chất:** Giao dịch $T_1$ cập nhật đơn giá dịch vụ nhưng **chưa COMMIT** (đang chờ và chuẩn bị ROLLBACK). Giao dịch $T_2$ chạy ở mức cô lập `READ UNCOMMITTED` truy vấn bảng dịch vụ và đọc được giá tiền chưa được xác nhận này. Khi $T_1$ thực hiện **ROLLBACK**, dữ liệu $T_2$ vừa đọc trở thành "dữ liệu rác" không tồn tại.
- **Code demo:**
  - `sua_dich_vu` (`db/queries.py`): Mở transaction `UPDATE` đơn giá $\rightarrow$ `time.sleep(8)` $\rightarrow$ `conn.rollback()`.
  - `lay_danh_sach_dich_vu` (`db/queries.py`): Thiết lập `SET SESSION TRANSACTION ISOLATION LEVEL READ UNCOMMITTED`.

#### 2. Các bước demo từng bước trên giao diện UI
1. **Cửa sổ 1 (Admin `admin` - Giao dịch sửa dữ liệu tạm):**
   - Đăng nhập `admin` $\rightarrow$ Vào **Quản trị** $\rightarrow$ **Quản lý danh mục dịch vụ** (`/dich-vu`).
   - Tìm dịch vụ **"Ăn sáng tại phòng"** (giá gốc là `100.000 VNĐ`), bấm nút **"Sửa"**.
   - Đổi đơn giá thành **`10.000`** (giảm 10 lần) $\rightarrow$ Bấm nút **"Cập nhật"**.
   - *(Trang web Cửa sổ 1 sẽ quay loading trong 8 giây trước khi tự động Rollback)*.
2. **Cửa sổ 2 (Lễ tân `letan01` - Người đọc dữ liệu rác):**
   - Đăng nhập `letan01` $\rightarrow$ Vào **Dịch vụ & Thanh toán** $\rightarrow$ **Danh mục Dịch vụ** (`/dich-vu`) **ngay trong 8 giây mà Cửa sổ 1 đang loading**.
   - **Quan sát:** Lễ tân nhìn thấy giá dịch vụ "Ăn sáng tại phòng" hiển thị là **`10.000 VNĐ`** (đây chính là Dirty Read!).
3. **Kết quả quan sát & Giải thích với Thầy:**
   - Hết 8 giây, Cửa sổ 1 báo thông báo đỏ: `[DEMO DIRTY READ] Giao dịch T1 đã tạm UPDATE giá thành 10,000 VNĐ, giữ trong 8s rồi ROLLBACK...`.
   - Tại Cửa sổ 2, nhấn **F5 (Tải lại trang)** $\rightarrow$ Đơn giá lập tức quay trở lại đúng giá gốc ban đầu là **`100.000 VNĐ`**.
   - **Giải thích:** Lễ tân ở Cửa sổ 2 đã đọc phải dữ liệu Uncommitted của Admin. Khi Admin hủy giao dịch (Rollback), dữ liệu rác đó biến mất, gây sai lệch giá nếu Lễ tân lập hóa đơn trong khoảnh khắc đó.

---

### VẤN ĐỀ 3: KHÔNG ĐỌC LẠI ĐƯỢC DỮ LIỆU (NON-REPEATABLE READ)

#### 1. Bản chất & Nguyên nhân
- **Bản chất:** Trong cùng một giao dịch $T_1$ (ở mức cô lập `READ COMMITTED`), $T_1$ đọc giá phòng lần 1. Giao dịch $T_2$ sửa giá loại phòng đó và `COMMIT`. Khi $T_1$ đọc lại lần 2 trong cùng giao dịch của mình thì thu được giá tiền mới bị thay đổi, kết quả đọc không lặp lại được như ban đầu.
- **Code demo:** `lay_phong_theo_id` (`db/queries.py`): Mở transaction `READ COMMITTED`, đọc lần 1 (giá $G_1$), tạm dừng `time.sleep(7)`, đọc lần 2 (giá $G_2$), `COMMIT` và bắn cảnh báo Flash lên màn hình.

#### 2. Các bước demo từng bước trên giao diện UI
1. **Cửa sổ 1 (Khách hàng `khach01` - Giao dịch đọc 2 lần):**
   - Đăng nhập `khach01` $\rightarrow$ Vào **Tìm & Đặt phòng** (`/tim-phong`).
   - Bấm nút **"Đặt ngay"** tại **Phòng P201** (Loại phòng Deluxe, đơn giá ban đầu `800.000 VNĐ`).
   - *(Cửa sổ 1 bắt đầu mở giao dịch T1, đọc lần 1 được 800.000đ và bắt đầu đếm lùi 7 giây)*.
2. **Cửa sổ 2 (Admin `admin` - Giao dịch sửa & Commit giữa chừng):**
   - **Nhanh tay trong 7 giây đó**, tại Cửa sổ 2 (Admin) vào **Quản lý phòng** $\rightarrow$ Tab **"Loại phòng"** (`/phong/loai-phong`).
   - Tại loại phòng **"Deluxe"**, bấm **"Sửa"** $\rightarrow$ Đổi giá từ `800.000` thành **`1.200.000`** $\rightarrow$ Bấm **"Cập nhật"** ($T_2$ đã COMMIT).
3. **Kết quả quan sát & Giải thích với Thầy:**
   - Sau khi hết 7 giây, Cửa sổ 1 hiển thị trang Đặt phòng kèm theo thông báo màu vàng nổi bật ở đầu trang:
     > **[DEMO NON-REPEATABLE READ] Phát hiện dữ liệu bị thay đổi trong cùng 1 Giao dịch! Lần 1 đọc: 800,000 VNĐ | Lần 2 đọc: 1,200,000 VNĐ do giao dịch khác đã UPDATE & COMMIT trong lúc đang đọc!**
   - **Giải thích:** Do mức cô lập `READ COMMITTED` không giữ khóa đọc dòng trong suốt giao dịch, nên khi giao dịch $T_2$ sửa dữ liệu và COMMIT giữa chừng, giao dịch $T_1$ đọc lại lần 2 thu được kết quả khác hoàn toàn lần 1.

---

### VẤN ĐỀ 4: BÓNG MA (PHANTOM READ)

#### 1. Bản chất & Nguyên nhân
- **Bản chất:** Trong cùng một giao dịch $T_1$ (ở mức cô lập `READ COMMITTED`), $T_1$ truy vấn danh sách phòng thuộc Tầng 3. Giao dịch $T_2$ thêm phòng mới ở Tầng 3 và `COMMIT`. Khi $T_1$ thực hiện lại câu truy vấn ban đầu thì tập kết quả xuất hiện thêm dòng mới ("bản ghi bóng ma" - Phantom row).
- **Code demo:** `lay_danh_sach_phong` (`db/queries.py`): Khi có tham số `tang=3`, mở transaction `READ COMMITTED`, `SELECT` lần 1 (đếm số phòng), delay `time.sleep(8)`, `SELECT` lần 2, so sánh số lượng phòng và bắn cảnh báo Flash lên màn hình.

#### 2. Các bước demo từng bước trên giao diện UI
1. **Cửa sổ 1 (Lễ tân/Admin - Giao dịch tra cứu danh sách phòng):**
   - Vào menu **"Tra cứu phòng"** (`/phong`).
   - Tại ô lọc **"Tầng"**, chọn **"Tầng 3"** $\rightarrow$ Bấm nút **"Lọc"**.
   - *(Cửa sổ 1 bắt đầu mở giao dịch T1, đọc lần 1 thấy 1 phòng P301, và chờ 8 giây)*.
2. **Cửa sổ 2 (Admin - Giao dịch thêm phòng mới vào Tầng 3):**
   - **Nhanh tay trong 8 giây đó**, tại Cửa sổ 2 (Admin) vào **Quản lý phòng** $\rightarrow$ Bấm nút **"Thêm phòng mới"** (`/phong/them`).
   - Nhập: Số phòng `P302`, Loại phòng `Suite`, Tầng `3` $\rightarrow$ Bấm **"Thêm phòng"** ($T_2$ đã INSERT & COMMIT).
3. **Kết quả quan sát & Giải thích với Thầy:**
   - Sau khi hết 8 giây, Cửa sổ 1 tải xong trang kèm theo thông báo màu vàng:
     > **[DEMO PHANTOM READ] Trong cùng 1 Giao dịch lọc Tầng 3: Lần 1 tìm thấy 1 phòng | Lần 2 tìm thấy 2 phòng -> Xuất hiện bản ghi 'Bóng ma' (Phantom) mới được thêm từ giao dịch khác và COMMIT!**
   - Bảng danh sách phòng hiển thị thêm phòng mới `P302` mà lần đọc 1 hoàn toàn không có.
   - **Giải thích:** Do `READ COMMITTED` không sử dụng khóa khoảng (Gap Lock / Predicate Lock), giao dịch $T_2$ thoải mái chèn bản ghi mới thỏa mãn điều kiện lọc của $T_1$, sinh ra dòng bóng ma (Phantom).

---

### VẤN ĐỀ 5: BẾ TẮC GIAO DỊCH (DEADLOCK / CIRCULAR WAIT)

#### 1. Bản chất & Nguyên nhân
- **Bản chất:** Deadlock xảy ra khi hai hay nhiều giao dịch nắm giữ khóa độc quyền (X-Lock) trên các tài nguyên khác nhau và cùng yêu cầu xin khóa trên tài nguyên mà giao dịch kia đang nắm giữ, tạo thành một chu trình chờ khép kín (*Circular Wait* trong đồ thị Wait-For Graph: $T_1 \rightarrow T_2 \rightarrow T_1$). Không giao dịch nào có thể tiếp tục.Buộc bộ phát hiện bế tắc của MySQL InnoDB phải can thiệp, chọn một giao dịch làm "nạn nhân" để `ROLLBACK` và ném ra mã lỗi `ERROR 1213 (40001)`
- **Code demo:** 
  - `check_out_lap_hoa_don` (`db/queries.py`): Khóa `dat_phong` $\rightarrow$ `time.sleep(5)` $\rightarrow$ Khóa `su_dung_dich_vu`.
  - `ghi_nhan_su_dung_dich_vu` (`db/queries.py`): Khóa `su_dung_dich_vu` $\rightarrow$ Khóa `dat_phong`.

- **Bối cảnh nghiệp vụ thực tế trong khách sạn:**
  - **Giao dịch $T_1$ (Lễ tân lập hóa đơn Check-out):** Khách làm thủ tục trả phòng tại quầy. Lễ tân mở giao dịch, khóa độc quyền phiếu đặt phòng trong bảng `dat_phong` $\rightarrow$ trì hoãn 5 giây $\rightarrow$ tiếp tục xin khóa bảng `su_dung_dich_vu` để tổng hợp tiền minibar lập hóa đơn.
  - **Giao dịch $T_2$ (Nhân viên buồng phòng (tạm thời là lễ tân 2) ghi nhận dịch vụ minibar):** Cùng lúc đó, nhân viên buồng phòng kiểm tra tủ lạnh thấy khách có dùng đồ uống, liền mở giao dịch khóa bảng `su_dung_dich_vu` $\rightarrow$ tiếp tục xin khóa bảng `dat_phong` để đối soát trạng thái phiếu đặt phòng.
  - $\Rightarrow$ $T_1$ giữ `dat_phong` chờ `su_dung_dich_vu`; $T_2$ giữ `su_dung_dich_vu` chờ `dat_phong` $\rightarrow$ **DEADLOCK xảy ra!**


#### 2. Các bước demo từng bước trên giao diện UI
1. **Chuẩn bị:** Đảm bảo có ít nhất một phiếu đặt phòng đang ở trạng thái **"Đã nhận phòng" / "Đang sử dụng"** (ví dụ phiếu đặt `#3`, kiểm tra tại `/luu-tru/check-in`).
2. **Cửa sổ 1 (Trình duyệt Chrome - Lễ tân tại quầy - đóng vai Giao dịch T1):**
   - Đăng nhập `letan01` $\rightarrow$ Vào **Check-out** (`/luu-tru/check-out/3`).
   - Bấm nút **"Lập hóa đơn & Check-out"**.
   - *(Cửa sổ 1 bắt đầu loading quay vòng trong 5 giây — T1 đang giữ khóa phiếu đặt phòng và chuẩn bị đọc bảng dịch vụ).*
3. **Cửa sổ 2 (Trình duyệt Edge Ẩn danh - Nhân viên buồng phòng - đóng vai Giao dịch T2):**
   - **Nhanh tay trong 5 giây đó**, đăng nhập `letan01` ở Edge $\rightarrow$ Vào **Sử dụng Dịch vụ** (`/luu-tru/dichvu?ma_dat_phong=3`).
   - Chọn một dịch vụ (ví dụ: *Nước ngọt*, số lượng: `2`) $\rightarrow$ Bấm nút **"Thêm dịch vụ"**.
   - *(Cả 2 cửa sổ cùng loading chờ đợi nhau do rơi vào chu trình Deadlock).*

#### 3. Kết quả quan sát & Giải thích với Thầy

* **TRÊN BRANCH DEMO LỖI (`demo-fix-all`):**
  - **Kết quả:** 
    - Cửa sổ 1 (Check-out) tải xong báo xanh: *"Check-out và lập hóa đơn thành công!"*.
    - Cửa sổ 2 (Dịch vụ) văng thông báo **MÀU ĐỎ**:  
      > `[DEMO DEADLOCK - LỖI 1213] Giao dịch Thêm dịch vụ bị MySQL hủy do Deadlock xảy ra!`
  - **Giải thích với Thầy:** MySQL InnoDB đã phát hiện bế tắc khóa vòng tròn và chủ động khai tử giao dịch $T_2$ để giải cứu hệ thống. Do hệ thống chưa có cơ chế xử lý ngoại lệ Deadlock, thao tác thêm dịch vụ bị thất bại hoàn toàn. Khách hàng đã check-out rời đi dẫn đến **khách sạn bị thất thoát tiền dịch vụ minibar**.

* **TRÊN BRANCH KHẮC PHỤC (`final`):**
  - **Kết quả:**
    - Cửa sổ 1 (Check-out) báo xanh thành công.
    - Cửa sổ 2 (Dịch vụ) ban đầu bị đụng độ Deadlock, nhưng code Python đã bắt được mã lỗi `1213`, tự động `ROLLBACK` và **TỰ ĐỘNG THỬ LẠI (RETRY LẦN 2)** sau 0.5 giây!
    - Cửa sổ 2 tải xong thành công mượt mà với thông báo nổi bật:  
      > `[XỬ LÝ DEADLOCK THÀNH CÔNG] Ban đầu bị Deadlock (Lỗi 1213) do quầy đang Check-out. Hệ thống đã tự động Retry ngầm lần 2 thành công!`
  - **Giải thích với Thầy:** Tầng ứng dụng Python đã triển khai cơ chế **Application-level Automatic Retry (Exponential Backoff)**. Thay vì báo lỗi làm hỏng việc, hệ thống tự động phục hồi và ghi nhận thành công, bảo toàn 100% dữ liệu hóa đơn và chống thất thoát doanh thu.

## V. NGUYÊN LÝ KHẮC PHỤC (CHO BRANCH THỨ 2 - KHẮC PHỤC)

Khi bạn chuyển sang **Branch Khắc Phục**:
1. **Khắc phục Lost Update:** Thêm lại `SELECT ma_phong INTO v_phong_id FROM phong WHERE ma_phong = p_ma_phong FOR UPDATE;` trong `sp_TaoDatPhong` để khóa độc quyền dòng phòng. Giao dịch đến sau bắt buộc phải chờ giao dịch trước COMMIT/ROLLBACK mới được đọc.
2. **Khắc phục Dirty Read:** Đặt mức cô lập tối thiểu là `READ COMMITTED` (hoặc mặc định `REPEATABLE READ`) cho hàm `lay_danh_sach_dich_vu`, không cho phép đọc dữ liệu chưa commit.
3. **Khắc phục Non-repeatable Read:** Sử dụng mức cô lập `REPEATABLE READ` (Snapshot Isolation của InnoDB) trong `lay_phong_theo_id`, đảm bảo các lần đọc trong cùng transaction luôn thấy cùng 1 phiên bản dữ liệu snapshot.
4. **Khắc phục Phantom Read:** Sử dụng `SERIALIZABLE` hoặc Next-Key Lock trong `lay_danh_sach_phong` để khóa khoảng giá trị tầng, ngăn chặn giao dịch khác INSERT thêm dòng mới vào tầng đó.
