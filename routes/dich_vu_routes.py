from flask import Blueprint, render_template, request, redirect, url_for, flash
from db.queries import lay_danh_sach_dich_vu, them_dich_vu, sua_dich_vu, xoa_dich_vu

dich_vu_bp = Blueprint('dich_vu', __name__, url_prefix='/dich-vu')

@dich_vu_bp.route('/')
def danh_sach():
    """Hiển thị danh sách dịch vụ."""
    ds_dich_vu = lay_danh_sach_dich_vu()
    return render_template('dich_vu/danh_sach.html', ds_dich_vu=ds_dich_vu)

@dich_vu_bp.route('/them', methods=['POST'])
def them():
    """Thêm dịch vụ mới."""
    ten = request.form.get('ten_dich_vu', '').strip()
    don_gia = request.form.get('don_gia')
    don_vi_tinh = request.form.get('don_vi_tinh', '').strip()
    
    if not ten or not don_gia:
        flash('Vui lòng điền đầy đủ tên dịch vụ và đơn giá!', 'danger')
    else:
        success, message = them_dich_vu(ten, float(don_gia), don_vi_tinh)
        flash(message, 'success' if success else 'danger')
    
    return redirect(url_for('dich_vu.danh_sach'))

@dich_vu_bp.route('/sua/<int:ma_dich_vu>', methods=['POST'])
def sua(ma_dich_vu):
    """Cập nhật thông tin dịch vụ."""
    ten = request.form.get('ten_dich_vu', '').strip()
    don_gia = request.form.get('don_gia')
    don_vi_tinh = request.form.get('don_vi_tinh', '').strip()
    
    if not ten or not don_gia:
        flash('Vui lòng điền đầy đủ thông tin!', 'danger')
    else:
        success, message = sua_dich_vu(ma_dich_vu, ten, float(don_gia), don_vi_tinh)
        flash(message, 'success' if success else 'danger')
    
    return redirect(url_for('dich_vu.danh_sach'))

@dich_vu_bp.route('/xoa/<int:ma_dich_vu>', methods=['POST'])
def xoa(ma_dich_vu):
    """Xóa dịch vụ."""
    success, message = xoa_dich_vu(ma_dich_vu)
    flash(message, 'success' if success else 'danger')
    return redirect(url_for('dich_vu.danh_sach'))
