import os
import glob
from flask import render_template, request, redirect, url_for, flash, current_app
from extensions import db
from blueprints.admin import admin_bp, admin_required
from models.site_asset import SiteAsset

SLOTS = [
    ('logo_header', 'ヘッダーロゴ', '推奨: 400x100px (横長)'),
    ('banner_home_1', 'ホーム上部バナー 1', '推奨: 1200x400px (3:1)'),
    ('banner_home_2', 'ホーム上部バナー 2', '推奨: 1200x400px (3:1)'),
    ('banner_home_3', 'タスク下バナー', '推奨: 1200x300px (4:1)'),
    ('banner_home_4', 'お知らせ下バナー', '推奨: 1200x300px (4:1)'),
    ('banner_footer', 'フッター上バナー', '推奨: 1200x200px (6:1)'),
    ('favicon', 'Favicon', '推奨: 32x32px'),
]

ALLOWED_EXT = {'png', 'jpg', 'jpeg', 'gif', 'webp', 'ico', 'svg'}


@admin_bp.route('/assets', methods=['GET', 'POST'])
@admin_required
def assets_manage():
    if request.method == 'POST':
        action = request.form.get('action', 'save')
        slot_key = request.form.get('slot_key')

        asset = SiteAsset.query.filter_by(slot_key=slot_key).first()

        # 削除アクション
        if action == 'delete':
            if asset and asset.file_path:
                # ファイル削除
                full_path = os.path.join(current_app.static_folder, asset.file_path)
                if os.path.exists(full_path):
                    os.remove(full_path)
                asset.file_path = None
                db.session.commit()
                flash('画像を削除しました。', 'success')
            return redirect(url_for('admin.assets_manage'))

        # 保存アクション
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

            # 保存先サブディレクトリ
            if 'logo' in slot_key or 'favicon' in slot_key:
                subdir = 'logo'
            else:
                subdir = 'banners'

            upload_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], subdir)
            os.makedirs(upload_dir, exist_ok=True)

            # 古いファイルを削除（拡張子が変わる場合に備える）
            old_files = glob.glob(os.path.join(upload_dir, f'{slot_key}.*'))
            for old in old_files:
                os.remove(old)

            filename = f'{slot_key}.{ext}'
            filepath = os.path.join(upload_dir, filename)
            file.save(filepath)

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
