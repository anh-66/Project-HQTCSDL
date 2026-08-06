-- 07_grants.sql: Phân quyền truy cập CSDL theo nguyên tắc bảo mật

-- 1. Tạo tài khoản admin_user (Quản trị CSDL cấp cao)
CREATE USER IF NOT EXISTS 'admin_user'@'localhost' IDENTIFIED BY 'Admin@123';
GRANT ALL PRIVILEGES ON *.* TO 'admin_user'@'localhost' WITH GRANT OPTION;

-- 2. Tạo tài khoản app_user (Dành riêng cho ứng dụng Python/Flask)
-- Chỉ cấp các quyền DML (SELECT, INSERT, UPDATE, DELETE) và EXECUTE thủ tục
CREATE USER IF NOT EXISTS 'app_user'@'localhost' IDENTIFIED BY 'App@123';
GRANT SELECT, INSERT, UPDATE, DELETE, EXECUTE ON *.* TO 'app_user'@'localhost';

-- Áp dụng thay đổi quyền
FLUSH PRIVILEGES;