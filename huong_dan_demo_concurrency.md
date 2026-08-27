# Hướng Dẫn Demo 4 Lỗi Tranh Chấp Giao Tác & Kịch Bản Thuyết Trình Đồ Án

Tài liệu này hướng dẫn chi tiết cách **tái hiện trực quan 4 lỗi tranh chấp giao tác** (Concurrency Anomalies) ngay trên giao diện Web UI của dự án Quản lý Khách sạn, đồng thời cung cấp **Kịch bản thuyết trình (Presentation Script)** đối chiếu giữa code lỗi và code đã khắc phục (code đã đẩy lên Git).

---

## I. Tổng Quan 4 Lỗi Tranh Chấp Giao Tác Trên Hệ Thống

| STT | Lỗi Tranh Chấp | Chức năng nghiệp vụ sử dụng demo | Cách tái hiện trên UI |
| :---: | :--- | :--- | :--- |
| **1** | **Mất dữ liệu cập nhật (Lost Update)** | Cập nhật hồ sơ khách hàng (`/ho-so`) / Sửa phòng | 2 Trình duyệt cùng sửa 1 thông tin $\rightarrow$ Thao tác sau ghi đè mất thông tin trước. |
| **2** | **Đọc dữ liệu rác (Dirty Read)** | Đặt phòng / Check-in & Báo cáo | Giao dịch T1 thay đổi dữ liệu chưa COMMIT, T2 đọc được dữ liệu đó; T1 ROLLBACK $\rightarrow$ T2 giữ dữ liệu rác. |
| **3** | **Không đọc lại được dữ liệu (Non-repeatable Read)** | Hủy đặt phòng (`/dat-phong/huy`) vs Check-in (`/luu-tru/check-in`) | T1 đọc trạng thái `'DaDat'`, trì hoãn 10s (`DO SLEEP(10)`), T2 Check-in thành `'DaNhanPhong'`, T1 ghi đè thành `'DaHuy'`. |
| **4** | **Bóng ma (Phantom Read)** | Tra cứu phòng trống (`/tim-phong`) & Đặt phòng | T1 tìm phòng trống thấy 3 phòng, T2 đặt thành công 1 phòng $\rightarrow$ T1 truy vấn lại xuất hiện bản ghi mới làm đổi danh sách. |

> [!TIP]
> **Lưu ý về thời gian Demo (Delay 10s)**:
> Để người thuyết trình kịp chuyển tab từ **Browser 1 (Chrome)** sang **Browser 2 (Edge)** và bấm nút trên UI mà không sợ bị trễ, các thủ tục / câu lệnh demo lỗi đã được tích hợp lệnh chờ 10 giây (`DO SLEEP(10);` trong SQL hoặc `time.sleep(10)` trong Python). Bạn sẽ có đủ 10 giây thoải mái thao tác trên giao diện.

---

## II. Hướng Dẫn Chi Tiết Thao Tác Demo & Kịch Bản Thuyết Trình

### 1. Mất dữ liệu cập nhật (Lost Update)

####  Thao tác Demo trên Giao diện (UI):
1. **Chuẩn bị**: Mở 2 trình duyệt độc lập (Ví dụ: **Chrome** đại diện cho Khách A, **Edge/Incognito** đại diện cho Khách B hoặc Lễ tân).
2. **Bước 1**: Cả 2 trình duyệt cùng đăng nhập tài khoản Khách hàng (hoặc Lễ tân) và cùng mở trang **Cập nhật Hồ sơ Cá nhân** (`http://127.0.0.1:5000/ho-so`).
3. **Bước 2**: 
   - Trên **Chrome (Khách A)**: Nhập SĐT mới là `0911111111`.
   - Trên **Edge (Khách B)**: Nhập SĐT mới là `0922222222`.
4. **Bước 3**: 
   - Khách A trên Chrome nhấn nút **"Lưu thay đổi"** trước $\rightarrow$ Hệ thống báo thành công. CSDL lưu `0911111111`.
   - Khách B trên Edge nhấn nút **"Lưu thay đổi"** sau $\rightarrow$ Hệ thống báo thành công. CSDL bị ghi đè thành `0922222222`.
