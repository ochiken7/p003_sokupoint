from flask import render_template, request, redirect, url_for, flash
from extensions import db
from blueprints.admin import admin_bp, admin_required
from models.user import User, Rank
from models.point import PointHistory
from services.rank_service import check_rank_up


@admin_bp.route('/users')
@admin_required
def users_list():
    users = User.query.order_by(User.id).all()
    return render_template('admin/users/list.html', users=users)


@admin_bp.route('/users/<int:user_id>', methods=['GET', 'POST'])
@admin_required
def users_detail(user_id):
    user = User.query.get_or_404(user_id)
    ranks = Rank.query.order_by(Rank.min_lifetime_points).all()

    if request.method == 'POST':
        action = request.form.get('action')

        if action == 'adjust_points':
            amount = int(request.form.get('amount', 0))
            if amount != 0:
                user.total_points += amount
                if amount > 0:
                    user.lifetime_points += amount
                log = PointHistory(
                    user_id=user_id,
                    amount=amount,
                    source='admin',
                    description=f'管理者によるポイント調整({amount:+d})',
                )
                db.session.add(log)
                check_rank_up(user_id)
                db.session.commit()
                flash(f'{amount:+d}P を調整しました。', 'success')

        elif action == 'change_rank':
            new_rank = request.form.get('rank_code')
            if new_rank:
                user.rank_code = new_rank
                db.session.commit()
                flash(f'ランクを {new_rank} に変更しました。', 'success')

        return redirect(url_for('admin.users_detail', user_id=user_id))

    histories = PointHistory.query.filter_by(user_id=user_id)\
        .order_by(PointHistory.created_at.desc()).limit(30).all()

    return render_template('admin/users/detail.html',
                           user=user, ranks=ranks, histories=histories)
