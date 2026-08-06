-- 02_triggers.sql: Tạo 4 Triggers xử lý ràng buộc tự động

DELIMITER $$

-- 1. Trigger kiểm tra thời gian đặt phòng khi INSERT
CREATE TRIGGER trg_CheckThoiGianDatPhong_Insert
BEFORE INSERT ON dat_phong
FOR EACH ROW
BEGIN
    IF NEW.ngay_tra_du_kien <= NEW.ngay_nhan_du_kien THEN
        SIGNAL SQLSTATE '45000' 
        SET MESSAGE_TEXT = 'Ngày trả dự kiến phải lớn hơn ngày nhận dự kiến!';
    END IF;
END$$

-- 2. Trigger kiểm tra thời gian đặt phòng khi UPDATE
CREATE TRIGGER trg_CheckThoiGianDatPhong_Update
BEFORE UPDATE ON dat_phong
FOR EACH ROW
BEGIN
    IF NEW.ngay_tra_du_kien <= NEW.ngay_nhan_du_kien THEN
        SIGNAL SQLSTATE '45000' 
        SET MESSAGE_TEXT = 'Ngày trả dự kiến phải lớn hơn ngày nhận dự kiến!';
    END IF;
END$$

-- 3. Trigger tự động tính thành tiền khi thêm dịch vụ sử dụng
CREATE TRIGGER trg_TinhThanhTienDichVu
BEFORE INSERT ON su_dung_dich_vu
FOR EACH ROW
BEGIN
    DECLARE v_don_gia DECIMAL(12,2);
    SELECT don_gia INTO v_don_gia FROM dich_vu WHERE ma_dich_vu = NEW.ma_dich_vu;
    SET NEW.thanh_tien = NEW.so_luong * v_don_gia;
END$$

-- 4. Trigger tự động chuyển trạng thái phòng thành 'Trong' khi check-out thực tế
CREATE TRIGGER trg_CapNhatTrangThaiPhongSauCheckOut
AFTER UPDATE ON chi_tiet_dat_phong
FOR EACH ROW
BEGIN
    IF NEW.ngay_tra_thuc_te IS NOT NULL AND OLD.ngay_tra_thuc_te IS NULL THEN
        UPDATE phong SET trang_thai = 'Trong' WHERE ma_phong = NEW.ma_phong;
    END IF;
END$$

DELIMITER ;