SET NAMES utf8mb4;
SET CHARACTER SET utf8mb4;
-- 08_sample_data.sql: Dữ liệu mẫu thử nghiệm hệ thống
USE hotel_management;

-- LƯU Ý: mật khẩu mẫu bên dưới đều là "123456", đã được hash thật bằng
-- werkzeug.security.generate_password_hash("123456") (thuật toán mặc định scrypt).
INSERT INTO nhan_vien (ho_ten, ngay_sinh, gioi_tinh, sdt, email, vai_tro, tai_khoan, mat_khau, trang_thai) VALUES
('Nguyen Van Admin', '1990-01-01', 'Nam', '0901111111', 'admin@hotel.com', 'Admin', 'admin', 'scrypt:32768:8:1$N2VfM3A9Pj1iZ4Qx$21b38fec62fbcfb8602b9e67d2643a0d5c80889f074d2bcf398eb79e8cf16892fc0a316c0fa1a96edaa3ef775317b3bc3ff6aa62bb9ffbf4a51e60dc3fdf4728', 'HoatDong'),
('Tran Thi Le Tan', '1995-05-15', 'Nu', '0902222222', 'letan@hotel.com', 'LeTan', 'letan', 'scrypt:32768:8:1$N2VfM3A9Pj1iZ4Qx$21b38fec62fbcfb8602b9e67d2643a0d5c80889f074d2bcf398eb79e8cf16892fc0a316c0fa1a96edaa3ef775317b3bc3ff6aa62bb9ffbf4a51e60dc3fdf4728', 'HoatDong')
ON DUPLICATE KEY UPDATE ho_ten=VALUES(ho_ten);

INSERT INTO khach_hang (ho_ten, cccd, sdt, email, tai_khoan, mat_khau, dia_chi) VALUES
('Le Van Khach', '012345678901', '0903333333', 'khach1@gmail.com', 'khach1', 'scrypt:32768:8:1$N2VfM3A9Pj1iZ4Qx$21b38fec62fbcfb8602b9e67d2643a0d5c80889f074d2bcf398eb79e8cf16892fc0a316c0fa1a96edaa3ef775317b3bc3ff6aa62bb9ffbf4a51e60dc3fdf4728', 'Hà Nội'),
('Pham Thi Khach', '098765432109', '0904444444', 'khach2@gmail.com', 'khach2', 'scrypt:32768:8:1$N2VfM3A9Pj1iZ4Qx$21b38fec62fbcfb8602b9e67d2643a0d5c80889f074d2bcf398eb79e8cf16892fc0a316c0fa1a96edaa3ef775317b3bc3ff6aa62bb9ffbf4a51e60dc3fdf4728', 'TP. Hồ Chí Minh')
ON DUPLICATE KEY UPDATE ho_ten=VALUES(ho_ten);

INSERT INTO loai_phong (ma_loai_phong, ten_loai_phong, gia_theo_ngay, suc_chua, mo_ta) VALUES
(1, 'Phòng Đơn Standard', 500000.00, 1, 'Phòng 1 giường đơn, thoáng mát, đầy đủ tiện nghi'),
(2, 'Phòng Đôi Deluxe', 800000.00, 2, 'Phòng 1 giường đôi lớn, trang thiết bị hiện đại, view đẹp'),
(3, 'Phòng VIP Suite', 1500000.00, 4, 'Phòng tổng thống cao cấp, rộng rãi, đầy đủ tiện nghi cao cấp')
ON DUPLICATE KEY UPDATE ten_loai_phong=VALUES(ten_loai_phong), gia_theo_ngay=VALUES(gia_theo_ngay), suc_chua=VALUES(suc_chua), mo_ta=VALUES(mo_ta);

INSERT INTO phong (so_phong, ma_loai_phong, tang, trang_thai) VALUES
('101', 1, 1, 'Trong'),
('102', 1, 1, 'Trong'),
('201', 2, 2, 'DangSuDung'),
('202', 2, 2, 'Trong'),
('301', 3, 3, 'Trong')
ON DUPLICATE KEY UPDATE trang_thai=VALUES(trang_thai);

INSERT INTO dich_vu (ten_dich_vu, don_gia, don_vi_tinh) VALUES
('Giặt ủi', 30000.00, 'Bộ'),
('Nước uống đóng chai', 15000.00, 'Chai'),
('Ăn sáng tại phòng', 100000.00, 'Suất')
ON DUPLICATE KEY UPDATE ten_dich_vu=VALUES(ten_dich_vu);

INSERT INTO dat_phong (ma_dat_phong, ma_kh, ma_nv, ngay_nhan_du_kien, ngay_tra_du_kien, trang_thai, nguon_dat) VALUES
(1, 1, 2, '2026-08-18', '2026-08-20', 'DaNhanPhong', 'TaiQuay')
ON DUPLICATE KEY UPDATE trang_thai=VALUES(trang_thai);

INSERT INTO chi_tiet_dat_phong (ma_dat_phong, ma_phong, gia_tai_thoi_diem, ngay_nhan_thuc_te) VALUES
(1, 3, 800000.00, '2026-08-18 14:00:00')
ON DUPLICATE KEY UPDATE gia_tai_thoi_diem=VALUES(gia_tai_thoi_diem);

INSERT INTO su_dung_dich_vu (ma_dat_phong, ma_phong, ma_dich_vu, so_luong) VALUES
(1, 3, 2, 2),
(1, 3, 3, 1)
ON DUPLICATE KEY UPDATE so_luong=VALUES(so_luong);
