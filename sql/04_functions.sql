-- 04_functions.sql: Tạo 4 Functions hỗ trợ tính toán
USE hotel_management;

DELIMITER $$

-- Function 1: fn_KiemTraPhongTrong
CREATE FUNCTION fn_KiemTraPhongTrong (
    p_ma_phong INT,
    p_ngay_nhan DATE,
    p_ngay_tra DATE
)
RETURNS TINYINT(1)
READS SQL DATA
BEGIN
    DECLARE v_count INT;

    SELECT COUNT(*) INTO v_count
    FROM chi_tiet_dat_phong ct
    JOIN dat_phong dp ON ct.ma_dat_phong = dp.ma_dat_phong
    WHERE ct.ma_phong = p_ma_phong
      AND dp.trang_thai NOT IN ('DaHuy', 'DaTraPhong')
      AND dp.ngay_nhan_du_kien < p_ngay_tra
      AND dp.ngay_tra_du_kien > p_ngay_nhan;

    IF v_count > 0 THEN
        RETURN 0; -- Đã bị trùng (Không trống)
    ELSE
        RETURN 1; -- Trống
    END IF;
END$$

-- Function 2: fn_TinhTienPhong
CREATE FUNCTION fn_TinhTienPhong (
    p_ma_dat_phong INT
)
RETURNS DECIMAL(12,2)
READS SQL DATA
BEGIN
    DECLARE v_tong_tien DECIMAL(12,2) DEFAULT 0;
    
    SELECT IFNULL(SUM(ct.gia_tai_thoi_diem * GREATEST(DATEDIFF(dp.ngay_tra_du_kien, dp.ngay_nhan_du_kien), 1)), 0)
    INTO v_tong_tien
    FROM chi_tiet_dat_phong ct
    JOIN dat_phong dp ON ct.ma_dat_phong = dp.ma_dat_phong
    WHERE ct.ma_dat_phong = p_ma_dat_phong;

    RETURN v_tong_tien;
END$$

-- Function 3: fn_TinhTienDichVu
CREATE FUNCTION fn_TinhTienDichVu (
    p_ma_dat_phong INT
)
RETURNS DECIMAL(12,2)
READS SQL DATA
BEGIN
    DECLARE v_tong_dv DECIMAL(12,2) DEFAULT 0;

    SELECT IFNULL(SUM(thanh_tien), 0)
    INTO v_tong_dv
    FROM su_dung_dich_vu
    WHERE ma_dat_phong = p_ma_dat_phong;

    RETURN v_tong_dv;
END$$

-- Function 4: fn_DoanhThuTheoThang
CREATE FUNCTION fn_DoanhThuTheoThang (
    p_thang INT,
    p_nam INT
)
RETURNS DECIMAL(12,2)
READS SQL DATA
BEGIN
    DECLARE v_tong_doanh_thu DECIMAL(12,2) DEFAULT 0;

    SELECT IFNULL(SUM(tong_thanh_toan), 0) INTO v_tong_doanh_thu
    FROM hoa_don
    WHERE MONTH(ngay_lap) = p_thang 
      AND YEAR(ngay_lap) = p_nam 
      AND trang_thai_tt = 'DaThanhToan';

    RETURN v_tong_doanh_thu;
END$$

DELIMITER ;