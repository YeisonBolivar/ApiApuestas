from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models.entities.Partido import Partido
from models.entities.Pronostico import Pronostico
from models.entities.Tournament import Tournament
from models.entities.TournamentStats import TournamentStats
from models.entities.User import User
from utils.db import db
from utils.helpers import admin_required
from datetime import datetime
import logging

admin = Blueprint("admin", __name__)
logger = logging.getLogger(__name__)

# ====================== Gestión de Torneos ======================
@admin.route('/admin/tournaments')
@admin_required
def admin_tournaments():
    tournaments = Tournament.query.all()
    return render_template('admin/tournaments.html', tournaments=tournaments)

@admin.route('/admin/tournament/create', methods=['GET', 'POST'])
@admin_required
def create_tournament():
    if request.method == 'POST':
        name = request.form['name']
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')
        tournament = Tournament(name=name)
        if start_date:
            tournament.start_date = datetime.strptime(start_date, '%Y-%m-%d')
        if end_date:
            tournament.end_date = datetime.strptime(end_date, '%Y-%m-%d')
        db.session.add(tournament)
        db.session.commit()
        flash('Torneo creado exitosamente.', 'success')
        logger.info(f"Torneo creado: {name} por admin {session['username']}")
        return redirect(url_for('admin.admin_tournaments'))
    return render_template('admin/create_tournament.html')

@admin.route('/admin/tournament/<int:id>/matches')
@admin_required
def admin_tournament_matches(id):
    tournament = Tournament.query.get_or_404(id)
    partidos = Partido.query.filter_by(tournament_id=id).all()
    return render_template('admin/tournament_matches.html', tournament=tournament, partidos=partidos)

# ====================== Crear partido ======================
@admin.route('/admin/tournament/<int:id>/match/create', methods=['GET', 'POST'])
@admin_required
def create_match(id):
    tournament = Tournament.query.get_or_404(id)
    if tournament.status == 'finished':
        flash('No se pueden agregar partidos a un torneo finalizado.', 'danger')
        return redirect(url_for('admin.admin_tournament_matches', id=tournament.id))
    
    if request.method == 'POST':
        local = request.form.get('equipo_local')
        visitante = request.form.get('equipo_visitante')
        fecha_str = request.form.get('fecha')
        if not local or not visitante or not fecha_str:
            flash('Todos los campos son obligatorios', 'danger')
            return redirect(url_for('admin.create_match', id=tournament.id))
        
        try:
            fecha = datetime.strptime(fecha_str, '%Y-%m-%dT%H:%M')
        except ValueError:
            flash('Formato de fecha inválido. Use YYYY-MM-DD HH:MM', 'danger')
            return redirect(url_for('admin.create_match', id=tournament.id))
        
        # Validar que la fecha no sea en el pasado (si el torneo ya empezó, podría permitirse, pero mejor avisar)
        if fecha < datetime.now():
            flash('La fecha del partido no puede ser en el pasado.', 'danger')
            return redirect(url_for('admin.create_match', id=tournament.id))
        
        nuevo_partido = Partido(local, visitante, fecha, tournament.id)
        db.session.add(nuevo_partido)
        db.session.commit()
        flash(f'Partido {local} vs {visitante} creado exitosamente.', 'success')
        logger.info(f"Partido creado: {local} vs {visitante} en torneo {tournament.name}")
        return redirect(url_for('admin.admin_tournament_matches', id=tournament.id))
    
    return render_template('admin/create_match.html', tournament=tournament)

