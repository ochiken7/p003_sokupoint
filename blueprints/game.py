import json
from datetime import date
from flask import Blueprint, render_template, session, redirect, url_for, flash, request
from extensions import db
from models.user import User
from models.game import Game, GamePlayLog, QuizQuestion
from services.game_engine import get_template, can_play_today, determine_result, get_outcomes
from services.point_service import add_points

game_bp = Blueprint('game', __name__)


@game_bp.route('/games')
def index():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('auth.demo_switch'))

    games = Game.query.filter_by(is_active=True).order_by(Game.priority).all()
    today = date.today()

    played_today = set()
    logs = GamePlayLog.query.filter_by(user_id=user_id, played_date=today).all()
    for log in logs:
        played_today.add(log.game_id)

    return render_template('game/list.html', games=games, played_today=played_today)


@game_bp.route('/games/<int:game_id>/play')
def play(game_id):
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('auth.demo_switch'))

    game = Game.query.get_or_404(game_id)
    user = User.query.get(user_id)

    if not game.is_active:
        flash('このゲームは現在利用できません。', 'warning')
        return redirect(url_for('game.index'))

    if not can_play_today(user_id, game_id):
        flash('このゲームは本日プレイ済みです。', 'warning')
        return redirect(url_for('game.index'))

    questions = []
    if game.game_type == 'quiz':
        questions = QuizQuestion.query.filter_by(game_id=game_id).all()

    config = {}
    if game.config_json:
        config = json.loads(game.config_json)

    # 6つの結果を取得（ルーレット等で使用）
    outcomes = get_outcomes(game_id)

    template = get_template(game)
    return render_template('game/play.html',
                           game=game, user=user,
                           questions=questions, config=config,
                           outcomes=outcomes,
                           game_template=template)


@game_bp.route('/games/<int:game_id>/result', methods=['POST'])
def result(game_id):
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('auth.demo_switch'))

    game = Game.query.get_or_404(game_id)
    user = User.query.get(user_id)

    if not can_play_today(user_id, game_id):
        flash('このゲームは本日プレイ済みです。', 'warning')
        return redirect(url_for('game.index'))

    # クイズ: 正解数を渡す / その他: 重み付き抽選
    quiz_correct = None
    quiz_total = None
    if game.game_type == 'quiz':
        quiz_correct = int(request.form.get('correct_count', 0))
        quiz_total = int(request.form.get('total', 0))

    position, points, label = determine_result(game, user,
                                                quiz_correct_count=quiz_correct,
                                                quiz_total=quiz_total)

    # プレイログ記録
    log = GamePlayLog(
        user_id=user_id,
        game_id=game_id,
        played_date=date.today(),
        outcome_position=position,
        result_label=label,
        points_awarded=points,
    )
    db.session.add(log)
    db.session.commit()

    # ポイント付与
    actual = add_points(user_id, points, 'game', f'{game.name}「{label}」')

    return render_template('game/result.html',
                           game=game, label=label, position=position,
                           points=actual, user=user)
