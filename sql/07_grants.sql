-- 07_grants.sql: Phân quyền bảo mật CSDL
USE hotel_management;

-- Tài khoản Admin
CREATE USER IF NOT EXISTS 'admin_user'@'localhost' IDENTIFIED BY 'Admin@123';
GRANT ALL PRIVILEGES ON hotel_management.* TO 'admin_user'@'localhost' WITH GRANT OPTION;

-- Tài khoản App Flask (chỉ DML và EXECUTE Stored Procedures)
CREATE USER IF NOT EXISTS 'app_user'@'localhost' IDENTIFIED BY 'App@123';
GRANT SELECT, INSERT, UPDATE, DELETE, EXECUTE ON hotel_management.* TO 'app_user'@'localhost';

FLUSH PRIVILEGES;

-- Thu hồi bớt quyền nguy hiểm khỏi app_user (không cho phép DROP/ALTER cấu trúc từ tầng ứng dụng)
REVOKE DROP, ALTER, CREATE, INDEX ON hotel_management.* FROM 'app_user'@'localhost';

-- Thu hồi quyền GRANT OPTION mặc định của user PUBLIC nếu có (chuẩn hoá bảo mật)
FLUSH PRIVILEGES;