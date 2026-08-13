"""
db/queries.py
--------------
Cac ham truy van CSDL phuc vu module Auth & Admin (Thanh vien 2):
- Dang ky / kiem tra trung lap Khach hang
- Dang nhap (tim tai khoan trong KhachHang hoac NhanVien)
- Cap nhat thong tin ca nhan (Khach hang / Nhan vien)
- Quan ly tai khoan Nhan vien (them, khoa/mo, danh sach)
- Bao cao doanh thu (goi fn_DoanhThuTheoThang, vw_BaoCaoDoanhThuHoaDon)

Quy uoc chung:
- Moi ham tu mo/dong connection bang get_connection() / close_connection().
- Ham INSERT/UPDATE luon conn.commit() truoc khi dong ket noi.
- Khong hash mat khau o tang nay -> tang route (auth_routes.py) chiu trach nhiem
  hash bang werkzeug.security truoc khi goi xuong day.
"""

from db.connection import get_connection, close_connection


# 1. KHACH HANG: dang ky, kiem tra trung lap, tim kiem, cap nhat ho so

def kiem_tra_trung_khach_hang(cccd=None, email=None, tai_khoan=None, exclude_ma_kh=None):
    """
    Kiem tra CCCD / email / tai khoan da ton tai trong bang khach_hang chua.
    exclude_ma_kh: dung khi CAP NHAT ho so (loai tru chinh ban ghi dang sua).
    Tra ve dict {'cccd': bool, 'email': bool, 'tai_khoan': bool}
    """
    ket_qua = {'cccd': False, 'email': False, 'tai_khoan': False}
    conn = get_connection()
    if not conn:
        return ket_qua
    try:
        with conn.cursor() as cursor:
            if cccd:
                sql = "SELECT ma_kh FROM khach_hang WHERE cccd = %s"
                params = [cccd]
                if exclude_ma_kh:
                    sql += " AND ma_kh != %s"
                    params.append(exclude_ma_kh)
                cursor.execute(sql, params)
                ket_qua['cccd'] = cursor.fetchone() is not None

            if email:
                sql = "SELECT ma_kh FROM khach_hang WHERE email = %s"
                params = [email]
                if exclude_ma_kh:
                    sql += " AND ma_kh != %s"
                    params.append(exclude_ma_kh)
                cursor.execute(sql, params)
                ket_qua['email'] = cursor.fetchone() is not None

            if tai_khoan:
                sql = "SELECT ma_kh FROM khach_hang WHERE tai_khoan = %s"
                params = [tai_khoan]
                if exclude_ma_kh:
                    sql += " AND ma_kh != %s"
                    params.append(exclude_ma_kh)
                cursor.execute(sql, params)
                ket_qua['tai_khoan'] = cursor.fetchone() is not None
        return ket_qua
    finally:
        close_connection(conn)


