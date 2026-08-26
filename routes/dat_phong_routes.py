import time
"""
routes/dat_phong_routes.py
--------------------------
Blueprint 'dat_phong': xu ly luong dat phong online (KhachHang)
va walk-in tai quay (LeTan/Admin).

Cac route chinh:
  GET/POST /tim-phong              -> Tim phong trong theo ngay
  GET/POST /dat-phong/<ma_phong>   -> Khach hang dat phong online
  GET/POST /dat-phong/walk-in      -> Le tan tao phieu dat cho khach vang lai
  GET      /dat-phong/lich-su      -> Lich su dat phong cua khach hang
  POST     /dat-phong/<id>/huy     -> Huy dat phong (sp_HuyDatPhong)
  GET      /dat-phong/quan-ly      -> Danh sach phieu dat cho le tan

Tat ca cac giao dich INSERT/UPDATE deu goi qua Stored Procedure
da dinh nghia trong 03_procedures.sql.
"""

from datetime import date, datetime, timedelta
from flask import (
    Blueprint, render_template, request,
    redirect, url_for, session, flash, jsonify
)
from routes.auth_routes import login_required
from db import queries

dat_phong_bp = Blueprint('dat_phong', __name__)


# ---------------------------------------------------------------------------
# TIM PHONG TRONG
# ---------------------------------------------------------------------------

