```
# Hệ thống quản lý khách sạn

Đồ án môn Hệ quản trị cơ sở dữ liệu — Nhóm 5

## Công nghệ sử dụng
- Backend: Python (Flask)
- Frontend: HTML, Jinja2, Bootstrap
- Database: MySQL (InnoDB)
## Thành viên nhóm
| Họ tên | MSSV | Phụ trách |

## Cấu trúc thư mục
hotel-management/
│
├── app.py                          BACKEND — điểm khởi động Flask, khai báo route
├── config.py                       BACKEND — thông tin kết nối MySQL (host, user, password)
├── requirements.txt                BACKEND — danh sách thư viện Python cần cài
│
├── routes/                         BACKEND — xử lý logic nghiệp vụ theo từng nhóm chức năng
│   ├── phong_routes.py              (route quản lý phòng)
│   ├── dat_phong_routes.py          (route đặt phòng — chứa transaction/lock)
│   ├── khach_hang_routes.py
│   ├── hoa_don_routes.py
│   └── auth_routes.py               (đăng nhập, phân quyền)
│
├── db/                              BACKEND — tầng kết nối & truy vấn CSDL
│   ├── connection.py                 (hàm tạo kết nối tới MySQL)
│   └── queries.py                    (các hàm gọi SQL: dat_phong(), check_in(), ...)
│
├── templates/                      FRONTEND — giao diện HTML (Jinja2)
│   ├── layout.html                   (khung chung: navbar, Bootstrap CDN)
│   ├── trang_chu.html
│   ├── phong/
│   │   ├── danh_sach.html
│   │   └── them_moi.html
│   ├── dat_phong/
│   │   ├── form_dat_phong.html
│   │   └── xac_nhan.html
│   ├── checkin_checkout.html
│   ├── hoa_don.html
│   └── dang_nhap.html
│
├── static/                         FRONTEND — file tĩnh
│   ├── css/style.css                 (CSS tùy chỉnh, ngoài Bootstrap)
│   ├── js/main.js                    (validate form, xác nhận xoá...)
│   └── img/
│
└── sql/                             CƠ SỞ DỮ LIỆU — toàn bộ mã nguồn MySQL
    ├── 01_schema.sql                  (CREATE TABLE, PK, FK, CHECK, UNIQUE)
    ├── 02_triggers.sql                (CREATE TRIGGER)
    ├── 03_procedures.sql              (CREATE PROCEDURE)
    ├── 04_function.sql
    ├── 05_views.sql                   (CREATE VIEW)
    ├── 06_indexes.sql                 (CREATE INDEX)
    ├── 07_grants.sql                  (tạo user, phân quyền GRANT/REVOKE)
    └── 08_sample_data.sql             (dữ liệu mẫu để demo)
## Cài đặt

### 1. Clone project
\`\`\`bash
git clone <link_repo>
cd hotel-management
\`\`\`

### 2. Tạo virtual environment
\`\`\`bash
python -m venv venv
venv\Scripts\activate      # Windows
source venv/bin/activate   # macOS/Linux
\`\`\`

### 3. Cài thư viện
\`\`\`bash
pip install -r requirements.txt
\`\`\`

### 4. Cấu hình database
- Tạo file `.env` từ `.env.example`, điền thông tin MySQL của bạn
- Chạy các file SQL để tạo cấu trúc CSDL:
\`\`\`bash
mysql -u root -p < sql/01_schema.sql
mysql -u root -p < sql/02_triggers.sql
mysql -u root -p < sql/03_procedures.sql
mysql -u root -p < sql/04_views.sql
mysql -u root -p < sql/05_indexes.sql
mysql -u root -p < sql/07_sample_data.sql
\`\`\`

### 5. Chạy ứng dụng
\`\`\`bash
python app.py
\`\`\`
Truy cập: http://localhost:5000

## Cấu trúc thư mục
(dán sơ đồ cây thư mục đã có ở trên)

## Tính năng chính
- Đặt phòng, check-in/check-out
- Quản lý phòng, khách hàng, hóa đơn
- Xử lý tranh chấp đặt phòng đồng thời (transaction + row lock)
- Báo cáo doanh thu (view)

## Demo xử lý tranh chấp CSDL
Mô tả ngắn cách chạy test script mô phỏng nhiều người dùng đặt trùng 1 phòng (thêm sau khi có script test)

