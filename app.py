from flask import Flask, jsonify, render_template, session
from db.connection import get_connection, close_connection
from config import Config

from routes.auth_routes import auth_bp
from routes.khach_hang_routes import kh_bp

from routes.dat_phong_routes import dat_phong_bp
from routes.luu_tru_routes import luu_tru_bp

from routes.phong_routes import phong_bp
from routes.dich_vu_routes import dich_vu_bp

app = Flask(__name__)
app.config.from_object(Config)
app.secret_key = app.config.get('SECRET_KEY', 'khach-san-secret-key-2024')
app.json.ensure_ascii = False

app.register_blueprint(auth_bp)
app.register_blueprint(kh_bp)
app.register_blueprint(dat_phong_bp)
app.register_blueprint(luu_tru_bp)
app.register_blueprint(phong_bp)
app.register_blueprint(dich_vu_bp)

@app.route('/')
def trang_chu():
    return render_template('trang_chu.html')

@app.route('/test-db')
def test_db():
    """
    Route này dùng để kiểm tra thử kết nối Cơ sở dữ liệu:
    Kiểm tra xem Flask có kết nối thành công tới MySQL và lấy thông tin version hay không.
    """
    conn = get_connection()
    if conn:
        try:
            with conn.cursor() as cursor:
                cursor.execute("SELECT VERSION() as version")
                result = cursor.fetchone()
                return jsonify({
                    "status": "success",
                    "message": "Kết nối Cơ sở dữ liệu thành công!",
                    "mysql_version": result['version']
                })
        except Exception as e:
            return jsonify({
                "status": "error",
                "message": f"Lỗi truy vấn: {str(e)}"
            })
        finally:
            close_connection(conn)
    else:
        return jsonify({
            "status": "error",
            "message": "Không thể kết nối đến Cơ sở dữ liệu. Vui lòng kiểm tra lại config.py và MySQL server!"
        }), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)