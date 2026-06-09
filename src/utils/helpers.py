from functools import wraps
from flask import session, redirect, url_for, flash
from models.entities.User import User

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Por favor, inicia sesión para acceder a esta página.', 'warning')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash("Debes iniciar sesión primero", "warning")
            return redirect(url_for('auth.login'))
        user = User.query.get(session['user_id'])
        if not user or not user.is_admin:
            flash("No tienes permisos para acceder a esta página", "danger")
            return redirect(url_for('auth.index'))  # antes redirigía a main.index
        return f(*args, **kwargs)
    return decorated_function