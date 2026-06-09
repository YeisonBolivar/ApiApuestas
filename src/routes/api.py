from flask import Blueprint, jsonify, request, session
from models.entities.Partido import Partido
from models.entities.Pronostico import Pronostico
from models.entities.User import User
from models.entities.Tournament import Tournament
from models.entities.TournamentStats import TournamentStats
from utils.db import db
from utils.helpers import login_required
from datetime import datetime

api = Blueprint("api", __name__, url_prefix="/api")

@api.route('/tournaments')
def get_tournaments():
    tournaments = Tournament.query.all()
    return jsonify([{
        'id': t.id,
        'name': t.name,
        'status': t.status,
        'global_pool': t.global_pool
    } for t in tournaments])

@api.route('/tournaments/<int:tid>/matches')
def get_tournament_matches(tid):
    partidos = Partido.query.filter_by(tournament_id=tid).all()
    return jsonify([{
        'id': p.id,
        'local': p.equipo_local,
        'visitante': p.equipo_visitante,
        'fecha': p.fecha.isoformat() if p.fecha else None,
        'estado': p.estado,
        'prize_pool': p.prize_pool,
        'resultado_local': p.resultado_local,
        'resultado_visitante': p.resultado_visitante
    } for p in partidos])

@api.route('/tournaments/<int:tid>/ranking')
def get_tournament_ranking(tid):
    stats = TournamentStats.query.filter_by(tournament_id=tid).join(User).order_by(TournamentStats.points.desc(), TournamentStats.balance.desc()).all()
    return jsonify([{
        'username': s.user.username,
        'points': s.points,
        'balance': s.balance,
        'total_won': s.total_won,
        'total_lost': s.total_lost,
        'exact_predictions': s.exact_predictions,
        'exact_earnings': s.exact_earnings,
        'correct_outcome_predictions': s.correct_outcome_predictions
    } for s in stats])

@api.route('/predict', methods=['POST'])
@login_required
def api_predict():
    data = request.get_json()
    if not data:
        return jsonify({'status': 'error', 'message': 'Se requiere JSON'}), 400
    partido_id = data.get('partido_id')
    goles_local = data.get('goles_local')
    goles_visitante = data.get('goles_visitante')
    if not partido_id or goles_local is None or goles_visitante is None:
        return jsonify({'status': 'error', 'message': 'Faltan campos requeridos'}), 400
    if goles_local < 0 or goles_visitante < 0:
        return jsonify({'status': 'error', 'message': 'Los goles no pueden ser negativos'}), 400
    
    user_id = session['user_id']
    partido = Partido.query.get(partido_id)
    if not partido or partido.estado != "abierto":
        return jsonify({'status': 'error', 'message': 'Partido no encontrado o cerrado'}), 400
    if partido.fecha < datetime.now():
        return jsonify({'status': 'error', 'message': 'No se puede pronosticar un partido ya comenzado'}), 400
    
    ya = Pronostico.query.filter_by(partido_id=partido_id, user_id=user_id).first()
    if ya:
        return jsonify({'status': 'error', 'message': 'Ya has pronosticado este partido'}), 400
    
    try:
        stats = TournamentStats.query.filter_by(user_id=user_id, tournament_id=partido.tournament_id).first()
        if not stats:
            stats = TournamentStats(user_id=user_id, tournament_id=partido.tournament_id)
            db.session.add(stats)
        
        stats.balance -= 1000
        stats.total_lost += 1000
        partido.prize_pool += 1000
        pronostico = Pronostico(partido_id=partido_id, user_id=user_id, goles_local=goles_local, goles_visitante=goles_visitante)
        db.session.add(pronostico)
        db.session.commit()
        return jsonify({'status': 'success', 'message': 'Pronóstico creado', 'new_balance': stats.balance})
    except Exception as e:
        db.session.rollback()
        return jsonify({'status': 'error', 'message': f'Error interno: {str(e)}'}), 500

@api.route('/user/me')
@login_required
def user_me():
    user = User.query.get(session['user_id'])
    return jsonify({
        'username': user.username,
        'is_admin': user.is_admin
    })