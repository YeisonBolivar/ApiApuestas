from utils.db import db

class Pronostico(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    partido_id = db.Column(db.Integer, db.ForeignKey('partido.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    goles_local = db.Column(db.Integer, nullable=False)
    goles_visitante = db.Column(db.Integer, nullable=False)
    is_exacto = db.Column(db.Boolean, default=False)
    points_awarded = db.Column(db.Integer, default=0)
    prize_awarded = db.Column(db.Float, default=0.0)

    def __init__(self, partido_id, user_id, goles_local, goles_visitante):
        self.partido_id = partido_id
        self.user_id = user_id
        self.goles_local = goles_local
        self.goles_visitante = goles_visitante

    __table_args__ = (
        db.Index('idx_pronostico_partido_user', 'partido_id', 'user_id', unique=False),
        db.Index('idx_pronostico_user', 'user_id'),
    )