"""
db/queries.py
-------------
Tập hợp tất cả các hàm truy vấn Cơ sở dữ liệu MySQL hoàn chỉnh cho toàn bộ hệ thống (TV1, TV2, TV3, TV4, TV5).
Bao gồm:
- Auth, Quản lý Nhân viên & Hồ sơ Khách hàng (TV2)
- Phòng, Loại phòng & Danh mục Dịch vụ (TV3)
- Đặt phòng trực tuyến & Check-in (TV4)
- Báo cáo Doanh thu & Thống kê (TV2)
- Sử dụng Dịch vụ phát sinh, Check-out & Thanh toán Hóa đơn (TV5)
"""

import time

from db.connection import get_connection, close_connection
import pymysql



# 1. AUTH & HỒ SƠ KHÁCH HÀNG (MEMBER 2)


def kiem_tra_trung_khach_hang(cccd=None, email=None, tai_khoan=None, exclude_ma_kh=None):
    """
    Kiểm tra CCCD / email / tài khoản đã tồn tại trong bảng khach_hang chưa.
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
    Thêm khách hàng mới tự đăng ký online (loai_khach = 'TuDangKy').
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
        print(f"Lỗi dang_ky_khach_hang: {e}")
        return None
    finally:
        close_connection(conn)


def lay_khach_hang_theo_tai_khoan(tai_khoan):
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
        print(f"Lỗi cap_nhat_ho_so_khach_hang: {e}")
        return False
    finally:
        close_connection(conn)


def tim_khach_hang_theo_cccd(cccd):
    conn = get_connection()
    if not conn:
        return None
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM khach_hang WHERE cccd = %s", (cccd,))
            return cursor.fetchone()
    finally:
        close_connection(conn)


def them_khach_hang_tai_quay(ho_ten, cccd, sdt, ngay_sinh=None, email=None, dia_chi=None):
    conn = get_connection()
    if not conn:
        return None, "Không thể kết nối CSDL"
    try:
        with conn.cursor() as cursor:
            sql = """
                INSERT INTO khach_hang (ho_ten, cccd, ngay_sinh, sdt, email, dia_chi, loai_khach)
                VALUES (%s, %s, %s, %s, %s, %s, 'TaiQuay')
            """
            cursor.execute(sql, (ho_ten, cccd, ngay_sinh, sdt, email, dia_chi))
            ma_kh = cursor.lastrowid
        conn.commit()
        return ma_kh, "Thêm khách hàng thành công"
    except Exception as e:
        conn.rollback()
        return None, f"Lỗi khi thêm khách hàng: {str(e)}"
    finally:
        close_connection(conn)



# 2. QUẢN LÝ NHÂN VIÊN & TÀI KHOẢN (MEMBER 2)


def lay_nhan_vien_theo_tai_khoan(tai_khoan):
    conn = get_connection()
    if not conn:
        return None
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM nhan_vien WHERE tai_khoan = %s", (tai_khoan,))
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
        print(f"Lỗi them_nhan_vien: {e}")
        return None
    finally:
        close_connection(conn)


def doi_trang_thai_nhan_vien(ma_nv, trang_thai_moi):
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
        print(f"Lỗi doi_trang_thai_nhan_vien: {e}")
        return False
    finally:
        close_connection(conn)


def cap_nhat_ho_so_nhan_vien(ma_nv, sdt, email, mat_khau_hash=None):
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
        print(f"Lỗi cap_nhat_ho_so_nhan_vien: {e}")
        return False
    finally:
        close_connection(conn)


def lay_danh_sach_nhan_vien():
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



# 3. PHÒNG, LOẠI PHÒNG, DỊCH VỤ (MEMBER 3 & MEMBER 4)


def lay_tat_ca_loai_phong():
    conn = get_connection()
    if not conn:
        return []
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM loai_phong ORDER BY ma_loai_phong ASC")
            return cursor.fetchall()
    finally:
        close_connection(conn)


def lay_phong_trong(ngay_nhan, ngay_tra, ma_loai_phong=None):
    conn = get_connection()
    if not conn:
        return []
    try:
        with conn.cursor() as cursor:
            sql = """
                SELECT p.ma_phong, p.so_phong, p.tang, p.trang_thai,
                       lp.ma_loai_phong, lp.ten_loai_phong, lp.gia_theo_ngay, lp.suc_chua, lp.mo_ta
                FROM phong p
                JOIN loai_phong lp ON p.ma_loai_phong = lp.ma_loai_phong
                WHERE p.trang_thai != 'BaoTri'
                  AND fn_KiemTraPhongTrong(p.ma_phong, %s, %s) = 1
            """
            params = [ngay_nhan, ngay_tra]
            if ma_loai_phong:
                sql += " AND p.ma_loai_phong = %s"
                params.append(ma_loai_phong)

            sql += " ORDER BY lp.gia_theo_ngay, p.so_phong ASC"
            cursor.execute(sql, params)
            return cursor.fetchall()
    finally:
        close_connection(conn)


def lay_phong_theo_id(ma_phong):
    conn = get_connection()
    if not conn:
        return None
    try:
        with conn.cursor() as cursor:
            sql = """
                SELECT p.*, lp.ten_loai_phong, lp.gia_theo_ngay, lp.suc_chua, lp.mo_ta
                FROM phong p
                JOIN loai_phong lp ON p.ma_loai_phong = lp.ma_loai_phong
                WHERE p.ma_phong = %s
            """
            cursor.execute(sql, (ma_phong,))
            return cursor.fetchone()
    finally:
        close_connection(conn)


def lay_danh_sach_phong(trang_thai=None, tang=None):
    conn = get_connection()
    if not conn:
        return []
    try:
        with conn.cursor() as cursor:
            sql = """
                SELECT p.ma_phong, p.so_phong, p.tang, p.trang_thai,
                       lp.ma_loai_phong, lp.ten_loai_phong, lp.gia_theo_ngay, lp.suc_chua
                FROM phong p
                JOIN loai_phong lp ON p.ma_loai_phong = lp.ma_loai_phong
                WHERE 1=1
            """
            params = []
            if trang_thai:
                sql += " AND p.trang_thai = %s"
                params.append(trang_thai)
            if tang:
                sql += " AND p.tang = %s"
                params.append(tang)

            sql += " ORDER BY p.tang ASC, p.so_phong ASC"
            cursor.execute(sql, params)
            return cursor.fetchall()
    except Exception as e:
        print(f"Lỗi lay_danh_sach_phong: {e}")
        return []
    finally:
        close_connection(conn)


def lay_phong_theo_ma(ma_phong):
    return lay_phong_theo_id(ma_phong)


def them_phong(so_phong, ma_loai_phong, tang, trang_thai='Trong'):
    conn = get_connection()
    if not conn:
        return False, "Không thể kết nối CSDL"
    try:
        with conn.cursor() as cursor:
            sql = "INSERT INTO phong (so_phong, ma_loai_phong, tang, trang_thai) VALUES (%s, %s, %s, %s)"
            cursor.execute(sql, (so_phong, ma_loai_phong, tang, trang_thai))
        conn.commit()
        return True, "Thêm phòng thành công!"
    except pymysql.err.IntegrityError:
        return False, "Số phòng đã tồn tại!"
    except Exception as e:
        return False, f"Lỗi thêm phòng: {e}"
    finally:
        close_connection(conn)


def sua_phong(ma_phong, so_phong, ma_loai_phong, tang, trang_thai):
    conn = get_connection()
    if not conn:
        return False, "Không thể kết nối CSDL"
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT trang_thai, ma_loai_phong FROM phong WHERE ma_phong = %s FOR UPDATE", (ma_phong,))
            hien_tai = cursor.fetchone()
            if hien_tai and hien_tai['trang_thai'] in ('DaDat', 'DangSuDung') and int(ma_loai_phong) != int(hien_tai['ma_loai_phong']):
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
    conn = get_connection()
    if not conn:
        return False, "Không thể kết nối CSDL"
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


def lay_danh_sach_loai_phong():
    return lay_tat_ca_loai_phong()


def lay_loai_phong_theo_ma(ma_loai_phong):
    conn = get_connection()
    if not conn:
        return None
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM loai_phong WHERE ma_loai_phong = %s", (ma_loai_phong,))
            return cursor.fetchone()
    except Exception as e:
        print(f"Lỗi lay_loai_phong_theo_ma: {e}")
        return None
    finally:
        close_connection(conn)


def them_loai_phong(ten_loai_phong, gia_theo_ngay, suc_chua, mo_ta):
    conn = get_connection()
    if not conn:
        return False, "Không thể kết nối CSDL"
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


def sua_loai_phong(ma_loai_phong, ten_loai_phong, gia_theo_ngay, suc_chua, mo_ta, gia_cu=None):
    conn = get_connection()
    if not conn:
        return False, "Không thể kết nối CSDL"
    try:
        with conn.cursor() as cursor:
            # (1) Khóa độc quyền dòng loai_phong trong suốt giao dịch này.
            cursor.execute(
                "SELECT gia_theo_ngay FROM loai_phong WHERE ma_loai_phong = %s FOR UPDATE",
                (ma_loai_phong,)
            )
            row = cursor.fetchone()
            if not row:
                conn.rollback()
                return False, "Loại phòng không tồn tại!"

            gia_hien_tai = float(row['gia_theo_ngay'])

            # (2) Kiểm tra optimistic: giá vừa đọc (đã có khóa) có còn khớp với
            # giá mà người dùng thấy lúc mở form hay không.
            if gia_cu is not None and abs(gia_hien_tai - float(gia_cu)) > 0.001:
                conn.rollback()
                return False, (
                    f"Cập nhật thất bại: Giá loại phòng đã bị một giao dịch khác thay đổi "
                    f"(từ {float(gia_cu):,.0f} VNĐ thành {gia_hien_tai:,.0f} VNĐ) ngay trong lúc bạn "
                    f"đang chỉnh sửa. Vui lòng tải lại trang để lấy dữ liệu mới nhất rồi thử lại, "
                    f"tránh ghi đè mất thay đổi vừa rồi (chống Lost Update)."
                )

            sql = """UPDATE loai_phong SET ten_loai_phong = %s, gia_theo_ngay = %s, suc_chua = %s, mo_ta = %s
                     WHERE ma_loai_phong = %s"""
            cursor.execute(sql, (ten_loai_phong, gia_theo_ngay, suc_chua, mo_ta, ma_loai_phong))
        conn.commit()
        return True, "Cập nhật loại phòng thành công!"
    except Exception as e:
        conn.rollback()
        return False, f"Lỗi cập nhật loại phòng: {e}"
    finally:
        close_connection(conn)


def xoa_loai_phong(ma_loai_phong):
    conn = get_connection()
    if not conn:
        return False, "Không thể kết nối CSDL"
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


def lay_danh_sach_dich_vu():
    conn = get_connection()
    if not conn:
        return []
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM dich_vu ORDER BY ma_dich_vu")
            return cursor.fetchall()
    except Exception as e:
        print(f"Lỗi lay_danh_sach_dich_vu: {e}")
        return []
    finally:
        close_connection(conn)


def them_dich_vu(ten_dich_vu, don_gia, don_vi_tinh):
    conn = get_connection()
    if not conn:
        return False, "Không thể kết nối CSDL"
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
    conn = get_connection()
    if not conn:
        return False, "Không thể kết nối CSDL"
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
    conn = get_connection()
    if not conn:
        return False, "Không thể kết nối CSDL"
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
    conn = get_connection()
    if not conn:
        return []
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT DISTINCT tang FROM phong ORDER BY tang")
            return [row['tang'] for row in cursor.fetchall()]
    except Exception as e:
        print(f"Lỗi lay_danh_sach_tang: {e}")
        return []
    finally:
        close_connection(conn)



# 4. ĐẶT PHÒNG, CHECK-IN & QUẢN LÝ PHIẾU ĐẶT (MEMBER 4)


def dat_phong_sp(ma_kh, ma_nv, nguon_dat, ma_phong, ngay_nhan_du_kien=None, ngay_tra_du_kien=None, ngay_nhan=None, ngay_tra=None):
    ngay_nhan = ngay_nhan_du_kien or ngay_nhan
    ngay_tra = ngay_tra_du_kien or ngay_tra
    conn = get_connection()
    if not conn:
        return False, "Không thể kết nối CSDL"
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "CALL sp_TaoDatPhong(%s, %s, %s, %s, %s, %s, @p_msg)",
                (ma_kh, ma_nv, nguon_dat, ma_phong, ngay_nhan, ngay_tra)
            )
            cursor.execute("SELECT @p_msg AS message")
            row = cursor.fetchone()
            msg = row['message'] if row else "Thao tác hoàn tất."

            if 'thành công' in msg.lower() or 'thanh cong' in msg.lower():
                conn.commit()
                return True, msg
            else:
                conn.rollback()
                return False, msg
    except Exception as e:
        conn.rollback()
        return False, f"Lỗi hệ thống: {str(e)}"
    finally:
        close_connection(conn)


def lay_dat_phong_cua_kh(ma_kh):
    conn = get_connection()
    if not conn:
        return []
    try:
        with conn.cursor() as cursor:
            sql = """
                SELECT dp.ma_dat_phong, dp.ngay_dat, dp.ngay_nhan_du_kien, dp.ngay_tra_du_kien,
                       dp.trang_thai, dp.nguon_dat,
                       ct.ma_phong, ct.gia_tai_thoi_diem, ct.ngay_nhan_thuc_te, ct.ngay_tra_thuc_te,
                       p.so_phong, lp.ten_loai_phong, lp.gia_theo_ngay,
                       fn_TinhTienPhong(dp.ma_dat_phong) AS tong_tien_phong
                FROM dat_phong dp
                JOIN chi_tiet_dat_phong ct ON dp.ma_dat_phong = ct.ma_dat_phong
                JOIN phong p ON ct.ma_phong = p.ma_phong
                JOIN loai_phong lp ON p.ma_loai_phong = lp.ma_loai_phong
                WHERE dp.ma_kh = %s
                ORDER BY dp.ngay_dat DESC
            """
            cursor.execute(sql, (ma_kh,))
            return cursor.fetchall()
    finally:
        close_connection(conn)


def lay_tat_ca_dat_phong(trang_thai=None):
    conn = get_connection()
    if not conn:
        return []
    try:
        with conn.cursor() as cursor:
            sql = """
                SELECT dp.ma_dat_phong, dp.ngay_dat, dp.ngay_nhan_du_kien, dp.ngay_tra_du_kien,
                       dp.trang_thai, dp.nguon_dat,
                       kh.ho_ten AS ten_khach, kh.sdt AS sdt_khach, kh.cccd,
                       p.so_phong, p.ma_phong, lp.ten_loai_phong, lp.gia_theo_ngay,
                       ct.gia_tai_thoi_diem, ct.ngay_nhan_thuc_te, ct.ngay_tra_thuc_te,
                       nv.ho_ten AS ten_le_tan,
                       fn_TinhTienPhong(dp.ma_dat_phong) AS tong_tien_phong
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
    conn = get_connection()
    if not conn:
        return None
    try:
        with conn.cursor() as cursor:
            sql = """
                SELECT dp.ma_dat_phong, dp.ma_kh, dp.ma_nv, dp.ngay_dat, 
                       dp.ngay_nhan_du_kien, dp.ngay_tra_du_kien,
                       dp.trang_thai, dp.nguon_dat,
                       kh.ho_ten AS ten_khach, kh.sdt AS sdt_khach, kh.cccd, kh.email,
                       p.ma_phong, p.so_phong, lp.ten_loai_phong, lp.gia_theo_ngay,
                       ct.gia_tai_thoi_diem, ct.ngay_nhan_thuc_te, ct.ngay_tra_thuc_te,
                       fn_TinhTienPhong(dp.ma_dat_phong) AS tong_tien_phong
                FROM dat_phong dp
                JOIN khach_hang kh ON dp.ma_kh = kh.ma_kh
                JOIN chi_tiet_dat_phong ct ON dp.ma_dat_phong = ct.ma_dat_phong
                JOIN phong p ON ct.ma_phong = p.ma_phong
                JOIN loai_phong lp ON p.ma_loai_phong = lp.ma_loai_phong
                WHERE dp.ma_dat_phong = %s
            """
            cursor.execute(sql, (ma_dat_phong,))
            return cursor.fetchone()
    finally:
        close_connection(conn)


