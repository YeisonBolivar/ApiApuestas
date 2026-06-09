# Torneo Pronósticos - Sistema Web de Pronósticos Deportivos

##  Descripción del Proyecto

**Torneo Pronósticos** es una aplicación web desarrollada para la gestión de torneos de fútbol basados en pronósticos deportivos. Los usuarios pueden predecir los resultados de los partidos, acumular puntos según su precisión y competir por premios dentro de cada torneo.

El sistema incluye un panel de administración para gestionar torneos, partidos, resultados oficiales y distribución de premios, además de una API REST propia para el acceso a la información del sistema.

---

#  Objetivos del Proyecto

### Objetivo General

Desarrollar una plataforma web que permita a los usuarios participar en torneos de pronósticos deportivos mediante un sistema de puntuación y recompensas.

### Objetivos Específicos

* Gestionar usuarios con diferentes roles (Administrador y Usuario).
* Permitir la creación y administración de torneos deportivos.
* Registrar partidos y resultados oficiales.
* Gestionar pronósticos realizados por los participantes.
* Calcular automáticamente puntuaciones y premios.
* Mantener rankings actualizados en tiempo real.
* Proporcionar una API REST para consultas externas.

---

#  Tecnologías Utilizadas

| Tecnología       | Uso                      |
| ---------------- | ------------------------ |
| Python 3.11+     | Lenguaje principal       |
| Flask            | Framework Backend        |
| Flask-SQLAlchemy | ORM para acceso a datos  |
| SQLite           | Base de datos            |
| HTML5            | Estructura de interfaz   |
| Bootstrap 5      | Diseño responsive        |
| CSS3             | Personalización visual   |
| FontAwesome      | Iconografía              |
| Git              | Control de versiones     |
| GitHub           | Repositorio del proyecto |

---

#  Arquitectura del Sistema

El proyecto sigue una arquitectura modular basada en Flask Blueprints para separar responsabilidades y facilitar el mantenimiento.

```text
├── app.py
├── config.py
├── requirements.txt
├── static/
│   └── css/
│       └── custom.css
├── templates/
│   ├── base.html
│   ├── dashboard.html
│   ├── 404.html
│   ├── auth/
│   ├── admin/
│   ├── tournaments/
│   └── partials/
├── models/
│   └── entities/
│       ├── User.py
│       ├── Tournament.py
│       ├── Partido.py
│       ├── Pronostico.py
│       └── TournamentStats.py
├── routes/
│   ├── auth.py
│   ├── admin.py
│   ├── tournaments.py
│   ├── matches.py
│   ├── ranking.py
│   └── api.py
└── utils/
    ├── db.py
    └── helpers.py
```

---

#  Programación Orientada a Objetos (POO)

El sistema implementa los principios fundamentales de Programación Orientada a Objetos mediante entidades que representan los elementos principales del negocio.

## Clase User

Representa a los usuarios registrados en la plataforma.

**Atributos principales:**

* id
* username
* password
* is_admin
* balance
* points
* total_won
* total_lost

**Relaciones:**

* Un usuario puede tener múltiples pronósticos.
* Un usuario puede participar en múltiples torneos.

---

## Clase Tournament

Representa un torneo activo dentro del sistema.

**Atributos principales:**

* id
* name
* start_date
* end_date
* status
* global_pool

**Relaciones:**

* Un torneo contiene múltiples partidos.

---

## Clase Partido

Representa un encuentro deportivo perteneciente a un torneo.

**Atributos principales:**

* id
* equipo_local
* equipo_visitante
* fecha
* resultado_local
* resultado_visitante
* estado
* prize_pool
* tournament_id

**Relaciones:**

* Pertenece a un torneo.
* Puede contener múltiples pronósticos.

---

## Clase Pronostico

Representa la predicción realizada por un usuario.

**Atributos principales:**

* id
* partido_id
* user_id
* goles_local
* goles_visitante
* is_exacto
* points_awarded
* prize_awarded

**Relaciones:**

* Pertenece a un usuario.
* Pertenece a un partido.

---

## Clase TournamentStats

Almacena estadísticas individuales de cada usuario por torneo.

**Atributos principales:**

* points
* balance
* total_won
* total_lost
* exact_predictions
* exact_earnings
* correct_outcome_predictions

---

## Evidencia de POO

### Encapsulamiento

Cada entidad contiene sus propios atributos y comportamientos, permitiendo una gestión organizada de la información.

