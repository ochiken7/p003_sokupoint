from flask import Blueprint, render_template, session, redirect, url_for
from models.user import User
from models.point import PointHistory
from models.trophy import UserTrophy

me_bp = Blueprint('me', __name__)


@me_bp.route('/me')
def index():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('auth.demo_switch'))

    user = User.query.get(user_id)

    # 最近のポイント履歴
    histories = PointHistory.query.filter_by(user_id=user_id)\
        .order_by(PointHistory.created_at.desc()).limit(20).all()

    # 取得済みトロフィー数
    trophy_count = UserTrophy.query.filter_by(user_id=user_id).count()

    return render_template('me.html',
                           user=user, histories=histories,
                           trophy_count=trophy_count)
