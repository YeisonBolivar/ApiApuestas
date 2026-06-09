# AGENTS.md – Torneo de Pronósticos de Fútbol (Guía para GitHub Copilot)

## Contexto general
Aplicación web Flask con SQLAlchemy y SQLite para gestionar un torneo de pronósticos. Los usuarios registrados predicen resultados de partidos. Cada pronóstico cuesta 1000 unidades virtuales (no reales) que se descuentan del balance del usuario. Los aciertos dan puntos y pueden repartir el pozo del partido. Existe un pozo global que se acumula cuando no hay aciertos exactos y se reparte al final del torneo entre los mejores del ranking.

## Objetivo para Copilot
Generar el código completo de la aplicación que cumpla:
- Principios POO (clases, encapsulamiento, atributos, métodos, herencia opcional).
- API REST propia (endpoints JSON).
- Persistencia con SQLite y SQLAlchemy (CRUD).
- Vistas con Jinja2 y Bootstrap.
- Autenticación por sesiones.
- Roles: usuario normal y administrador (is_admin).
- Reglas de negocio detalladas más abajo.

## Tecnologías
- Python 3.10+
- Flask
- Flask-SQLAlchemy
- Flask-Login (opcional, pero se usa sesión manual)
- Werkzeug (password hashing)
- SQLite
- Jinja2
- Bootstrap 5 (CDN)

## Estructura de archivos esperada (Crear desde cero o ampliar existente)

/app.py
/config.py
/models/
/entities/
init.py
User.py
Partido.py
Pronostico.py
GlobalPool.py
/routes/
init.py
auth.py
matches.py
admin.py
ranking.py
api.py
/templates/
base.html
auth/
login.html
register.html
dashboard.html
matches.html
ranking.html
admin/
matches.html
/utils/
db.py
helpers.py
/static/
css/
custom.css
/instance/
(database.db se crea automáticamente)


## Modelos de Datos (Clases Principales)

### User
Representa a un usuario del sistema. Atributos: id (entero, PK), username (cadena única), password (cadena con hash), is_admin (booleano), balance (entero), points (entero), total_won (entero), total_lost (entero). Métodos: constructor con username, password y is_admin opcional.

### Partido
Representa un partido de fútbol. Atributos: id (PK), equipo_local, equipo_visitante, fecha (datetime), resultado_local (entero, nulo hasta cerrar), resultado_visitante (entero), estado ('abierto' o 'cerrado'), prize_pool (entero, pozo acumulado del partido). Constructor recibe local, visitante y fecha.

### Pronostico
Representa la predicción de un usuario para un partido. Atributos: id (PK), partido_id (FK), user_id (FK), goles_local, goles_visitante, is_exact (booleano), points_awarded (entero), prize_awarded (entero). Constructor recibe partido_id, user_id, goles_local, goles_visitante.

### GlobalPool
Modelo singleton que guarda el pozo global del torneo. Atributos: id (siempre 1), amount (entero). Método de clase `get()` que obtiene o crea la única instancia.

## Reglas de Negocio (Lógica Principal)

### Registro de Usuario
Se recibe username y password. Se genera el hash de la contraseña con generate_password_hash. Se crea un nuevo User con balance=0, points=0, total_won=0, total_lost=0, is_admin=False. Se guarda en la base de datos.

### Inicio de Sesión
Se busca el usuario por username. Se verifica la contraseña con check_password_hash. Si es correcto, se guarda user_id y username en la sesión.

### Pronosticar un Partido
La ruta POST /predict/<partido_id> (o desde formulario en /matches) requiere usuario autenticado. Verifica que el partido esté en estado 'abierto' y que el usuario no haya pronosticado ya ese partido. Resta 1000 del balance del usuario (puede quedar negativo). Suma 1000 a total_lost del usuario. Suma 1000 al prize_pool del partido. Crea un nuevo Pronostico con los goles ingresados. Guarda todos los cambios.

### Cierre de Partido (solo administrador)
Ruta POST /admin/close-match/<id>. Requiere que el usuario tenga is_admin=True. Recibe los goles reales (local y visitante). Actualiza el partido con esos resultados y cambia estado a 'cerrado'. Obtiene todos los pronósticos de ese partido. Identifica los pronósticos exactos (coinciden goles local y visitante). Si hay al menos un acierto exacto: el premio individual = prize_pool dividido entre la cantidad de acertantes exactos. Para cada acertante exacto: suma el premio a su balance y a su total_won, suma 3 puntos a points, marca is_exact=True, points_awarded=3, prize_awarded=premio. Para los pronósticos no exactos: se evalúa si aciertan el ganador o empate (comparando el resultado real con la predicción). Si aciertan, suman 1 punto a points y se registra points_awarded=1. Si no hay aciertos exactos: se transfiere el prize_pool del partido al global_pool (usando GlobalPool.get().amount += prize_pool). Para todos los pronósticos: se evalúa acierto de ganador/empate y se otorga 1 punto a quienes acierten. Se guardan todos los cambios.

### Ranking
Ruta GET /ranking (pública para autenticados). Consulta todos los usuarios ordenados por points descendente y, en caso de empate, por balance descendente. Muestra en una tabla: username, puntos, balance, total ganado, total perdido.

### Finalización del Torneo (solo administrador)
Ruta POST /admin/finish-tournament. Requiere admin. Obtiene el monto del global_pool. Obtiene los 3 primeros del ranking (mismo orden que el ranking). Calcula la distribución del pozo global: si hay 1 usuario: 100% para él; si hay 2: 60% para el primero, 40% para el segundo; si hay 3 o más: 50% para el primero, 30% para el segundo, 20% para el tercero. Para cada beneficiario, suma el monto correspondiente a su balance y a su total_won. Pone el global_pool a 0. Guarda los cambios.

