from flask import render_template, request, redirect, url_for, flash
from extensions import db
from blueprints.admin import admin_bp, admin_required
from models.trophy import Trophy


@admin_bp.route('/trophies')
@admin_required
def trophies_list():
    trophies = Trophy.query.order_by(Trophy.id).all()
    return render_template('admin/trophies/list.html', trophies=trophies)


@admin_bp.route('/trophies/new', methods=['GET', 'POST'])
@admin_required
def trophies_create():
    if request.method == 'POST':
        trophy = _save_trophy(Trophy(), request.form)
        db.session.add(trophy)
        db.session.commit()
        flash(f'トロフィー「{trophy.name}」を作成しました。', 'success')
        return redirect(url_for('admin.trophies_list'))
    return render_template('admin/trophies/edit.html', trophy=None)


@admin_bp.route('/trophies/<int:trophy_id>/edit', methods=['GET', 'POST'])
@admin_required
def trophies_edit(trophy_id):
    trophy = Trophy.query.get_or_404(trophy_id)
    if request.method == 'POST':
        _save_trophy(trophy, request.form)
        db.session.commit()
        flash(f'トロフィー「{trophy.name}」を更新しました。', 'success')
        return redirect(url_for('admin.trophies_list'))
    return render_template('admin/trophies/edit.html', trophy=trophy)


@admin_bp.route('/trophies/<int:trophy_id>/delete', methods=['POST'])
@admin_required
def trophies_delete(trophy_id):
    trophy = Trophy.query.get_or_404(trophy_id)
    name = trophy.name
    db.session.delete(trophy)
    db.session.commit()
    flash(f'トロフィー「{name}」を削除しました。', 'success')
    return redirect(url_for('admin.trophies_list'))


def _save_trophy(trophy, form):
    trophy.code = form['code']
    trophy.name = form['name']
    trophy.description = form.get('description', '')
    trophy.icon_name = form.get('icon_name', 'trophy')
    trophy.condition_type = form['condition_type']
    trophy.condition_value = int(form.get('condition_value', 1))
    trophy.points_reward = int(form.get('points_reward', 0))
    trophy.is_active = 'is_active' in form
    return trophy
