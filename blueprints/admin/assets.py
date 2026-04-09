import os
from flask import render_template, request, redirect, url_for, flash, current_app
from extensions import db
from blueprints.admin import admin_bp, admin_required
from models.site_asset import SiteAsset
from werkzeug.utils import secure_filename

SLOTS = [
    ('logo_header', 'ヘッダーロゴ', '推奨: 200x50px'),
    ('banner_home_1', 'ホーム上部バナー 1', '推奨: 1200x400px'),
    ('banner_home_2', 'ホーム上部バナー 2', '推奨: 1200x400px'),
    ('favicon', 'Favicon', '推奨: 32x32px'),
]

ALLOWED_EXT = {'png', 'jpg', 'jpeg', 'gif', 'webp', 'ico', 'svg'}


@admin_bp.route('/assets', methods=['GET', 'POST'])
@admin_required
def assets_manage():
    if request.method == 'POST':
        slot_key = request.form.get('slot_key')
        asset = SiteAsset.query.filter_by(slot_key=slot_key).first()
        if not asset:
            asset = SiteAsset(slot_key=slot_key)
            db.session.add(asset)

        asset.alt_text = request.form.get('alt_text', '')
        asset.link_url = request.form.get('link_url', '')

        file = request.files.get('file')
        if file and file.filename:
            ext = file.filename.rsplit('.', 1)[-1].lower()
            if ext not in ALLOWED_EXT:
                flash('許可されていないファイル形式です。', 'error')
                return redirect(url_for('admin.assets_manage'))

            # 保存先ディレクトリ
            if 'logo' in slot_key:
                subdir = 'logo'
            elif 'banner' in slot_key:
                subdir = 'banners'
            else:
                subdir = 'logo'

            upload_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], subdir)
            os.makedirs(upload_dir, exist_ok=True)

            filename = f'{slot_key}.{ext}'
            filepath = os.path.join(upload_dir, filename)
            file.save(filepath)

            # DB上のパスは static/ からの相対
            rel_path = os.path.join('uploads', subdir, filename).replace('\\', '/')
            asset.file_path = rel_path

        db.session.commit()
        flash('画像設定を更新しました。', 'success')
        return redirect(url_for('admin.assets_manage'))

    assets = {}
    for slot_key, label, hint in SLOTS:
        asset = SiteAsset.query.filter_by(slot_key=slot_key).first()
        assets[slot_key] = {
            'label': label,
            'hint': hint,
            'asset': asset,
        }

    return render_template('admin/assets.html', slots=SLOTS, assets=assets)
