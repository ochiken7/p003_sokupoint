from datetime import datetime
from extensions import db


class HomeBanner(db.Model):
    """ホーム上部のメインバナー。複数登録するとスライドショー表示される"""
    __tablename__ = 'home_banners'

    id = db.Column(db.Integer, primary_key=True)
    position = db.Column(db.Integer, nullable=False, default=0)
    file_path_pc = db.Column(db.Text, nullable=False)
    file_path_sp = db.Column(db.Text)
    alt_text = db.Column(db.Text)
    link_url = db.Column(db.Text)
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
