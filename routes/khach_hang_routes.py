"""
routes/khach_hang_routes.py
-----------------------------
Blueprint 'khach_hang': cac chuc nang danh rieng cho actor Khach hang
lien quan toi ho so ca nhan.
(Cac chuc nang Tim phong / Dat phong / Xem hoa don thuoc module cua
Thanh vien 4 & 5, khong dua vao day.)
"""

from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash

from db import queries
from routes.auth_routes import login_required

kh_bp = Blueprint('khach_hang', __name__, url_prefix='/khach-hang')


@kh_bp.route('/ho-so', methods=['GET', 'POST'])
@login_required(['KhachHang'])
def ho_so():
    kh = queries.lay_khach_hang_theo_id(session['user_id'])

    if request.method == 'GET':
        return render_template('ho_so.html', nguoi_dung=kh, loai='khach_hang')

    sdt = request.form.get('sdt', '').strip()
    email = request.form.get('email', '').strip()
    dia_chi = request.form.get('dia_chi', '').strip()
    mat_khau_moi = request.form.get('mat_khau_moi', '')

    if not sdt:
        flash('So dien thoai khong duoc de trong.', 'danger')
        return render_template('ho_so.html', nguoi_dung=kh, loai='khach_hang')

    if email:
        trung = queries.kiem_tra_trung_khach_hang(email=email, exclude_ma_kh=kh['ma_kh'])
        if trung['email']:
            flash('Email nay da duoc su dung boi tai khoan khac.', 'danger')
            return render_template('ho_so.html', nguoi_dung=kh, loai='khach_hang')

    mat_khau_hash = generate_password_hash(mat_khau_moi) if mat_khau_moi else None
    ok = queries.cap_nhat_ho_so_khach_hang(kh['ma_kh'], sdt, email or None, dia_chi or None, mat_khau_hash)

    if ok:
        flash('Cap nhat thong tin ca nhan thanh cong!', 'success')
    else:
        flash('Cap nhat that bai, vui long thu lai.', 'danger')

    return redirect(url_for('khach_hang.ho_so'))