from flask import Blueprint, render_template, redirect, url_for, session, request
from models.user import User

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/age-gate')
def age_gate():
    if session.get('age_verified'):
        return redirect(url_for('auth.demo_switch'))
    return render_template('age_gate.html')


@auth_bp.route('/age-gate/confirm', methods=['POST'])
def age_gate_confirm():
    session['age_verified'] = True
    return redirect(url_for('auth.demo_switch'))


@auth_bp.route('/demo/switch')
def demo_switch():
    if not session.get('age_verified'):
        return redirect(url_for('auth.age_gate'))
    users = User.query.order_by(User.id).all()
    return render_template('user_switch.html', users=users)


@auth_bp.route('/demo/switch/<int:user_id>', methods=['POST'])
def switch_user(user_id):
    if not session.get('age_verified'):
        return redirect(url_for('auth.age_gate'))
    user = User.query.get_or_404(user_id)
    session['user_id'] = user.id
    return redirect(url_for('home.index'))


@auth_bp.before_app_request
def require_age_gate():
    """年齢確認されていなければゲートへリダイレクト"""
    allowed = ['auth.age_gate', 'auth.age_gate_confirm', 'static']
    # 管理画面は除外
    if request.endpoint and request.endpoint.startswith('admin'):
        return
    if request.endpoint in allowed:
        return
    if not session.get('age_verified'):
        return redirect(url_for('auth.age_gate'))