def dang_ky_khach_hang(ho_ten, cccd, ngay_sinh, sdt, email, dia_chi, tai_khoan, mat_khau_hash):
    """
    Them khach hang moi voi loai_khach = 'TuDangKy'.
    Tra ve ma_kh vua tao, hoac None neu loi.
    """
    conn = get_connection()
    if not conn:
        return None
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO khach_hang
                    (ho_ten, cccd, ngay_sinh, sdt, email, dia_chi,
                     tai_khoan, mat_khau, loai_khach)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 'TuDangKy')
                """,
                (ho_ten, cccd, ngay_sinh, sdt, email, dia_chi, tai_khoan, mat_khau_hash)
            )
            conn.commit()
            return cursor.lastrowid
    except Exception as e:
        conn.rollback()
        print(f"Loi dang_ky_khach_hang: {e}")
        return None
    finally:
        close_connection(conn)


def lay_khach_hang_theo_tai_khoan(tai_khoan):
    """Dung khi dang nhap: lay ho so khach hang theo tai khoan."""
    conn = get_connection()
    if not conn:
        return None
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM khach_hang WHERE tai_khoan = %s", (tai_khoan,)
            )
            return cursor.fetchone()
    finally:
        close_connection(conn)


def lay_khach_hang_theo_id(ma_kh):
    conn = get_connection()
    if not conn:
        return None
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM khach_hang WHERE ma_kh = %s", (ma_kh,))
            return cursor.fetchone()
    finally:
        close_connection(conn)


def cap_nhat_ho_so_khach_hang(ma_kh, sdt, email, dia_chi, mat_khau_hash=None):
    """
    Cap nhat SDT / email / dia chi (va mat khau neu co doi).
    Luu y: phai goi kiem_tra_trung_khach_hang(email=..., exclude_ma_kh=ma_kh)
    o tang route TRUOC khi goi ham nay de dam bao email khong bi trung.
    """
    conn = get_connection()
    if not conn:
        return False
    try:
        with conn.cursor() as cursor:
            if mat_khau_hash:
                cursor.execute(
                    """UPDATE khach_hang
                       SET sdt = %s, email = %s, dia_chi = %s, mat_khau = %s
                       WHERE ma_kh = %s""",
                    (sdt, email, dia_chi, mat_khau_hash, ma_kh)
                )
            else:
                cursor.execute(
                    """UPDATE khach_hang
                       SET sdt = %s, email = %s, dia_chi = %s
                       WHERE ma_kh = %s""",
                    (sdt, email, dia_chi, ma_kh)
                )
            conn.commit()
            return cursor.rowcount > 0
    except Exception as e:
        conn.rollback()
        print(f"Loi cap_nhat_ho_so_khach_hang: {e}")
        return False
    finally:
        close_connection(conn)


# 2. NHAN VIEN: dang nhap, quan ly tai khoan (them, khoa/mo, danh sach), ho so

def lay_nhan_vien_theo_tai_khoan(tai_khoan):
    conn = get_connection()
    if not conn:
        return None
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM nhan_vien WHERE tai_khoan = %s", (tai_khoan,)
            )
            return cursor.fetchone()
    finally:
        close_connection(conn)


def lay_nhan_vien_theo_id(ma_nv):
    conn = get_connection()
    if not conn:
        return None
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM nhan_vien WHERE ma_nv = %s", (ma_nv,))
            return cursor.fetchone()
    finally:
        close_connection(conn)


def kiem_tra_trung_nhan_vien(email=None, tai_khoan=None, exclude_ma_nv=None):
    """Tuong tu kiem_tra_trung_khach_hang nhung cho bang nhan_vien."""
    ket_qua = {'email': False, 'tai_khoan': False}
    conn = get_connection()
    if not conn:
        return ket_qua
    try:
        with conn.cursor() as cursor:
            if email:
                sql = "SELECT ma_nv FROM nhan_vien WHERE email = %s"
                params = [email]
                if exclude_ma_nv:
                    sql += " AND ma_nv != %s"
                    params.append(exclude_ma_nv)
                cursor.execute(sql, params)
                ket_qua['email'] = cursor.fetchone() is not None

            if tai_khoan:
                sql = "SELECT ma_nv FROM nhan_vien WHERE tai_khoan = %s"
                params = [tai_khoan]
                if exclude_ma_nv:
                    sql += " AND ma_nv != %s"
                    params.append(exclude_ma_nv)
                cursor.execute(sql, params)
                ket_qua['tai_khoan'] = cursor.fetchone() is not None
        return ket_qua
    finally:
        close_connection(conn)


def them_nhan_vien(ho_ten, ngay_sinh, gioi_tinh, sdt, email, vai_tro, tai_khoan, mat_khau_hash):
    """Admin them tai khoan Nhan vien moi (Admin hoac LeTan)."""
    conn = get_connection()
    if not conn:
        return None
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO nhan_vien
                    (ho_ten, ngay_sinh, gioi_tinh, sdt, email, vai_tro, tai_khoan, mat_khau)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (ho_ten, ngay_sinh, gioi_tinh, sdt, email, vai_tro, tai_khoan, mat_khau_hash)
            )
            conn.commit()
            return cursor.lastrowid
    except Exception as e:
        conn.rollback()
        print(f"Loi them_nhan_vien: {e}")
        return None
    finally:
        close_connection(conn)


def doi_trang_thai_nhan_vien(ma_nv, trang_thai_moi):
    """
    Khoa / mo tai khoan nhan vien.
    trang_thai_moi: 'DangLam' hoac 'NghiViec'
    """
    conn = get_connection()
    if not conn:
        return False
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "UPDATE nhan_vien SET trang_thai = %s WHERE ma_nv = %s",
                (trang_thai_moi, ma_nv)
            )
            conn.commit()
            return cursor.rowcount > 0
    except Exception as e:
        conn.rollback()
        print(f"Loi doi_trang_thai_nhan_vien: {e}")
        return False
    finally:
        close_connection(conn)


def cap_nhat_ho_so_nhan_vien(ma_nv, sdt, email, mat_khau_hash=None):
    """Nhan vien (Le tan/Admin) tu cap nhat SDT/email/mat khau cua minh."""
    conn = get_connection()
    if not conn:
        return False
    try:
        with conn.cursor() as cursor:
            if mat_khau_hash:
                cursor.execute(
                    "UPDATE nhan_vien SET sdt = %s, email = %s, mat_khau = %s WHERE ma_nv = %s",
                    (sdt, email, mat_khau_hash, ma_nv)
                )
            else:
                cursor.execute(
                    "UPDATE nhan_vien SET sdt = %s, email = %s WHERE ma_nv = %s",
                    (sdt, email, ma_nv)
                )
            conn.commit()
            return cursor.rowcount > 0
    except Exception as e:
        conn.rollback()
        print(f"Loi cap_nhat_ho_so_nhan_vien: {e}")
        return False
    finally:
        close_connection(conn)


def lay_danh_sach_nhan_vien():
    """Danh sach toan bo nhan vien cho Admin quan ly."""
    conn = get_connection()
    if not conn:
        return []
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT ma_nv, ho_ten, sdt, email, vai_tro, tai_khoan, trang_thai, ngay_tao "
                "FROM nhan_vien ORDER BY ma_nv"
            )
            return cursor.fetchall()
    finally:
        close_connection(conn)


# 3. BAO CAO DOANH THU (Admin) - fn_DoanhThuTheoThang, vw_BaoCaoDoanhThuHoaDon

def doanh_thu_theo_thang(thang, nam):
    """
    Goi ham SQL fn_DoanhThuTheoThang(thang, nam) -> tong doanh thu da thu trong thang/nam.
    """
    conn = get_connection()
    if not conn:
        return 0
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT fn_DoanhThuTheoThang(%s, %s) AS doanh_thu", (thang, nam)
            )
            row = cursor.fetchone()
            return row['doanh_thu'] if row and row['doanh_thu'] is not None else 0
    finally:
        close_connection(conn)


def bao_cao_doanh_thu_hoa_don():
    """
    Lay toan bo du lieu tu view vw_BaoCaoDoanhThuHoaDon
    (ma hoa don, ten khach, ten le tan, tien phong, tien dich vu, tong thanh toan...)
    """
    conn = get_connection()
    if not conn:
        return []
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM vw_BaoCaoDoanhThuHoaDon ORDER BY ngay_lap DESC"
            )
            return cursor.fetchall()
    finally:
        close_connection(conn)

# ===========================================================================
# THANH VIEN 4 - MODULE DAT PHONG & CHECK-IN
# ===========================================================================

# 4a. PHONG & LOAI PHONG

def lay_tat_ca_loai_phong():
    """Tra ve danh sach tat ca loai phong (dung cho bo loc tim phong)."""
    conn = get_connection()
    if not conn:
        return []
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM loai_phong ORDER BY gia_theo_ngay")
            return cursor.fetchall()
    finally:
        close_connection(conn)


def lay_phong_trong(ngay_nhan, ngay_tra, ma_loai_phong=None):
    """
    Tim phong trong trong khoang [ngay_nhan, ngay_tra).
    Phong trong = phong khong co phieu dat active nao chong ngay.
    """
    conn = get_connection()
    if not conn:
        return []
    try:
        with conn.cursor() as cursor:
            sql = """
                SELECT p.ma_phong, p.so_phong, p.tang, p.trang_thai,
                       lp.ma_loai_phong, lp.ten_loai_phong,
                       lp.gia_theo_ngay, lp.suc_chua, lp.mo_ta
                FROM phong p
                JOIN loai_phong lp ON p.ma_loai_phong = lp.ma_loai_phong
                WHERE p.trang_thai NOT IN ('BaoTri')
                  AND p.ma_phong NOT IN (
                      SELECT ct.ma_phong
                      FROM chi_tiet_dat_phong ct
                      JOIN dat_phong dp ON ct.ma_dat_phong = dp.ma_dat_phong
                      WHERE dp.trang_thai NOT IN ('DaHuy', 'DaTraPhong')
                        AND dp.ngay_nhan_du_kien < %s
                        AND dp.ngay_tra_du_kien > %s
                  )
            """
            params = [ngay_tra, ngay_nhan]
            if ma_loai_phong:
                sql += " AND p.ma_loai_phong = %s"
                params.append(ma_loai_phong)
            sql += " ORDER BY lp.gia_theo_ngay, p.so_phong"
            cursor.execute(sql, params)
            return cursor.fetchall()
    finally:
        close_connection(conn)


def lay_phong_theo_id(ma_phong):
    """Lay thong tin day du 1 phong kem loai phong."""
    conn = get_connection()
    if not conn:
        return None
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT p.ma_phong, p.so_phong, p.tang, p.trang_thai,
                       lp.ma_loai_phong, lp.ten_loai_phong,
                       lp.gia_theo_ngay, lp.suc_chua, lp.mo_ta
                FROM phong p
                JOIN loai_phong lp ON p.ma_loai_phong = lp.ma_loai_phong
                WHERE p.ma_phong = %s
                """,
                (ma_phong,)
            )
            return cursor.fetchone()
    finally:
        close_connection(conn)


