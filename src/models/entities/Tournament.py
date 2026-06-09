from utils.db import db


class Tournament(db.Model):
    __tablename__ = 'tournament'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    start_date = db.Column(db.DateTime, nullable=True)
    end_date = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.String(50), default='active')
    global_pool = db.Column(db.Float, default=0.0)

    # Relacion con partidos

    matches = db.relationship('Partido', backref='tournament', lazy=True)

    def __init__(self, name, start_date=None, end_date=None, status='active'):
        self.name = name
        self.start_date = start_date
        self.end_date = end_date
        self.status = status