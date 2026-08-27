import threading
import time
import sys
sys.stdout.reconfigure(encoding='utf-8')

from db.connection import get_connection, close_connection

def thread_writer_uncommitted():
    """Luồng 1: Thay đổi dữ liệu nhưng ngâm 10s rồi ROLLBACK (chưa COMMIT)"""
    conn = get_connection()
    if not conn:
        print("[Writer T1] Lỗi kết nối CSDL.")
        return
    try:
        conn.begin()
        with conn.cursor() as cursor:
            print("[Writer T1] Bắt đầu Giao dịch T1 (Cập nhật trạng thái phiếu đặt 1 sang 'DaNhanPhong' nhưng CHƯA COMMIT)...")
            cursor.execute("UPDATE dat_phong SET trang_thai = 'DaNhanPhong' WHERE ma_dat_phong = 8")
            print("[Writer T1] Đã UPDATE xong. T1 tạm dừng (Sleep 8s)...")
            time.sleep(8)
            print("[Writer T1] T1 thực hiện ROLLBACK (Hủy bỏ giao dịch)...")
            conn.rollback()
            print("[Writer T1] T1 đã ROLLBACK xong!")
    except Exception as e:
        print(f"[Writer T1] Lỗi: {e}")
        conn.rollback()
    finally:
        close_connection(conn)

def thread_reader_dirty():
    """Luồng 2: Đọc dữ liệu với READ UNCOMMITTED"""
    time.sleep(2)  # Chờ Luồng 1 chạy xong lệnh UPDATE
    conn = get_connection()
    if not conn:
        print("[Reader T2] Lỗi kết nối CSDL.")
        return
    try:
        with conn.cursor() as cursor:
            print("[Reader T2] Giao dịch T2 bật SET TRANSACTION ISOLATION LEVEL READ UNCOMMITTED...")
            cursor.execute("SET TRANSACTION ISOLATION LEVEL READ UNCOMMITTED")
            print("[Reader T2] Giao dịch T2 đọc trạng thái phiếu đặt 1...")
            cursor.execute("SELECT ma_dat_phong, trang_thai FROM dat_phong WHERE ma_dat_phong = 8")
            row = cursor.fetchone()
            print(f"[Reader T2] ==> KẾT QUẢ ĐỌC ĐƯỢC (DIRTY READ RÁC): {row}")
    except Exception as e:
        print(f"[Reader T2] Lỗi: {e}")
    finally:
        close_connection(conn)

if __name__ == "__main__":
    print("=== DEMO TRỰC QUAN: DIRTY READ (ĐỌC DỮ LIỆU RÁC) ===")
    t1 = threading.Thread(target=thread_writer_uncommitted)
    t2 = threading.Thread(target=thread_reader_dirty)
    t1.start()
    t2.start()
    t1.join()
    t2.join()
    print("=== KẾT THÚC DEMO DIRTY READ ===")
