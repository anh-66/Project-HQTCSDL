"""
routes/auth_routes.py
----------------------
Blueprint 'auth': dang ky, dang nhap, dang xuat, phan quyen bang Flask Session,
va cac route quan tri (Admin) lien quan toi tai khoan Nhan vien + bao cao doanh thu.

Quy uoc session sau khi dang nhap thanh cong:
    session['user_id']  -> ma_kh hoac ma_nv
    session['ho_ten']   -> ten hien thi
    session['vai_tro']  -> 'KhachHang' | 'LeTan' | 'Admin'
"""

from functools import wraps
from datetime import datetime

from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash

from db import queries

auth_bp = Blueprint('auth', __name__)


# Decorator phan quyen dung chung cho toan bo project

def login_required(vai_tro_cho_phep=None):
    """
    vai_tro_cho_phep: None -> chi can dang nhap (bat ky vai tro nao).
                       list/tuple -> chi cac vai tro trong danh sach moi duoc vao.
    Vi du dung o file khac:  @login_required(['Admin'])
                              @login_required(['Admin', 'LeTan'])
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapped(*args, **kwargs):
            if 'user_id' not in session:
                flash('Vui long dang nhap de tiep tuc.', 'warning')
                return redirect(url_for('auth.dang_nhap', next=request.path))

            if vai_tro_cho_phep and session.get('vai_tro') not in vai_tro_cho_phep:
                flash('Ban khong co quyen truy cap chuc nang nay.', 'danger')
                return redirect(url_for('trang_chu'))

            return view_func(*args, **kwargs)
        return wrapped
    return decorator


# DANG KY (chi danh cho Khach hang - tu dang ky online)

@auth_bp.route('/dang-ky', methods=['GET', 'POST'])
def dang_ky():
    if request.method == 'GET':
        return render_template('dang_ky.html')

    ho_ten = request.form.get('ho_ten', '').strip()
    cccd = request.form.get('cccd', '').strip()
    ngay_sinh = request.form.get('ngay_sinh') or None
    sdt = request.form.get('sdt', '').strip()
    email = request.form.get('email', '').strip()
    dia_chi = request.form.get('dia_chi', '').strip()
    tai_khoan = request.form.get('tai_khoan', '').strip()
    mat_khau = request.form.get('mat_khau', '')
    xac_nhan_mat_khau = request.form.get('xac_nhan_mat_khau', '')

    # --- Validate co ban ---
    if not all([ho_ten, cccd, sdt, tai_khoan, mat_khau]):
        flash('Vui long dien day du cac truong bat buoc (*)', 'danger')
        return render_template('dang_ky.html', form=request.form)

    if mat_khau != xac_nhan_mat_khau:
        flash('Mat khau xac nhan khong khop.', 'danger')
        return render_template('dang_ky.html', form=request.form)

    if len(mat_khau) < 6:
        flash('Mat khau phai co it nhat 6 ky tu.', 'danger')
        return render_template('dang_ky.html', form=request.form)

    # --- Kiem tra trung lap CCCD / email / tai khoan ---
    trung = queries.kiem_tra_trung_khach_hang(cccd=cccd, email=email or None, tai_khoan=tai_khoan)
    if trung['cccd']:
        flash('So CCCD nay da duoc dang ky.', 'danger')
        return render_template('dang_ky.html', form=request.form)
    if email and trung['email']:
        flash('Email nay da duoc su dung.', 'danger')
        return render_template('dang_ky.html', form=request.form)
    if trung['tai_khoan']:
        flash('Ten tai khoan da ton tai, vui long chon ten khac.', 'danger')
        return render_template('dang_ky.html', form=request.form)

    # --- Ma hoa mat khau va luu ---
    mat_khau_hash = generate_password_hash(mat_khau)
    ma_kh = queries.dang_ky_khach_hang(
        ho_ten, cccd, ngay_sinh, sdt, email or None, dia_chi or None, tai_khoan, mat_khau_hash
    )

    if ma_kh:
        flash('Dang ky thanh cong! Vui long dang nhap.', 'success')
        return redirect(url_for('auth.dang_nhap'))
    else:
        flash('Co loi xay ra, vui long thu lai.', 'danger')
        return render_template('dang_ky.html', form=request.form)


# DANG NHAP chung cho Khach hang / Nhan vien (Le tan, Admin)
# Thu tim trong bang khach_hang truoc, khong thay thi tim trong nhan_vien.

@auth_bp.route('/dang-nhap', methods=['GET', 'POST'])
def dang_nhap():
    if request.method == 'GET':
        return render_template('dang_nhap.html')

    tai_khoan = request.form.get('tai_khoan', '').strip()
    mat_khau = request.form.get('mat_khau', '')

    if not tai_khoan or not mat_khau:
        flash('Vui long nhap tai khoan va mat khau.', 'danger')
        return render_template('dang_nhap.html')

    # 1) Thu voi Khach hang
    kh = queries.lay_khach_hang_theo_tai_khoan(tai_khoan)
    if kh and kh.get('mat_khau') and check_password_hash(kh['mat_khau'], mat_khau):
        session.clear()
        session['user_id'] = kh['ma_kh']
        session['ho_ten'] = kh['ho_ten']
        session['vai_tro'] = 'KhachHang'
        flash(f"Xin chao, {kh['ho_ten']}!", 'success')
        return redirect(request.args.get('next') or url_for('trang_chu'))

    # 2) Thu voi Nhan vien (Le tan / Admin)
    nv = queries.lay_nhan_vien_theo_tai_khoan(tai_khoan)
    if nv and check_password_hash(nv['mat_khau'], mat_khau):
        if nv['trang_thai'] == 'NghiViec':
            flash('Tai khoan nay da bi khoa. Lien he Admin de duoc ho tro.', 'danger')
            return render_template('dang_nhap.html')

        session.clear()
        session['user_id'] = nv['ma_nv']
        session['ho_ten'] = nv['ho_ten']
        session['vai_tro'] = nv['vai_tro']  # 'Admin' hoac 'LeTan'
        flash(f"Xin chao, {nv['ho_ten']}!", 'success')
        return redirect(request.args.get('next') or url_for('trang_chu'))

    flash('Tai khoan hoac mat khau khong chinh xac.', 'danger')
    return render_template('dang_nhap.html')


@auth_bp.route('/dang-xuat')
def dang_xuat():
    session.clear()
    flash('Ban da dang xuat.', 'info')
    return redirect(url_for('auth.dang_nhap'))


# HO SO NHAN VIEN (Le tan / Admin tu cap nhat thong tin ca nhan)

@auth_bp.route('/nhan-vien/ho-so', methods=['GET', 'POST'])
@login_required(['Admin', 'LeTan'])
def ho_so_nhan_vien():
    nv = queries.lay_nhan_vien_theo_id(session['user_id'])

    if request.method == 'GET':
        return render_template('ho_so.html', nguoi_dung=nv, loai='nhan_vien')

    sdt = request.form.get('sdt', '').strip()
    email = request.form.get('email', '').strip()
    mat_khau_moi = request.form.get('mat_khau_moi', '')

    if email:
        trung = queries.kiem_tra_trung_nhan_vien(email=email, exclude_ma_nv=nv['ma_nv'])
        if trung['email']:
            flash('Email nay da duoc su dung boi tai khoan khac.', 'danger')
            return render_template('ho_so.html', nguoi_dung=nv, loai='nhan_vien')

    mat_khau_hash = generate_password_hash(mat_khau_moi) if mat_khau_moi else None
    ok = queries.cap_nhat_ho_so_nhan_vien(nv['ma_nv'], sdt, email, mat_khau_hash)

    if ok:
        session['ho_ten'] = nv['ho_ten']
        flash('Cap nhat thong tin ca nhan thanh cong!', 'success')
    else:
        flash('Cap nhat that bai, vui long thu lai.', 'danger')

    return redirect(url_for('auth.ho_so_nhan_vien'))


# ADMIN: QUAN LY TAI KHOAN NHAN VIEN (them, khoa/mo)

@auth_bp.route('/admin/nhan-vien')
@login_required(['Admin'])
def admin_danh_sach_nhan_vien():
    danh_sach = queries.lay_danh_sach_nhan_vien()
    return render_template('admin/nhan_vien.html', danh_sach=danh_sach)


@auth_bp.route('/admin/nhan-vien/them', methods=['GET', 'POST'])
@login_required(['Admin'])
def admin_them_nhan_vien():
    if request.method == 'GET':
        return render_template('admin/them_nhan_vien.html')

    ho_ten = request.form.get('ho_ten', '').strip()
    ngay_sinh = request.form.get('ngay_sinh') or None
    gioi_tinh = request.form.get('gioi_tinh') or None
    sdt = request.form.get('sdt', '').strip()
    email = request.form.get('email', '').strip()
    vai_tro = request.form.get('vai_tro', 'LeTan')
    tai_khoan = request.form.get('tai_khoan', '').strip()
    mat_khau = request.form.get('mat_khau', '')

    if not all([ho_ten, tai_khoan, mat_khau]):
        flash('Vui long dien day du cac truong bat buoc (*)', 'danger')
        return render_template('admin/them_nhan_vien.html', form=request.form)

    trung = queries.kiem_tra_trung_nhan_vien(email=email or None, tai_khoan=tai_khoan)
    if trung['tai_khoan']:
        flash('Ten tai khoan da ton tai.', 'danger')
        return render_template('admin/them_nhan_vien.html', form=request.form)
    if email and trung['email']:
        flash('Email da duoc su dung.', 'danger')
        return render_template('admin/them_nhan_vien.html', form=request.form)

    mat_khau_hash = generate_password_hash(mat_khau)
    ma_nv = queries.them_nhan_vien(
        ho_ten, ngay_sinh, gioi_tinh, sdt, email or None, vai_tro, tai_khoan, mat_khau_hash
    )

    if ma_nv:
        flash(f'Da them nhan vien "{ho_ten}" thanh cong!', 'success')
        return redirect(url_for('auth.admin_danh_sach_nhan_vien'))
    else:
        flash('Co loi xay ra, vui long thu lai.', 'danger')
        return render_template('admin/them_nhan_vien.html', form=request.form)


@auth_bp.route('/admin/nhan-vien/<int:ma_nv>/khoa', methods=['POST'])
@login_required(['Admin'])
def admin_khoa_nhan_vien(ma_nv):
    if queries.doi_trang_thai_nhan_vien(ma_nv, 'NghiViec'):
        flash('Da khoa tai khoan nhan vien.', 'success')
    else:
        flash('Khoa tai khoan that bai.', 'danger')
    return redirect(url_for('auth.admin_danh_sach_nhan_vien'))


@auth_bp.route('/admin/nhan-vien/<int:ma_nv>/mo-khoa', methods=['POST'])
@login_required(['Admin'])
def admin_mo_khoa_nhan_vien(ma_nv):
    if queries.doi_trang_thai_nhan_vien(ma_nv, 'DangLam'):
        flash('Da mo khoa tai khoan nhan vien.', 'success')
    else:
        flash('Mo khoa tai khoan that bai.', 'danger')
    return redirect(url_for('auth.admin_danh_sach_nhan_vien'))


# ADMIN: BAO CAO DOANH THU TONG QUAN

@auth_bp.route('/admin/bao-cao-doanh-thu')
@login_required(['Admin'])
def admin_bao_cao_doanh_thu():
    now = datetime.now()
    thang = request.args.get('thang', default=now.month, type=int)
    nam = request.args.get('nam', default=now.year, type=int)

    tong_doanh_thu_thang = queries.doanh_thu_theo_thang(thang, nam)
    chi_tiet_hoa_don = queries.bao_cao_doanh_thu_hoa_don()

    return render_template(
        'admin/bao_cao_doanh_thu.html',
        thang=thang, nam=nam,
        tong_doanh_thu_thang=tong_doanh_thu_thang,
        chi_tiet_hoa_don=chi_tiet_hoa_don
    )