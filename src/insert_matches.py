from app import app, db
from models.entities.Tournament import Tournament
from models.entities.Partido import Partido
from datetime import datetime

with app.app_context():
    # Crear torneo por defecto si no existe
    default_tournament = Tournament.query.filter_by(name="Torneo Inaugural").first()
    if not default_tournament:
        default_tournament = Tournament(name="Torneo Inaugural", start_date=datetime.now())
        db.session.add(default_tournament)
        db.session.commit()
        print("Torneo por defecto creado.")
    else:
        print("Torneo por defecto ya existe.")
    
    # Insertar partidos de ejemplo si no existen
    partidos_data = [
        ("Real Madrid", "Barcelona", datetime(2026, 6, 15, 20, 0)),
        ("Atlético Madrid", "Sevilla", datetime(2026, 6, 16, 18, 0)),
        ("Bayern Munich", "Borussia Dortmund", datetime(2026, 6, 17, 20, 0)),
        ("Manchester City", "Liverpool", datetime(2026, 6, 18, 21, 0)),
        ("PSG", "Marseille", datetime(2026, 6, 19, 20, 30)),
    ]
    for local, visitante, fecha in partidos_data:
        exists = Partido.query.filter_by(equipo_local=local, equipo_visitante=visitante, tournament_id=default_tournament.id).first()
        if not exists:
            p = Partido(local, visitante, fecha, default_tournament.id)
            db.session.add(p)
    db.session.commit()
    print("Datos iniciales insertados.")