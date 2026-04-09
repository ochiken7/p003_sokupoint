import json
from datetime import date
from flask import Blueprint, render_template, session, redirect, url_for, flash, request, jsonify
from extensions import db
from models.user import User
from models.game import Game, GamePlayLog, QuizQuestion
from services.game_engine import get_template, can_play_today, determine_result
from services.point_service import add_points

game_bp = Blueprint('game', __name__)


@game_bp.route('/games')
def index():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('auth.demo_switch'))

    games = Game.query.filter_by(is_active=True).order_by(Game.priority).all()
    today = date.today()

    # 各ゲームのプレイ済み状態を取得
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

    # クイズの場合は問題データも渡す
    questions = []
    if game.game_type == 'quiz':
        questions = QuizQuestion.query.filter_by(game_id=game_id).all()

    config = {}
    if game.config_json:
        config = json.loads(game.config_json)

    template = get_template(game)
    return render_template('game/play.html',
                           game=game, user=user,
                           questions=questions, config=config,
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

    # クイズの場合は正解判定
    if game.game_type == 'quiz':
        correct_count = int(request.form.get('correct_count', 0))
        total = int(request.form.get('total', 0))
        is_win = correct_count == total and total > 0
        result_text = 'win' if is_win else 'lose'
        if is_win:
            points = game.points_on_win_min
        else:
            points = game.points_on_lose
    else:
        result_text, points = determine_result(game, user)

    # プレイログ記録
    log = GamePlayLog(
        user_id=user_id,
        game_id=game_id,
        played_date=date.today(),
        result=result_text,
        points_awarded=points,
    )
    db.session.add(log)
    db.session.commit()

    # ポイント付与
    actual = add_points(user_id, points, 'game',
                        f'{game.name}({result_text})')

    return render_template('game/result.html',
                           game=game, result=result_text,
                           points=actual, user=user)