5. **Kết quả**: Thao tác cập nhật SĐT `0911111111` của Khách A đã hoàn toàn bị **MẤT (Lost Update)** mà không hề có cảnh báo xung đột.

####  Kịch bản thuyết trình (Script):
> **Lời nói thuyết trình**:
> *"Kính thưa thầy cô, lỗi đầu tiên chúng em demo là **Lost Update (Mất dữ liệu cập nhật)**. Như thầy cô đã thấy trên màn hình, khi 2 người dùng cùng mở form chỉnh sửa thông tin hồ sơ cùng lúc, Khách A đổi SĐT thành `0911111111` và bấm Lưu. Ngay sau đó, Khách B bấm Lưu với SĐT `0922222222`. Kết quả là SĐT của Khách A bị ghi đè hoàn toàn.*
> 
> **Nguyên nhân kỹ thuật trong code ban đầu**:
> *Hàm `cap_nhat_ho_so_khach_hang` thực hiện câu lệnh `UPDATE khach_hang SET sdt = ... WHERE ma_kh = ...` trực tiếp mà không có khóa giao dịch (Pessimistic Lock) hay kiểm tra phiên bản dữ liệu (Optimistic Locking).*
> 
> **Cách code đã được Fix (trên GitHub)**:
> *Để khắc phục, trong code đã sửa, chúng em đã áp dụng cơ chế khóa dòng `SELECT ... FOR UPDATE` trong giao dịch database và kiểm tra thời gian cập nhật/phiên bản trước khi `UPDATE`, buộc giao dịch đến sau phải chờ hoặc nhận cảnh báo dữ liệu đã bị thay đổi."*

---

### 2. Đọc dữ liệu rác (Dirty Read)

> [!IMPORTANT]
> **Giải thích cơ chế MySQL InnoDB**: InnoDB mặc định ở mức `REPEATABLE READ`, ngăn Dirty Read hoàn toàn. Do đó, để minh họa lỗi Dirty Read trực quan cho thầy cô xem:
> - **Cách 1 (Chạy Script Python trực tiếp)**: Chạy file `python demo_dirty_read.py` (Script mở Luồng T1 cập nhật dữ liệu nhưng ngâm 8s chưa COMMIT rồi ROLLBACK; Luồng T2 đọc dưới mức `SET TRANSACTION ISOLATION LEVEL READ UNCOMMITTED`).
> - **Cách 2 (Demo trên Web UI)**: Mở đường dẫn `http://127.0.0.1:5000/dat-phong/quan-ly?dirty_read=1` ở Trình duyệt 2.

####  Thao tác Demo trực quan:
* **Cách 1 - Chạy Script Python (`demo_dirty_read.py`)**:
  1. Mở Terminal và gõ: `python demo_dirty_read.py`.
  2. Luồng T1 cập nhật `trang_thai = 'DaNhanPhong'` cho phiếu #8 nhưng ngâm 8 giây chưa `COMMIT`.
  3. Luồng T2 truy vấn dưới mức `READ UNCOMMITTED` và in ra kết quả:
     `==> KẾT QUẢ ĐỌC ĐƯỢC (DIRTY READ RÁC): {'ma_dat_phong': 8, 'trang_thai': 'DaNhanPhong'}`.
  4. Luồng T1 sau 8 giây thực hiện `ROLLBACK;`.
  5. **Kết quả**: Luồng T2 đã đọc được trạng thái `'DaNhanPhong'` **rác** mà thực tế CSDL chưa từng `COMMIT`.

* **Cách 2 - Thao tác trên Web UI**:
  1. Mở Giao dịch T1 trên MySQL Workbench / Python giữ câu lệnh UPDATE phiếu đặt dở dở chừng (chưa `COMMIT`).
  2. Mở trình duyệt 2 truy cập: `http://127.0.0.1:5000/dat-phong/quan-ly?dirty_read=1`.
  3. Màn hình Web UI vẫn hiển thị dòng dữ liệu chưa `COMMIT` của T1.
  4. T1 hủy (`ROLLBACK`), khi tải lại trang thường `http://127.0.0.1:5000/dat-phong/quan-ly` dữ liệu đó biến mất.

