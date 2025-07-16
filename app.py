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

# Función para ordenar registros por fecha y hora
def ordenar_por_fecha_y_hora(registros):
    return sorted(registros, key=lambda x: x.fecha_y_hora, reverse=True)

@app.route('/')
def index():
    registros = Log.query.all()
    registros_ordenados = ordenar_por_fecha_y_hora(registros)
    return render_template('index.html', registros=registros_ordenados)

# Función para guardar mensajes en la base de datos
def agregar_mensajes_log(texto):
    nuevo_registro = Log(texto=texto)
    db.session.add(nuevo_registro)
    db.session.commit()

# Token de verificación para Meta
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

# Recepción de mensajes del webhook
def recibir_mensajes(req):
    try:
        req = request.get_json()
        print("JSON recibido:")
        print(json.dumps(req, indent=2))

        entry = req['entry'][0]
        changes = entry['changes'][0]
        value = changes['value']
        objeto_mensaje = value.get('messages')

        if objeto_mensaje:
            messages = objeto_mensaje[0]

            # Ignorar mensajes interactivos
            if "type" in messages and messages["type"] == "interactive":
                return jsonify({'message': 'EVENT_RECEIVED'})

            if "text" in messages and "body" in messages["text"]:
                text = messages["text"]["body"]
                numero = messages["from"].strip()

                print("Texto:", text)
                print("Número:", numero)

                enviar_mensajes_whatsapp(text, numero)
                agregar_mensajes_log(f"{numero}: {text}")

        return jsonify({'message': 'EVENT_RECEIVED'})

    except Exception as e:
        print("Error:", str(e))
        return jsonify({'message': 'EVENT_RECEIVED'})

# Envío de respuestas por WhatsApp
def enviar_mensajes_whatsapp(texto, numero):
    texto = texto.lower().strip()

    if "hola" in texto:
        body_text = "Hola, encuentra más información en https://dithermichel.com"
    elif "1" in texto:
        body_text = "Seleccionaste la opción 1. Más info en https://dithermichel.com"
    else:
        body_text = "OTRA COOOOSAAAA"

    data = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": numero,
        "type": "text",
        "text": {
            "preview_url": False,
            "body": body_text
        }
    }

    data = json.dumps(data)

    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer EAAVPtixyt4QBPOXksdZAZCd8fTKs4uquZAxRMdq8pxs65VZCAZBGOJIG7vTgUDFKmrYeoHk4gdqlIbh0OBmCjzYjVVwdXrdvrXyYZBQZAQOUKAZBN5WwlChaOwChrEdZCBZBavp7aIH6LiKNYp1ZAC4m99szQ2TImkySmZAIbgsIb1lpa8rnQGPJeZA19GI5tTS9HqlQGmoxODo6k008Mb7tjgE4JupRL1OPqgqsm2xk7LkC6HsEGrLEZD"  # ← Token de acceso válido
    }

    connection = http.client.HTTPSConnection("graph.facebook.com")

    try:
        connection.request("POST", "/v17.0/762799950241046/messages", data, headers)
        response = connection.getresponse()
        print(response.status, response.reason)
        print(response.read().decode())  # Muestra el detalle de la respuesta

    except Exception as e:
        print("Error al enviar mensaje:", str(e))
        agregar_mensajes_log(f"Error al enviar: {str(e)}")

    finally:
        connection.close()

# Ejecutar la app
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
