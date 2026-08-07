import os

class Config:
    """
    Cấu hình ứng dụng và kết nối Cơ sở dữ liệu
    """
    DB_CONFIG = {
        'host': 'localhost',
        'user': 'app_user',
        'password': 'App@123',
        'database': 'hotel_management',
        'port': 3306
    }
