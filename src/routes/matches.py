from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models.entities.Partido import Partido
from models.entities.Pronostico import Pronostico
from models.entities.TournamentStats import TournamentStats
from utils.db import db 
from utils.helpers import login_required
from datetime import datetime

matches = Blueprint("matches", __name__)

@matches.route('/matches')
@login_required
def matches_view():
    return redirect(url_for('tournaments.list_tournaments'))

@matches.route('/predict/<int:partido_id>', methods=['POST'])
@login_required
def predict(partido_id):
    user_id = session['user_id']
    partido = Partido.query.get_or_404(partido_id)

    # Validaciones
    if partido.estado != "abierto":
        flash("Este partido ya no acepta pronósticos.", "danger")
        return redirect(url_for('tournaments.matches', id=partido.tournament_id))
    
    if partido.fecha < datetime.now():
        flash("No puedes pronosticar un partido que ya ha comenzado o ha terminado.", "danger")
        return redirect(url_for('tournaments.matches', id=partido.tournament_id))
    
    ya_pronosticado = Pronostico.query.filter_by(user_id=user_id, partido_id=partido_id).first()
    if ya_pronosticado:
        flash("Ya has pronosticado este partido.", "warning")
        return redirect(url_for('tournaments.matches', id=partido.tournament_id))
    
    goles_local = request.form.get('goles_local', type=int)
    goles_visitante = request.form.get('goles_visitante', type=int)
    if goles_local is None or goles_visitante is None or goles_local < 0 or goles_visitante < 0:
        flash("Por favor, ingresa números válidos de goles (0 o más).", "danger")
        return redirect(url_for('tournaments.matches', id=partido.tournament_id))
    
    try:
        # Obtener o crear TournamentStats para este usuario y torneo
        stats = TournamentStats.query.filter_by(user_id=user_id, tournament_id=partido.tournament_id).first()
        if not stats:
            stats = TournamentStats(user_id=user_id, tournament_id=partido.tournament_id)
            db.session.add(stats)
        
        # Restar 1000 del balance del torneo
        stats.balance -= 1000
        stats.total_lost += 1000
        partido.prize_pool += 1000
        
        pronostico = Pronostico(partido_id=partido_id, user_id=user_id, goles_local=goles_local, goles_visitante=goles_visitante)
        db.session.add(pronostico)
        db.session.commit()
        flash(f"Pronóstico registrado (costo 1000). Balance en el torneo: {stats.balance}", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error al registrar el pronóstico: {str(e)}", "danger")
        print(f"Error en predict: {e}")
    
    return redirect(url_for('tournaments.matches', id=partido.tournament_id))