####  Kịch bản thuyết trình (Script):
> **Lời nói thuyết trình**:
> *"Kính thưa thầy cô, đối với lỗi **Dirty Read (Đọc dữ liệu rác)**, hệ quản trị CSDL MySQL InnoDB ở mức mặc định sẽ chủ động ngăn chặn bằng cơ chế MVCC. Vì vậy, để demo lỗi này trực quan, chúng em cấu hình truy vấn tra cứu dưới mức cô lập `SET TRANSACTION ISOLATION LEVEL READ UNCOMMITTED`.*
> 
> *Khi chạy script/truy vấn demo, Giao dịch T1 tiến hành đổi trạng thái phiếu đặt nhưng chưa `COMMIT` (đang ngâm). Giao dịch T2 ở mức `READ UNCOMMITTED` đọc được ngay trạng thái mới đó. Nhưng ngay sau đó T1 bị `ROLLBACK`, làm cho dữ liệu mà T2 đã đọc và thông báo trở thành **dữ liệu rác**.*
> 
> **Cách code đã được Fix (trên GitHub)**:
> *Trong mã nguồn sản phẩm chính thức trên Git, chúng em giữ nguyên mức cô lập mặc định **`REPEATABLE READ`** của InnoDB. Mọi câu truy vấn `SELECT` đều đọc qua Snapshot MVCC của các dữ liệu đã `COMMIT` hợp lệ, ngăn chặn 100% hiện tượng Dirty Read."*

---

### 3. Không đọc lại được dữ liệu (Non-repeatable Read)

