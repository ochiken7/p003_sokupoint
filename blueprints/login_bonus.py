from datetime import date, datetime
from flask import Blueprint, render_template, session, redirect, url_for, flash
from extensions import db
from models.user import User
from models.login_bonus import LoginBonusLog
from services.point_service import add_points

login_bonus_bp = Blueprint('login_bonus', __name__)


@login_bonus_bp.route('/bonus')
def index():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('auth.demo_switch'))

    user = User.query.get(user_id)
    today = date.today()

    # 本日受取済かチェック
    already_received = LoginBonusLog.query.filter_by(
        user_id=user_id, received_date=today
    ).first()

    # 連続ログイン日数に応じたボーナス計算
    base_points = _calc_bonus_points(user.consecutive_login_days + 1)

    return render_template('login_bonus.html',
                           user=user,
                           already_received=already_received,
                           base_points=base_points)


@login_bonus_bp.route('/bonus/receive', methods=['POST'])
def receive():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('auth.demo_switch'))

    user = User.query.get(user_id)
    today = date.today()

    # 重複チェック
    existing = LoginBonusLog.query.filter_by(
        user_id=user_id, received_date=today
    ).first()
    if existing:
        flash('本日のログインボーナスは既に受取済みです。', 'warning')
        return redirect(url_for('login_bonus.index'))

    # 連続ログイン日数更新
    if user.last_login_at and user.last_login_at.date() == today:
        pass  # 同日なのでそのまま
    else:
        user.consecutive_login_days += 1
    user.last_login_at = datetime.utcnow()

    consecutive = user.consecutive_login_days
    base_points = _calc_bonus_points(consecutive)

    # ログ記録
    log = LoginBonusLog(
        user_id=user_id,
        received_date=today,
        points_awarded=base_points,
        consecutive_day=consecutive,
    )
    db.session.add(log)
    db.session.commit()

    # ポイント付与（ランク倍率適用）
    actual = add_points(user_id, base_points, 'login_bonus',
                        f'ログインボーナス({consecutive}日目)')

    flash(f'ログインボーナス {actual}P を獲得しました!', 'success')
    return redirect(url_for('login_bonus.index'))


def _calc_bonus_points(consecutive_day):
    """連続ログイン日数に応じた基本ポイント"""
    if consecutive_day >= 30 and consecutive_day % 30 == 0:
        return 500
    elif consecutive_day >= 14 and consecutive_day % 14 == 0:
        return 200
    elif consecutive_day >= 7 and consecutive_day % 7 == 0:
        return 100
    return 50
