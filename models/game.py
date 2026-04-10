from datetime import datetime
from extensions import db


class Game(db.Model):
    __tablename__ = 'games'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False)
    game_type = db.Column(db.Text, nullable=False)  # scratch / roulette / quiz
    description = db.Column(db.Text)
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    priority = db.Column(db.Integer, nullable=False, default=0)
    config_json = db.Column(db.Text)
    thumbnail_path = db.Column(db.Text)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    questions = db.relationship('QuizQuestion', backref='game', lazy='dynamic', cascade='all, delete-orphan')
    outcomes = db.relationship('GameOutcome', backref='game', lazy='dynamic',
                               cascade='all, delete-orphan',
                               order_by='GameOutcome.position')


class GameOutcome(db.Model):
    """ゲームの抽選結果（6通り固定）"""
    __tablename__ = 'game_outcomes'

    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.Integer, db.ForeignKey('games.id'), nullable=False)
    position = db.Column(db.Integer, nullable=False)  # 1-6
    label = db.Column(db.Text, nullable=False, default='結果')
    points = db.Column(db.Integer, nullable=False, default=0)
    weight = db.Column(db.Float, nullable=False, default=1.0)  # 当選確率の重み
    color = db.Column(db.Text, nullable=False, default='#E63946')

    __table_args__ = (
        db.UniqueConstraint('game_id', 'position', name='uq_game_outcome_position'),
    )


class QuizQuestion(db.Model):
    __tablename__ = 'quiz_questions'

    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.Integer, db.ForeignKey('games.id'), nullable=False)
    question_text = db.Column(db.Text, nullable=False)
    image_path = db.Column(db.Text)
    choice_1 = db.Column(db.Text, nullable=False)
    choice_2 = db.Column(db.Text, nullable=False)
    choice_3 = db.Column(db.Text, nullable=False)
    choice_4 = db.Column(db.Text, nullable=False)
    correct_choice = db.Column(db.Integer, nullable=False)  # 1-4
    explanation = db.Column(db.Text)


class GamePlayLog(db.Model):
    __tablename__ = 'game_play_logs'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    game_id = db.Column(db.Integer, db.ForeignKey('games.id'), nullable=False)
    played_date = db.Column(db.Date, nullable=False)
    outcome_position = db.Column(db.Integer)  # 1-6 (旧データは null)
    result_label = db.Column(db.Text)  # 表示用の結果名
    points_awarded = db.Column(db.Integer, nullable=False)
    played_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint('user_id', 'game_id', 'played_date', name='uq_game_play_user_game_date'),
    )

    user = db.relationship('User', backref='game_play_logs')
    game = db.relationship('Game', backref='play_logs')
