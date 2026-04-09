from flask import Blueprint, session, redirect, url_for, request, render_template, flash
from functools import wraps

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


def admin_required(f):
    """管理画面認証デコレータ"""
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('admin_logged_in'):
            return redirect(url_for('admin.login'))
        return f(*args, **kwargs)
    return decorated


@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    from flask import current_app
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        if (username == current_app.config['ADMIN_USERNAME'] and
                password == current_app.config['ADMIN_PASSWORD']):
            session['admin_logged_in'] = True
            return redirect(url_for('admin.dashboard'))
        flash('ユーザー名またはパスワードが正しくありません。', 'error')
    return render_template('admin/login.html')


@admin_bp.route('/logout')
def logout():
    session.pop('admin_logged_in', None)
    return redirect(url_for('admin.login'))


# サブモジュールのインポート（Blueprint登録後に読み込む）
from blueprints.admin import dashboard, games, coupons, stores, users, trophies, assets  # noqa: F401, E402