def huy_dat_phong_sp(ma_dat_phong):
    conn = get_connection()
    if not conn:
        return False, "Không thể kết nối CSDL"
    try:
        with conn.cursor() as cursor:
            cursor.execute("CALL sp_HuyDatPhong(%s, @p_msg)", (ma_dat_phong,))
            cursor.execute("SELECT @p_msg AS message")
            row = cursor.fetchone()
            msg = row['message'] if row else "Thao tác hoàn tất."

            if 'thành công' in msg.lower() or 'thanh cong' in msg.lower():
                conn.commit()
                return True, msg
            else:
                conn.rollback()
                return False, msg
    except Exception as e:
        conn.rollback()
        return False, f"Lỗi hệ thống: {str(e)}"
    finally:
        close_connection(conn)


def xac_nhan_checkin_sp(ma_dat_phong, ma_phong):
    conn = get_connection()
    if not conn:
        return False, "Không thể kết nối CSDL"
    try:
        with conn.cursor() as cursor:
            cursor.execute("CALL sp_XacNhanCheckIn(%s, %s, @p_msg)", (ma_dat_phong, ma_phong))
            cursor.execute("SELECT @p_msg AS message")
            row = cursor.fetchone()
            msg = row['message'] if row else "Thao tác hoàn tất."

            if 'thành công' in msg.lower() or 'thanh cong' in msg.lower():
                conn.commit()
                return True, msg
            else:
                conn.rollback()
                return False, msg
    except Exception as e:
        conn.rollback()
        return False, f"Lỗi hệ thống: {str(e)}"
    finally:
        close_connection(conn)


