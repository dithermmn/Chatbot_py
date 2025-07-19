from flask import Flask, request, render_template
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from zoneinfo import ZoneInfo
import http.client
import json

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///metapython.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# TOKENES Y CONFIG
VERIFY_TOKEN = "FARABOT"
ACCESS_TOKEN = "TU_ACCESS_TOKEN"
ID_NUMERO = "762799950241046"

# 📌 Base de datos
class Log(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.String(10))
    hora = db.Column(db.String(8))
    numero = db.Column(db.String(20))
    mensaje = db.Column(db.Text)

class ErrorLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.String(10))
    hora = db.Column(db.String(8))
    detalle = db.Column(db.Text)

db.create_all()

# 📌 Guardar log con hora local
def agregar_mensajes_log(numero, mensaje):
    ahora = datetime.now(ZoneInfo("America/Mexico_City"))
    fecha = ahora.strftime("%d/%m/%Y")
    hora = ahora.strftime("%H:%M:%S")
    nuevo = Log(fecha=fecha, hora=hora, numero=numero, mensaje=mensaje)
    db.session.add(nuevo)
    db.session.commit()

def agregar_error_log(detalle):
    ahora = datetime.now(ZoneInfo("America/Mexico_City"))
    fecha = ahora.strftime("%d/%m/%Y")
    hora = ahora.strftime("%H:%M:%S")
    error = ErrorLog(fecha=fecha, hora=hora, detalle=detalle)
    db.session.add(error)
    db.session.commit()

# 📌 Verificar si es primer mensaje
def es_primer_mensaje(numero):
    return not Log.query.filter_by(numero=numero).first()

# 📌 Enviar mensaje por WhatsApp
def enviar_texto(numero, texto):
    try:
        conn = http.client.HTTPSConnection("graph.facebook.com")
        payload = json.dumps({
            "messaging_product": "whatsapp",
            "to": numero,
            "type": "text",
            "text": {"body": texto}
        })
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {ACCESS_TOKEN}'
        }
        conn.request("POST", f"/v17.0/{ID_NUMERO}/messages", payload, headers)
        res = conn.getresponse()
        data = res.read().decode("utf-8")
        print("Respuesta WhatsApp:", data)
    except Exception as e:
        agregar_error_log(f"Error al enviar mensaje: {str(e)}")

# 📌 Enviar menú con botones
def enviar_menu(numero):
    try:
        conn = http.client.HTTPSConnection("graph.facebook.com")
        payload = json.dumps({
            "messaging_product": "whatsapp",
            "to": numero,
            "type": "interactive",
            "interactive": {
                "type": "button",
                "body": {"text": "¿En qué puedo ayudarte?"},
                "action": {
                    "buttons": [
                        {"type": "reply", "reply": {"id": "opcion1", "title": "📌 Información"}},
                        {"type": "reply", "reply": {"id": "opcion2", "title": "💰 Precios"}},
                        {"type": "reply", "reply": {"id": "opcion3", "title": "📦 Productos"}},
                        {"type": "reply", "reply": {"id": "opcion4", "title": "📞 Contacto"}},
                        {"type": "reply", "reply": {"id": "opcion5", "title": "🧑‍💼 Hablar con asesor"}}
                    ]
                }
            }
        })
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {ACCESS_TOKEN}'
        }
        conn.request("POST", f"/v17.0/{ID_NUMERO}/messages", payload, headers)
        res = conn.getresponse()
        data = res.read().decode("utf-8")
        print("Respuesta WhatsApp:", data)
    except Exception as e:
        agregar_error_log(f"Error al enviar menú: {str(e)}")

# 📌 Webhook verificación
@app.route("/webhook", methods=["GET"])
def verificar_token():
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")
    return challenge if token == VERIFY_TOKEN else "Token inválido"

# 📌 Webhook recepción
@app.route("/webhook", methods=["POST"])
def recibir_mensajes():
    try:
        data = request.get_json()
        print("JSON recibido:", json.dumps(data, indent=2))

        for entry in data.get("entry", []):
            for change in entry.get("changes", []):
                value = change.get("value", {})
                mensajes = value.get("messages", [])

                for msg in mensajes:
                    numero = msg.get("from")
                    tipo = msg.get("type")

                    if tipo == "text":
                        texto = msg["text"]["body"].strip().lower()
                        agregar_mensajes_log(numero, texto)

                        if es_primer_mensaje(numero) or texto == "menu":
                            enviar_texto(numero, "👋 Hola, soy Farabot. Estoy para servirte.")
                            enviar_menu(numero)
                        else:
                            enviar_texto(numero, "🕐 Un asesor se pondrá en contacto contigo en breve.")

                    elif tipo == "interactive":
                        respuesta_id = msg["interactive"]["button_reply"]["id"]
                        if respuesta_id == "opcion1":
                            enviar_texto(numero, "📌 Aquí tienes la información general...")
                            enviar_menu(numero)
                        elif respuesta_id == "opcion2":
                            enviar_texto(numero, "💰 Nuestros precios son...")
                            enviar_menu(numero)
                        elif respuesta_id == "opcion3":
                            enviar_texto(numero, "📦 Ofrecemos estos productos...")
                            enviar_menu(numero)
                        elif respuesta_id == "opcion4":
                            enviar_texto(numero, "📞 Puedes contactarnos al +52...")
                            enviar_menu(numero)
                        elif respuesta_id == "opcion5":
                            enviar_texto(numero, "🧑‍💼 Un asesor te contactará pronto.")

        return "ok", 200
    except Exception as e:
        agregar_error_log(f"Error en webhook: {str(e)}")
        return "error", 500

# 📌 Página de visualización de logs
@app.route("/")
def index():
    logs = Log.query.order_by(Log.id.desc()).limit(20).all()
    errores = ErrorLog.query.order_by(ErrorLog.id.desc()).limit(10).all()
    return render_template("index.html", logs=logs, errores=errores)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)