@dat_phong_bp.route('/tim-phong', methods=['GET', 'POST'])
def tim_phong():
    """
    DEMO PHANTOM READ (BÓNG MA):
    1. Đếm tổng số phòng trống thỏa điều kiện ban đầu
    2. Nghỉ 5 giây (time.sleep(5)) để Tab khác kịp đặt 1 phòng
    3. Lấy danh sách chi tiết các phòng trống thực tế
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
            flash('Vui long nhap day du ngay nhan va ngay tra.', 'danger')
        elif ngay_tra <= ngay_nhan:
            flash('Ngay tra phai sau ngay nhan phong.', 'danger')
        else:
            phong_trong_so_luong_ban_dau = len(queries.lay_phong_trong(
                ngay_nhan, ngay_tra,
                int(ma_loai_phong_filter) if ma_loai_phong_filter else None
            ))

            print(f"[PHANTOM READ DEMO] Đếm ban đầu: {phong_trong_so_luong_ban_dau} phòng. Dừng 5s...")
            time.sleep(5)

            phong_trong = queries.lay_phong_trong(
                ngay_nhan, ngay_tra,
                int(ma_loai_phong_filter) if ma_loai_phong_filter else None
            )

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


# ---------------------------------------------------------------------------
# DAT PHONG ONLINE (KhachHang)
# ---------------------------------------------------------------------------

@dat_phong_bp.route('/dat-phong/<int:ma_phong>', methods=['GET', 'POST'])
@login_required(['KhachHang'])
def dat_phong_online(ma_phong):
    """
    GET : Hien thi form xac nhan dat phong cho khach hang.
    POST: Goi sp_TaoDatPhong de tao phieu dat, chuyen sang trang xac nhan.
    """
    phong = queries.lay_phong_theo_id(ma_phong)
    if not phong:
        flash('Phong khong ton tai.', 'danger')
        return redirect(url_for('dat_phong.tim_phong'))

    # Lay ngay tu query string (tu trang tim phong)
    ngay_nhan = request.args.get('ngay_nhan', date.today().strftime('%Y-%m-%d'))
    ngay_tra = request.args.get('ngay_tra', (date.today() + timedelta(days=1)).strftime('%Y-%m-%d'))

    if request.method == 'GET':
        return render_template(
            'dat_phong/form_dat_phong.html',
            phong=phong,
            ngay_nhan=ngay_nhan,
            ngay_tra=ngay_tra,
            mode='confirm'
        )

    # POST: xu ly dat phong
    ngay_nhan = request.form.get('ngay_nhan', '').strip()
    ngay_tra = request.form.get('ngay_tra', '').strip()

    if not ngay_nhan or not ngay_tra:
        flash('Vui long nhap day du ngay nhan va ngay tra.', 'danger')
        return render_template(
            'dat_phong/form_dat_phong.html',
            phong=phong, ngay_nhan=ngay_nhan, ngay_tra=ngay_tra, mode='confirm'
        )

    if ngay_tra <= ngay_nhan:
        flash('Ngay tra phai sau ngay nhan phong.', 'danger')
        return render_template(
            'dat_phong/form_dat_phong.html',
            phong=phong, ngay_nhan=ngay_nhan, ngay_tra=ngay_tra, mode='confirm'
        )

    ma_kh = session['user_id']
    
    # DEMO LOST UPDATE: Tạm dừng 5 giây để 2 tab cùng bấm đặt phòng 101
    print("[LOST UPDATE DEMO] Tạm dừng 5 giây trước khi gọi Stored Procedure...")
    time.sleep(5)

    success, msg = queries.dat_phong_sp(
        ma_kh=ma_kh,
        ma_nv=None,
        nguon_dat='Online',
        ma_phong=ma_phong,
        ngay_nhan_du_kien=ngay_nhan,
        ngay_tra_du_kien=ngay_tra
    )

    if success:
        flash(f'Dat phong thanh cong! {msg}', 'success')
        return redirect(url_for('dat_phong.lich_su_dat_phong'))
    else:
        flash(f'Dat phong that bai: {msg}', 'danger')
        return render_template(
            'dat_phong/form_dat_phong.html',
            phong=phong, ngay_nhan=ngay_nhan, ngay_tra=ngay_tra, mode='confirm'
        )


# ---------------------------------------------------------------------------
# WALK-IN (Le tan / Admin tao phieu dat cho khach vang lai)
# ---------------------------------------------------------------------------

@dat_phong_bp.route('/dat-phong/walk-in', methods=['GET', 'POST'])
@login_required(['LeTan', 'Admin'])
def walk_in():
    """
    GET : Hien thi form walk-in: tim khach theo CCCD, chon phong va ngay.
    POST: Tao khach hang tai quay (neu can) -> goi sp_TaoDatPhong.
    """
    today = date.today()
    tomorrow = today + timedelta(days=1)
    loai_phong_list = queries.lay_tat_ca_loai_phong()

    if request.method == 'GET':
        return render_template(
            'dat_phong/walk_in.html',
            loai_phong_list=loai_phong_list,
            ngay_nhan=today.strftime('%Y-%m-%d'),
            ngay_tra=tomorrow.strftime('%Y-%m-%d'),
            today=today.strftime('%Y-%m-%d'),
            tomorrow=tomorrow.strftime('%Y-%m-%d')
        )

    # --- POST ---
    cccd = request.form.get('cccd', '').strip()
    ho_ten = request.form.get('ho_ten', '').strip()
    sdt = request.form.get('sdt', '').strip()
    ngay_sinh = request.form.get('ngay_sinh') or None
    email = request.form.get('email', '').strip() or None
    dia_chi = request.form.get('dia_chi', '').strip() or None
    ma_phong = request.form.get('ma_phong', '')
    ngay_nhan = request.form.get('ngay_nhan', '').strip()
    ngay_tra = request.form.get('ngay_tra', '').strip()

    # Validate
    if not all([cccd, ho_ten, sdt, ma_phong, ngay_nhan, ngay_tra]):
        flash('Vui long dien day du thong tin bat buoc (*).', 'danger')
        return render_template(
            'dat_phong/walk_in.html',
            loai_phong_list=loai_phong_list,
            form=request.form
        )

    if ngay_tra <= ngay_nhan:
        flash('Ngay tra phai sau ngay nhan phong.', 'danger')
        return render_template(
            'dat_phong/walk_in.html',
            loai_phong_list=loai_phong_list,
            form=request.form
        )

    # Tim hoac tao khach hang
    kh = queries.tim_khach_hang_theo_cccd(cccd)
    if kh:
        ma_kh = kh['ma_kh']
    else:
        # Tao khach vang lai moi
        if not ho_ten or not sdt:
            flash('Khach hang chua co trong he thong. Vui long nhap Ho ten va SDT.', 'danger')
            return render_template(
                'dat_phong/walk_in.html',
                loai_phong_list=loai_phong_list,
                form=request.form
            )
        ma_kh, message = queries.them_khach_hang_tai_quay(
            ho_ten, cccd, sdt, ngay_sinh, email, dia_chi
        )
        if not ma_kh:
            flash(message, 'danger')
            return render_template(
                'dat_phong/walk_in.html',
                loai_phong_list=loai_phong_list,
                form=request.form
            )

    ma_nv = session['user_id']
    success, msg = queries.dat_phong_sp(
        ma_kh=ma_kh,
        ma_nv=ma_nv,
        nguon_dat='TaiQuay',
        ma_phong=int(ma_phong),
        ngay_nhan_du_kien=ngay_nhan,
        ngay_tra_du_kien=ngay_tra
    )

    if success:
        flash(f'Lap phieu dat phong walk-in thanh cong! {msg}', 'success')
        return redirect(url_for('dat_phong.quan_ly_dat_phong'))
    else:
        flash(f'That bai: {msg}', 'danger')
        return render_template(
            'dat_phong/walk_in.html',
            loai_phong_list=loai_phong_list,
            form=request.form
        )


# ---------------------------------------------------------------------------
# AJAX: TIM KHACH THEO CCCD (dung trong form walk-in)
# ---------------------------------------------------------------------------

@dat_phong_bp.route('/dat-phong/tim-khach')
@login_required(['LeTan', 'Admin'])
def tim_khach_ajax():
    """AJAX endpoint tra ve thong tin khach hang theo CCCD."""
    cccd = request.args.get('cccd', '').strip()
    if not cccd:
        return jsonify({'found': False})
    kh = queries.tim_khach_hang_theo_cccd(cccd)
    if kh:
        return jsonify({
            'found': True,
            'ho_ten': kh['ho_ten'],
            'sdt': kh['sdt'],
            'email': kh.get('email', ''),
            'dia_chi': kh.get('dia_chi', '')
        })
    return jsonify({'found': False})


# ---------------------------------------------------------------------------
# AJAX: LAY PHONG TRONG THEO NGAY (dung trong form walk-in)
# ---------------------------------------------------------------------------

@dat_phong_bp.route('/dat-phong/phong-trong')
@login_required(['LeTan', 'Admin'])
def phong_trong_ajax():
    """AJAX endpoint tra ve danh sach phong trong theo ngay."""
    ngay_nhan = request.args.get('ngay_nhan', '')
    ngay_tra = request.args.get('ngay_tra', '')
    if not ngay_nhan or not ngay_tra or ngay_tra <= ngay_nhan:
        return jsonify([])
    phong_list = queries.lay_phong_trong(ngay_nhan, ngay_tra)
    result = [
        {
            'ma_phong': p['ma_phong'],
            'so_phong': p['so_phong'],
            'ten_loai_phong': p['ten_loai_phong'],
            'gia_theo_ngay': float(p['gia_theo_ngay']),
            'suc_chua': p['suc_chua']
        }
        for p in phong_list
    ]
    return jsonify(result)


# ---------------------------------------------------------------------------
# LICH SU DAT PHONG (KhachHang)
# ---------------------------------------------------------------------------

@dat_phong_bp.route('/dat-phong/lich-su')
@login_required(['KhachHang'])
def lich_su_dat_phong():
    """Hien thi lich su tat ca phieu dat phong cua khach hang dang dang nhap."""
    ma_kh = session['user_id']
    danh_sach = queries.lay_dat_phong_cua_kh(ma_kh)
    return render_template('dat_phong/xac_nhan.html', danh_sach=danh_sach)


# ---------------------------------------------------------------------------
# HUY DAT PHONG
# Goi sp_HuyDatPhong (kiem tra dieu kien huy truoc 24h).
# Trigger trg_CapNhatTrangThaiPhongDat tu dong chuyen phong.trang_thai = 'Trong'.
# ---------------------------------------------------------------------------

@dat_phong_bp.route('/dat-phong/<int:ma_dat_phong>/huy', methods=['POST'])
@login_required()
def huy_dat_phong(ma_dat_phong):
    """
    POST: Huy phieu dat phong.
    sp_HuyDatPhong:
      - Kiem tra trang_thai = 'DaDat'
      - Kiem tra DATEDIFF(ngay_nhan_du_kien, CURDATE()) >= 1
      - UPDATE dat_phong.trang_thai = 'DaHuy'
    Trigger tu dong: phong.trang_thai = 'Trong' (giai phong phong).
    """
    phieu = queries.lay_dat_phong_theo_id(ma_dat_phong)
    if not phieu:
        flash('Phieu dat khong ton tai.', 'danger')
        return redirect(url_for('dat_phong.lich_su_dat_phong'))

    # Phan quyen: chi cho chinh khach hang hoac le tan/admin
    vai_tro = session.get('vai_tro')
    if vai_tro == 'KhachHang' and phieu['ma_kh'] != session['user_id']:
        flash('Ban khong co quyen huy phieu dat nay.', 'danger')
        return redirect(url_for('dat_phong.lich_su_dat_phong'))

    success, msg = queries.huy_dat_phong_sp(ma_dat_phong)

    if success:
        flash(f'Huy dat phong thanh cong! {msg}', 'success')
    else:
        flash(f'Huy that bai: {msg}', 'danger')

    if vai_tro == 'KhachHang':
        return redirect(url_for('dat_phong.lich_su_dat_phong'))
    return redirect(url_for('dat_phong.quan_ly_dat_phong'))


# ---------------------------------------------------------------------------
# QUAN LY PHIEU DAT (Le tan / Admin)
# ---------------------------------------------------------------------------

@dat_phong_bp.route('/dat-phong/quan-ly')
@login_required(['LeTan', 'Admin'])
def quan_ly_dat_phong():
    """
    Hien thi toan bo phieu dat phong cho le tan quan ly.
    Co the loc theo trang_thai qua query string ?trang_thai=DaDat ...
    """
    trang_thai_filter = request.args.get('trang_thai') or None
    danh_sach = queries.lay_tat_ca_dat_phong(trang_thai=trang_thai_filter)
    return render_template(
        'dat_phong/quan_ly.html',
        danh_sach=danh_sach,
        trang_thai_filter=trang_thai_filter
    )
