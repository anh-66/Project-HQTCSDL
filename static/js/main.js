
document.addEventListener('DOMContentLoaded', function() {
    var btnXoaList = document.querySelectorAll('.btn-xoa');
    btnXoaList.forEach(function(btn) {
        btn.addEventListener('click', function(e) {
            if (!confirm('Bạn có chắc chắn muốn xóa dữ liệu này? Hành động này không thể hoàn tác!')) {
                e.preventDefault();
            }
        });
    });

    var alerts = document.querySelectorAll('.alert');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            if (typeof bootstrap !== 'undefined' && bootstrap.Alert) {
                var bsAlert = bootstrap.Alert.getInstance(alert) || new bootstrap.Alert(alert);
                if (bsAlert) {
                    bsAlert.close();
                }
            }
        }, 5000);
    });
});
