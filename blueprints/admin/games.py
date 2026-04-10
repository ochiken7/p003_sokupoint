from flask import render_template, request, redirect, url_for, flash
from extensions import db
from blueprints.admin import admin_bp, admin_required
from models.game import Game, GameOutcome, QuizQuestion

DEFAULT_OUTCOMES = [
    {'label': '1等', 'points': 500, 'weight': 1.0, 'color': '#E63946'},
    {'label': '2等', 'points': 200, 'weight': 5.0, 'color': '#EF476F'},
    {'label': '3等', 'points': 100, 'weight': 10.0, 'color': '#F5C542'},
    {'label': '4等', 'points': 50, 'weight': 20.0, 'color': '#10B981'},
    {'label': '5等', 'points': 10, 'weight': 30.0, 'color': '#6B7280'},
    {'label': 'はずれ', 'points': 1, 'weight': 34.0, 'color': '#9CA3AF'},
]


def _ensure_outcomes(game):
    """ゲームに6つの結果が無ければ初期値で作成"""
    existing = GameOutcome.query.filter_by(game_id=game.id).count()
    if existing < 6:
        for i in range(1, 7):
            pos_exists = GameOutcome.query.filter_by(game_id=game.id, position=i).first()
            if not pos_exists:
                d = DEFAULT_OUTCOMES[i - 1]
                db.session.add(GameOutcome(
                    game_id=game.id, position=i,
                    label=d['label'], points=d['points'],
                    weight=d['weight'], color=d['color'],
                ))
        db.session.commit()


@admin_bp.route('/games')
@admin_required
def games_list():
    games = Game.query.order_by(Game.priority).all()
    return render_template('admin/games/list.html', games=games)


@admin_bp.route('/games/new', methods=['GET', 'POST'])
@admin_required
def games_create():
    if request.method == 'POST':
        game = _save_game(Game(), request.form)
        db.session.add(game)
        db.session.commit()
        _save_outcomes(game, request.form)
        _ensure_outcomes(game)
        flash(f'ゲーム「{game.name}」を作成しました。', 'success')
        if game.game_type == 'quiz':
            return redirect(url_for('admin.games_questions', game_id=game.id))
        return redirect(url_for('admin.games_list'))
    return render_template('admin/games/edit.html', game=None, outcomes=DEFAULT_OUTCOMES_LIST())


@admin_bp.route('/games/<int:game_id>/edit', methods=['GET', 'POST'])
@admin_required
def games_edit(game_id):
    game = Game.query.get_or_404(game_id)
    _ensure_outcomes(game)
    if request.method == 'POST':
        _save_game(game, request.form)
        _save_outcomes(game, request.form)
        db.session.commit()
        flash(f'ゲーム「{game.name}」を更新しました。', 'success')
        return redirect(url_for('admin.games_list'))

    outcomes = GameOutcome.query.filter_by(game_id=game.id).order_by(GameOutcome.position).all()
    return render_template('admin/games/edit.html', game=game, outcomes=outcomes)


@admin_bp.route('/games/<int:game_id>/toggle', methods=['POST'])
@admin_required
def games_toggle(game_id):
    game = Game.query.get_or_404(game_id)
    game.is_active = not game.is_active
    db.session.commit()
    status = '有効' if game.is_active else '無効'
    flash(f'ゲーム「{game.name}」を{status}にしました。', 'success')
    return redirect(url_for('admin.games_list'))


@admin_bp.route('/games/<int:game_id>/delete', methods=['POST'])
@admin_required
def games_delete(game_id):
    game = Game.query.get_or_404(game_id)
    name = game.name
    db.session.delete(game)
    db.session.commit()
    flash(f'ゲーム「{name}」を削除しました。', 'success')
    return redirect(url_for('admin.games_list'))


@admin_bp.route('/games/<int:game_id>/questions', methods=['GET', 'POST'])
@admin_required
def games_questions(game_id):
    game = Game.query.get_or_404(game_id)
    if request.method == 'POST':
        q = QuizQuestion(
            game_id=game_id,
            question_text=request.form['question_text'],
            choice_1=request.form['choice_1'],
            choice_2=request.form['choice_2'],
            choice_3=request.form['choice_3'],
            choice_4=request.form['choice_4'],
            correct_choice=int(request.form['correct_choice']),
            explanation=request.form.get('explanation', ''),
        )
        db.session.add(q)
        db.session.commit()
        flash('問題を追加しました。', 'success')
        return redirect(url_for('admin.games_questions', game_id=game_id))
    questions = QuizQuestion.query.filter_by(game_id=game_id).all()
    return render_template('admin/games/questions.html', game=game, questions=questions)


@admin_bp.route('/games/<int:game_id>/questions/<int:q_id>/delete', methods=['POST'])
@admin_required
def games_question_delete(game_id, q_id):
    q = QuizQuestion.query.get_or_404(q_id)
    db.session.delete(q)
    db.session.commit()
    flash('問題を削除しました。', 'success')
    return redirect(url_for('admin.games_questions', game_id=game_id))


def _save_game(game, form):
    game.name = form['name']
    game.game_type = form['game_type']
    game.description = form.get('description', '')
    game.priority = int(form.get('priority', 0))
    game.is_active = 'is_active' in form
    config = form.get('config_json', '').strip()
    game.config_json = config if config else None
    return game


def _save_outcomes(game, form):
    """フォームから6つの結果を保存"""
    for i in range(1, 7):
        label = form.get(f'outcome_{i}_label')
        if label is None:
            continue
        outcome = GameOutcome.query.filter_by(game_id=game.id, position=i).first()
        if not outcome:
            outcome = GameOutcome(game_id=game.id, position=i)
            db.session.add(outcome)
        outcome.label = label or f'{i}等'
        outcome.points = int(form.get(f'outcome_{i}_points', 0))
        outcome.weight = float(form.get(f'outcome_{i}_weight', 1.0))
        outcome.color = form.get(f'outcome_{i}_color', '#E63946')
    db.session.commit()


def DEFAULT_OUTCOMES_LIST():
    """新規作成画面用のダミーオブジェクトリスト"""
    class DummyOutcome:
        def __init__(self, position, data):
            self.position = position
            self.label = data['label']
            self.points = data['points']
            self.weight = data['weight']
            self.color = data['color']
    return [DummyOutcome(i + 1, d) for i, d in enumerate(DEFAULT_OUTCOMES)]
