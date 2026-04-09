import random
from datetime import date
from models.game import Game, GamePlayLog


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


def determine_result(game, user):
    """勝敗判定と付与ポイント計算"""
    is_win = random.random() < game.win_rate
    if is_win:
        points = random.randint(game.points_on_win_min, game.points_on_win_max)
        return 'win', points
    else:
        return 'lose', game.points_on_lose
