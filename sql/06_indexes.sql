-- 06_indexes.sql: Tạo các Index tối ưu truy vấn
USE hotel_management;

CREATE INDEX idx_cccd ON khach_hang(cccd);
CREATE INDEX idx_checkindate ON chi_tiet_dat_phong(ngay_nhan_thuc_te);
CREATE INDEX idx_checkoutdate ON chi_tiet_dat_phong(ngay_tra_thuc_te);
CREATE INDEX idx_phong_trangthai ON phong(trang_thai);
CREATE INDEX idx_datphong_khachhang ON dat_phong(ma_kh);