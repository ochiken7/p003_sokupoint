from datetime import datetime
from flask import render_template, request, redirect, url_for, flash
from extensions import db
from blueprints.admin import admin_bp, admin_required
from models.coupon import Coupon


@admin_bp.route('/coupons')
@admin_required
def coupons_list():
    coupons = Coupon.query.order_by(Coupon.id.desc()).all()
    return render_template('admin/coupons/list.html', coupons=coupons)


@admin_bp.route('/coupons/new', methods=['GET', 'POST'])
@admin_required
def coupons_create():
    if request.method == 'POST':
        coupon = _save_coupon(Coupon(), request.form)
        db.session.add(coupon)
        db.session.commit()
        flash(f'クーポン「{coupon.title}」を作成しました。', 'success')
        return redirect(url_for('admin.coupons_list'))
    return render_template('admin/coupons/edit.html', coupon=None)


@admin_bp.route('/coupons/<int:coupon_id>/edit', methods=['GET', 'POST'])
@admin_required
def coupons_edit(coupon_id):
    coupon = Coupon.query.get_or_404(coupon_id)
    if request.method == 'POST':
        _save_coupon(coupon, request.form)
        db.session.commit()
        flash(f'クーポン「{coupon.title}」を更新しました。', 'success')
        return redirect(url_for('admin.coupons_list'))
    return render_template('admin/coupons/edit.html', coupon=coupon)


@admin_bp.route('/coupons/<int:coupon_id>/delete', methods=['POST'])
@admin_required
def coupons_delete(coupon_id):
    coupon = Coupon.query.get_or_404(coupon_id)
    name = coupon.title
    db.session.delete(coupon)
    db.session.commit()
    flash(f'クーポン「{name}」を削除しました。', 'success')
    return redirect(url_for('admin.coupons_list'))


def _save_coupon(coupon, form):
    coupon.title = form['title']
    coupon.description = form.get('description', '')
    coupon.required_rank = form.get('required_rank', 'BRONZE')
    coupon.winner_count = int(form.get('winner_count', 1))
    coupon.is_active = 'is_active' in form
    start = form.get('entry_start')
    end = form.get('entry_end')
    if start:
        coupon.entry_start = datetime.fromisoformat(start)
    if end:
        coupon.entry_end = datetime.fromisoformat(end)
    return coupon
