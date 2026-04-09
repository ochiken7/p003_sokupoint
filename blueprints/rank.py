from flask import Blueprint, render_template, session, redirect, url_for
from models.user import User, Rank

rank_bp = Blueprint('rank', __name__)


@rank_bp.route('/rank')
def index():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('auth.demo_switch'))

    user = User.query.get(user_id)
    ranks = Rank.query.order_by(Rank.min_lifetime_points).all()

    # 次のランクへの進捗計算
    current_idx = next((i for i, r in enumerate(ranks) if r.code == user.rank_code), 0)
    next_rank = ranks[current_idx + 1] if current_idx + 1 < len(ranks) else None

    progress = 100
    points_to_next = 0
    if next_rank:
        current_min = ranks[current_idx].min_lifetime_points
        next_min = next_rank.min_lifetime_points
        range_total = next_min - current_min
        if range_total > 0:
            progress = min(100, int((user.lifetime_points - current_min) / range_total * 100))
            points_to_next = max(0, next_min - user.lifetime_points)

    return render_template('rank.html',
                           user=user, ranks=ranks,
                           next_rank=next_rank,
                           progress=progress,
                           points_to_next=points_to_next)
