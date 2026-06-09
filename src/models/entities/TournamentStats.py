from models.entities.User import User
from utils.db import db

class TournamentStats(db.Model):
    __tablename__ = 'tournament_stats'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    tournament_id = db.Column(db.Integer, db.ForeignKey('tournament.id'), nullable=False)
    points = db.Column(db.Integer, default=0)
    balance = db.Column(db.Integer, default=0)
    total_won = db.Column(db.Float, default=0)
    total_lost = db.Column(db.Float, default=0)
    exact_predictions = db.Column(db.Integer, default=0)
    exact_earnings = db.Column(db.Float, default=0.0)
    correct_outcome_predictions = db.Column(db.Integer, default=0)

    user = db.relationship('User', backref='tournament_stats')

    __table_args__ = (db.UniqueConstraint('user_id', 'tournament_id', name='_user_tournament_uc'),)

    def __init__(self, user_id, tournament_id):
        self.user_id = user_id
        self.tournament_id = tournament_id
        self.points = 0
        self.balance = 0
        self.total_won = 0.0
        self.total_lost = 0.0
        self.exact_predictions = 0
        self.exact_earnings = 0.0
        self.correct_outcome_predictions = 0