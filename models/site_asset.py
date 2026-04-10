from datetime import datetime
from extensions import db


class SiteAsset(db.Model):
    __tablename__ = 'site_assets'

    id = db.Column(db.Integer, primary_key=True)
    slot_key = db.Column(db.Text, unique=True, nullable=False)
    file_path = db.Column(db.Text)
    alt_text = db.Column(db.Text)
    link_url = db.Column(db.Text)
    content_html = db.Column(db.Text)  # カスタムHTMLコンテンツ
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
