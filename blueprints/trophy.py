from flask import Blueprint, render_template, session, redirect, url_for
from models.user import User
from models.trophy import Trophy, UserTrophy

trophy_bp = Blueprint('trophy', __name__)


@trophy_bp.route('/trophies')
def index():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('auth.demo_switch'))

    user = User.query.get(user_id)
    trophies = Trophy.query.filter_by(is_active=True).all()
    unlocked_ids = {ut.trophy_id for ut in UserTrophy.query.filter_by(user_id=user_id).all()}

    return render_template('trophy/list.html',
                           user=user, trophies=trophies, unlocked_ids=unlocked_ids)