def tinh_tien_phong(ma_dat_phong):
    conn = get_connection()
    if not conn:
        return 0
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT fn_TinhTienPhong(%s) AS tien_phong", (ma_dat_phong,))
            row = cursor.fetchone()
            return float(row['tien_phong']) if row and row['tien_phong'] else 0
    finally:
        close_connection(conn)



# 5. BÁO CÁO DOANH THU (MEMBER 2)


def doanh_thu_theo_thang(thang, nam):
    conn = get_connection()
    if not conn:
        return 0
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT fn_DoanhThuTheoThang(%s, %s) AS doanh_thu", (thang, nam))
            row = cursor.fetchone()
            return row['doanh_thu'] if row and row['doanh_thu'] is not None else 0
    finally:
        close_connection(conn)


def bao_cao_doanh_thu_hoa_don():
    conn = get_connection()
    if not conn:
        return []
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM vw_BaoCaoDoanhThuHoaDon ORDER BY ngay_lap DESC")
            return cursor.fetchall()
    finally:
        close_connection(conn)



# 6. SỬ DỤNG DỊCH VỤ, CHECK-OUT & HÓA ĐƠN (MEMBER 5)


def lay_danh_sach_phong_dung_dich_vu():
    """
    Lấy danh sách các phiếu đặt phòng đang ở trạng thái 'DaNhanPhong'
    (Đã sửa thứ tự JOIN đúng: JOIN chi_tiet_dat_phong trước rồi mới JOIN phong).
    """
    conn = get_connection()
    if not conn:
        return []
    try:
        with conn.cursor() as cursor:
            sql = """
                SELECT 
                    dp.ma_dat_phong,
                    dp.ma_kh, 
                    kh.ho_ten AS ten_khach_hang, 
                    dp.ngay_nhan_du_kien,
                    dp.ngay_tra_du_kien,
                    p.ma_phong,
                    p.so_phong
                FROM dat_phong dp
                JOIN khach_hang kh ON dp.ma_kh = kh.ma_kh
                JOIN chi_tiet_dat_phong ct ON dp.ma_dat_phong = ct.ma_dat_phong
                JOIN phong p ON ct.ma_phong = p.ma_phong
                WHERE dp.trang_thai = 'DaNhanPhong'
                ORDER BY p.so_phong ASC
            """
            cursor.execute(sql)
            return cursor.fetchall()
    except Exception as e:
        print(f"Lỗi lay_danh_sach_phong_dung_dich_vu: {e}")
        return []
    finally:
        close_connection(conn)


