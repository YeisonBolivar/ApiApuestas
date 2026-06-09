from flask import Blueprint, render_template, session, redirect, url_for, flash, abort, request
from models.entities.Tournament import Tournament
from models.entities.TournamentStats import TournamentStats
from models.entities.Partido import Partido
from models.entities.Pronostico import Pronostico
from models.entities.User import User
from utils.db import db
from utils.helpers import login_required

tournaments_bp = Blueprint('tournaments', __name__, url_prefix='/tournaments')

@tournaments_bp.route('/')
def list_tournaments():
    status_filter = request.args.get('status', 'all')
    query = Tournament.query
    if status_filter == 'active':
        query = query.filter_by(status='active')
    elif status_filter == 'finished':
        query = query.filter_by(status='finished')
    tournaments = query.all()
    return render_template('tournaments/list.html', tournaments=tournaments, current_filter=status_filter)

@tournaments_bp.route('/<int:id>')
@login_required
def view_tournament(id):
    tournament = Tournament.query.get_or_404(id)
    return render_template('tournaments/detail.html', tournament=tournament)

@tournaments_bp.route('/<int:id>/matches')
@login_required
def matches(id):
    tournament = Tournament.query.get_or_404(id)
    user_id = session['user_id']
    # Mostramos todos los partidos del torneo (abiertos y cerrados)
    partidos = Partido.query.filter_by(tournament_id=id).all()
    # Obtener pronósticos del usuario para este torneo (para mostrar detalle)
    pronosticos_usuario = {}
    pronosticos = Pronostico.query.join(Partido).filter(
        Pronostico.user_id == user_id,
        Partido.tournament_id == id
    ).all()
    for p in pronosticos:
        pronosticos_usuario[p.partido_id] = p
    # IDs de partidos ya pronosticados (para saber si puede pronosticar)
    pronosticados_ids = list(pronosticos_usuario.keys())
    return render_template('tournaments/matches.html', 
                           tournament=tournament, 
                           partidos=partidos, 
                           pronosticados=pronosticados_ids,
                           pronosticos_usuario=pronosticos_usuario)

@tournaments_bp.route('/<int:id>/ranking')
@login_required
def ranking(id):
    tournament = Tournament.query.get_or_404(id)
    stats = TournamentStats.query.filter_by(tournament_id=id).join(User).order_by(
        TournamentStats.points.desc(), TournamentStats.balance.desc()
    ).all()
    return render_template('tournaments/ranking.html', tournament=tournament, stats=stats)


@tournaments_bp.route('/my_predictions')
@login_required
def my_predictions():
    user_id = session['user_id']
    # Obtener todos los pronósticos del usuario con información del partido y torneo
    predictions = db.session.query(
        Pronostico, Partido, Tournament
    ).join(
        Partido, Pronostico.partido_id == Partido.id
    ).join(
        Tournament, Partido.tournament_id == Tournament.id
    ).filter(
        Pronostico.user_id == user_id
    ).order_by(
        Partido.fecha.desc()
    ).all()
    
    return render_template('tournaments/my_predictions.html', predictions=predictions)