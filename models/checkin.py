from datetime import datetime
from extensions import db


class Store(db.Model):
    __tablename__ = 'stores'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False)
    area = db.Column(db.Text)
    qr_token = db.Column(db.Text)
    is_active = db.Column(db.Boolean, nullable=False, default=True)


class Checkin(db.Model):
    __tablename__ = 'checkins'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    store_id = db.Column(db.Integer, db.ForeignKey('stores.id'), nullable=False)
    checked_in_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    points_awarded = db.Column(db.Integer, nullable=False, default=300)

    user = db.relationship('User', backref='checkins')
    store = db.relationship('Store', backref='checkins')