def lay_dich_vu_da_dung(ma_dat_phong):
    conn = get_connection()
    if not conn:
        return []
    try:
        with conn.cursor() as cursor:
            sql = """
                SELECT
                    ma_su_dung,
                    ma_dat_phong,
                    ten_dich_vu,
                    so_luong,
                    don_gia,
                    thanh_tien,
                    ngay_su_dung
                FROM vw_ChiTietSuDungDichVu
                WHERE ma_dat_phong = %s
                ORDER BY ngay_su_dung DESC
            """
            cursor.execute(sql, (ma_dat_phong,))
            return cursor.fetchall()
    except Exception as e:
        print(f"Lỗi lay_dich_vu_da_dung: {e}")
        return []
    finally:
        close_connection(conn)


# def ghi_nhan_su_dung_dich_vu(ma_dat_phong, ma_phong, ma_dich_vu, so_luong):
#     conn = get_connection()
#     if not conn:
#         return False, "Không thể kết nối tới CSDL"
#     try:
#         with conn.cursor() as cursor:
#             cursor.execute(
#                 "CALL sp_GhiNhanSuDungDichVu(%s, %s, %s, %s, @msg)",
#                 (ma_dat_phong, ma_phong, ma_dich_vu, so_luong)              
#             )   
#             cursor.execute("SELECT @msg AS message") 
#             res = cursor.fetchone()
#             msg = res['message'] if res and res.get('message') else "Thêm dịch vụ thành công!"
#             conn.commit()
#             return True, msg
#     except Exception as e:
#         conn.rollback()
#         print(f"Lỗi ghi_nhan_su_dung_dich_vu: {e}")
#         return False, f"Lỗi: {str(e)}"
#     finally:
#         close_connection(conn)

