-- 06_indexes.sql: Tạo các Index tối ưu tốc độ truy vấn

-- Index tra cứu CCCD khách hàng nhanh
CREATE INDEX idx_cccd ON khach_hang(cccd);

-- Index cho thời gian check-in/check-out thực tế trên bảng chi tiết
CREATE INDEX idx_checkindate ON chi_tiet_dat_phong(ngay_nhan_thuc_te);
CREATE INDEX idx_checkoutdate ON chi_tiet_dat_phong(ngay_tra_thuc_te);

-- Index hỗ trợ tìm kiếm phòng theo trạng thái
CREATE INDEX idx_phong_trangthai ON phong(trang_thai);

-- Index khóa ngoại tra cứu lịch sử đặt phòng nhanh
CREATE INDEX idx_datphong_khachhang ON dat_phong(ma_kh);