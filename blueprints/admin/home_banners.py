import os
import glob
from flask import render_template, request, redirect, url_for, flash, current_app
from extensions import db
from blueprints.admin import admin_bp, admin_required
from models.home_banner import HomeBanner
from services.setting_service import get_setting_int, set_setting

DEFAULT_SLIDE_INTERVAL = 5  # 秒

ALLOWED_EXT = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
SUBDIR = 'banners/home_slider'


def _upload_dir():
    path = os.path.join(current_app.config['UPLOAD_FOLDER'], SUBDIR)
    os.makedirs(path, exist_ok=True)
    return path


def _save_file(file, banner_id, kind):
    """file を {banner_id}_{kind}.{ext} で保存して相対パスを返す。kind = 'pc' or 'sp'"""
    if not file or not file.filename:
        return None
    ext = file.filename.rsplit('.', 1)[-1].lower()
    if ext not in ALLOWED_EXT:
        return False  # 拒否を示す

    upload_dir = _upload_dir()
    # 同じidの古いファイル(拡張子違い)を削除
    old_files = glob.glob(os.path.join(upload_dir, f'{banner_id}_{kind}.*'))
    for old in old_files:
        try:
            os.remove(old)
        except OSError:
            pass

    filename = f'{banner_id}_{kind}.{ext}'
    filepath = os.path.join(upload_dir, filename)
    file.save(filepath)
    return os.path.join('uploads', SUBDIR, filename).replace('\\', '/')


def _delete_banner_files(banner):
    """バナーに紐づく画像ファイルを物理削除"""
    upload_dir = _upload_dir()
    for kind in ('pc', 'sp'):
        old_files = glob.glob(os.path.join(upload_dir, f'{banner.id}_{kind}.*'))
        for old in old_files:
            try:
                os.remove(old)
            except OSError:
                pass


@admin_bp.route('/home-banners')
@admin_required
def home_banners_list():
    banners = HomeBanner.query.order_by(HomeBanner.position, HomeBanner.id).all()
    slide_interval = get_setting_int('home_slide_interval', DEFAULT_SLIDE_INTERVAL)
    return render_template('admin/home_banners/list.html',
                           banners=banners, slide_interval=slide_interval)


@admin_bp.route('/home-banners/settings', methods=['POST'])
@admin_required
def home_banners_settings():
    """スライド間隔等の設定を保存"""
    try:
        interval = int(request.form.get('slide_interval', DEFAULT_SLIDE_INTERVAL))
        if interval < 1:
            interval = 1
        if interval > 60:
            interval = 60
    except ValueError:
        interval = DEFAULT_SLIDE_INTERVAL
    set_setting('home_slide_interval', interval)
    flash(f'スライド間隔を {interval} 秒に設定しました。', 'success')
    return redirect(url_for('admin.home_banners_list'))


@admin_bp.route('/home-banners/new', methods=['POST'])
@admin_required
def home_banners_create():
    pc_file = request.files.get('file_pc')
    if not pc_file or not pc_file.filename:
        flash('PC版画像は必須です。', 'error')
        return redirect(url_for('admin.home_banners_list'))

    # positionは現在の最大+1
    max_pos = db.session.query(db.func.max(HomeBanner.position)).scalar() or 0
    banner = HomeBanner(
        position=max_pos + 1,
        alt_text=request.form.get('alt_text', ''),
        link_url=request.form.get('link_url', ''),
        is_active='is_active' in request.form,
        file_path_pc='',  # flush後に更新
    )
    db.session.add(banner)
    db.session.flush()  # IDを確定

    # PC画像保存
    pc_path = _save_file(pc_file, banner.id, 'pc')
    if pc_path is False:
        db.session.rollback()
        flash('許可されていないファイル形式です。', 'error')
        return redirect(url_for('admin.home_banners_list'))
    banner.file_path_pc = pc_path

    # SP画像保存(任意)
    sp_file = request.files.get('file_sp')
    if sp_file and sp_file.filename:
        sp_path = _save_file(sp_file, banner.id, 'sp')
        if sp_path is False:
            db.session.rollback()
            flash('許可されていないファイル形式です。', 'error')
            return redirect(url_for('admin.home_banners_list'))
        banner.file_path_sp = sp_path

    db.session.commit()
    flash('バナーを追加しました。', 'success')
    return redirect(url_for('admin.home_banners_list'))