def ghi_nhan_su_dung_dich_vu(ma_dat_phong, ma_phong, ma_dich_vu, so_luong, max_retries=3):
    so_lan_retry = 0
    # 👉 [BỌC THÊM VÒNG LẶP RETRY NÀY]:
    for attempt in range(1, max_retries + 1):
        conn = get_connection()
        if not conn:
            return False, "Không thể kết nối tới CSDL"
        try:
            with conn.cursor() as cursor:
                cursor.execute("START TRANSACTION;")
                cursor.execute("SELECT * FROM su_dung_dich_vu WHERE ma_dat_phong = %s FOR UPDATE;", (ma_dat_phong,))
                cursor.execute("SELECT ma_dat_phong FROM dat_phong WHERE ma_dat_phong = %s FOR UPDATE;", (ma_dat_phong,))

                cursor.execute(
                    "CALL sp_GhiNhanSuDungDichVu(%s, %s, %s, %s, @msg)",
                    (ma_dat_phong, ma_phong, ma_dich_vu, so_luong)              
                )   
                cursor.execute("SELECT @msg AS message") 
                res = cursor.fetchone()
                msg = res['message'] if res and res.get('message') else "Thêm dịch vụ thành công!"
                conn.commit()
                
                # Nếu đã từng bị Deadlock và Retry thành công thì báo thông báo màu xanh
                if so_lan_retry > 0:
                    return True, f"[XỬ LÝ DEADLOCK THÀNH CÔNG] Ban đầu bị Deadlock (Lỗi 1213) do quầy đang Check-out. Hệ thống đã tự động Retry ngầm lần {attempt} thành công!"
                return True, msg
                
        except pymysql.err.OperationalError as e:
            conn.rollback()
            # 👉 [KHI DÍNH LỖI 1213 THÌ TỰ ĐỘNG THỬ LẠI CHỨ KHÔNG BÁO LỖI NỮA]
            if e.args[0] == 1213:
                so_lan_retry += 1
                if attempt < max_retries:
                    time.sleep(0.5) # Đợi bên Check-out commit xong
                    continue # Chạy lại lần nữa
                return False, "[DEADLOCK] Đã thử lại 3 lần thất bại!"
            return False, f"Lỗi CSDL: {e}"
        except Exception as e:
            conn.rollback()
            return False, f"Lỗi: {str(e)}"
        finally:
            close_connection(conn)
            
    return False, "Thao tác thất bại."


