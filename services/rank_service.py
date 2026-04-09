from models.user import User, Rank


def check_rank_up(user_id):
    """累計ポイントに基づいてランク昇格を判定"""
    user = User.query.get(user_id)
    ranks = Rank.query.order_by(Rank.min_lifetime_points.desc()).all()
    for rank in ranks:
        if user.lifetime_points >= rank.min_lifetime_points:
            if user.rank_code != rank.code:
                user.rank_code = rank.code
            break
