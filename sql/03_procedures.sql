-- 03_procedures.sql: Tạo 6 Stored Procedures quản lý giao dịch
USE hotel_management;

DELIMITER $$

-- Procedure 1: sp_TaoDatPhong (Dùng SELECT ... FOR UPDATE chống race condition)
CREATE PROCEDURE sp_TaoDatPhong (
    IN p_ma_kh INT,
    IN p_ma_nv INT,
    IN p_nguon_dat ENUM('Online', 'TaiQuay'),
    IN p_ma_phong INT,
    IN p_ngay_nhan_du_kien DATE,
    IN p_ngay_tra_du_kien DATE,
    OUT p_message VARCHAR(255)
)
BEGIN
    DECLARE v_phong_id INT;
    DECLARE v_conflict_count INT;
    DECLARE v_gia_phong DECIMAL(12,2);
    DECLARE v_new_ma_dat_phong INT;
    
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        SET p_message = 'Đã xảy ra lỗi hệ thống, giao dịch bị hủy.';
    END;

    START TRANSACTION;

    -- Khóa dòng phòng bằng FOR UPDATE
    SELECT ma_phong INTO v_phong_id FROM phong WHERE ma_phong = p_ma_phong FOR UPDATE;

    SELECT COUNT(*) INTO v_conflict_count
    FROM chi_tiet_dat_phong ct
    JOIN dat_phong dp ON ct.ma_dat_phong = dp.ma_dat_phong
    WHERE ct.ma_phong = p_ma_phong
      AND dp.trang_thai NOT IN ('DaHuy', 'DaTraPhong')
      AND dp.ngay_nhan_du_kien < p_ngay_tra_du_kien
      AND dp.ngay_tra_du_kien > p_ngay_nhan_du_kien;

    IF v_conflict_count > 0 THEN
        ROLLBACK;
        SET p_message = 'Phòng đã được đặt trong thời gian này.';
    ELSE
        SELECT lp.gia_theo_ngay INTO v_gia_phong
        FROM phong p JOIN loai_phong lp ON p.ma_loai_phong = lp.ma_loai_phong
        WHERE p.ma_phong = p_ma_phong;

        INSERT INTO dat_phong (ma_kh, ma_nv, nguon_dat, ngay_nhan_du_kien, ngay_tra_du_kien, trang_thai)
        VALUES (p_ma_kh, p_ma_nv, p_nguon_dat, p_ngay_nhan_du_kien, p_ngay_tra_du_kien, 'DaDat');
        
        SET v_new_ma_dat_phong = LAST_INSERT_ID();

        INSERT INTO chi_tiet_dat_phong (ma_dat_phong, ma_phong, gia_tai_thoi_diem)
        VALUES (v_new_ma_dat_phong, p_ma_phong, v_gia_phong);

        IF p_ngay_nhan_du_kien = CURDATE() THEN
            UPDATE phong SET trang_thai = 'DaDat' WHERE ma_phong = p_ma_phong;
        END IF;

        COMMIT;
        SET p_message = 'Đặt phòng thành công!';
    END IF;
END$$

-- Procedure 2: sp_XacNhanCheckIn
CREATE PROCEDURE sp_XacNhanCheckIn (
    IN p_ma_dat_phong INT,
    IN p_ma_phong INT,
    OUT p_message VARCHAR(255)
)
BEGIN
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        SET p_message = 'Lỗi hệ thống khi Check-in.';
    END;

    START TRANSACTION;

    UPDATE chi_tiet_dat_phong 
    SET ngay_nhan_thuc_te = NOW() 
    WHERE ma_dat_phong = p_ma_dat_phong AND ma_phong = p_ma_phong;

    UPDATE dat_phong SET trang_thai = 'DaNhanPhong' WHERE ma_dat_phong = p_ma_dat_phong;

    COMMIT;
    SET p_message = 'Check-in thành công!';
END$$

-- Procedure 3: sp_GhiNhanSuDungDichVu
CREATE PROCEDURE sp_GhiNhanSuDungDichVu (
    IN p_ma_dat_phong INT,
    IN p_ma_phong INT,
    IN p_ma_dich_vu INT,
    IN p_so_luong INT,
    OUT p_message VARCHAR(255)
)
BEGIN
    INSERT INTO su_dung_dich_vu (ma_dat_phong, ma_phong, ma_dich_vu, so_luong)
    VALUES (p_ma_dat_phong, p_ma_phong, p_ma_dich_vu, p_so_luong);
    
    SET p_message = 'Thêm dịch vụ thành công!';