def lay_thong_tin_check_out(ma_dat_phong):
    conn = get_connection()
    if not conn:
        return None
    try:
        with conn.cursor() as cursor:
            sql = """
                SELECT 
                    dp.ma_dat_phong,
                    kh.ho_ten AS ten_khach_hang,
                    kh.sdt AS sdt_khach_hang,
                    p.so_phong,
                    ct.ma_phong,
                    ct.gia_tai_thoi_diem,
                    dp.ngay_nhan_du_kien,
                    dp.ngay_tra_du_kien,
                    fn_TinhTienDichVu(dp.ma_dat_phong) AS tong_tien_dich_vu,
                    fn_TinhTienPhong(dp.ma_dat_phong) AS tong_tien_phong
                FROM dat_phong dp
                JOIN khach_hang kh ON dp.ma_kh = kh.ma_kh
                JOIN chi_tiet_dat_phong ct ON dp.ma_dat_phong = ct.ma_dat_phong
                JOIN phong p ON ct.ma_phong = p.ma_phong
                WHERE dp.ma_dat_phong = %s
            """
            cursor.execute(sql, (ma_dat_phong,))
            return cursor.fetchone()
    except Exception as e:
        print(f"Lỗi lay_thong_tin_check_out: {e}")
        return None
    finally:
        close_connection(conn)


