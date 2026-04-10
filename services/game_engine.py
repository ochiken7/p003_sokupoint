import random
from datetime import date
from models.game import Game, GameOutcome, GamePlayLog


def get_template(game):
    """ゲームタイプに応じたテンプレートパスを返す"""
    return f'game/types/{game.game_type}.html'


def can_play_today(user_id, game_id):
    """1日1回制限チェック"""
    today = date.today()
    existing = GamePlayLog.query.filter_by(
        user_id=user_id, game_id=game_id, played_date=today
    ).first()
    return existing is None


def get_outcomes(game_id):
    """ゲームの6つの結果を取得（position順）"""
    return GameOutcome.query.filter_by(game_id=game_id)\
        .order_by(GameOutcome.position).all()


def weighted_pick(outcomes):
    """重み付きランダム選択"""
    total_weight = sum(max(o.weight, 0) for o in outcomes)
    if total_weight <= 0:
        return random.choice(outcomes)

    r = random.random() * total_weight
    acc = 0
    for o in outcomes:
        acc += max(o.weight, 0)
        if r <= acc:
            return o
    return outcomes[-1]


def determine_result(game, user, quiz_correct_count=None, quiz_total=None):
    """
    抽選結果を決定。
    - scratch / roulette: 6つの結果から重み付き抽選
    - quiz: 全問正解なら1等(position=1)、それ以外は6等(position=6)
    戻り値: (outcome_position, points, label)
    """
    outcomes = get_outcomes(game.id)
    if not outcomes:
        return None, 0, '未設定'

    if game.game_type == 'quiz' and quiz_correct_count is not None:
        # 全問正解: 1等、それ以外: 6等
        if quiz_total and quiz_correct_count == quiz_total:
            picked = next((o for o in outcomes if o.position == 1), outcomes[0])
        else:
            picked = next((o for o in outcomes if o.position == 6), outcomes[-1])
    else:
        picked = weighted_pick(outcomes)

    return picked.position, picked.points, picked.label
