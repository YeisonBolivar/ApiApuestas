from utils.db import db

class Partido(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    equipo_local = db.Column(db.String(100))
    equipo_visitante = db.Column(db.String(100))
    fecha = db.Column(db.DateTime)
    resultado_local = db.Column(db.Integer, default=0)
    resultado_visitante = db.Column(db.Integer, default=0)
    estado = db.Column(db.String(20), default='abierto') 
    prize_pool = db.Column(db.Float, default=0.0)
    tournament_id = db.Column(db.Integer, db.ForeignKey('tournament.id'), nullable=False)

    def __init__(self, equipo_local, equipo_visitante, fecha, tournament_id):
        self.equipo_local = equipo_local
        self.equipo_visitante = equipo_visitante
        self.fecha = fecha
        self.tournament_id = tournament_id

    __table_args__ = (
        db.Index('idx_partido_tournament_estado', 'tournament_id', 'estado'),
        db.Index('idx_partido_fecha', 'fecha'),
    )