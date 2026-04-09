from datetime import datetime
from extensions import db


class LoginBonusLog(db.Model):
    __tablename__ = 'login_bonus_logs'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    received_date = db.Column(db.Date, nullable=False)
    points_awarded = db.Column(db.Integer, nullable=False)
    consecutive_day = db.Column(db.Integer, nullable=False)

    __table_args__ = (
        db.UniqueConstraint('user_id', 'received_date', name='uq_login_bonus_user_date'),
    )

    user = db.relationship('User', backref='login_bonus_logs')
