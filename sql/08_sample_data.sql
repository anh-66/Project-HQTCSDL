-- 08_sample_data.sql: Thêm dữ liệu mẫu thử nghiệm hệ thống

-- 1. NhanVien
INSERT INTO nhan_vien (ho_ten, ngay_sinh, gioi_tinh, sdt, email, vai_tro, tai_khoan, mat_khau) VALUES
('Nguyen Van Admin', '1990-01-01', 'Nam', '0901111111', 'admin@hotel.com', 'Admin', 'admin', 'pbkdf2:sha256:hash_sample_admin'),
('Tran Thi Le Tan', '1998-05-10', 'Nu', '0902222222', 'letan@hotel.com', 'LeTan', 'letan01', 'pbkdf2:sha256:hash_sample_letan');

-- 2. KhachHang
INSERT INTO khach_hang (ho_ten, cccd, ngay_sinh, sdt, email, dia_chi, loai_khach) VALUES
('Le Van Khach', '012345678901', '1995-03-15', '0988888888', 'khach1@gmail.com', 'Ha Noi', 'TuDangKy'),
('Pham Thi Mai', '012345678902', '1992-08-20', '0977777777', 'mai.pham@gmail.com', 'Da Nang', 'TaiQuay');

-- 3. LoaiPhong
INSERT INTO loai_phong (ten_loai_phong, gia_theo_ngay, suc_chua, mo_ta) VALUES
('Standard', 500000.00, 2, 'Phòng tiêu chuẩn 1 giường đôi'),
('Deluxe', 800000.00, 2, 'Phòng cao cấp hướng biển'),
('Suite', 1500000.00, 4, 'Phòng gia đình sang trọng');

-- 4. Phong
INSERT INTO phong (ma_loai_phong, so_phong, tang, trang_thai) VALUES
(1, 'P101', 1, 'Trong'),
(1, 'P102', 1, 'Trong'),
(2, 'P201', 2, 'Trong'),
(3, 'P301', 3, 'Trong');

-- 5. DichVu
INSERT INTO dich_vu (ten_dich_vu, don_gia, don_vi_tinh) VALUES
('Giặt ủi', 30000.00, 'Bộ'),
('Nước uống đóng chai', 15000.00, 'Chai'),
('Ăn sáng tại phòng', 100000.00, 'Suất');

-- 6. DatPhong mẫu
INSERT INTO dat_phong (ma_kh, ma_nv, nguon_dat, ngay_nhan_du_kien, ngay_tra_du_kien, trang_thai) VALUES
(1, NULL, 'Online', CURDATE(), DATE_ADD(CURDATE(), INTERVAL 2 DAY), 'DaDat');

-- 7. ChiTietDatPhong mẫu
INSERT INTO chi_tiet_dat_phong (ma_dat_phong, ma_phong, gia_tai_thoi_diem) VALUES
(1, 1, 500000.00);