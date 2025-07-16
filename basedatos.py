from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Log(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fecha_y_hora = db.Column(db.DateTime, default=datetime.utcnow)
    numero = db.Column(db.String(20))
    texto = db.Column(db.Text)

class EstadoUsuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    numero = db.Column(db.String(20), unique=True)
    recibio_menu = db.Column(db.Boolean, default=False)

def init_db(app):
    db.init_app(app)
    with app.app_context():
        db.create_all()

def agregar_mensajes_log(texto, numero=""):
    nuevo = Log(numero=numero, texto=texto)
    db.session.add(nuevo)
    db.session.commit()

def marcar_menu_enviado(numero):
    estado = EstadoUsuario.query.filter_by(numero=numero).first()
    if not estado:
        estado = EstadoUsuario(numero=numero, recibio_menu=True)
        db.session.add(estado)
    else:
        estado.recibio_menu = True
    db.session.commit()

def ya_envio_menu(numero):
    estado = EstadoUsuario.query.filter_by(numero=numero).first()
    return estado.recibio_menu if estado else False

def reiniciar_estado(numero):
    estado = EstadoUsuario.query.filter_by(numero=numero).first()
    if estado:
        estado.recibio_menu = False
        db.session.commit()