# def check_out_lap_hoa_don(ma_dat_phong, ma_nv, giam_gia, phuong_thuc_tt):
#     conn = get_connection()
#     if not conn:
#         return False, "Không thể kết nối tới CSDL"
#     try:
#         with conn.cursor() as cursor:

#             # 👉 [CHÈN THÊM 1]: Bắt đầu giao dịch để giữ khóa
#             cursor.execute("START TRANSACTION;")
            
#             # 👉 [CHÈN THÊM 2]: Khóa bảng dat_phong trước
#             cursor.execute("SELECT ma_dat_phong FROM dat_phong WHERE ma_dat_phong = %s FOR UPDATE;", (ma_dat_phong,))
            
#             # 👉 [CHÈN THÊM 3]: Delay 5 giây để bên kia kịp bấm nút Thêm dịch vụ
#             time.sleep(5)
            
#             # 👉 [CHÈN THÊM 4]: Đòi khóa bảng su_dung_dich_vu (bị bên Dịch vụ chặn lại)
#             cursor.execute("SELECT * FROM su_dung_dich_vu WHERE ma_dat_phong = %s FOR UPDATE;", (ma_dat_phong,))

#             cursor.execute(
#                 "CALL sp_CheckOut_LapHoaDon(%s, %s, %s, %s, @msg)",
#                 (ma_dat_phong, ma_nv, giam_gia, phuong_thuc_tt)
#             )
#             cursor.execute("SELECT @msg AS message")
#             res = cursor.fetchone()
#             msg = res['message'] if res and res.get('message') else "Check-out và lập hóa đơn thành công!"
#             conn.commit()
#             return True, msg
        
#     # 👉 [CHÈN THÊM 5]: Bắt riêng mã lỗi 1213 của MySQL để báo đỏ Deadlock
#     except pymysql.err.OperationalError as e:
#         conn.rollback()
#         if e.args[0] == 1213:
#             return False, "[DEMO DEADLOCK - LỖI 1213] Giao dịch bị MySQL hủy do bế tắc khóa chéo với tiến trình Thêm dịch vụ!"
#         return False, f"Lỗi CSDL: {e}"
            
#     except Exception as e:
#         conn.rollback()
#         print(f"Lỗi check_out_lap_hoa_don: {e}")
#         return False, f"Lỗi: {str(e)}"
#     finally:
#         close_connection(conn)