####  Thao tác Demo trên Giao diện (UI):
1. **Chuẩn bị**: Một phiếu đặt phòng đang ở trạng thái `DaDat` (Ví dụ: Mã đặt phòng #10).
2. **Bước 1**: 
   - Lễ tân A mở trang Quản lý đặt phòng (`/dat-phong/quan-ly`) và nhấn nút **Hủy đặt phòng** cho mã phiếu #10.
   - Hàm `sp_HuyDatPhong` ở bước 1 đọc `SELECT trang_thai ... FROM dat_phong WHERE ma_dat_phong = 10` $\rightarrow$ Nhận giá trị là `'DaDat'`.
3. **Bước 2**: 
   - Ngay giữa bước kiểm tra và bước cập nhật của Lễ tân A, Lễ tân B ở bàn bên cạnh thực hiện thủ tục **Check-in** cho phiếu #10 (`/luu-tru/check-in`).
   - Procedure `sp_XacNhanCheckIn` cập nhật `trang_thai = 'DaNhanPhong'` và `COMMIT` thành công.
4. **Bước 3**: 
   - `sp_HuyDatPhong` của Lễ tân A tiếp tục thực thi bước 2: `UPDATE dat_phong SET trang_thai = 'DaHuy' WHERE ma_dat_phong = 10`.
5. **Kết quả**: Phiếu đặt #10 vừa được Lễ tân B Check-in thành công cho khách ở tại phòng lập tức bị Lễ tân A đè thành `'DaHuy'`. Dữ liệu phiếu đặt bị thay đổi bất ngờ giữa 2 lần đọc/ghi trong cùng tiến trình.

####  Kịch bản thuyết trình (Script):
> **Lời nói thuyết trình**:
> *"Lỗi thứ ba là **Non-repeatable Read (Không đọc lại được dữ liệu)**. Trong kịch bản này, Lễ tân A bấm Hủy đơn đặt phòng #10 khi đơn này đang `DaDat`. Nhưng đúng lúc đó Lễ tân B tại quầy làm thủ tục Check-in cho khách và đổi đơn thành `DaNhanPhong`. Do Lễ tân A đã đọc dữ liệu `'DaDat'` từ trước, lệnh Hủy vẫn tiếp tục chạy và ghi đè đơn vừa Check-in thành `DaHuy`.*
> 
> **Nguyên nhân kỹ thuật trong code ban đầu**:
> *Thủ tục `sp_HuyDatPhong` ban đầu thiếu `START TRANSACTION` và không dùng khóa dòng `FOR UPDATE` ở câu lệnh `SELECT`, dẫn đến dữ liệu bị giao dịch Check-in thay đổi ngay giữa quá trình xử lý.*
> 
> **Cách code đã được Fix (trên GitHub)**:
> *Trong file `sql/03_procedures.sql` đã fix, chúng em đã bọc toàn bộ thủ tục `sp_HuyDatPhong` trong `START TRANSACTION;` và dùng khóa `SELECT ... FOR UPDATE`. Khi Lễ tân A bắt đầu kiểm tra hủy phòng, bản ghi phiếu đặt bị khóa chặt. Lễ tân B muốn Check-in phải chờ Lễ tân A hoàn tất, tránh hoàn toàn việc ghi đè sai lệch trạng thái."*

---

### 4. Bóng ma (Phantom Read)

####  Thao tác Demo trên Giao diện (UI):
1. **Chuẩn bị**: Vào trang Tra cứu phòng trống (`/tim-phong`).
2. **Bước 1**: 
   - Lễ tân A tra cứu phòng trống từ ngày `2026-12-01` đến `2026-12-05`.
   - Kết quả hiển thị danh sách 3 phòng trống (Phòng 101, 102, 103).
3. **Bước 2**: 
   - Trên trình duyệt 2, Khách B tiến hành **Đặt phòng online** chọn Phòng 101 trong khoảng ngày `2026-12-01` đến `2026-12-05` và bấm Xác nhận đặt (`sp_TaoDatPhong`).
   - Giao dịch của Khách B chèn 1 bản ghi mới vào bảng `dat_phong` & `chi_tiet_dat_phong` và `COMMIT`.
4. **Bước 3**: 
   - Lễ tân A thực hiện tìm kiếm lại hoặc làm mới trang trong cùng ca làm việc.
   - Số lượng phòng trống bị giảm từ 3 phòng xuống 2 phòng (Phòng 101 biến mất khỏi tập kết quả).
5. **Kết quả**: Một bản ghi mới được thêm vào từ giao dịch khác đã hoạt động như một **"Bóng ma" (Phantom Record)** làm thay đổi tập kết quả truy vấn đếm/tìm kiếm của Lễ tân A.

####  Kịch bản thuyết trình (Script):
> **Lời nói thuyết trình**:
> *"Lỗi cuối cùng là **Phantom Read (Bóng ma)**. Khi Lễ tân A tra cứu danh sách phòng trống trong khoảng thời gian đầu tháng 12, hệ thống trả về 3 phòng trống. Trong lúc đó Khách B thực hiện đặt thành công phòng 101. Bản ghi mới của Khách B chèn vào CSDL đóng vai trò là một 'bản ghi bóng ma', khiến tập kết quả tìm kiếm của Lễ tân A bị thay đổi đột ngột.*
> 
> **Nguyên nhân kỹ thuật trong code ban đầu**:
> *Do câu truy vấn đếm/tìm kiếm không thực hiện khóa khoảng (Gap Locking) hoặc khóa bảng liên quan, cho phép các giao dịch khác thoải mái `INSERT` thêm bản ghi thỏa mãn điều kiện tìm kiếm.*
> 
> **Cách code đã được Fix (trên GitHub)**:
> *Trong mã nguồn đã tối ưu trên Git, thủ tục `sp_TaoDatPhong` khóa bản ghi phòng cha bằng `SELECT ma_phong ... FOR UPDATE` và kiểm tra ràng buộc thời gian nghiêm ngặt qua `fn_KiemTraPhongTrong`, ngăn chặn 2 đơn đặt cùng thời điểm chèn đè lên nhau."*

---

## III. Hướng Dẫn Khôi Phục Code Khi Thuyết Trình Đồ Án

1. **Khi muốn Demo lỗi cho Hội đồng xem**:
   - Mở 2 trình duyệt song song và làm theo đúng 4 bước thao tác UI ở phần II.
2. **Khi muốn chỉ ra cách Fix lỗi trên GitHub**:
   - Mở các file [03_procedures.sql](file:///c:/Users/mtuan/Downloads/full/Project-HQTCSDL-main/Project-HQTCSDL-main/sql/03_procedures.sql) và [queries.py](file:///c:/Users/mtuan/Downloads/full/Project-HQTCSDL-main/Project-HQTCSDL-main/db/queries.py) đã sửa trên GitHub.
   - Nhấn mạnh các từ khóa: `START TRANSACTION`, `SELECT ... FOR UPDATE`, `COMMIT`, `ROLLBACK`, và `EXIT HANDLER FOR SQLEXCEPTION`.
