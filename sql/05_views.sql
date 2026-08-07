-- 05_views.sql: Tạo 4 Views chuẩn hóa theo tên trong giaoTac-obj.docx
USE hotel_management;

-- View 1: vw_DanhSachPhongTrong
CREATE OR REPLACE VIEW vw_DanhSachPhongTrong AS
SELECT 
    p.ma_phong,
    p.so_phong,
    p.tang,
    lp.ten_loai_phong,
    lp.suc_chua,
    lp.gia_theo_ngay,
    p.trang_thai
FROM phong p
JOIN loai_phong lp ON p.ma_loai_phong = lp.ma_loai_phong
WHERE p.trang_thai = 'Trong';

-- View 2: vw_LichSuDatPhong_KhachHang
CREATE OR REPLACE VIEW vw_LichSuDatPhong_KhachHang AS
SELECT 
    dp.ma_dat_phong,
    kh.ma_kh,
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

-- View 3: vw_ChiTietSuDungDichVu
CREATE OR REPLACE VIEW vw_ChiTietSuDungDichVu AS
SELECT 
    sd.ma_su_dung,
    sd.ma_dat_phong,
    dv.ten_dich_vu,
    sd.so_luong,
    dv.don_gia,
    sd.thanh_tien,
    sd.ngay_su_dung
FROM su_dung_dich_vu sd
JOIN dich_vu dv ON sd.ma_dich_vu = dv.ma_dich_vu;

-- View 4: vw_BaoCaoDoanhThuHoaDon
CREATE OR REPLACE VIEW vw_BaoCaoDoanhThuHoaDon AS
SELECT 
    hd.ma_hoa_don,
    kh.ho_ten AS ten_khach_hang,
    nv.ho_ten AS ten_le_tan,
    hd.tong_tien_phong,
    hd.tong_tien_dich_vu,
    hd.giam_gia,
    hd.tong_thanh_toan,
    hd.ngay_lap,
    hd.trang_thai_tt
FROM hoa_don hd
JOIN dat_phong dp ON hd.ma_dat_phong = dp.ma_dat_phong
JOIN khach_hang kh ON dp.ma_kh = kh.ma_kh
LEFT JOIN nhan_vien nv ON hd.ma_nv = nv.ma_nv;