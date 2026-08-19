import pymysql
import pymysql.cursors
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import Config

def get_connection():
    """
    Tạo và trả về một kết nối đến cơ sở dữ liệu MySQL bằng PyMySQL với charset utf8mb4 chuẩn.
    """
    try:
        connection = pymysql.connect(
            host=Config.DB_CONFIG['host'],
            user=Config.DB_CONFIG['user'],
            password=Config.DB_CONFIG['password'],
            database=Config.DB_CONFIG['database'],
            port=Config.DB_CONFIG['port'],
            cursorclass=pymysql.cursors.DictCursor,
            charset='utf8mb4',
            init_command="SET NAMES utf8mb4 COLLATE utf8mb4_unicode_ci"
        )
        return connection
    except pymysql.MySQLError as e:
        print(f"Lỗi kết nối cơ sở dữ liệu: {e}")
        return None

def close_connection(connection):
    """
    Đóng kết nối cơ sở dữ liệu.
    """
    if connection and connection.open:
        connection.close()
