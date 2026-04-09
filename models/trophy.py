from datetime import datetime
from extensions import db


class Trophy(db.Model):
    __tablename__ = 'trophies'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.Text, unique=True, nullable=False)
    name = db.Column(db.Text, nullable=False)
    description = db.Column(db.Text)
    icon_name = db.Column(db.Text, nullable=False, default='trophy')
    condition_type = db.Column(db.Text, nullable=False)
    condition_value = db.Column(db.Integer, nullable=False)
    points_reward = db.Column(db.Integer, nullable=False, default=0)
    is_active = db.Column(db.Boolean, nullable=False, default=True)


class UserTrophy(db.Model):
    __tablename__ = 'user_trophies'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    trophy_id = db.Column(db.Integer, db.ForeignKey('trophies.id'), nullable=False)
    unlocked_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    user = db.relationship('User', backref='user_trophies')
    trophy = db.relationship('Trophy', backref='user_trophies')
