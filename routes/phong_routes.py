from flask import Blueprint, render_template, request, redirect, url_for, flash
from db.queries import (
    lay_danh_sach_phong, lay_phong_theo_ma, them_phong, sua_phong, xoa_phong,
    lay_danh_sach_loai_phong, them_loai_phong, sua_loai_phong, xoa_loai_phong,
    lay_loai_phong_theo_ma, lay_danh_sach_tang
)

phong_bp = Blueprint('phong', __name__, url_prefix='/phong')

@phong_bp.route('/')
def danh_sach():
    """Hiển thị danh sách phòng, hỗ trợ lọc theo trạng thái, tầng và chuyển đổi chế độ xem (Bảng / Sơ đồ)."""
    filter_trang_thai = request.args.get('trang_thai', '')
    filter_tang = request.args.get('tang', '')
    view_mode = request.args.get('view_mode', 'table') # 'table' hoac 'grid'
    
    ds_phong = lay_danh_sach_phong(
        trang_thai=filter_trang_thai if filter_trang_thai else None,
        tang=int(filter_tang) if filter_tang else None
    )
    ds_loai_phong = lay_danh_sach_loai_phong()
    ds_tang = lay_danh_sach_tang()
    
    phong_theo_tang = {}
    for p in ds_phong:
        t = p['tang']
        if t not in phong_theo_tang:
            phong_theo_tang[t] = []
        phong_theo_tang[t].append(p)
    
    return render_template('phong/danh_sach.html',
        ds_phong=ds_phong,
        ds_loai_phong=ds_loai_phong,
        ds_tang=ds_tang,
        phong_theo_tang=phong_theo_tang,
        filter_trang_thai=filter_trang_thai,
        filter_tang=filter_tang,
        view_mode=view_mode
    )

@phong_bp.route('/them', methods=['GET', 'POST'])
def them():
    """Thêm phòng mới."""
    ds_loai_phong = lay_danh_sach_loai_phong()
    
    if request.method == 'POST':
        so_phong = request.form.get('so_phong', '').strip()
        ma_loai_phong = request.form.get('ma_loai_phong')
        tang = request.form.get('tang')
        
        if not so_phong or not ma_loai_phong or not tang:
            flash('Vui lòng điền đầy đủ thông tin!', 'danger')
            return render_template('phong/them_moi.html', ds_loai_phong=ds_loai_phong, phong=None)
        
        success, message = them_phong(so_phong, int(ma_loai_phong), int(tang))
        flash(message, 'success' if success else 'danger')
        if success:
            return redirect(url_for('phong.danh_sach'))
    
    return render_template('phong/them_moi.html', ds_loai_phong=ds_loai_phong, phong=None)

@phong_bp.route('/sua/<int:ma_phong>', methods=['GET', 'POST'])
def sua(ma_phong):
    """Sửa thông tin phòng."""
    ds_loai_phong = lay_danh_sach_loai_phong()
    phong = lay_phong_theo_ma(ma_phong)
    
    if not phong:
        flash('Không tìm thấy phòng!', 'danger')
        return redirect(url_for('phong.danh_sach'))
    
    if request.method == 'POST':
        so_phong = request.form.get('so_phong', '').strip()
        ma_loai_phong_new = request.form.get('ma_loai_phong')
        tang = request.form.get('tang')
        trang_thai = request.form.get('trang_thai')
        
        if not so_phong or not ma_loai_phong_new or not tang or not trang_thai:
            flash('Vui lòng điền đầy đủ thông tin!', 'danger')
            return render_template('phong/them_moi.html', ds_loai_phong=ds_loai_phong, phong=phong)
        
        success, message = sua_phong(ma_phong, so_phong, int(ma_loai_phong_new), int(tang), trang_thai)
        flash(message, 'success' if success else 'danger')
        if success:
            return redirect(url_for('phong.danh_sach'))
    
    return render_template('phong/them_moi.html', ds_loai_phong=ds_loai_phong, phong=phong)

@phong_bp.route('/xoa/<int:ma_phong>', methods=['POST'])
def xoa(ma_phong):
    """Xóa phòng."""
    success, message = xoa_phong(ma_phong)
    flash(message, 'success' if success else 'danger')
    return redirect(url_for('phong.danh_sach'))

@phong_bp.route('/loai-phong')
def danh_sach_loai_phong():
    """Hiển thị danh sách loại phòng."""
    ds_loai_phong = lay_danh_sach_loai_phong()
    return render_template('phong/danh_sach.html',
        ds_phong=lay_danh_sach_phong(),
        ds_loai_phong=ds_loai_phong,
        ds_tang=lay_danh_sach_tang(),
        filter_trang_thai='',
        filter_tang='',
        hien_tab='loai_phong'
    )

@phong_bp.route('/loai-phong/them', methods=['POST'])
def them_loai():
    """Thêm loại phòng mới."""
    ten = request.form.get('ten_loai_phong', '').strip()
    gia = request.form.get('gia_theo_ngay')
    suc_chua = request.form.get('suc_chua')
    mo_ta = request.form.get('mo_ta', '').strip()
    
    if not ten or not gia or not suc_chua:
        flash('Vui lòng điền đầy đủ thông tin loại phòng!', 'danger')
    else:
        success, message = them_loai_phong(ten, float(gia), int(suc_chua), mo_ta)
        flash(message, 'success' if success else 'danger')
    
    return redirect(url_for('phong.danh_sach_loai_phong'))

@phong_bp.route('/loai-phong/sua/<int:ma_loai_phong>', methods=['POST'])
def sua_loai(ma_loai_phong):
    """Cập nhật loại phòng."""
    ten = request.form.get('ten_loai_phong', '').strip()
    gia = request.form.get('gia_theo_ngay')
    suc_chua = request.form.get('suc_chua')
    mo_ta = request.form.get('mo_ta', '').strip()
    # Giá loại phòng tại thời điểm form sửa được mở trên trình duyệt - dùng để
    # phát hiện Lost Update (Optimistic Concurrency Control) trong sua_loai_phong().
    gia_cu = request.form.get('gia_cu')

    if not ten or not gia or not suc_chua:
        flash('Vui lòng điền đầy đủ thông tin!', 'danger')
    else:
        success, message = sua_loai_phong(
            ma_loai_phong, ten, float(gia), int(suc_chua), mo_ta,
            gia_cu=float(gia_cu) if gia_cu not in (None, '') else None
        )
        flash(message, 'success' if success else 'danger')
    
    return redirect(url_for('phong.danh_sach_loai_phong'))

@phong_bp.route('/loai-phong/xoa/<int:ma_loai_phong>', methods=['POST'])
def xoa_loai(ma_loai_phong):
    """Xóa loại phòng."""
    success, message = xoa_loai_phong(ma_loai_phong)
    flash(message, 'success' if success else 'danger')
    return redirect(url_for('phong.danh_sach_loai_phong'))
