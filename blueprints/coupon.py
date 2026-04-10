import random
from datetime import datetime
from flask import Blueprint, render_template, session, redirect, url_for, flash
from extensions import db
from models.user import User, Rank
from models.coupon import Coupon, CouponEntry
from services.point_service import add_points

coupon_bp = Blueprint('coupon', __name__)

RANK_ORDER = ['BRONZE', 'SILVER', 'GOLD', 'VIP']


@coupon_bp.route('/coupons')
def index():
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('auth.demo_switch'))

    user = User.query.get(user_id)
    now = datetime.utcnow()

    # 応募期間内 + 有効なクーポンを取得
    coupons = Coupon.query.filter(
        Coupon.is_active == True,
        Coupon.entry_start <= now,
        Coupon.entry_end >= now,
    ).all()

    # ユーザーランクで参加可能かフィルタ
    user_rank_idx = RANK_ORDER.index(user.rank_code) if user.rank_code in RANK_ORDER else 0
    available = []
    for c in coupons:
        req_idx = RANK_ORDER.index(c.required_rank) if c.required_rank in RANK_ORDER else 0
        if user_rank_idx >= req_idx:
            available.append(c)

    # 応募済みクーポンID
    entered_ids = {e.coupon_id for e in CouponEntry.query.filter_by(user_id=user_id).all()}

    return render_template('coupon/list.html',
                           user=user, coupons=available, entered_ids=entered_ids)


@coupon_bp.route('/coupons/<int:coupon_id>')
def detail(coupon_id):
    """クーポン詳細ページ"""
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('auth.demo_switch'))

    user = User.query.get(user_id)
    coupon = Coupon.query.get_or_404(coupon_id)

    # 応募済みか
    entered = CouponEntry.query.filter_by(user_id=user_id, coupon_id=coupon_id).first()
    # 応募可能期間か
    now = datetime.utcnow()
    in_period = coupon.is_active and coupon.entry_start <= now <= coupon.entry_end
    # ランク足りているか
    user_rank_idx = RANK_ORDER.index(user.rank_code) if user.rank_code in RANK_ORDER else 0
    req_idx = RANK_ORDER.index(coupon.required_rank) if coupon.required_rank in RANK_ORDER else 0
    rank_ok = user_rank_idx >= req_idx

    return render_template('coupon/detail.html',
                           user=user, coupon=coupon,
                           entered=entered, in_period=in_period, rank_ok=rank_ok)


@coupon_bp.route('/coupons/<int:coupon_id>/entry', methods=['POST'])
def entry(coupon_id):
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('auth.demo_switch'))

    coupon = Coupon.query.get_or_404(coupon_id)

    # 重複チェック
    existing = CouponEntry.query.filter_by(user_id=user_id, coupon_id=coupon_id).first()
    if existing:
        flash('既にこのクーポンに応募済みです。', 'warning')
        return redirect(url_for('coupon.detail', coupon_id=coupon_id))

    # 当落判定（プロトではランダム）
    entry_count = CouponEntry.query.filter_by(coupon_id=coupon_id).count()
    is_winner = entry_count < coupon.winner_count and random.random() < 0.5

    new_entry = CouponEntry(
        user_id=user_id,
        coupon_id=coupon_id,
        is_winner=is_winner,
    )
    db.session.add(new_entry)
    db.session.commit()

    # 応募ポイント付与
    actual = add_points(user_id, 10, 'coupon', f'クーポン「{coupon.title}」に応募')

    if is_winner:
        flash(f'当選! クーポン「{coupon.title}」に当選しました! (+{actual}P)', 'success')
    else:
        flash(f'クーポン「{coupon.title}」に応募しました (+{actual}P)', 'info')

    return redirect(url_for('coupon.detail', coupon_id=coupon_id))
