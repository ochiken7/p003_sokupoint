from extensions import db
from models.user import User
from models.trophy import Trophy, UserTrophy
from models.login_bonus import LoginBonusLog
from models.game import GamePlayLog
from models.checkin import Checkin


def check_and_unlock(user_id):
    """全未取得トロフィーについて条件を評価し、達成していれば解放する"""
    user = User.query.get(user_id)
    unlocked_ids = {ut.trophy_id for ut in UserTrophy.query.filter_by(user_id=user_id).all()}
    trophies = Trophy.query.filter_by(is_active=True).all()

    for trophy in trophies:
        if trophy.id in unlocked_ids:
            continue

        achieved = _evaluate_condition(user, trophy)
        if achieved:
            ut = UserTrophy(user_id=user_id, trophy_id=trophy.id)
            db.session.add(ut)
            # トロフィー報酬ポイントは倍率なしで直接加算
            if trophy.points_reward > 0:
                user.total_points += trophy.points_reward
                user.lifetime_points += trophy.points_reward
                from models.point import PointHistory
                log = PointHistory(
                    user_id=user_id,
                    amount=trophy.points_reward,
                    source='trophy',
                    description=f'トロフィー「{trophy.name}」獲得報酬',
                )
                db.session.add(log)


def _evaluate_condition(user, trophy):
    """条件タイプに応じて達成判定"""
    ct = trophy.condition_type
    cv = trophy.condition_value

    if ct == 'login_streak':
        return user.consecutive_login_days >= cv
    elif ct == 'game_play_count':
        count = GamePlayLog.query.filter_by(user_id=user.id).count()
        return count >= cv
    elif ct == 'checkin_count':
        count = Checkin.query.filter_by(user_id=user.id).count()
        return count >= cv
    elif ct == 'login_bonus_count':
        count = LoginBonusLog.query.filter_by(user_id=user.id).count()
        return count >= cv
    elif ct == 'lifetime_points':
        return user.lifetime_points >= cv
    elif ct == 'total_points':
        return user.total_points >= cv
    return False
