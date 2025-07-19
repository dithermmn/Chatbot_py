from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import http.client
import json

#------------------ VARIABLES ------------------

TOKEN_VERIFICACION = "FARABOT"
ACCESS_TOKEN = "EAAVPtixyt4QBPJYCqpZBCqbMxjWhuNQjA6GwwZAZA9RU4aFejEJIkXHLbZAWtg3h4Ag5ZAPt15TmlgJBIepAGHFoWT0AIZC4Rmt2qbEyb5QQK9tfRIS23Wn4UZBdcK9Xcq6ZBkEha1Vjz8qoj2aELQXAlHf2gwwf1dCZCWiXonNumFfimrZCmDnFPY07QmaatAWkWMPFAjosizqt9fdmI8ZCBqfhgXZAHTzjIJm27ZCdQ8ZBiPZC0269JtIsSq1SlqbA4Ifk5gZD"
PHONE_NUMBER_IDE = "762799950241046"

#------------------  Base de Datos Y Flask ------------------

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///metapython.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Modelo para mensajes y logs normales
class Log(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.Date, default=datetime.utcnow)
    hora = db.Column(db.Time, default=datetime.utcnow)
    telefono = db.Column(db.String(20))
    texto = db.Column(db.Text)

# Modelo para errores
class ErrorLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.Date, default=datetime.utcnow)
    hora = db.Column(db.Time, default=datetime.utcnow)
    texto = db.Column(db.Text)

with app.app_context():
    db.create_all()

# Función para agregar mensaje normal
def agregar_mensajes_log(texto, telefono=None):
    ahora = datetime.utcnow()
    nuevo_registro = Log(fecha=ahora.date(), hora=ahora.time(), telefono=telefono, texto=texto)
    db.session.add(nuevo_registro)
    db.session.commit()

# Función para agregar error
def agregar_error_log(texto):
    ahora = datetime.utcnow()
    nuevo_error = ErrorLog(fecha=ahora.date(), hora=ahora.time(), texto=texto)
    db.session.add(nuevo_error)
    db.session.commit()

def ordenar_por_fecha_y_hora(registros):
    return sorted(registros, key=lambda x: (x.fecha, x.hora), reverse=True)

# Ruta principal muestra 2 tablas: mensajes y errores
@app.route('/')
def index():
    logs = Log.query.all()
    logs = ordenar_por_fecha_y_hora(logs)
    errores = ErrorLog.query.all()
    errores = ordenar_por_fecha_y_hora(errores)
    return render_template('index.html', registros=logs, errores=errores)

# Webhook y funciones principales

@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    if request.method == 'GET':
        return verificar_token(request)
    elif request.method == 'POST':
        return recibir_mensajes(request)

def verificar_token(req):
    token = req.args.get('hub.verify_token')
    challenge = req.args.get('hub.challenge')
    if challenge and token == TOKEN_VERIFICACION:
        return challenge
    else:
        return jsonify({'error': 'Token inválido'}), 401

def recibir_mensajes(req):
    try:
        req = request.get_json()
        agregar_mensajes_log("JSON recibido:")
        agregar_mensajes_log(json.dumps(req, indent=2))

        entry = req['entry'][0]
        changes = entry['changes'][0]
        value = changes['value']

        mensajes = value.get('messages')
        estados = value.get('statuses')

        if mensajes:
            msg = mensajes[0]
            numero = msg["from"].strip()

            if msg.get("type") == "interactive":
                seleccion = msg["interactive"]["button_reply"]["id"]
                agregar_mensajes_log(f"{numero} seleccionó: {seleccion}", numero)
                responder_seleccion(seleccion, numero)

            elif msg.get("type") == "text":
                texto = msg["text"]["body"].strip().lower()
                agregar_mensajes_log(f"{numero}: {texto}", numero)

                if es_primer_mensaje(numero) or texto == "menu":
                    enviar_texto(numero, "👋 Hola, soy Farabot. Estoy para servirte.")
                    enviar_menu(numero)
                else:
                    enviar_texto(numero, "🕐 Un asesor se pondrá en contacto contigo en breve.")

        elif estados:
            # No guardar logs de estado
            pass

        else:
            agregar_mensajes_log("⚠️ No se recibió mensaje. Nada que responder.")

        return jsonify({'message': 'EVENT_RECEIVED'})

    except Exception as e:
        error = f"Error en webhook: {str(e)}"
        print(error)
        agregar_error_log(error)
        return jsonify({'message': 'EVENT_RECEIVED'})

# Función para saber si es primer mensaje
def es_primer_mensaje(numero):
    return Log.query.filter_by(telefono=numero).count() == 0

# Funciones para enviar respuestas, menú y botones (igual que antes)

def responder_seleccion(opcion, numero):
    if opcion == "op1":
        texto = ("📘 *Información general*:\n\n🎓 Nuestro bachillerato en línea ...")
        enviar_boton_regreso(texto, numero)

    elif opcion == "op2":
        texto = ("📋 *¿Cómo me inscribo?*\n\n✍️ ¡El proceso es muy sencillo! ...")
        enviar_boton_regreso(texto, numero)

    elif opcion == "op3":
        texto = ("💰 *Costos y promociones*:\n\n💰 Nuestro modelo es accesible ...")
        enviar_boton_regreso(texto, numero)

    elif opcion == "enviar_menu":
        enviar_menu(numero)

def enviar_menu(numero, recordar=False):
    numero = "524611777249"  # borrar en producción
    texto = "*Selecciona una opción para continuar:*\n" if not recordar else "⚠️ Por favor selecciona una opción del menú:"
    data = {
        "messaging_product": "whatsapp",
        "to": numero,
        "type": "interactive",
        "interactive": {
            "type": "button",
            "body": {"text": texto},
            "action": {
                "buttons": [
                    {"type": "reply", "reply": {"id": "op1", "title": "1️⃣ Informacion"}},
                    {"type": "reply", "reply": {"id": "op2", "title": "2️⃣ Inscripción"}},
                    {"type": "reply", "reply": {"id": "op3", "title": "3️⃣ Costos"}},
                ]
            }
        }
    }
    enviar_peticion(data)

def enviar_boton_regreso(texto, numero):
    numero = "524611777249"  # borrar en producción
    data = {
        "messaging_product": "whatsapp",
        "to": numero,
        "type": "interactive",
        "interactive": {
            "type": "button",
            "body": {"text": texto},
            "action": {
                "buttons": [
                    {"type": "reply", "reply": {"id": "enviar_menu", "title": "🔙 Menú"}}
                ]
            }
        }
    }
    enviar_peticion(data)

def enviar_texto(numero, texto):
    numero = "524611777249"  # borrar en producción
    data = {
        "messaging_product": "whatsapp",
        "to": numero,
        "type": "text",
        "text": {"body": texto}
    }
    enviar_peticion(data)

def enviar_peticion(data):
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    conn = http.client.HTTPSConnection("graph.facebook.com")
    try:
        conn.request("POST", f"/v22.0/{PHONE_NUMBER_IDE}/messages", json.dumps(data), headers)
        res = conn.getresponse()
        body = res.read().decode()
        print("📤 Enviado:", body)
        agregar_mensajes_log("Respuesta WhatsApp:\n" + body)
    except Exception as e:
        error = f"Error al enviar mensaje: {str(e)}"
        print(error)
        agregar_error_log(error)
    finally:
        conn.close()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
