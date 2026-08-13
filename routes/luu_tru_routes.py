"""
routes/luu_tru_routes.py
------------------------
Blueprint 'luu_tru': xu ly quy trinh Check-in / Nhan phong.

Cac route:
  GET  /luu-tru/check-in                      -> Danh sach phieu dat cho check-in
  POST /luu-tru/check-in/<ma_dat_phong>        -> Xac nhan check-in (goi sp_XacNhanCheckIn)

sp_XacNhanCheckIn thuc hien:
  1. UPDATE chi_tiet_dat_phong SET ngay_nhan_thuc_te = NOW()
  2. UPDATE dat_phong SET trang_thai = 'DaNhanPhong'
  => Trigger trg_CapNhatTrangThaiPhongDat (AFTER UPDATE tren dat_phong)
     tu dong: UPDATE phong SET trang_thai = 'DangSuDung'
"""

from datetime import date
from flask import (
    Blueprint, render_template, request,
    redirect, url_for, session, flash
)
from routes.auth_routes import login_required
from db import queries

luu_tru_bp = Blueprint('luu_tru', __name__)


# ---------------------------------------------------------------------------
# CHECK-IN: DANH SACH PHIEU DAT CHO CHECK-IN
# ---------------------------------------------------------------------------

@luu_tru_bp.route('/luu-tru/check-in')
@login_required(['LeTan', 'Admin'])
def danh_sach_checkin():
    """
    Hien thi danh sach phieu dat co trang_thai = 'DaDat' de le tan thuc hien check-in.
    """
    danh_sach = queries.lay_tat_ca_dat_phong(trang_thai='DaDat')
    today_str = date.today().strftime('%Y-%m-%d')
    return render_template(
        'luu_tru/checkin_checkout.html',
        danh_sach=danh_sach,
        today=today_str
    )


# ---------------------------------------------------------------------------
# CHECK-IN: XAC NHAN CHECK-IN
# Goi sp_XacNhanCheckIn:
#   1. cap nhat chi_tiet_dat_phong.ngay_nhan_thuc_te = NOW()
#   2. dat_phong.trang_thai = 'DaNhanPhong'
# Trigger trg_CapNhatTrangThaiPhongDat tu dong:
#   -> phong.trang_thai = 'DangSuDung'
# ---------------------------------------------------------------------------

@luu_tru_bp.route('/luu-tru/check-in/<int:ma_dat_phong>', methods=['POST'])
@login_required(['LeTan', 'Admin'])
def xac_nhan_checkin(ma_dat_phong):
    """
    POST: Thuc hien check-in cho phieu dat ma_dat_phong.
    Lay ma_phong tu phieu dat, goi sp_XacNhanCheckIn(ma_dat_phong, ma_phong).
    Sau khi thanh cong:
      - chi_tiet_dat_phong.ngay_nhan_thuc_te duoc ghi nhan = NOW()
      - dat_phong.trang_thai = 'DaNhanPhong'
      - Trigger tu dong chuyen phong.trang_thai = 'DangSuDung'
    """
    phieu = queries.lay_dat_phong_theo_id(ma_dat_phong)
    if not phieu:
        flash('Phieu dat khong ton tai.', 'danger')
        return redirect(url_for('luu_tru.danh_sach_checkin'))

    if phieu['trang_thai'] != 'DaDat':
        flash(f'Phieu dat nay dang o trang thai "{phieu["trang_thai"]}", khong the check-in.', 'warning')
        return redirect(url_for('luu_tru.danh_sach_checkin'))

    ma_phong = phieu['ma_phong']
    success, msg = queries.xac_nhan_checkin_sp(ma_dat_phong, ma_phong)

    if success:
        flash(
            f'Check-in thanh cong cho khach {phieu["ten_khach"]} - Phong {phieu["so_phong"]}! '
            f'Phong da duoc chuyen sang trang thai DangSuDung.',
            'success'
        )
    else:
        flash(f'Check-in that bai: {msg}', 'danger')

    return redirect(url_for('luu_tru.danh_sach_checkin'))