# 4b. KHACH HANG - TIM KIEM & TAO TAI QUAY

def tim_khach_hang_theo_cccd(cccd):
    """Tra cuu khach hang theo CCCD (dung khi le tan walk-in)."""
    conn = get_connection()
    if not conn:
        return None
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM khach_hang WHERE cccd = %s", (cccd,)
            )
            return cursor.fetchone()
    finally:
        close_connection(conn)


def them_khach_hang_tai_quay(ho_ten, cccd, sdt, ngay_sinh=None, email=None, dia_chi=None):
    """
    Tao khach hang vang lai (loai_khach='TaiQuay') khong co tai khoan.
    Tra ve ma_kh vua tao, hoac None neu loi.
    """
    conn = get_connection()
    if not conn:
        return None
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO khach_hang
                    (ho_ten, cccd, ngay_sinh, sdt, email, dia_chi, loai_khach)
                VALUES (%s, %s, %s, %s, %s, %s, 'TaiQuay')
                """,
                (ho_ten, cccd, ngay_sinh, sdt, email, dia_chi)
            )
            conn.commit()
            return cursor.lastrowid
    except Exception as e:
        conn.rollback()
        print(f"Loi them_khach_hang_tai_quay: {e}")
        return None
    finally:
        close_connection(conn)


# 4c. DAT PHONG - GOI STORED PROCEDURE sp_TaoDatPhong

def dat_phong_sp(ma_kh, ma_nv, nguon_dat, ma_phong, ngay_nhan_du_kien, ngay_tra_du_kien):
    """
    Goi CALL sp_TaoDatPhong(..., @p_message).
    sp_TaoDatPhong xu ly:
      - Khoa phong bang SELECT FOR UPDATE (chong race condition)
      - Kiem tra xung dot ngay
      - INSERT dat_phong + chi_tiet_dat_phong (luu gia_tai_thoi_diem)
      - Cap nhat phong.trang_thai = 'DaDat' neu ngay_nhan = hom nay
    Tra ve (success: bool, message: str).
    """
    conn = get_connection()
    if not conn:
        return False, "Khong the ket noi co so du lieu."
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "CALL sp_TaoDatPhong(%s, %s, %s, %s, %s, %s, @p_message)",
                (ma_kh, ma_nv, nguon_dat, ma_phong,
                 ngay_nhan_du_kien, ngay_tra_du_kien)
            )
            conn.commit()
            cursor.execute("SELECT @p_message AS msg")
            row = cursor.fetchone()
            msg = row['msg'] if row else "Khong co phan hoi tu he thong."
            success = ("thành công" in msg.lower() or "thanh cong" in msg.lower())
            return success, msg
    except Exception as e:
        conn.rollback()
        print(f"Loi dat_phong_sp: {e}")
        return False, f"Loi he thong: {str(e)}"
    finally:
        close_connection(conn)


# 4d. LICH SU & QUAN LY PHIEU DAT

def lay_dat_phong_cua_kh(ma_kh):
    """Lay toan bo lich su dat phong cua mot khach hang (moi nhat truoc)."""
    conn = get_connection()
    if not conn:
        return []
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT dp.ma_dat_phong, dp.nguon_dat, dp.ngay_dat,
                       dp.ngay_nhan_du_kien, dp.ngay_tra_du_kien,
                       dp.trang_thai,
                       p.so_phong, p.ma_phong,
                       lp.ten_loai_phong, lp.gia_theo_ngay,
                       ct.ngay_nhan_thuc_te, ct.ngay_tra_thuc_te,
                       ct.gia_tai_thoi_diem
                FROM dat_phong dp
                JOIN chi_tiet_dat_phong ct ON dp.ma_dat_phong = ct.ma_dat_phong
                JOIN phong p ON ct.ma_phong = p.ma_phong
                JOIN loai_phong lp ON p.ma_loai_phong = lp.ma_loai_phong
                WHERE dp.ma_kh = %s
                ORDER BY dp.ngay_dat DESC
                """,
                (ma_kh,)
            )
            return cursor.fetchall()
    finally:
        close_connection(conn)


