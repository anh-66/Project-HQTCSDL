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