import uuid
from flask import render_template, request, redirect, url_for, flash
from extensions import db
from blueprints.admin import admin_bp, admin_required
from models.checkin import Store


@admin_bp.route('/stores')
@admin_required
def stores_list():
    stores = Store.query.order_by(Store.id).all()
    return render_template('admin/stores/list.html', stores=stores)


@admin_bp.route('/stores/new', methods=['GET', 'POST'])
@admin_required
def stores_create():
    if request.method == 'POST':
        store = Store(
            name=request.form['name'],
            area=request.form.get('area', ''),
            qr_token=uuid.uuid4().hex[:12],
            is_active='is_active' in request.form,
        )
        db.session.add(store)
        db.session.commit()
        flash(f'店舗「{store.name}」を作成しました。', 'success')
        return redirect(url_for('admin.stores_list'))
    return render_template('admin/stores/edit.html', store=None)


@admin_bp.route('/stores/<int:store_id>/edit', methods=['GET', 'POST'])
@admin_required
def stores_edit(store_id):
    store = Store.query.get_or_404(store_id)
    if request.method == 'POST':
        store.name = request.form['name']
        store.area = request.form.get('area', '')
        store.is_active = 'is_active' in request.form
        db.session.commit()
        flash(f'店舗「{store.name}」を更新しました。', 'success')
        return redirect(url_for('admin.stores_list'))
    return render_template('admin/stores/edit.html', store=store)


@admin_bp.route('/stores/<int:store_id>/delete', methods=['POST'])
@admin_required
def stores_delete(store_id):
    store = Store.query.get_or_404(store_id)
    name = store.name
    db.session.delete(store)
    db.session.commit()
    flash(f'店舗「{name}」を削除しました。', 'success')
    return redirect(url_for('admin.stores_list'))
