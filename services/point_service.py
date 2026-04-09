from extensions import db
from models.user import User, Rank
from models.point import PointHistory


def add_points(user_id, amount, source, description=''):
    """ポイント付与（ランク倍率適用 → 残高更新 → 履歴記録 → ランク判定）"""
    user = User.query.get(user_id)
    rank = Rank.query.get(user.rank_code)

    # ランク倍率適用
    actual_amount = int(amount * rank.bonus_multiplier)

    # ユーザーの残高と累計を更新
    user.total_points += actual_amount
    user.lifetime_points += actual_amount

    # 履歴に記録
    log = PointHistory(
        user_id=user_id,
        amount=actual_amount,
        source=source,
        description=description,
    )
    db.session.add(log)

    # ランクアップ判定
    from services.rank_service import check_rank_up
    check_rank_up(user_id)

    # トロフィー判定
    from services.trophy_service import check_and_unlock
    check_and_unlock(user_id)

    db.session.commit()
    return actual_amount