END$$

-- Procedure 4: sp_CheckOut_LapHoaDon
CREATE PROCEDURE sp_CheckOut_LapHoaDon (
    IN p_ma_dat_phong INT,
    IN p_ma_nv INT,
    IN p_giam_gia DECIMAL(12,2),
    IN p_phuong_thuc_tt ENUM('TienMat', 'ChuyenKhoan', 'The'),
    OUT p_message VARCHAR(255)
)
BEGIN
    DECLARE v_tien_phong DECIMAL(12,2);
    DECLARE v_tien_dv DECIMAL(12,2);
    DECLARE v_tong_thanhtoan DECIMAL(12,2);

    SET v_tien_phong = fn_TinhTienPhong(p_ma_dat_phong);
    SET v_tien_dv = fn_TinhTienDichVu(p_ma_dat_phong);
    SET v_tong_thanhtoan = (v_tien_phong + v_tien_dv) - p_giam_gia;

    UPDATE chi_tiet_dat_phong 
    SET ngay_tra_thuc_te = NOW() 
    WHERE ma_dat_phong = p_ma_dat_phong;

    INSERT INTO hoa_don (ma_dat_phong, ma_nv, tong_tien_phong, tong_tien_dich_vu, giam_gia, tong_thanh_toan, phuong_thuc_tt, trang_thai_tt)
    VALUES (p_ma_dat_phong, p_ma_nv, v_tien_phong, v_tien_dv, p_giam_gia, v_tong_thanhtoan, p_phuong_thuc_tt, 'ChuaThanhToan')
    ON DUPLICATE KEY UPDATE 
        tong_tien_phong = v_tien_phong,
        tong_tien_dich_vu = v_tien_dv,
        giam_gia = p_giam_gia,
        tong_thanh_toan = v_tong_thanhtoan,
        phuong_thuc_tt = p_phuong_thuc_tt;

    SET p_message = 'Check-out và lập hóa đơn thành công!';
END$$

-- Procedure 5: sp_XacNhanThanhToan
CREATE PROCEDURE sp_XacNhanThanhToan (
    IN p_ma_dat_phong INT,
    OUT p_message VARCHAR(255)
)
BEGIN
    DECLARE EXIT HANDLER FOR SQLEXCEPTION
    BEGIN
        ROLLBACK;
        SET p_message = 'Lỗi hệ thống khi xác nhận thanh toán.';
    END;

    START TRANSACTION;

    UPDATE hoa_don SET trang_thai_tt = 'DaThanhToan' WHERE ma_dat_phong = p_ma_dat_phong;
    UPDATE dat_phong SET trang_thai = 'DaTraPhong' WHERE ma_dat_phong = p_ma_dat_phong;

    COMMIT;
    SET p_message = 'Thanh toán thành công và giải phóng phòng!';
END$$

-- Procedure 6: sp_HuyDatPhong (Kiểm tra điều kiện trước 24h)
CREATE PROCEDURE sp_HuyDatPhong (
    IN p_ma_dat_phong INT,
    OUT p_message VARCHAR(255)
)
BEGIN
    DECLARE v_trang_thai VARCHAR(20);
    DECLARE v_ngay_nhan DATE;

    SELECT trang_thai, ngay_nhan_du_kien INTO v_trang_thai, v_ngay_nhan 
    FROM dat_phong WHERE ma_dat_phong = p_ma_dat_phong;

    IF v_trang_thai != 'DaDat' THEN
        SET p_message = 'Không thể hủy đơn đặt phòng ở trạng thái này.';
    ELSEIF DATEDIFF(v_ngay_nhan, CURDATE()) < 1 THEN
        SET p_message = 'Chỉ được phép hủy đặt phòng trước 24 giờ!';
    ELSE
        UPDATE dat_phong SET trang_thai = 'DaHuy' WHERE ma_dat_phong = p_ma_dat_phong;
        SET p_message = 'Hủy đặt phòng thành công!';
    END IF;
END$$

DELIMITER ;