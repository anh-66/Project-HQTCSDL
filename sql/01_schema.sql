-- 01_schema.sql: Tạo cấu trúc 9 bảng CSDL (Engine InnoDB)

CREATE TABLE IF NOT EXISTS nhan_vien (
    ma_nv INT AUTO_INCREMENT PRIMARY KEY,
    ho_ten VARCHAR(100) NOT NULL,
    ngay_sinh DATE,
    gioi_tinh ENUM('Nam', 'Nu', 'Khac'),
    sdt VARCHAR(15),
    email VARCHAR(100) UNIQUE,
    vai_tro ENUM('Admin', 'LeTan') NOT NULL,
    tai_khoan VARCHAR(50) UNIQUE NOT NULL,
    mat_khau VARCHAR(255) NOT NULL,
    trang_thai ENUM('DangLam', 'NghiViec') DEFAULT 'DangLam',
    ngay_tao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS khach_hang (
    ma_kh INT AUTO_INCREMENT PRIMARY KEY,
    ho_ten VARCHAR(100) NOT NULL,
    cccd VARCHAR(20) UNIQUE NOT NULL,
    ngay_sinh DATE,
    sdt VARCHAR(15) NOT NULL,
    email VARCHAR(100),
    dia_chi VARCHAR(255),
    tai_khoan VARCHAR(50) UNIQUE NULL,
    mat_khau VARCHAR(255) NULL,
    loai_khach ENUM('TuDangKy', 'TaiQuay') DEFAULT 'TaiQuay',
    ngay_tao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS loai_phong (
    ma_loai_phong INT AUTO_INCREMENT PRIMARY KEY,
    ten_loai_phong VARCHAR(50) NOT NULL,
    gia_theo_ngay DECIMAL(12,2) CHECK (gia_theo_ngay > 0),
    suc_chua INT CHECK (suc_chua > 0),
    mo_ta TEXT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS phong (
    ma_phong INT AUTO_INCREMENT PRIMARY KEY,
    ma_loai_phong INT,
    so_phong VARCHAR(10) UNIQUE NOT NULL,
    tang INT,
    trang_thai ENUM('Trong', 'DaDat', 'DangSuDung', 'BaoTri') DEFAULT 'Trong',
    FOREIGN KEY (ma_loai_phong) REFERENCES loai_phong(ma_loai_phong) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS dat_phong (
    ma_dat_phong INT AUTO_INCREMENT PRIMARY KEY,
    ma_kh INT,
    ma_nv INT NULL,
    nguon_dat ENUM('Online', 'TaiQuay') DEFAULT 'Online',
    ngay_dat DATETIME DEFAULT CURRENT_TIMESTAMP,
    ngay_nhan_du_kien DATE NOT NULL,
    ngay_tra_du_kien DATE NOT NULL,
    trang_thai ENUM('DaDat', 'DaNhanPhong', 'DaTraPhong', 'DaHuy') DEFAULT 'DaDat',
    FOREIGN KEY (ma_kh) REFERENCES khach_hang(ma_kh) ON DELETE RESTRICT ON UPDATE CASCADE,
    FOREIGN KEY (ma_nv) REFERENCES nhan_vien(ma_nv) ON DELETE SET NULL ON UPDATE CASCADE,
    CONSTRAINT chk_ngay_tra_du_kien CHECK (ngay_tra_du_kien > ngay_nhan_du_kien)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS chi_tiet_dat_phong (
    ma_dat_phong INT,
    ma_phong INT,
    gia_tai_thoi_diem DECIMAL(12,2) NOT NULL,
    ngay_nhan_thuc_te DATETIME NULL,
    ngay_tra_thuc_te DATETIME NULL,
    PRIMARY KEY (ma_dat_phong, ma_phong),
    FOREIGN KEY (ma_dat_phong) REFERENCES dat_phong(ma_dat_phong) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (ma_phong) REFERENCES phong(ma_phong) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS hoa_don (
    ma_hoa_don INT AUTO_INCREMENT PRIMARY KEY,
    ma_dat_phong INT UNIQUE,
    ma_nv INT,
    ngay_lap DATETIME DEFAULT CURRENT_TIMESTAMP,
    tong_tien_phong DECIMAL(12,2) DEFAULT 0 CHECK (tong_tien_phong >= 0),
    tong_tien_dich_vu DECIMAL(12,2) DEFAULT 0 CHECK (tong_tien_dich_vu >= 0),
    giam_gia DECIMAL(12,2) DEFAULT 0,
    tong_thanh_toan DECIMAL(12,2) DEFAULT 0,
    phuong_thuc_tt ENUM('TienMat', 'ChuyenKhoan', 'The'),
    trang_thai_tt ENUM('ChuaThanhToan', 'DaThanhToan') DEFAULT 'ChuaThanhToan',
    FOREIGN KEY (ma_dat_phong) REFERENCES dat_phong(ma_dat_phong) ON DELETE RESTRICT ON UPDATE CASCADE,
    FOREIGN KEY (ma_nv) REFERENCES nhan_vien(ma_nv) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS dich_vu (
    ma_dich_vu INT AUTO_INCREMENT PRIMARY KEY,
    ten_dich_vu VARCHAR(100) NOT NULL,
    don_gia DECIMAL(12,2) CHECK (don_gia > 0),
    don_vi_tinh VARCHAR(20)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS su_dung_dich_vu (
    ma_su_dung INT AUTO_INCREMENT PRIMARY KEY,
    ma_dat_phong INT,
    ma_phong INT,
    ma_dich_vu INT,
    so_luong INT CHECK (so_luong > 0),
    ngay_su_dung DATETIME DEFAULT CURRENT_TIMESTAMP,
    thanh_tien DECIMAL(12,2),
    FOREIGN KEY (ma_dat_phong, ma_phong) REFERENCES chi_tiet_dat_phong(ma_dat_phong, ma_phong) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (ma_dich_vu) REFERENCES dich_vu(ma_dich_vu) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;