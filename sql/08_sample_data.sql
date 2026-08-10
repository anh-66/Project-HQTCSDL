-- 08_sample_data.sql: Dữ liệu mẫu thử nghiệm hệ thống
USE hotel_management;

-- LƯU Ý: mật khẩu mẫu bên dưới đều là "123456", đã được hash thật bằng
-- werkzeug.security.generate_password_hash("123456") (thuật toán mặc định scrypt).
-- Dùng đúng chuỗi hash này để đăng nhập thử được ngay từ giao diện (không cần hash lại).
INSERT INTO nhan_vien (ho_ten, ngay_sinh, gioi_tinh, sdt, email, vai_tro, tai_khoan, mat_khau, trang_thai) VALUES
('Nguyen Van Admin', '1990-01-01', 'Nam', '0901111111', 'admin@hotel.com', 'Admin', 'admin',
 'scrypt:32768:8:1$Xql1i0SoYCapYKPf$319fb3ad96ed06cda579a617472686d2e472f817791b51bfc5eb8d26ac5a3421a9861edc4ece002370ed023727987cb135d83c79f9c43d9798fca552c5d84f0e', 'DangLam'),
('Tran Thi Le Tan', '1998-05-10', 'Nu', '0902222222', 'letan@hotel.com', 'LeTan', 'letan01',
 'scrypt:32768:8:1$Xql1i0SoYCapYKPf$319fb3ad96ed06cda579a617472686d2e472f817791b51bfc5eb8d26ac5a3421a9861edc4ece002370ed023727987cb135d83c79f9c43d9798fca552c5d84f0e', 'DangLam'),
('Hoang Van Le Tan 2', '1999-11-02', 'Nam', '0903333333', 'letan2@hotel.com', 'LeTan', 'letan02',
 'scrypt:32768:8:1$Xql1i0SoYCapYKPf$319fb3ad96ed06cda579a617472686d2e472f817791b51bfc5eb8d26ac5a3421a9861edc4ece002370ed023727987cb135d83c79f9c43d9798fca552c5d84f0e', 'NghiViec');

INSERT INTO khach_hang (ho_ten, cccd, ngay_sinh, sdt, email, dia_chi, tai_khoan, mat_khau, loai_khach) VALUES
('Le Van Khach', '012345678901', '1995-03-15', '0988888888', 'khach1@gmail.com', 'Ha Noi', 'khach01',
 'scrypt:32768:8:1$Xql1i0SoYCapYKPf$319fb3ad96ed06cda579a617472686d2e472f817791b51bfc5eb8d26ac5a3421a9861edc4ece002370ed023727987cb135d83c79f9c43d9798fca552c5d84f0e', 'TuDangKy'),
('Pham Thi Mai', '012345678902', '1992-08-20', '0977777777', 'mai.pham@gmail.com', 'Da Nang', NULL, NULL, 'TaiQuay'),
('Nguyen Van Walk-in', '012345678903', '1988-12-01', '0966666666', NULL, NULL, NULL, NULL, 'TaiQuay');

INSERT INTO loai_phong (ten_loai_phong, gia_theo_ngay, suc_chua, mo_ta) VALUES
('Standard', 500000.00, 2, 'Phòng tiêu chuẩn 1 giường đôi'),
('Deluxe', 800000.00, 2, 'Phòng cao cấp hướng biển'),
('Suite', 1500000.00, 4, 'Phòng gia đình sang trọng');

INSERT INTO phong (ma_loai_phong, so_phong, tang, trang_thai) VALUES
(1, 'P101', 1, 'Trong'),
(1, 'P102', 1, 'Trong'),
(2, 'P201', 2, 'Trong'),
(3, 'P301', 3, 'Trong');

INSERT INTO dich_vu (ten_dich_vu, don_gia, don_vi_tinh) VALUES
('Giặt ủi', 30000.00, 'Bộ'),
('Nước uống đóng chai', 15000.00, 'Chai'),
('Ăn sáng tại phòng', 100000.00, 'Suất');