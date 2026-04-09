from datetime import date, datetime
from flask import Blueprint, render_template, session, redirect, url_for, flash
from extensions import db
from models.user import User
from models.checkin import Store, Checkin
from services.point_service import add_points

checkin_bp = Blueprint('checkin', __name__)


@checkin_bp.route('/checkin')
def index():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('auth.demo_switch'))

    user = User.query.get(user_id)
    stores = Store.query.filter_by(is_active=True).all()
    today = date.today()

    # 本日チェックイン済みの店舗ID
    checked_store_ids = set()
    today_checkins = Checkin.query.filter(
        Checkin.user_id == user_id,
        db.func.date(Checkin.checked_in_at) == today
    ).all()
    for ci in today_checkins:
        checked_store_ids.add(ci.store_id)

    return render_template('checkin.html',
                           user=user, stores=stores,
                           checked_store_ids=checked_store_ids)


@checkin_bp.route('/checkin/<int:store_id>', methods=['POST'])
def do_checkin(store_id):
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('auth.demo_switch'))

    store = Store.query.get_or_404(store_id)
    today = date.today()

    # 同日同店舗チェック
    existing = Checkin.query.filter(
        Checkin.user_id == user_id,
        Checkin.store_id == store_id,
        db.func.date(Checkin.checked_in_at) == today
    ).first()
    if existing:
        flash('本日この店舗には既にチェックイン済みです。', 'warning')
        return redirect(url_for('checkin.index'))

    ci = Checkin(
        user_id=user_id,
        store_id=store_id,
        points_awarded=300,
    )
    db.session.add(ci)
    db.session.commit()

    actual = add_points(user_id, 300, 'checkin', f'{store.name}にチェックイン')

    flash(f'{store.name}にチェックイン! {actual}P を獲得!', 'success')
    return redirect(url_for('checkin.index'))
