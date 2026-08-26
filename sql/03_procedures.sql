-- test_loi/sql/03_procedures.sql
-- (File SQL được chỉnh sửa cố tình để gây ra LỖI 1: Lost Update và LỖI 2: Dirty Read khi demo trên Web)
USE hotel_management;

DELIMITER $$

-- ============================================================================
-- LỖI 1: LOST UPDATE (MẤT DỮ LIỆU CẬP NHẬT) TRONG SP_TAODATPHONG
-- Nguyên nhân: Đã BỎ câu lệnh FOR UPDATE khóa dòng phòng và THÊM SLEEP(5)
-- Khi 2 khách hàng bấm Đặt phòng cùng lúc trên Web UI, cả 2 tiến trình đều đọc
-- conflict_count = 0 trước khi INSERT. Kết quả cả 2 đều đặt thành công cùng 1 phòng!
-- ============================================================================
DROP PROCEDURE IF EXISTS sp_TaoDatPhong$$
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
        SET p_message = 'Lỗi hệ thống trong phiên bản test lỗi.';
    END;

    START TRANSACTION;

    -- LỖI: SELECT KHÔNG CÓ "FOR UPDATE" -> Không khóa bản ghi phòng
    SELECT ma_phong INTO v_phong_id FROM phong WHERE ma_phong = p_ma_phong;

    -- TẠO ĐỘ TRỄ 5 GIÂY ĐỂ DỄ DÀNG THAO TÁC 2 TAB TRÊN BÌNH THƯỜNG (DEMO WEB UI)
    SELECT SLEEP(5) INTO v_phong_id;

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
        SET p_message = '[DEMO LOST UPDATE] Đặt phòng thành công!';
    END IF;
END$$


-- ============================================================================
-- LỖI 2: DIRTY READ (ĐỌC DỮ LIỆU RÁC)
-- Thủ tục này tạm thời UPDATE giá của loại phòng 1 thành 9.999.999 VNĐ, ngủ 8 giây
-- rồi ROLLBACK. Nếu người dùng khác xem giá phòng ở mức READ UNCOMMITTED sẽ thấy 9.999.999 VNĐ
-- ============================================================================
DROP PROCEDURE IF EXISTS sp_DemoDirtyRead_CapNhatGia$$
CREATE PROCEDURE sp_DemoDirtyRead_CapNhatGia (
    IN p_ma_loai_phong INT,
    IN p_gia_moi DECIMAL(12,2),
    OUT p_message VARCHAR(255)
)
BEGIN
    START TRANSACTION;

    -- Thay đổi giá phòng nhưng CHƯA COMMIT
    UPDATE loai_phong SET gia_theo_ngay = p_gia_moi WHERE ma_loai_phong = p_ma_loai_phong;
    
    -- Tạm dừng 8 giây để tab khác đọc dữ liệu rác
    SELECT SLEEP(8);

    -- HỦY GIAO DỊCH (ROLLBACK)
    ROLLBACK;
    SET p_message = 'Đã Rollback giá phòng về ban đầu!';
END$$

-- Giữ nguyên các procedure khác
CREATE PROCEDURE IF NOT EXISTS sp_XacNhanCheckIn (
    IN p_ma_dat_phong INT, IN p_ma_phong INT, OUT p_message VARCHAR(255)
)
BEGIN
    START TRANSACTION;
    UPDATE chi_tiet_dat_phong SET ngay_nhan_thuc_te = NOW() WHERE ma_dat_phong = p_ma_dat_phong AND ma_phong = p_ma_phong;
    UPDATE dat_phong SET trang_thai = 'DaNhanPhong' WHERE ma_dat_phong = p_ma_dat_phong;
    COMMIT;
    SET p_message = 'Check-in thành công!';
END$$

CREATE PROCEDURE IF NOT EXISTS sp_GhiNhanSuDungDichVu (
    IN p_ma_dat_phong INT, IN p_ma_phong INT, IN p_ma_dich_vu INT, IN p_so_luong INT, OUT p_message VARCHAR(255)
)
BEGIN
    INSERT INTO su_dung_dich_vu (ma_dat_phong, ma_phong, ma_dich_vu, so_luong) VALUES (p_ma_dat_phong, p_ma_phong, p_ma_dich_vu, p_so_luong);
    SET p_message = 'Thêm dịch vụ thành công!';
END$$

CREATE PROCEDURE IF NOT EXISTS sp_CheckOut_LapHoaDon (
    IN p_ma_dat_phong INT, IN p_ma_nv INT, IN p_giam_gia DECIMAL(12,2), IN p_phuong_thuc_tt ENUM('TienMat', 'ChuyenKhoan', 'The'), OUT p_message VARCHAR(255)
)
BEGIN
    DECLARE v_tien_phong DECIMAL(12,2); DECLARE v_tien_dv DECIMAL(12,2); DECLARE v_tong_thanhtoan DECIMAL(12,2);
    SET v_tien_phong = fn_TinhTienPhong(p_ma_dat_phong); SET v_tien_dv = fn_TinhTienDichVu(p_ma_dat_phong); SET v_tong_thanhtoan = (v_tien_phong + v_tien_dv) - p_giam_gia;
    UPDATE chi_tiet_dat_phong SET ngay_tra_thuc_te = NOW() WHERE ma_dat_phong = p_ma_dat_phong;
    INSERT INTO hoa_don (ma_dat_phong, ma_nv, tong_tien_phong, tong_tien_dich_vu, giam_gia, tong_thanh_toan, phuong_thuc_tt, trang_thai_tt)
    VALUES (p_ma_dat_phong, p_ma_nv, v_tien_phong, v_tien_dv, p_giam_gia, v_tong_thanhtoan, p_phuong_thuc_tt, 'ChuaThanhToan')
    ON DUPLICATE KEY UPDATE tong_tien_phong = v_tien_phong, tong_tien_dich_vu = v_tien_dv, giam_gia = p_giam_gia, tong_thanh_toan = v_tong_thanhtoan, phuong_thuc_tt = p_phuong_thuc_tt;
    SET p_message = 'Check-out thành công!';
END$$

CREATE PROCEDURE IF NOT EXISTS sp_XacNhanThanhToan (IN p_ma_dat_phong INT, OUT p_message VARCHAR(255))
BEGIN
    START TRANSACTION;
    UPDATE hoa_don SET trang_thai_tt = 'DaThanhToan' WHERE ma_dat_phong = p_ma_dat_phong;
    UPDATE dat_phong SET trang_thai = 'DaTraPhong' WHERE ma_dat_phong = p_ma_dat_phong;
    COMMIT;
    SET p_message = 'Thanh toán thành công!';
END$$

CREATE PROCEDURE IF NOT EXISTS sp_HuyDatPhong (IN p_ma_dat_phong INT, OUT p_message VARCHAR(255))
BEGIN
    UPDATE dat_phong SET trang_thai = 'DaHuy' WHERE ma_dat_phong = p_ma_dat_phong;
    SET p_message = 'Hủy đặt phòng thành công!';
END$$

DELIMITER ;
