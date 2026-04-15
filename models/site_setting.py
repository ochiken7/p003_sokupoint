from datetime import datetime
from extensions import db


class SiteSetting(db.Model):
    """サイト全体の設定値 (key/value)"""
    __tablename__ = 'site_settings'

    key = db.Column(db.Text, primary_key=True)
    value = db.Column(db.Text)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
