from datetime import date
from flask import (
    Blueprint, render_template, request,
    redirect, url_for, session, flash
)
from routes.auth_routes import login_required
from db import queries

luu_tru_bp = Blueprint('luu_tru', __name__, url_prefix='/luu-tru')


# ---------------------------------------------------------------------------
# CHECK-IN (MEMBER 4)
# ---------------------------------------------------------------------------

@luu_tru_bp.route('/check-in', methods=['GET'])
@login_required(['LeTan', 'Admin'])
def danh_sach_checkin():
    """
    Hiển thị danh sách phiếu đặt có trang_thai = 'DaDat' để lễ tân thực hiện check-in.
    """
    danh_sach = queries.lay_tat_ca_dat_phong(trang_thai='DaDat')
    today_str = date.today().strftime('%Y-%m-%d')
    return render_template(
        'luu_tru/checkin_checkout.html',
        danh_sach=danh_sach,
        today=today_str,
        mode='checkin'
    )


@luu_tru_bp.route('/check-in/<int:ma_dat_phong>', methods=['POST'])
@login_required(['LeTan', 'Admin'])
def xac_nhan_checkin(ma_dat_phong):
    """
    POST: Thực hiện check-in cho phiếu đặt ma_dat_phong.
    """
    phieu = queries.lay_dat_phong_theo_id(ma_dat_phong)
    if not phieu:
        flash('Phiếu đặt không tồn tại.', 'danger')
        return redirect(url_for('luu_tru.danh_sach_checkin'))

    if phieu['trang_thai'] != 'DaDat':
        flash(f'Phiếu đặt này đang ở trạng thái "{phieu["trang_thai"]}", không thể check-in.', 'warning')
        return redirect(url_for('luu_tru.danh_sach_checkin'))

    ma_phong = phieu['ma_phong']
    success, msg = queries.xac_nhan_checkin_sp(ma_dat_phong, ma_phong)

    if success:
        flash(
            f'Check-in thành công cho khách {phieu["ten_khach"]} - Phòng {phieu["so_phong"]}! '
            f'Phòng đã được chuyển sang trạng thái Đang sử dụng.',
            'success'
        )
    else:
        flash(f'Check-in thất bại: {msg}', 'danger')

    return redirect(url_for('luu_tru.danh_sach_checkin'))


# ---------------------------------------------------------------------------
# SỬ DỤNG DỊCH VỤ (MEMBER 5)
# ---------------------------------------------------------------------------

@luu_tru_bp.route('/dichvu', methods=['GET', 'POST'])
@login_required(['LeTan', 'Admin'])
def su_dung_dich_vu():
    if request.method == 'POST':
        ma_dat_phong = request.form.get('ma_dat_phong', type=int) 
        ma_phong = request.form.get('ma_phong', type=int)
        ma_dich_vu = request.form.get('ma_dich_vu', type=int)
        so_luong = request.form.get('so_luong', type=int)

        if not all([ma_dat_phong, ma_phong, ma_dich_vu, so_luong]) or so_luong <= 0:
            flash('Vui lòng điền đầy đủ thông tin.', 'warning')
            return redirect(url_for('luu_tru.su_dung_dich_vu', ma_dat_phong=ma_dat_phong))

        success, message = queries.ghi_nhan_su_dung_dich_vu(ma_dat_phong, ma_phong, ma_dich_vu, so_luong)
        if success:
            flash(message, 'success')
        else:
            flash(message, 'danger')
        return redirect(url_for('luu_tru.su_dung_dich_vu', ma_dat_phong=ma_dat_phong))

    ma_dat_phong_selected = request.args.get('ma_dat_phong', type=int)
    phong_list = queries.lay_danh_sach_phong_dung_dich_vu()
    dich_vu_list = queries.lay_danh_sach_dich_vu()  

    dich_vu_da_dung_list = []
    phong_selected_info = None
    if ma_dat_phong_selected:
        dich_vu_da_dung_list = queries.lay_dich_vu_da_dung(ma_dat_phong_selected)
        for p in phong_list:
            if p['ma_dat_phong'] == ma_dat_phong_selected:
                phong_selected_info = p
                break

    return render_template(
        'luu_tru/su_dung_dich_vu.html',
        phong_list=phong_list,
        dich_vu_list=dich_vu_list,
        dich_vu_da_dung_list=dich_vu_da_dung_list,
        ma_dat_phong_selected=ma_dat_phong_selected,
        phong_selected_info=phong_selected_info
    )


# ---------------------------------------------------------------------------
# CHECK-OUT & LẬP HÓA ĐƠN (MEMBER 5)
# ---------------------------------------------------------------------------

@luu_tru_bp.route('/check-out', methods=['GET'])
@luu_tru_bp.route('/check-out/<int:ma_dat_phong>', methods=['GET', 'POST'])
@login_required(['LeTan', 'Admin'])
def check_out(ma_dat_phong=None):
    if not ma_dat_phong:
        phong_list = queries.lay_danh_sach_phong_dung_dich_vu()
        return render_template('luu_tru/checkin_checkout.html', phong_list=phong_list, mode='select_checkout')

    if request.method == 'POST':
        ma_nv = session.get('user_id')
        try:
            giam_gia = float(request.form.get('giam_gia', 0))
        except ValueError:
            giam_gia = 0.0

        phuong_thuc_tt = request.form.get('phuong_thuc_tt', 'TienMat')

        success, message = queries.check_out_lap_hoa_don(ma_dat_phong, ma_nv, giam_gia, phuong_thuc_tt)
        if success:
            flash(message, 'success')
            return redirect(url_for('hoa_don.chi_tiet', ma_dat_phong=ma_dat_phong))
        else:
            flash(message, 'danger')
            return redirect(url_for('luu_tru.check_out', ma_dat_phong=ma_dat_phong))

    thong_tin = queries.lay_thong_tin_check_out(ma_dat_phong)
    if not thong_tin:
        flash('Không tìm thấy thông tin lượt ở để check-out!', 'warning')
        return redirect(url_for('luu_tru.check_out'))

    dich_vu_list = queries.lay_dich_vu_da_dung(ma_dat_phong)
    return render_template(
        'luu_tru/checkin_checkout.html',
        thong_tin=thong_tin,
        dich_vu_list=dich_vu_list,
        mode='checkout_detail'
    )
