from flask import Flask, render_template
from routes.auth import auth
from routes.matches import matches
from routes.admin import admin
from routes.ranking import ranking
from routes.api import api
from routes.tournaments import tournaments_bp
from config import config
from utils.db import db
import logging

app = Flask(__name__)

# Configuración
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config.from_object(config['development'])

db.init_app(app)

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Registrar blueprints
app.register_blueprint(auth)
app.register_blueprint(matches)
app.register_blueprint(admin)
app.register_blueprint(ranking)
app.register_blueprint(api)
app.register_blueprint(tournaments_bp)

@app.context_processor
def inject_user():
    from models.entities.User import User
    from flask import session
    user = None
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
    return dict(current_user=user)

# Manejador de error 404
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

with app.app_context():
    db.create_all()
    logger.info("Base de datos creada/actualizada")

if __name__ == '__main__':
    app.run(debug=True)