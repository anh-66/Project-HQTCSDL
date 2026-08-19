from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from routes.auth_routes import login_required
from db.queries import (
    bao_cao_doanh_thu_hoa_don,
    lay_chi_tiet_hoa_don,
    lay_dich_vu_da_dung,
    xac_nhan_thanh_toan
)

hoa_don_bp = Blueprint('hoa_don', __name__, url_prefix='/hoa-don')


# 1. ROUTE XEM DANH SÁCH TẤT CẢ HÓA ĐƠN
@hoa_don_bp.route('/', methods=['GET'])
@login_required(['LeTan', 'Admin'])
def danhsach():
    danh_sach_hd = bao_cao_doanh_thu_hoa_don()
    return render_template('hoa_don.html', danh_sach_hd=danh_sach_hd)


# 2. ROUTE XEM CHI TIẾT 1 HÓA ĐƠN
@hoa_don_bp.route('/chi_tiet/<int:ma_dat_phong>', methods=['GET'])
@login_required(['LeTan', 'Admin'])
def chi_tiet(ma_dat_phong):
    hoa_don = lay_chi_tiet_hoa_don(ma_dat_phong)
    if not hoa_don:
        flash('Không tìm thấy hóa đơn!', 'warning')
        return redirect(url_for('hoa_don.danhsach'))

    danh_sach_dv = lay_dich_vu_da_dung(hoa_don['ma_dat_phong'])
    return render_template('hoa_don_chi_tiet.html', hoa_don=hoa_don, danh_sach_dv=danh_sach_dv)


# 3. ROUTE XÁC NHẬN THANH TOÁN (THU TIỀN)
@hoa_don_bp.route('/xac-nhan-thanh-toan/<int:ma_dat_phong>', methods=['POST'])
@login_required(['LeTan', 'Admin'])
def thanh_toan(ma_dat_phong):
    success, message = xac_nhan_thanh_toan(ma_dat_phong)
    if success:
        flash(message, 'success')
    else:
        flash(message, 'danger')
    return redirect(url_for('hoa_don.danhsach'))
