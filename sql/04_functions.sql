-- 04_functions.sql: Tạo 4 Functions tính toán logic

DELIMITER $$

-- Function 1: Đếm số ngày lưu trú giữa 2 mốc ngày
CREATE FUNCTION fn_DemSoNgayLuuTru (
    p_ngay_nhan DATE,
    p_ngay_tra DATE
)
RETURNS INT
DETERMINISTIC
BEGIN
    DECLARE v_so_ngay INT;
    SET v_so_ngay = DATEDIFF(p_ngay_tra, p_ngay_nhan);
    IF v_so_ngay <= 0 THEN
        SET v_so_ngay = 1;
    END IF;
    RETURN v_so_ngay;
END$$

-- Function 2: Tính tổng tiền phòng của 1 đơn đặt phòng
CREATE FUNCTION fn_TinhTongTienPhong (
    p_ma_dat_phong INT
)
RETURNS DECIMAL(12,2)
READS SQL DATA
BEGIN
    DECLARE v_tong_tien DECIMAL(12,2) DEFAULT 0;
    
    SELECT IFNULL(SUM(ct.gia_tai_thoi_diem * fn_DemSoNgayLuuTru(dp.ngay_nhan_du_kien, dp.ngay_tra_du_kien)), 0)
    INTO v_tong_tien
    FROM chi_tiet_dat_phong ct
    JOIN dat_phong dp ON ct.ma_dat_phong = dp.ma_dat_phong
    WHERE ct.ma_dat_phong = p_ma_dat_phong;

    RETURN v_tong_tien;
END$$

-- Function 3: Tính tổng tiền dịch vụ của 1 đơn đặt phòng
CREATE FUNCTION fn_TinhTongTienDichVu (
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

-- Function 4: Kiểm tra phòng có đang trống trong khoảng thời gian hay không (Trả về 1: Trống, 0: Bận)
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
        RETURN 0;
    ELSE
        RETURN 1;
    END IF;
END$$

DELIMITER ;