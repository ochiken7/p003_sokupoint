import os
import glob
from flask import render_template, request, redirect, url_for, flash, current_app
from extensions import db
from blueprints.admin import admin_bp, admin_required
from models.site_asset import SiteAsset

# --- スロット定義 ---
# (slot_key, label, hint, type)  type: 'image' | 'html'

IMAGE_SLOTS = [
    ('logo_header', 'ヘッダーロゴ', '推奨: 400x100px (横長)'),
    # ※ホーム上部メインバナーは「トップバナー管理」(/admin/home-banners) で複数登録・スライドショー化
    ('banner_home_3', 'タスク下バナー', '推奨: 1200x300px (4:1)'),
    # お知らせ下バナー 2枠 (600x300)
    ('banner_news_1', 'お知らせ下バナー 左', '推奨: 600x300px (2:1)'),
    ('banner_news_2', 'お知らせ下バナー 右', '推奨: 600x300px (2:1)'),
    # フッター上バナー 8枠 (300x150, 4列x2段)
    ('banner_ft_1', 'フッターバナー 1', '推奨: 300x150px (2:1)'),
    ('banner_ft_2', 'フッターバナー 2', '推奨: 300x150px (2:1)'),
    ('banner_ft_3', 'フッターバナー 3', '推奨: 300x150px (2:1)'),
    ('banner_ft_4', 'フッターバナー 4', '推奨: 300x150px (2:1)'),
    ('banner_ft_5', 'フッターバナー 5', '推奨: 300x150px (2:1)'),
    ('banner_ft_6', 'フッターバナー 6', '推奨: 300x150px (2:1)'),
    ('banner_ft_7', 'フッターバナー 7', '推奨: 300x150px (2:1)'),
    ('banner_ft_8', 'フッターバナー 8', '推奨: 300x150px (2:1)'),
    ('favicon', 'Favicon', '推奨: 32x32px'),
]

HTML_SLOTS = [
    ('article_wide', '記事エリア (1200幅)', 'お知らせ下バナーとフッターバナーの間に表示。全幅1カラム。'),
    ('article_half_1', '記事エリア 左上 (600幅)', '2カラムの左上に表示。'),
    ('article_half_2', '記事エリア 右上 (600幅)', '2カラムの右上に表示。'),
    ('article_half_3', '記事エリア 左下 (600幅)', '2カラムの左下に表示。'),
    ('article_half_4', '記事エリア 右下 (600幅)', '2カラムの右下に表示。'),
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
                full_path = os.path.join(current_app.static_folder, asset.file_path)
                if os.path.exists(full_path):
                    os.remove(full_path)
                asset.file_path = None
                db.session.commit()
                flash('画像を削除しました。', 'success')
            return redirect(url_for('admin.assets_manage'))

        # HTML保存アクション
        if action == 'save_html':
            if not asset:
                asset = SiteAsset(slot_key=slot_key)
                db.session.add(asset)
            asset.content_html = request.form.get('content_html', '')
            db.session.commit()
            flash('記事を更新しました。', 'success')
            return redirect(url_for('admin.assets_manage'))

        # 画像保存アクション
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

            if 'logo' in slot_key or 'favicon' in slot_key:
                subdir = 'logo'
            else:
                subdir = 'banners'

            upload_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], subdir)
            os.makedirs(upload_dir, exist_ok=True)

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

    # GET: 全スロット読み込み
    image_assets = {}
    for slot_key, label, hint in IMAGE_SLOTS:
        asset = SiteAsset.query.filter_by(slot_key=slot_key).first()
        image_assets[slot_key] = {'label': label, 'hint': hint, 'asset': asset}

    html_assets = {}
    for slot_key, label, hint in HTML_SLOTS:
        asset = SiteAsset.query.filter_by(slot_key=slot_key).first()
        html_assets[slot_key] = {'label': label, 'hint': hint, 'asset': asset}

    return render_template('admin/assets.html',
                           image_slots=IMAGE_SLOTS, image_assets=image_assets,
                           html_slots=HTML_SLOTS, html_assets=html_assets)