def check_out_lap_hoa_don(ma_dat_phong, ma_nv, giam_gia, phuong_thuc_tt, max_retries=3):
    so_lan_retry = 0
    # 👉 [BỌC VÒNG LẶP RETRY CHO CHECK-OUT]:
    for attempt in range(1, max_retries + 1):
        conn = get_connection()
        if not conn:
            return False, "Không thể kết nối tới CSDL"
        try:
            with conn.cursor() as cursor:
                cursor.execute("START TRANSACTION;")
                
                cursor.execute("SELECT ma_dat_phong FROM dat_phong WHERE ma_dat_phong = %s FOR UPDATE;", (ma_dat_phong,))
                
                # Chỉ delay 5s ở lần thử đầu tiên để tạo va chạm
                if attempt == 1:
                    time.sleep(5)
                
                cursor.execute("SELECT * FROM su_dung_dich_vu WHERE ma_dat_phong = %s FOR UPDATE;", (ma_dat_phong,))

                cursor.execute(
                    "CALL sp_CheckOut_LapHoaDon(%s, %s, %s, %s, @msg)",
                    (ma_dat_phong, ma_nv, giam_gia, phuong_thuc_tt)
                )
                cursor.execute("SELECT @msg AS message")
                res = cursor.fetchone()
                msg = res['message'] if res and res.get('message') else "Check-out và lập hóa đơn thành công!"
                conn.commit()
                
                # Nếu ban đầu bị Deadlock nhưng đã Retry thành công thì báo xanh
                if so_lan_retry > 0:
                    return True, f"[XỬ LÝ DEADLOCK THÀNH CÔNG] Tiến trình Check-out ban đầu bị Deadlock (1213). Hệ thống đã tự động Retry lần {attempt} và lập hóa đơn thành công!"
                return True, msg
                
        except pymysql.err.OperationalError as e:
            conn.rollback()
            if e.args[0] == 1213: # KHI DÍNH DEADLOCK THÌ TỰ ĐỘNG THỬ LẠI
                so_lan_retry += 1
                if attempt < max_retries:
                    time.sleep(0.5) # Chờ bên kia nhả khóa
                    continue # THỬ LẠI LẦN NỮA
                return False, "[DEADLOCK] Thử lại quá 3 lần thất bại!"
            return False, f"Lỗi CSDL: {e}"
        except Exception as e:
            conn.rollback()
            print(f"Lỗi check_out_lap_hoa_don: {e}")
            return False, f"Lỗi: {str(e)}"
        finally:
            close_connection(conn)
            
    return False, "Thao tác thất bại."

def xac_nhan_thanh_toan(ma_dat_phong):
    conn = get_connection()
    if not conn:
        return False, "Không thể kết nối CSDL."
    try:
        with conn.cursor() as cursor:
            cursor.execute("CALL sp_XacNhanThanhToan(%s, @msg)", (ma_dat_phong,))
            cursor.execute("SELECT @msg AS message")
            res = cursor.fetchone()
            msg = res['message'] if res and res.get('message') else "Xác nhận thanh toán thành công."
            conn.commit()
            return True, msg
    except Exception as e:
        conn.rollback()
        print(f"Lỗi xac_nhan_thanh_toan: {e}")
        return False, f"Lỗi: {str(e)}"
    finally:
        close_connection(conn)


def lay_chi_tiet_hoa_don(identifier):
    conn = get_connection()
    if not conn:
        return None
    try:
        with conn.cursor() as cursor:
            sql = """
                SELECT 
                    hd.*,
                    kh.ho_ten AS ten_khach_hang,
                    kh.sdt,
                    nv.ho_ten AS ten_le_tan,
                    p.so_phong
                FROM hoa_don hd
                JOIN dat_phong dp ON hd.ma_dat_phong = dp.ma_dat_phong
                JOIN khach_hang kh ON dp.ma_kh = kh.ma_kh
                LEFT JOIN nhan_vien nv ON hd.ma_nv = nv.ma_nv
                JOIN chi_tiet_dat_phong ct ON dp.ma_dat_phong = ct.ma_dat_phong
                JOIN phong p ON ct.ma_phong = p.ma_phong
                WHERE hd.ma_dat_phong = %s OR hd.ma_hoa_don = %s
            """
            cursor.execute(sql, (identifier, identifier))
            return cursor.fetchone()
    except Exception as e:
        print(f"Lỗi lay_chi_tiet_hoa_don: {e}")
        return None
    finally:
        close_connection(conn)
