import os

class Config:
    """
    Cấu hình ứng dụng và kết nối Cơ sở dữ liệu
    """
# Dùng để ký (sign) session cookie của Flask. 
    SECRET_KEY = os.environ.get('SECRET_KEY', 'doi-key-nay-truoc-khi-deploy-that-2024')

    DB_CONFIG = {
        'host': 'localhost',
        'user': 'app_user',
        'password': 'App@123',
        'database': 'hotel_management',
        'port': 3306
    }
