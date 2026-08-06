import threading
import time
from db.connection import get_connection, close_connection

def book_room(thread_name, ma_kh, ma_nv, nguon_dat, ma_phong, check_in, check_out):
    conn = get_connection()
    if not conn:
        print(f"[{thread_name}] Lỗi kết nối CSDL.")
        return

    try:
        with conn.cursor() as cursor:
            print(f"[{thread_name}] Bắt đầu đặt phòng {ma_phong} từ {check_in} đến {check_out}...")
            
            # Gọi Stored Procedure trực tiếp để cố định tên biến OUT là @msg
            sql_call = "CALL sp_TaoDatPhong(%s, %s, %s, %s, %s, %s, @msg)"
            cursor.execute(sql_call, (ma_kh, ma_nv, nguon_dat, ma_phong, check_in, check_out))
            
            # Lấy thông báo trả về từ biến @msg
            cursor.execute("SELECT @msg AS message")
            result = cursor.fetchone()
            message = result.get('message') if result else "Không có phản hồi"
            
            conn.commit()
            print(f"[{thread_name}] Kết quả: {message}")
            
    except Exception as e:
        print(f"[{thread_name}] Exception: {e}")
    finally:
        close_connection(conn)

if __name__ == "__main__":
    print("--- DEMO RACE CONDITION: ĐẶT PHÒNG ĐỒNG THỜI ---")
    
    # Dữ liệu test
    ma_kh_1, ma_kh_2 = 1, 2
    ma_nv = 1
    nguon_dat = 'Online'
    ma_phong = 101
    check_in = '2023-12-01'
    check_out = '2023-12-05'

    # Tạo 2 luồng đặt phòng cùng lúc
    t1 = threading.Thread(target=book_room, args=("User 1", ma_kh_1, ma_nv, nguon_dat, ma_phong, check_in, check_out))
    t2 = threading.Thread(target=book_room, args=("User 2", ma_kh_2, ma_nv, nguon_dat, ma_phong, check_in, check_out))

    # Chạy song song
    t1.start()
    t2.start()

    t1.join()
    t2.join()
    
    print("--- KẾT THÚC DEMO ---")