from datetime import datetime
from extensions import db


class Coupon(db.Model):
    __tablename__ = 'coupons'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.Text, nullable=False)
    description = db.Column(db.Text)
    required_rank = db.Column(db.Text)
    entry_start = db.Column(db.DateTime)
    entry_end = db.Column(db.DateTime)
    winner_count = db.Column(db.Integer, nullable=False, default=1)
    image_path = db.Column(db.Text)
    is_active = db.Column(db.Boolean, nullable=False, default=True)

    entries = db.relationship('CouponEntry', backref='coupon', lazy='dynamic', cascade='all, delete-orphan')


class CouponEntry(db.Model):
    __tablename__ = 'coupon_entries'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    coupon_id = db.Column(db.Integer, db.ForeignKey('coupons.id'), nullable=False)
    entered_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    is_winner = db.Column(db.Boolean, nullable=False, default=False)

    user = db.relationship('User', backref='coupon_entries')
