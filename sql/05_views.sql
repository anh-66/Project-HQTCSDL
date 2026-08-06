-- 05_views.sql: Tạo 4 Views phục vụ truy vấn và báo cáo

-- View 1: Tình trạng phòng hiện tại kèm tên loại phòng và giá
CREATE OR REPLACE VIEW vw_TinhTrangPhongHienTai AS
SELECT 
    p.ma_phong,
    p.so_phong,
    p.tang,
    lp.ten_loai_phong,
    lp.gia_theo_ngay,
    p.trang_thai
FROM phong p
JOIN loai_phong lp ON p.ma_loai_phong = lp.ma_loai_phong;

-- View 2: Xem lịch sử đặt phòng của khách hàng
CREATE OR REPLACE VIEW vw_LichSuDatPhongKhachHang AS
SELECT 
    dp.ma_dat_phong,
    kh.ho_ten AS ten_khach_hang,
    kh.sdt,
    p.so_phong,
    dp.ngay_nhan_du_kien,
    dp.ngay_tra_du_kien,
    dp.trang_thai AS trang_thai_dat_phong
FROM dat_phong dp
JOIN khach_hang kh ON dp.ma_kh = kh.ma_kh
JOIN chi_tiet_dat_phong ct ON dp.ma_dat_phong = ct.ma_dat_phong
JOIN phong p ON ct.ma_phong = p.ma_phong;

-- View 3: Báo cáo doanh thu tổng hợp theo tháng
CREATE OR REPLACE VIEW vw_DoanhThuTheoThang AS
SELECT 
    YEAR(ngay_lap) AS nam,
    MONTH(ngay_lap) AS thang,
    COUNT(ma_hoa_don) AS so_luong_hoa_don,
    SUM(tong_tien_phong) AS tong_tien_phong,
    SUM(tong_tien_dich_vu) AS tong_tien_dich_vu,
    SUM(tong_thanh_toan) AS tong_doanh_thu
FROM hoa_don
WHERE trang_thai_tt = 'DaThanhToan'
GROUP BY YEAR(ngay_lap), MONTH(ngay_lap);

-- View 4: Báo cáo tần suất sử dụng và doanh thu dịch vụ
CREATE OR REPLACE VIEW vw_BaoCaoSuDungDichVu AS
SELECT 
    dv.ma_dich_vu,
    dv.ten_dich_vu,
    SUM(sd.so_luong) AS tong_so_luong,
    SUM(sd.thanh_tien) AS tong_doanh_thu_dich_vu
FROM dich_vu dv
LEFT JOIN su_dung_dich_vu sd ON dv.ma_dich_vu = sd.ma_dich_vu
GROUP BY dv.ma_dich_vu, dv.ten_dich_vu;