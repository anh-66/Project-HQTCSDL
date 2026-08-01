# Hệ thống quản lý khách sạn

Đồ án môn Hệ quản trị cơ sở dữ liệu — Nhóm 5

## Công nghệ sử dụng
- Backend: Python (Flask)
- Frontend: HTML, Jinja2, Bootstrap
- Database: MySQL (InnoDB)

## Thành viên nhóm
| Họ tên | MSSV | Phụ trách |


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