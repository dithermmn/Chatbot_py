from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Log(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fecha_y_hora = db.Column(db.DateTime, default=datetime.utcnow)
    texto = db.Column(db.TEXT)

def init_db(app):
    db.init_app(app)
    with app.app_context():
        db.create_all()

def agregar_mensajes_log(texto):
    from basedatos import db
    nuevo = Log(texto=texto)
    db.session.add(nuevo)
    db.session.commit()

def ordenar_por_fecha_y_hora(registros):
    return sorted(registros, key=lambda x: x.fecha_y_hora, reverse=True)
