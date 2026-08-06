-- 02_triggers.sql: Tạo 4 Triggers ràng buộc chuẩn hóa theo giaoTac-obj.docx
USE hotel_management;

DELIMITER $$

-- 1. trg_CheckThoiGianDatPhong (BEFORE INSERT)
CREATE TRIGGER trg_CheckThoiGianDatPhong_Insert
BEFORE INSERT ON dat_phong
FOR EACH ROW
BEGIN
    IF NEW.ngay_tra_du_kien <= NEW.ngay_nhan_du_kien THEN
        SIGNAL SQLSTATE '45000' 
        SET MESSAGE_TEXT = 'Ngày trả dự kiến phải lớn hơn ngày nhận dự kiến!';
    END IF;
END$$

-- 2. trg_CheckThoiGianDatPhong (BEFORE UPDATE)
CREATE TRIGGER trg_CheckThoiGianDatPhong_Update
BEFORE UPDATE ON dat_phong
FOR EACH ROW
BEGIN
    IF NEW.ngay_tra_du_kien <= NEW.ngay_nhan_du_kien THEN
        SIGNAL SQLSTATE '45000' 
        SET MESSAGE_TEXT = 'Ngày trả dự kiến phải lớn hơn ngày nhận dự kiến!';
    END IF;
END$$

-- 3. trg_KiemTraXoaPhong: Chống xóa phòng đang được đặt hoặc đang ở
CREATE TRIGGER trg_KiemTraXoaPhong
BEFORE DELETE ON phong
FOR EACH ROW
BEGIN
    IF OLD.trang_thai IN ('DaDat', 'DangSuDung') THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Không thể xóa phòng đang có khách đặt hoặc đang sử dụng!';
    END IF;
END$$

-- 4. trg_TinhThanhTienDichVu: Tự động gán thành tiền = so_luong * don_gia
CREATE TRIGGER trg_TinhThanhTienDichVu
BEFORE INSERT ON su_dung_dich_vu
FOR EACH ROW
BEGIN
    DECLARE v_don_gia DECIMAL(12,2);
    SELECT don_gia INTO v_don_gia FROM dich_vu WHERE ma_dich_vu = NEW.ma_dich_vu;
    SET NEW.thanh_tien = NEW.so_luong * v_don_gia;
END$$

-- 5. trg_CapNhatTrangThaiPhongDat: Tự động đổi trạng thái phòng tương ứng khi phiếu đặt đổi trạng thái
CREATE TRIGGER trg_CapNhatTrangThaiPhongDat
AFTER UPDATE ON dat_phong
FOR EACH ROW
BEGIN
    IF NEW.trang_thai = 'DaTraPhong' OR NEW.trang_thai = 'DaHuy' THEN
        UPDATE phong p 
        JOIN chi_tiet_dat_phong ct ON p.ma_phong = ct.ma_phong 
        SET p.trang_thai = 'Trong' 
        WHERE ct.ma_dat_phong = NEW.ma_dat_phong;
    ELSEIF NEW.trang_thai = 'DaNhanPhong' THEN
        UPDATE phong p 
        JOIN chi_tiet_dat_phong ct ON p.ma_phong = ct.ma_phong 
        SET p.trang_thai = 'DangSuDung' 
        WHERE ct.ma_dat_phong = NEW.ma_dat_phong;
    END IF;
END$$

DELIMITER ;