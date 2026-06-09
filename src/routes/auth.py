from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models.entities.User import User
from utils.db import db 
from werkzeug.security import generate_password_hash, check_password_hash


auth = Blueprint("auth", __name__)

@auth.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    user = User.query.get(session['user_id'])
    return render_template('dashboard.html', username=session['username'], user=user)

@auth.route('/login', methods = ['GET','POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            
            print("Login correcto")
            session['user_id'] = user.id
            session['username'] = user.username
            return redirect(url_for("auth.index"))
        else:
            flash("Credenciales incorrectas")
            return render_template("auth/login.html", error= "Usuario o contraseña incorrectos")

    return render_template('auth/login.html')
    
@auth.route('/register', methods = ['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        # Verificar si el usuario ya existe
        if User.query.filter_by(username=username).first():
            flash("El nombre de usuario ya existe")
            return redirect(url_for('auth.register'))
        hashed_password = generate_password_hash(password)
        new_user = User(username=username, password = hashed_password)
        db.session.add(new_user)
        db.session.commit()
        flash("Registro exitoso, por favor inicia sesión")
        return redirect(url_for('auth.login'))
    else:
        return render_template('auth/register.html')

@auth.route('/logout')
def logout():
    session.clear()
    flash("Has cerrado sesión exitosamente")
    return redirect(url_for('auth.login'))