def lay_tat_ca_dat_phong(trang_thai=None):
    """Lay toan bo phieu dat (cho le tan quan ly). Loc theo trang_thai neu co."""
    conn = get_connection()
    if not conn:
        return []
    try:
        with conn.cursor() as cursor:
            sql = """
                SELECT dp.ma_dat_phong, dp.nguon_dat, dp.ngay_dat,
                       dp.ngay_nhan_du_kien, dp.ngay_tra_du_kien,
                       dp.trang_thai,
                       kh.ho_ten AS ten_khach, kh.sdt, kh.cccd,
                       p.so_phong, p.ma_phong,
                       lp.ten_loai_phong, lp.gia_theo_ngay,
                       ct.ngay_nhan_thuc_te, ct.ngay_tra_thuc_te,
                       ct.gia_tai_thoi_diem,
                       nv.ho_ten AS ten_le_tan
                FROM dat_phong dp
                JOIN khach_hang kh ON dp.ma_kh = kh.ma_kh
                JOIN chi_tiet_dat_phong ct ON dp.ma_dat_phong = ct.ma_dat_phong
                JOIN phong p ON ct.ma_phong = p.ma_phong
                JOIN loai_phong lp ON p.ma_loai_phong = lp.ma_loai_phong
                LEFT JOIN nhan_vien nv ON dp.ma_nv = nv.ma_nv
            """
            params = []
            if trang_thai:
                sql += " WHERE dp.trang_thai = %s"
                params.append(trang_thai)
            sql += " ORDER BY dp.ngay_dat DESC"
            cursor.execute(sql, params)
            return cursor.fetchall()
    finally:
        close_connection(conn)


