from datetime import datetime
from extensions import db


class Rank(db.Model):
    __tablename__ = 'ranks'

    code = db.Column(db.Text, primary_key=True)
    name = db.Column(db.Text, nullable=False)
    min_lifetime_points = db.Column(db.Integer, nullable=False, default=0)
    color = db.Column(db.Text, nullable=False)
    bonus_multiplier = db.Column(db.Float, nullable=False, default=1.0)


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    nickname = db.Column(db.Text, nullable=False)
    rank_code = db.Column(db.Text, db.ForeignKey('ranks.code'), nullable=False, default='BRONZE')
    total_points = db.Column(db.Integer, nullable=False, default=0)
    lifetime_points = db.Column(db.Integer, nullable=False, default=0)
    consecutive_login_days = db.Column(db.Integer, nullable=False, default=0)
    last_login_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    rank = db.relationship('Rank', backref='users', lazy='joined')