## API REST Propia (Endpoints JSON)
La aplicación expone una API con prefijo /api. Todos los endpoints devuelven JSON con formato {"status": "success", "data": ...} o {"status": "error", "message": ...}.

- GET /api/matches → Lista de partidos con id, local, visitante, fecha, estado, prize_pool, resultado_local, resultado_visitante (pueden ser nulos).
- GET /api/ranking → Lista de usuarios con username, points, balance, total_won, total_lost.
- GET /api/global-pool → Devuelve {"global_pool": monto}.
- POST /api/predict → Requiere autenticación por sesión. Recibe JSON: {"partido_id": 1, "goles_local": 2, "goles_visitante": 1}. Ejecuta la misma lógica que pronosticar y devuelve el nuevo balance del usuario.
- GET /api/user/me → Devuelve datos del usuario autenticado: username, balance, points, total_won, total_lost.

La autenticación para la API utiliza la misma sesión de Flask (cookie). Para acceder desde aplicaciones externas, se puede extender con tokens, pero no es requerido.

## Vistas Jinja2 (Interfaz Web)
Se implementan las siguientes plantillas heredando de base.html que incluye Bootstrap y una barra de navegación.

- auth/login.html: formulario con campos username, password, checkbox para mostrar contraseña.
- auth/register.html: similar para registro.
- dashboard.html: muestra balance actual, puntos totales, total ganado y perdido, y enlaces rápidos.
- matches.html: lista los partidos con estado 'abierto'. Para cada partido, muestra equipos, fecha, pozo actual, costo del pronóstico (1000). Incluye un formulario para ingresar goles local y visitante y un botón para pronosticar. Si el usuario ya pronosticó ese partido, se deshabilita el formulario.
- ranking.html: tabla con la lista de usuarios ordenada por puntos y balance.
- admin/matches.html: lista todos los partidos (abiertos y cerrados). Para los abiertos, muestra botón "Cerrar" que despliega un formulario para ingresar resultado real (local y visitante). También incluye un botón global "Finalizar Torneo" que ejecuta el reparto del pozo global.

## Principios de POO Aplicados
- Encapsulamiento: Los modelos definen atributos y métodos; el acceso a la base de datos se hace a través de la instancia de SQLAlchemy, ocultando detalles de conexión.
- Clases y objetos: Cada entidad es una clase que se instancia al crear registros.
- Atributos y métodos: Las clases tienen atributos de columna y métodos como __init__ y métodos de clase como GlobalPool.get().
- Herencia (opcional): Se puede crear una clase base Model con métodos comunes (ej. save, delete) si se desea, pero no es obligatorio. Se considera que el uso de db.Model de SQLAlchemy ya proporciona una herencia base.

## Persistencia de Datos (Base de Datos)
- Motor: SQLite, archivo database.db en la carpeta instance/.
- Las operaciones CRUD están cubiertas: Insert (registro de usuarios, creación de pronósticos, inserción de partidos por script o admin), Select (consulta de partidos, ranking, pronósticos, pozo global), Update (actualización de balances, puntos, pozos, estado de partidos, resultados reales), Delete (opcional: se podría implementar eliminación de partidos o pronósticos, pero no es crítico para el funcionamiento).

## Cómo Ejecutar el Proyecto
1. Clonar o descargar el código fuente.
2. Crear un entorno virtual: python -m venv venv
3. Activar el entorno: Windows: venv\Scripts\activate; Mac/Linux: source venv/bin/activate
4. Instalar dependencias: pip install flask flask-sqlalchemy werkzeug
5. Ejecutar la aplicación: python app.py
6. Abrir el navegador en http://127.0.0.1:5000
7. Para crear un usuario administrador, ejecutar un script o usar la consola de Python con el siguiente código: desde app import app, db; desde models.entities.User import User; desde werkzeug.security import generate_password_hash; con app.app_context(): si no User.query.filter_by(username='admin').first(): admin = User(username='admin', password=generate_password_hash('admin123'), is_admin=True); db.session.add(admin); db.session.commit()

## Credenciales de Administrador por Defecto
Usuario: admin, Contraseña: admin123

## Notas para el Desarrollador (y para Copilot)
- Utilizar from utils.db import db para acceder a la base de datos.
- Los decoradores @login_required y @admin_required se definen en utils/helpers.py y verifican la existencia de session['user_id'] y el flag is_admin respectivamente.
- Al crear la app en app.py, registrar todos los blueprints: auth, matches, admin, ranking, api.
- Configurar app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db' y app.config['SECRET_KEY'] desde config.py.
- Llamar a db.create_all() dentro de with app.app_context(): para crear las tablas automáticamente.
- Los partidos se pueden crear inicialmente mediante un script o desde la interfaz de administración (si se implementa un formulario de creación de partidos). Para simplificar, se pueden insertar manualmente usando SQL o la shell de Flask.

## Requisitos Académicos Cubiertos
- POO: Implementación de clases, objetos, atributos, métodos, encapsulamiento (a través de módulos y funciones de acceso).
- API propia: Endpoints REST en /api/* que devuelven JSON.
- Persistencia: SQLite con SQLAlchemy, operaciones CRUD completas.
- Framework: Flask.
- Documentación técnica: Este mismo archivo AGENTS.md explica el proyecto en detalle.