def lay_dat_phong_theo_id(ma_dat_phong):
    """Lay chi tiet day du 1 phieu dat phong."""
    conn = get_connection()
    if not conn:
        return None
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT dp.ma_dat_phong, dp.ma_kh, dp.ma_nv,
                       dp.nguon_dat, dp.ngay_dat,
                       dp.ngay_nhan_du_kien, dp.ngay_tra_du_kien,
                       dp.trang_thai,
                       kh.ho_ten AS ten_khach, kh.sdt, kh.cccd, kh.email,
                       p.so_phong, p.ma_phong,
                       lp.ten_loai_phong, lp.gia_theo_ngay,
                       ct.ngay_nhan_thuc_te, ct.ngay_tra_thuc_te,
                       ct.gia_tai_thoi_diem
                FROM dat_phong dp
                JOIN khach_hang kh ON dp.ma_kh = kh.ma_kh
                JOIN chi_tiet_dat_phong ct ON dp.ma_dat_phong = ct.ma_dat_phong
                JOIN phong p ON ct.ma_phong = p.ma_phong
                JOIN loai_phong lp ON p.ma_loai_phong = lp.ma_loai_phong
                WHERE dp.ma_dat_phong = %s
                """,
                (ma_dat_phong,)
            )
            return cursor.fetchone()
    finally:
        close_connection(conn)


# 4e. CHECK-IN - GOI STORED PROCEDURE sp_XacNhanCheckIn
#
# sp_XacNhanCheckIn thuc hien trong 1 transaction:
#   1. UPDATE chi_tiet_dat_phong SET ngay_nhan_thuc_te = NOW()
#      WHERE ma_dat_phong = p_ma_dat_phong AND ma_phong = p_ma_phong
#   2. UPDATE dat_phong SET trang_thai = 'DaNhanPhong'
#      WHERE ma_dat_phong = p_ma_dat_phong
#   => Trigger trg_CapNhatTrangThaiPhongDat (AFTER UPDATE tren dat_phong)
#      tu dong chay: UPDATE phong SET trang_thai = 'DangSuDung'
#      cho tat ca phong trong phieu dat do.

def xac_nhan_checkin_sp(ma_dat_phong, ma_phong):
    """
    Goi CALL sp_XacNhanCheckIn(p_ma_dat_phong, p_ma_phong, @p_message).
    Tra ve (success: bool, message: str).
    Sau khi goi thanh cong:
      - chi_tiet_dat_phong.ngay_nhan_thuc_te = NOW()
      - dat_phong.trang_thai = 'DaNhanPhong'
      - Trigger tu dong: phong.trang_thai = 'DangSuDung'
    """
    conn = get_connection()
    if not conn:
        return False, "Khong the ket noi co so du lieu."
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "CALL sp_XacNhanCheckIn(%s, %s, @p_message)",
                (ma_dat_phong, ma_phong)
            )
            conn.commit()
            cursor.execute("SELECT @p_message AS msg")
            row = cursor.fetchone()
            msg = row['msg'] if row else "Khong co phan hoi tu he thong."
            success = ("thành công" in msg.lower() or "thanh cong" in msg.lower())
            return success, msg
    except Exception as e:
        conn.rollback()
        print(f"Loi xac_nhan_checkin_sp: {e}")
        return False, f"Loi he thong: {str(e)}"
    finally:
        close_connection(conn)


# 4f. HUY DAT PHONG - GOI STORED PROCEDURE sp_HuyDatPhong
#
# sp_HuyDatPhong thuc hien:
#   1. Kiem tra trang_thai = 'DaDat' (chi huy khi chua nhan phong)
#   2. Kiem tra DATEDIFF(ngay_nhan_du_kien, CURDATE()) >= 1 (phai truoc 24h)
#   3. UPDATE dat_phong SET trang_thai = 'DaHuy'
#   => Trigger trg_CapNhatTrangThaiPhongDat tu dong:
#      UPDATE phong SET trang_thai = 'Trong' (giai phong phong)

def huy_dat_phong_sp(ma_dat_phong):
    """
    Goi CALL sp_HuyDatPhong(p_ma_dat_phong, @p_message).
    Tra ve (success: bool, message: str).
    Sau khi huy thanh cong:
      - dat_phong.trang_thai = 'DaHuy'
      - Trigger tu dong: phong.trang_thai = 'Trong' (giai phong phong)
    """
    conn = get_connection()
    if not conn:
        return False, "Khong the ket noi co so du lieu."
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "CALL sp_HuyDatPhong(%s, @p_message)",
                (ma_dat_phong,)
            )
            conn.commit()
            cursor.execute("SELECT @p_message AS msg")
            row = cursor.fetchone()
            msg = row['msg'] if row else "Khong co phan hoi tu he thong."
            success = ("thành công" in msg.lower() or "thanh cong" in msg.lower())
            return success, msg
    except Exception as e:
        conn.rollback()
        print(f"Loi huy_dat_phong_sp: {e}")
        return False, f"Loi he thong: {str(e)}"
    finally:
        close_connection(conn)


# 4g. TINH TIEN PHONG - GOI FUNCTION fn_TinhTienPhong
#
# fn_TinhTienPhong(p_ma_dat_phong) tinh:
#   SUM( gia_tai_thoi_diem  <- gia tai thoi diem dat (luu trong chi_tiet_dat_phong)
#        * GREATEST(DATEDIFF(ngay_tra_du_kien, ngay_nhan_du_kien), 1) )
# Dung dung gia_tai_thoi_diem, khong phai gia hien tai loai phong.

def tinh_tien_phong(ma_dat_phong):
    """
    Goi fn_TinhTienPhong(ma_dat_phong) tu DB.
    Tra ve so tien phong (Decimal), hoac 0 neu loi.
    """
    conn = get_connection()
    if not conn:
        return 0
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT fn_TinhTienPhong(%s) AS tien_phong", (ma_dat_phong,)
            )
            row = cursor.fetchone()
            return row['tien_phong'] if row and row['tien_phong'] is not None else 0
    finally:
        close_connection(conn)


# ===========================================================================
# THANH VIEN 3 - MODULE QUAN LY PHONG & DICH VU
# ===========================================================================

# 5a. QUAN LY PHONG

def lay_danh_sach_phong(trang_thai=None, tang=None):
    """Lay danh sach phong, JOIN loai phong. Co the filter theo trang thai va tang."""
    conn = get_connection()
    if not conn:
        return []
    try:
        with conn.cursor() as cursor:
            sql = """SELECT p.ma_phong, p.so_phong, p.tang, p.trang_thai,
                            lp.ma_loai_phong, lp.ten_loai_phong, lp.gia_theo_ngay, lp.suc_chua
                     FROM phong p
                     JOIN loai_phong lp ON p.ma_loai_phong = lp.ma_loai_phong
                     WHERE 1=1"""
            params = []
            if trang_thai:
                sql += " AND p.trang_thai = %s"
                params.append(trang_thai)
            if tang:
                sql += " AND p.tang = %s"
                params.append(tang)
            sql += " ORDER BY p.so_phong"
            cursor.execute(sql, params)
            return cursor.fetchall()
    except Exception as e:
        print(f"Loi truy van danh sach phong: {e}")
        return []
    finally:
        close_connection(conn)

def lay_phong_theo_ma(ma_phong):
    """Lay thong tin 1 phong theo ma."""
    conn = get_connection()
    if not conn:
        return None
    try:
        with conn.cursor() as cursor:
            sql = """SELECT p.*, lp.ten_loai_phong, lp.gia_theo_ngay
                     FROM phong p
                     JOIN loai_phong lp ON p.ma_loai_phong = lp.ma_loai_phong
                     WHERE p.ma_phong = %s"""
            cursor.execute(sql, (ma_phong,))
            return cursor.fetchone()
    except Exception as e:
        print(f"Loi truy van phong: {e}")
        return None
    finally:
        close_connection(conn)

def them_phong(so_phong, ma_loai_phong, tang):
    """Them phong moi. Tra ve (success, message)."""
    import pymysql
    conn = get_connection()
    if not conn:
        return False, "Khong the ket noi CSDL"
    try:
        with conn.cursor() as cursor:
            sql = "INSERT INTO phong (so_phong, ma_loai_phong, tang, trang_thai) VALUES (%s, %s, %s, 'Trong')"
            cursor.execute(sql, (so_phong, ma_loai_phong, tang))
        conn.commit()
        return True, "Thêm phòng thành công!"
    except pymysql.err.IntegrityError:
        return False, "Số phòng đã tồn tại!"
    except Exception as e:
        return False, f"Lỗi thêm phòng: {e}"
    finally:
        close_connection(conn)

def sua_phong(ma_phong, so_phong, ma_loai_phong, tang, trang_thai):
    """
    Cap nhat thong tin phong.
    Quy tac nghiep vu: khong duoc doi ma_loai_phong khi phong đang DaDat hoac DangSuDung.
    """
    import pymysql
    conn = get_connection()
    if not conn:
        return False, "Khong the ket noi CSDL"
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT ma_loai_phong, trang_thai FROM phong WHERE ma_phong = %s", (ma_phong,))
            hien_tai = cursor.fetchone()
            if hien_tai:
                if hien_tai['trang_thai'] in ('DaDat', 'DangSuDung') and int(hien_tai['ma_loai_phong']) != int(ma_loai_phong):
                    return False, "Không thể đổi loại phòng khi phòng đang có khách đặt hoặc đang sử dụng!"
            
            sql = """UPDATE phong SET so_phong = %s, ma_loai_phong = %s, tang = %s, trang_thai = %s
                     WHERE ma_phong = %s"""
            cursor.execute(sql, (so_phong, ma_loai_phong, tang, trang_thai, ma_phong))
        conn.commit()
        return True, "Cập nhật phòng thành công!"
    except pymysql.err.IntegrityError:
        return False, "Số phòng đã tồn tại!"
    except pymysql.err.OperationalError as e:
        if '45000' in str(e):
            return False, "Không thể đổi loại phòng khi phòng đang có khách đặt hoặc đang sử dụng!"
        return False, f"Lỗi cập nhật phòng: {e}"
    except Exception as e:
        return False, f"Lỗi cập nhật phòng: {e}"
    finally:
        close_connection(conn)

def xoa_phong(ma_phong):
    """
    Xoa phong. Trigger trg_KiemTraXoaPhong / Python check se chan neu phong dang DaDat/DangSuDung.
    """
    import pymysql
    conn = get_connection()
    if not conn:
        return False, "Khong the ket noi CSDL"
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT trang_thai FROM phong WHERE ma_phong = %s", (ma_phong,))
            hien_tai = cursor.fetchone()
            if hien_tai and hien_tai['trang_thai'] in ('DaDat', 'DangSuDung'):
                return False, "Không thể xóa phòng đang có khách đặt hoặc đang sử dụng!"
            cursor.execute("DELETE FROM phong WHERE ma_phong = %s", (ma_phong,))
        conn.commit()
        return True, "Xóa phòng thành công!"
    except pymysql.err.OperationalError as e:
        if '45000' in str(e):
            return False, "Không thể xóa phòng đang có khách đặt hoặc đang sử dụng!"
        return False, f"Lỗi xóa phòng: {e}"
    except Exception as e:
        return False, f"Lỗi xóa phòng: {e}"
    finally:
        close_connection(conn)

# 5b. QUAN LY LOAI PHONG

def lay_danh_sach_loai_phong():
    """Lay danh sach tat ca loai phong."""
    conn = get_connection()
    if not conn:
        return []
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM loai_phong ORDER BY ma_loai_phong")
            return cursor.fetchall()
    except Exception as e:
        print(f"Loi truy van loai phong: {e}")
        return []
    finally:
        close_connection(conn)

def lay_loai_phong_theo_ma(ma_loai_phong):
    """Lay thong tin 1 loai phong theo ma."""
    conn = get_connection()
    if not conn:
        return None
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM loai_phong WHERE ma_loai_phong = %s", (ma_loai_phong,))
            return cursor.fetchone()
    except Exception as e:
        print(f"Loi truy van loai phong: {e}")
        return None
    finally:
        close_connection(conn)

def them_loai_phong(ten_loai_phong, gia_theo_ngay, suc_chua, mo_ta):
    """Them loai phong moi."""
    conn = get_connection()
    if not conn:
        return False, "Khong the ket noi CSDL"
    try:
        with conn.cursor() as cursor:
            sql = "INSERT INTO loai_phong (ten_loai_phong, gia_theo_ngay, suc_chua, mo_ta) VALUES (%s, %s, %s, %s)"
            cursor.execute(sql, (ten_loai_phong, gia_theo_ngay, suc_chua, mo_ta))
        conn.commit()
        return True, "Thêm loại phòng thành công!"
    except Exception as e:
        return False, f"Lỗi thêm loại phòng: {e}"
    finally:
        close_connection(conn)

def sua_loai_phong(ma_loai_phong, ten_loai_phong, gia_theo_ngay, suc_chua, mo_ta):
    """Cap nhat thong tin loai phong va don gia theo ngay."""
    conn = get_connection()
    if not conn:
        return False, "Khong the ket noi CSDL"
    try:
        with conn.cursor() as cursor:
            sql = """UPDATE loai_phong SET ten_loai_phong = %s, gia_theo_ngay = %s, suc_chua = %s, mo_ta = %s
                     WHERE ma_loai_phong = %s"""
            cursor.execute(sql, (ten_loai_phong, gia_theo_ngay, suc_chua, mo_ta, ma_loai_phong))
        conn.commit()
        return True, "Cập nhật loại phòng thành công!"
    except Exception as e:
        return False, f"Lỗi cập nhật loại phòng: {e}"
    finally:
        close_connection(conn)

def xoa_loai_phong(ma_loai_phong):
    """Xoa loai phong. Se loi neu con phong thuoc loai nay (FK RESTRICT)."""
    import pymysql
    conn = get_connection()
    if not conn:
        return False, "Khong the ket noi CSDL"
    try:
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM loai_phong WHERE ma_loai_phong = %s", (ma_loai_phong,))
        conn.commit()
        return True, "Xóa loại phòng thành công!"
    except pymysql.err.IntegrityError:
        return False, "Không thể xóa loại phòng đang có phòng sử dụng!"
    except Exception as e:
        return False, f"Lỗi xóa loại phòng: {e}"
    finally:
        close_connection(conn)

# 5c. QUAN LY DICH VU

def lay_danh_sach_dich_vu():
    """Lay danh sach tat ca dich vu."""
    conn = get_connection()
    if not conn:
        return []
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM dich_vu ORDER BY ma_dich_vu")
            return cursor.fetchall()
    except Exception as e:
        print(f"Loi truy van dich vu: {e}")
        return []
    finally:
        close_connection(conn)

def them_dich_vu(ten_dich_vu, don_gia, don_vi_tinh):
    """Them dich vu moi."""
    conn = get_connection()
    if not conn:
        return False, "Khong the ket noi CSDL"
    try:
        with conn.cursor() as cursor:
            sql = "INSERT INTO dich_vu (ten_dich_vu, don_gia, don_vi_tinh) VALUES (%s, %s, %s)"
            cursor.execute(sql, (ten_dich_vu, don_gia, don_vi_tinh))
        conn.commit()
        return True, "Thêm dịch vụ thành công!"
    except Exception as e:
        return False, f"Lỗi thêm dịch vụ: {e}"
    finally:
        close_connection(conn)

def sua_dich_vu(ma_dich_vu, ten_dich_vu, don_gia, don_vi_tinh):
    """Cap nhat thong tin dich vu va don gia."""
    conn = get_connection()
    if not conn:
        return False, "Khong the ket noi CSDL"
    try:
        with conn.cursor() as cursor:
            sql = "UPDATE dich_vu SET ten_dich_vu = %s, don_gia = %s, don_vi_tinh = %s WHERE ma_dich_vu = %s"
            cursor.execute(sql, (ten_dich_vu, don_gia, don_vi_tinh, ma_dich_vu))
        conn.commit()
        return True, "Cập nhật dịch vụ thành công!"
    except Exception as e:
        return False, f"Lỗi cập nhật dịch vụ: {e}"
    finally:
        close_connection(conn)

def xoa_dich_vu(ma_dich_vu):
    """Xoa dich vu. Se loi neu dich vu đang duoc su dung (FK RESTRICT)."""
    import pymysql
    conn = get_connection()
    if not conn:
        return False, "Khong the ket noi CSDL"
    try:
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM dich_vu WHERE ma_dich_vu = %s", (ma_dich_vu,))
        conn.commit()
        return True, "Xóa dịch vụ thành công!"
    except pymysql.err.IntegrityError:
        return False, "Không thể xóa dịch vụ đang được sử dụng!"
    except Exception as e:
        return False, f"Lỗi xóa dịch vụ: {e}"
    finally:
        close_connection(conn)

def lay_danh_sach_tang():
    """Lay danh sach cac tang co phong (dung cho filter & so do phong)."""
    conn = get_connection()
    if not conn:
        return []
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT DISTINCT tang FROM phong ORDER BY tang")
            return [row['tang'] for row in cursor.fetchall()]
    except Exception as e:
        print(f"Loi truy van tang: {e}")
        return []
    finally:
        close_connection(conn)