@admin_bp.route('/home-banners/<int:banner_id>/edit', methods=['GET', 'POST'])
@admin_required
def home_banners_edit(banner_id):
    banner = HomeBanner.query.get_or_404(banner_id)

    if request.method == 'POST':
        banner.alt_text = request.form.get('alt_text', '')
        banner.link_url = request.form.get('link_url', '')
        banner.is_active = 'is_active' in request.form

        pc_file = request.files.get('file_pc')
        if pc_file and pc_file.filename:
            pc_path = _save_file(pc_file, banner.id, 'pc')
            if pc_path is False:
                flash('許可されていないファイル形式です。', 'error')
                return redirect(url_for('admin.home_banners_edit', banner_id=banner.id))
            banner.file_path_pc = pc_path

        sp_file = request.files.get('file_sp')
        if sp_file and sp_file.filename:
            sp_path = _save_file(sp_file, banner.id, 'sp')
            if sp_path is False:
                flash('許可されていないファイル形式です。', 'error')
                return redirect(url_for('admin.home_banners_edit', banner_id=banner.id))
            banner.file_path_sp = sp_path

        db.session.commit()
        flash('バナーを更新しました。', 'success')
        return redirect(url_for('admin.home_banners_list'))

    return render_template('admin/home_banners/edit.html', banner=banner)


@admin_bp.route('/home-banners/<int:banner_id>/delete', methods=['POST'])
@admin_required
def home_banners_delete(banner_id):
    banner = HomeBanner.query.get_or_404(banner_id)
    _delete_banner_files(banner)
    db.session.delete(banner)
    db.session.commit()
    flash('バナーを削除しました。', 'success')
    return redirect(url_for('admin.home_banners_list'))


@admin_bp.route('/home-banners/<int:banner_id>/toggle', methods=['POST'])
@admin_required
def home_banners_toggle(banner_id):
    banner = HomeBanner.query.get_or_404(banner_id)
    banner.is_active = not banner.is_active
    db.session.commit()
    return redirect(url_for('admin.home_banners_list'))


@admin_bp.route('/home-banners/<int:banner_id>/delete-sp', methods=['POST'])
@admin_required
def home_banners_delete_sp(banner_id):
    """SP版だけ削除 (PC版は保持)"""
    banner = HomeBanner.query.get_or_404(banner_id)
    upload_dir = _upload_dir()
    old_files = glob.glob(os.path.join(upload_dir, f'{banner.id}_sp.*'))
    for old in old_files:
        try:
            os.remove(old)
        except OSError:
            pass
    banner.file_path_sp = None
    db.session.commit()
    flash('SP版画像を削除しました。', 'success')
    return redirect(url_for('admin.home_banners_edit', banner_id=banner.id))


@admin_bp.route('/home-banners/<int:banner_id>/move', methods=['POST'])
@admin_required
def home_banners_move(banner_id):
    """direction=up/down で隣と position を入れ替え"""
    banner = HomeBanner.query.get_or_404(banner_id)
    direction = request.form.get('direction')

    ordered = HomeBanner.query.order_by(HomeBanner.position, HomeBanner.id).all()
    idx = next((i for i, b in enumerate(ordered) if b.id == banner.id), None)
    if idx is None:
        return redirect(url_for('admin.home_banners_list'))

    if direction == 'up' and idx > 0:
        other = ordered[idx - 1]
    elif direction == 'down' and idx < len(ordered) - 1:
        other = ordered[idx + 1]
    else:
        return redirect(url_for('admin.home_banners_list'))

    banner.position, other.position = other.position, banner.position
    db.session.commit()
    return redirect(url_for('admin.home_banners_list'))
