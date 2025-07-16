from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import http.client
import json

app = Flask(__name__)

# Configuración de la base de datos SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///metapython.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Modelo de la tabla log
class Log(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fecha_y_hora = db.Column(db.DateTime, default=datetime.utcnow)
    texto = db.Column(db.TEXT)

# Crear la tabla si no existe
with app.app_context():
    db.create_all()

# Función para ordenar registros por fecha
def ordenar_por_fecha_y_hora(registros):
    return sorted(registros, key=lambda x: x.fecha_y_hora, reverse=True)

@app.route('/')
def index():
    registros = Log.query.all()
    registros_ordenados = ordenar_por_fecha_y_hora(registros)
    return render_template('index.html', registros=registros_ordenados)

# Guardar en la base de datos
def agregar_mensajes_log(texto):
    nuevo_registro = Log(texto=texto)
    db.session.add(nuevo_registro)
    db.session.commit()

# Token para validación webhook
TOKEN_FARABOT = "FARABOT"

@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    if request.method == 'GET':
        return verificar_token(request)
    elif request.method == 'POST':
        return recibir_mensajes(request)

def verificar_token(req):
    token = req.args.get('hub.verify_token')
    challenge = req.args.get('hub.challenge')
    if challenge and token == TOKEN_FARABOT:
        return challenge
    else:
        return jsonify({'error': 'Token inválido'}), 401

# Manejo del webhook POST
def recibir_mensajes(req):
    try:
        req = request.get_json()
        agregar_mensajes_log("JSON recibido:")
        agregar_mensajes_log(json.dumps(req, indent=2))

        entry = req['entry'][0]
        changes = entry['changes'][0]
        value = changes['value']
        objeto_mensaje = value.get('messages')

        if objeto_mensaje:
            messages = objeto_mensaje[0]

            if "type" in messages and messages["type"] == "interactive":
                return jsonify({'message': 'EVENT_RECEIVED'})

            if "text" in messages and "body" in messages["text"]:
                text = messages["text"]["body"]
                numero = messages["from"].strip()

                print("Texto:", text)
                print("Número:", numero)
                agregar_mensajes_log(f"Texto: {text}")
                agregar_mensajes_log(f"Número: {numero}")

                enviar_mensajes_whatsapp(text, numero)
                agregar_mensajes_log(f"{numero}: {text}")

        return jsonify({'message': 'EVENT_RECEIVED'})

    except Exception as e:
        error_msg = f"Error en recibir_mensajes: {str(e)}"
        print(error_msg)
        agregar_mensajes_log(error_msg)
        return jsonify({'message': 'EVENT_RECEIVED'})

# Enviar respuesta por WhatsApp
def enviar_mensajes_whatsapp(texto, numero):
    texto = texto.lower().strip()

    if "hola" in texto:
        body_text = "👋 ¡Hola! Soy Farabot, tu asistente del Instituto Michael Faraday. Estoy aquí para ayudarte a conocer más sobre nuestro Bachillerato en Línea. ¿Con qué deseas comenzar? 📝 Selecciona una opción respondiendo con el número correspondiente: 1️⃣ Información general 2️⃣ ¿Cómo me inscribo? 3️⃣ Costos y promociones 4️⃣ Hablar con un asesor 5️⃣ Otra pregunta"
    elif "1" in texto:
        body_text = "Seleccionaste la opción 1. Más info en https://dithermichel.com"
    else:
        body_text = "OTRA COOOOSAAAA"

    data = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": 524611777249,
        "type": "text",
        "text": {
            "preview_url": False,
            "body": body_text
        }
    }

    data_json = json.dumps(data)

    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer EAAVPtixyt4QBPCUDM8KmJ27ZCTQVCZCsUYMxRTRTVr6ZAvNMKgNjjTO4SkYdmLMLWnA0jBPjZACEtZBGbiZAHLi4uswIUVqe3TniZBYiZCZB6fvvoQk0phksZCsE7ywvO77baUmef3e8PCCPuWcw4wZC1aH0xrhht6qR3vHnJCYBblp8hLOedz9TkUOprgItXy63bzGFUSyIQDHMUVQYvyhV02Nj9o7IsQPZBCyStowkcI2Gvh2DVtAZD"
    }

    connection = http.client.HTTPSConnection("graph.facebook.com")

    try:
        connection.request("POST", "/v22.0/762799950241046/messages", data_json, headers)
        response = connection.getresponse()
        status = response.status
        reason = response.reason
        body = response.read().decode()

        print("Status:", status)
        print("Reason:", reason)
        print("Body:", body)

        agregar_mensajes_log(f"Status: {status}")
        agregar_mensajes_log(f"Reason: {reason}")
        agregar_mensajes_log(f"Body: {body}")

    except Exception as e:
        error_msg = f"Error al enviar mensaje: {str(e)}"
        print(error_msg)
        agregar_mensajes_log(error_msg)

    finally:
        connection.close()

# Ejecutar servidor Flask
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