### Abstracción

Las clases modelan elementos reales del sistema como usuarios, torneos, partidos y pronósticos.

### Modularidad

La lógica se encuentra separada mediante Blueprints y modelos independientes, facilitando la escalabilidad y el mantenimiento.

---

#  Base de Datos

## Motor Utilizado

* SQLite
* Archivo generado: `database.db`

## ORM

* Flask-SQLAlchemy

## Operaciones CRUD Implementadas

### Create

* Registro de usuarios.
* Creación de torneos.
* Registro de partidos.
* Creación de pronósticos.

### Read

* Consulta de torneos.
* Consulta de partidos.
* Ranking de participantes.
* Historial de pronósticos.

### Update

* Registro de resultados oficiales.
* Actualización de puntuaciones.
* Repartición de premios.
* Finalización de torneos.

---

#  Instalación y Ejecución

## 1. Clonar el repositorio

```bash
git clone https://github.com/tu-usuario/torneo-pronosticos.git
cd torneo-pronosticos
```

## 2. Crear entorno virtual

### Linux / macOS

```bash
python -m venv venv
source venv/bin/activate
```

### Windows

```bash
python -m venv venv
venv\Scripts\activate
```

## 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

Si no existe el archivo:

```bash
pip install flask flask-sqlalchemy werkzeug
```

## 4. Inicializar la base de datos

```python
from app import app, db

with app.app_context():
    db.create_all()
```

## 5. Crear administrador (Opcional)

```python
from app import app, db
from models.entities.User import User
from werkzeug.security import generate_password_hash

with app.app_context():
    admin = User(
        username='admin',
        password=generate_password_hash('admin123'),
        is_admin=True
    )

    db.session.add(admin)
    db.session.commit()
```

## 6. Ejecutar la aplicación

```bash
python app.py
```

Abrir en el navegador:

```text
http://127.0.0.1:5000
```

---

#  API REST

## Endpoints Disponibles

| Método | Endpoint                       | Descripción                         |
| ------ | ------------------------------ | ----------------------------------- |
| GET    | /api/tournaments               | Lista todos los torneos             |
| GET    | /api/tournaments/"<tid>"/matches | Obtiene partidos de un torneo       |
| GET    | /api/tournaments/"<tid>"/ranking | Obtiene ranking del torneo          |
| POST   | /api/predict                   | Registra un pronóstico              |
| GET    | /api/user/me                   | Información del usuario autenticado |

### Ejemplo de solicitud

```json
{
    "partido_id": 1,
    "goles_local": 2,
    "goles_visitante": 1
}
```

---

#  Funcionalidades Principales

 Registro e inicio de sesión.
 Gestión de usuarios y administradores.
 Creación y administración de torneos.
 Gestión de partidos y resultados oficiales.
 Sistema de pronósticos deportivos.
 Ranking automático por puntos.
 Historial de participación del usuario.
 Distribución automática de premios.
 API REST propia.
 Diseño responsive adaptable a dispositivos móviles.
---

#  Sistema de Puntuación

| Acción                                | Puntos |
| ------------------------------------- | ------ |
| Resultado exacto                      | 3      |
| Resultado correcto (ganador o empate) | 1      |

### Reglas Económicas

* Cada pronóstico tiene un costo de participación.
* El valor se acumula en el pozo del partido.
* Los acertantes exactos comparten el premio del encuentro.
* Al finalizar el torneo, el pozo global se distribuye entre los mejores participantes.

---

#  Consideraciones Académicas

Este proyecto cumple con los requisitos de:

* Programación Orientada a Objetos (POO).
* Uso de Framework Web (Flask).
* Persistencia de datos mediante SQLite.
* Operaciones CRUD.
* Arquitectura modular.
* Desarrollo de API REST propia.
* Control de versiones con Git y GitHub.
* Interfaz web responsive.

---

#  Recomendaciones para Producción

Para un entorno de producción se recomienda:

* Configurar variables de entorno para claves sensibles.
* Utilizar PostgreSQL o MySQL en lugar de SQLite.
* Deshabilitar el modo Debug.
* Implementar HTTPS.
* Configurar copias de seguridad periódicas de la base de datos.

---
Proyecto desarrollado con fines académicos para demostrar el uso de Programación Orientada a Objetos, desarrollo web con Flask, persistencia de datos y diseño de APIs REST.
