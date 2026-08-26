"""
test_loi/db/queries.py
----------------------
Phiên bản chỉnh sửa để demo LỖI 3: Non-Repeatable Read (Không đọc lại được dữ liệu) 
và hỗ trợ LỖI 2: Dirty Read trên giao diện Web.
"""

from db.connection import get_connection, close_connection
import pymysql
import time

# Import tất cả các hàm gốc từ db.queries
from db.queries import *

# ===========================================================================
# LỖI 3: NON-REPEATABLE READ (KHÔNG ĐỌC LẠI ĐƯỢC DỮ LIỆU) TRONG CHECK-OUT
# Đọc tổng tiền dịch vụ lần 1 -> Nghỉ 6 giây -> Đọc lại lần 2.
# Trong 6s nghỉ này, nếu Lễ tân ở Tab 2 thêm dịch vụ mới, kết quả đọc lần 2 
# bị thay đổi so với lần 1 dù đang ở trong cùng một thao tác xử lý!
# ===========================================================================
def lay_thong_tin_check_out(ma_dat_phong):
    conn = get_connection()
    if not conn:
        return None
    try:
        with conn.cursor() as cursor:
            # Lần đọc 1
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
            res1 = cursor.fetchone()
            
            print(f"[NON-REPEATABLE READ TEST] Đọc lần 1: Tiền DV = {res1.get('tong_tien_dich_vu') if res1 else 0}")
            
            # Tạm dừng 6 giây để thao tác thêm dịch vụ ở Tab 2
            time.sleep(6)
            
            # Lần đọc 2 (Trong cùng 1 lượt gọi hàm)
            cursor.execute(sql, (ma_dat_phong,))
            res2 = cursor.fetchone()
            
            print(f"[NON-REPEATABLE READ TEST] Đọc lần 2: Tiền DV = {res2.get('tong_tien_dich_vu') if res2 else 0}")
            
            return res2
    except Exception as e:
        print(f"Lỗi lay_thong_tin_check_out (test_loi): {e}")
        return None
    finally:
        close_connection(conn)


# ===========================================================================
# LỖI 2 HỖ TRỢ: DIRTY READ - ĐỌC GIÁ PHÒNG VỚI ISOLATION READ UNCOMMITTED
# ===========================================================================
def lay_phong_dirty_read(ma_phong):
    conn = get_connection()
    if not conn:
        return None
    try:
        with conn.cursor() as cursor:
            # Cho phép đọc dữ liệu rác chưa commit
            cursor.execute("SET SESSION TRANSACTION ISOLATION LEVEL READ UNCOMMITTED;")
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
