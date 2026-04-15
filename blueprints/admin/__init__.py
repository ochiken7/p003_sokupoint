from flask import Blueprint, session, redirect, url_for, request, render_template, flash
from functools import wraps

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


def admin_required(f):
    """管理画面認証デコレータ（認証スキップ中）"""
    @wraps(f)
    def decorated(*args, **kwargs):
        # 認証をスキップ（誰でもアクセス可能）
        return f(*args, **kwargs)
    return decorated


@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    # 認証が無効化されているのでダッシュボードに直接リダイレクト
    return redirect(url_for('admin.dashboard'))


@admin_bp.route('/logout')
def logout():
    return redirect(url_for('admin.dashboard'))


# サブモジュールのインポート（Blueprint登録後に読み込む）
from blueprints.admin import dashboard, games, coupons, stores, users, trophies, assets, home_banners  # noqa: F401, E402
