from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

# Modelo de la tabla de logs
class Log(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fecha_y_hora = db.Column(db.DateTime, default=datetime.utcnow)
    texto = db.Column(db.TEXT)

# Inicializa la base de datos y crea las tablas si no existen
def init_db(app):
    db.init_app(app)
    with app.app_context():
        db.create_all()

# Guarda mensajes en la base de datos
def agregar_mensajes_log(texto):
    nuevo = Log(texto=texto)
    db.session.add(nuevo)
    db.session.commit()

# Ordena registros por fecha descendente
def ordenar_por_fecha_y_hora(registros):
    return sorted(registros, key=lambda x: x.fecha_y_hora, reverse=True)
