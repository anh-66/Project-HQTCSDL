
- **File cập nhật**: `sql/03_procedures.sql`
- **Nội dung xử lý**:
  - Bổ sung `START TRANSACTION`, `COMMIT`, `ROLLBACK` và bẫy ngoại lệ `DECLARE EXIT HANDLER FOR SQLEXCEPTION`.
  - Áp dụng khóa độc quyền `FOR UPDATE` cho tất cả các Stored Procedure quản lý giao dịch: `sp_TaoDatPhong`, `sp_CheckOut_LapHoaDon`, `sp_GhiNhanSuDungDichVu`, `sp_HuyDatPhong`, `sp_XacNhanCheckIn`, `sp_XacNhanThanhToan`.
  - Đảm bảo hệ thống vận hành đúng 4 thuộc tính ACID, chống race condition và bảo toàn tính nhất quán CSDL.

---
