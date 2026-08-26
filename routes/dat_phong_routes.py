"""
test_loi/routes/dat_phong_routes.py
----------------------------------
Phiên bản demo LỖI 4: Phantom Read (Bóng ma) hiển thị trực tiếp trên Giao diện Web.
"""

from datetime import date, datetime, timedelta
import time
from flask import (
    Blueprint, render_template, request,
    redirect, url_for, session, flash, jsonify
)
from routes.auth_routes import login_required
from db import queries

dat_phong_bp = Blueprint('dat_phong', __name__)

@dat_phong_bp.route('/tim-phong', methods=['GET', 'POST'])
def tim_phong():
    """
    DEMO PHANTOM READ:
    1. Đếm tổng số phòng trống thỏa điều kiện (Query COUNT)
    2. Tạm dừng 5 giây (time.sleep(5)) để Tab khác thực hiện Đặt phòng mới
    3. Lấy danh sách danh sách chi tiết các phòng trống (Query SELECT List)
    => Kết quả: Thông báo hiển thị "Tìm thấy 5 phòng trống", nhưng bảng chi tiết bên dưới chỉ có 4 phòng!
    """
    today = date.today()
    tomorrow = today + timedelta(days=1)

    loai_phong_list = queries.lay_tat_ca_loai_phong()
    phong_trong = []
    ngay_nhan = today.strftime('%Y-%m-%d')
    ngay_tra = tomorrow.strftime('%Y-%m-%d')
    ma_loai_phong_filter = None

    if request.method == 'POST':
        ngay_nhan = request.form.get('ngay_nhan', '').strip()
        ngay_tra = request.form.get('ngay_tra', '').strip()
        ma_loai_phong_filter = request.form.get('ma_loai_phong') or None

        if not ngay_nhan or not ngay_tra:
            flash('Vui lòng nhập đầy đủ ngày nhận và ngày trả.', 'danger')
        elif ngay_tra <= ngay_nhan:
            flash('Ngày trả phải sau ngày nhận phòng.', 'danger')
        else:
            # QUERY 1: Đếm số phòng trống ban đầu
            phong_trong_so_luong_ban_dau = len(queries.lay_phong_trong(
                ngay_nhan, ngay_tra,
                int(ma_loai_phong_filter) if ma_loai_phong_filter else None
            ))

            print(f"[PHANTOM READ DEMO] Đếm ban đầu: {phong_trong_so_luong_ban_dau} phòng trống. Đang chờ 5s...")
            
            # TẠO ĐỘ TRỄ 5 GIÂY ĐỂ USER B KỊP BẤM ĐẶT PHÒNG Ở TAB KHÁC
            time.sleep(5)

            # QUERY 2: Lấy danh sách thực tế sau 5 giây
            phong_trong = queries.lay_phong_trong(
                ngay_nhan, ngay_tra,
                int(ma_loai_phong_filter) if ma_loai_phong_filter else None
            )

            # Tạo thông báo gây nhiễu Phantom Read trên UI Web
            flash(
                f'[DEMO PHANTOM READ] Kết quả thống kê ban đầu: Tìm thấy {phong_trong_so_luong_ban_dau} phòng trống. '
                f'(Thực tế danh sách bên dưới hiện có {len(phong_trong)} phòng)!',
                'info'
            )

    return render_template(
        'dat_phong/form_dat_phong.html',
        loai_phong_list=loai_phong_list,
        phong_trong=phong_trong,
        ngay_nhan=ngay_nhan,
        ngay_tra=ngay_tra,
        ma_loai_phong_filter=ma_loai_phong_filter
    )
