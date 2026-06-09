from flask import Blueprint, redirect, url_for
from utils.helpers import login_required

ranking = Blueprint("ranking", __name__)    

@ranking.route('/ranking')
@login_required 
def show_ranking():
    # Redirigimos a la lista de torneos, porque el ranking ahora es por torneo
    return redirect(url_for('tournaments.list_tournaments'))