# ====================== Cerrar un partido ======================
@admin.route('/admin/close_match/<int:id>', methods=['POST'])
@admin_required
def close_match(id):
    partido = Partido.query.get_or_404(id)
    if partido.estado != "abierto":
        flash("El partido ya está cerrado.", "warning")
        return redirect(url_for('admin.admin_tournament_matches', id=partido.tournament_id))
    
    if partido.tournament.status == 'finished':
        flash("No se puede cerrar un partido de un torneo finalizado.", "danger")
        return redirect(url_for('admin.admin_tournament_matches', id=partido.tournament_id))
    
    real_local = request.form.get('real_local', type=int)
    real_visitante = request.form.get('real_visitante', type=int)
    if real_local is None or real_visitante is None or real_local < 0 or real_visitante < 0:
        flash("Por favor, ingresa números válidos de goles (0 o más).", "danger")
        return redirect(url_for('admin.admin_tournament_matches', id=partido.tournament_id))
    
    try:
        partido.resultado_local = real_local
        partido.resultado_visitante = real_visitante
        partido.estado = "cerrado"
        
        pronosticos = Pronostico.query.filter_by(partido_id=id).all()
        exactos = [p for p in pronosticos if p.goles_local == real_local and p.goles_visitante == real_visitante]
        tournament = partido.tournament
        
        if exactos:
            premio_individual = partido.prize_pool / len(exactos)
            for p in exactos:
                stats = TournamentStats.query.filter_by(user_id=p.user_id, tournament_id=tournament.id).first()
                if not stats:
                    stats = TournamentStats(user_id=p.user_id, tournament_id=tournament.id)
                    db.session.add(stats)
                stats.balance += premio_individual
                stats.total_won += premio_individual
                stats.points += 3
                stats.exact_predictions += 1
                stats.exact_earnings += premio_individual
                p.is_exacto = True
                p.points_awarded = 3
                p.prize_awarded = premio_individual
                
                user = User.query.get(p.user_id)
                user.balance += premio_individual
                user.total_won += premio_individual
                user.points += 3
                db.session.add(user)
            
            # Puntos por resultado (no exactos)
            for p in pronosticos:
                if p in exactos:
                    continue
                if p.goles_local > p.goles_visitante:
                    resultado_pronosticado = "local"
                elif p.goles_local < p.goles_visitante:
                    resultado_pronosticado = "visitante"
                else:
                    resultado_pronosticado = "empate"
                
                if real_local > real_visitante:
                    resultado_real = "local"
                elif real_local < real_visitante:
                    resultado_real = "visitante"
                else:
                    resultado_real = "empate"
                
                if resultado_pronosticado == resultado_real:
                    stats = TournamentStats.query.filter_by(user_id=p.user_id, tournament_id=tournament.id).first()
                    if not stats:
                        stats = TournamentStats(user_id=p.user_id, tournament_id=tournament.id)
                        db.session.add(stats)
                    stats.points += 1
                    stats.correct_outcome_predictions += 1
                    p.points_awarded = 1
                    
                    user = User.query.get(p.user_id)
                    user.points += 1
                    db.session.add(user)
        else:
            tournament.global_pool += partido.prize_pool
            for p in pronosticos:
                if p.goles_local > p.goles_visitante:
                    resultado_pronosticado = "local"
                elif p.goles_local < p.goles_visitante:
                    resultado_pronosticado = "visitante"
                else:
                    resultado_pronosticado = "empate"
                if real_local > real_visitante:
                    resultado_real = "local"
                elif real_local < real_visitante:
                    resultado_real = "visitante"
                else:
                    resultado_real = "empate"
                if resultado_pronosticado == resultado_real:
                    stats = TournamentStats.query.filter_by(user_id=p.user_id, tournament_id=tournament.id).first()
                    if not stats:
                        stats = TournamentStats(user_id=p.user_id, tournament_id=tournament.id)
                        db.session.add(stats)
                    stats.points += 1
                    stats.correct_outcome_predictions += 1
                    p.points_awarded = 1
                    
                    user = User.query.get(p.user_id)
                    user.points += 1
                    db.session.add(user)
        
        db.session.commit()
        flash(f"Partido cerrado. Aciertos exactos: {len(exactos)}.", "success")
        logger.info(f"Partido {partido.id} cerrado. Resultado {real_local}-{real_visitante}")
    except Exception as e:
        db.session.rollback()
        flash(f"Error al cerrar el partido: {str(e)}", "danger")
        logger.error(f"Error cerrando partido {partido.id}: {e}")
    
    return redirect(url_for('admin.admin_tournament_matches', id=partido.tournament_id))

# ====================== Cerrar torneo completo ======================
@admin.route('/admin/tournament/<int:id>/close', methods=['POST'])
@admin_required
def close_tournament(id):
    tournament = Tournament.query.get_or_404(id)
    if tournament.status == 'finished':
        flash("El torneo ya está finalizado.", "warning")
        return redirect(url_for('admin.admin_tournaments'))
    
    abiertos = Partido.query.filter_by(tournament_id=id, estado='abierto').count()
    if abiertos > 0:
        flash(f"No puedes cerrar el torneo porque hay {abiertos} partidos abiertos. Ciérralos primero.", "danger")
        return redirect(url_for('admin.admin_tournament_matches', id=id))
    
    try:
        stats_top = TournamentStats.query.filter_by(tournament_id=id).order_by(TournamentStats.points.desc(), TournamentStats.balance.desc()).limit(3).all()
        total = tournament.global_pool
        n = len(stats_top)
        if n == 1:
            shares = [1.0]
        elif n == 2:
            shares = [0.6, 0.4]
        else:
            shares = [0.5, 0.3, 0.2]
        
        for i, stats in enumerate(stats_top):
            if i >= len(shares):
                break
            prize = total * shares[i]
            stats.balance += prize
            stats.total_won += prize
            db.session.add(stats)
            
            user = User.query.get(stats.user_id)
            user.balance += prize
            user.total_won += prize
            db.session.add(user)
            flash(f"{stats.user.username} recibió {prize} del pozo global del torneo.", "success")
        
        tournament.global_pool = 0
        tournament.status = 'finished'
        tournament.end_date = datetime.now()
        db.session.commit()
        flash("Torneo finalizado. Ranking disponible.", "success")
        logger.info(f"Torneo {tournament.name} finalizado por admin {session['username']}")
    except Exception as e:
        db.session.rollback()
        flash(f"Error al finalizar el torneo: {str(e)}", "danger")
        logger.error(f"Error cerrando torneo {id}: {e}")
    
    return redirect(url_for('tournaments.ranking', id=id))