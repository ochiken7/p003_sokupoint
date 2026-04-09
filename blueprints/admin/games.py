import json
from flask import render_template, request, redirect, url_for, flash
from extensions import db
from blueprints.admin import admin_bp, admin_required
from models.game import Game, QuizQuestion


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
        flash(f'ゲーム「{game.name}」を作成しました。', 'success')
        if game.game_type == 'quiz':
            return redirect(url_for('admin.games_questions', game_id=game.id))
        return redirect(url_for('admin.games_list'))
    return render_template('admin/games/edit.html', game=None)


@admin_bp.route('/games/<int:game_id>/edit', methods=['GET', 'POST'])
@admin_required
def games_edit(game_id):
    game = Game.query.get_or_404(game_id)
    if request.method == 'POST':
        _save_game(game, request.form)
        db.session.commit()
        flash(f'ゲーム「{game.name}」を更新しました。', 'success')
        return redirect(url_for('admin.games_list'))
    return render_template('admin/games/edit.html', game=game)


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
    game.win_rate = float(form.get('win_rate', 0.3))
    game.points_on_win_min = int(form.get('points_on_win_min', 10))
    game.points_on_win_max = int(form.get('points_on_win_max', 100))
    game.points_on_lose = int(form.get('points_on_lose', 1))
    game.is_active = 'is_active' in form
    config = form.get('config_json', '').strip()
    game.config_json = config if config else None
    return game
