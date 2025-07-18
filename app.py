# Importación de librerías necesarias
from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import http.client
import json


#------------------ VARIABLES ------------------

TOKEN_VERIFICACION = "FARABOT" # Token de seguridad para el webhook
ACCESS_TOKEN = "EAAVPtixyt4QBPHoxc6NyJqUznpZCZCDUehcROghlUlJt1ZAnagyO5OwRWlSPCvZAaZBYRwZAMTg6U6zCOB7UJq3I8gsb0JMkREYyQ8EO39jCfMJ0hHOnHF8OHioDkwWxSeSHawkWc1WlWbnj3TDZBZAUXMZAPybVucWUFg4ZCFNgwCKZCV0Aur4L1IFXwvRL6Ud9Fsa2J0tkVCdOumSZCZAZCqI5bp3o3xnyPGY4nHBlrwXEa8ZBGurqlUo"
PHONE_NUMBER_IDE ="762799950241046" #Identificador del numero (del numero de faraday)
API_URL = f"https://graph.facebook.com/v22.0/762799950241046/messages" # Url de la app

HEADERS = {
    "Authorization": f"Bearer {ACCESS_TOKEN}",
    "Content-Type": "application/json"
}

#------------------  Base de Datos Y Flask ------------------

# Configuración De Flask
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///metapython.db'  # Base de datos local SQLite
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Modelo de tabla para guardar mensajes y logs
class Log(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fecha_y_hora = db.Column(db.DateTime, default=datetime.utcnow)
    texto = db.Column(db.TEXT)

# Crear la tabla en la base de datos si no existe
with app.app_context():
    db.create_all()

# -------------> FUNCIONES DE BD

# Función - guardar mensajes en la BD
def agregar_mensajes_log(texto):
    nuevo_registro = Log(texto=texto)
    db.session.add(nuevo_registro)
    db.session.commit()

# Función auxiliar - ordenar mensajes por fecha descendente
def ordenar_por_fecha_y_hora(registros):
    return sorted(registros, key=lambda x: x.fecha_y_hora, reverse=True)

# -------------> HTML

# Ruta raíz que muestra los mensajes en HTML
@app.route('/')
def index():
    registros = Log.query.all()
    registros_ordenados = ordenar_por_fecha_y_hora(registros)
    return render_template('index.html', registros=registros_ordenados)



#------------------ WEBHOOK ------------------ 
# ----> Configurcion del token para validacion

# Ruta principal del webhook 
@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    if request.method == 'GET': # Verificacion
        return verificar_token(request)
    elif request.method == 'POST': # Recepcion de Mensajes
        return recibir_mensajes(request)

# Verificar el token cuando se conecta a la API de Facebook
def verificar_token(req):
    token = req.args.get('hub.verify_token')
    challenge = req.args.get('hub.challenge')
    if challenge and token == TOKEN_VERIFICACION:
        return challenge
    else:
        return jsonify({'error': 'Token inválido'}), 401


#------------------ Codigo Del MENSAJE ------------------ 

# Función principal - procesa los mensajes recibidos desde WhatsApp
def recibir_mensajes(req):
    try:
        req = request.get_json()
        agregar_mensajes_log("JSON recibido:")
        agregar_mensajes_log(json.dumps(req, indent=2))

        entry = req['entry'][0]
        changes = entry['changes'][0]
        value = changes['value']
        mensajes = value.get('messages')

        if mensajes:
            msg = mensajes[0]
            numero = msg["from"].strip()  # Número del usuario

            # Si el mensaje es un botón presionado
            if msg.get("type") == "interactive":
                seleccion = msg["interactive"]["button_reply"]["id"]
                responder_seleccion(seleccion, numero)

            # Si es texto, mostrar el menú
            elif msg.get("type") == "text":
                texto = msg["text"]["body"].strip().lower()
                agregar_mensajes_log(f"{numero}: {texto}")
                enviar_menu(numero)

        else:
            # Si no hubo interacción con botones, reenviar el menú
            numero = value['contacts'][0]['wa_id']
            enviar_menu(numero, recordar=True)

        return jsonify({'message': 'EVENT_RECEIVED'})

    except Exception as e:
        error = f"Error en webhook: {str(e)}"
        print(error)
        agregar_mensajes_log(error)
        return jsonify({'message': 'EVENT_RECEIVED'})

# ------------->  Función - Respuestas Segun el Boton

def responder_seleccion(opcion, numero):
    if opcion == "op1":
        texto = "📘 *Información general*:\n\nBachillerato en línea 100% flexible, 2 años de duración, sin exámenes presenciales.\n\n"
        enviar_boton_regreso(texto, numero)
    elif opcion == "op2":
        texto = "📋 *¿Cómo me inscribo?*\n\nLlena el formulario en https://dithermichel.com y te contactamos."
        enviar_boton_regreso(texto, numero)
    elif opcion == "op3":
        texto = "💰 *Costos y promociones*:\n\nConsulta precios actualizados en https://dithermichel.com"
        enviar_boton_regreso(texto, numero)


# -------------> Funcion Envio - MENU PRINCIPAL 

def enviar_menu(numero, recordar=False):
    texto = "👋 Hola, soy Farabot.\nSelecciona una opción para continuar:" if not recordar else "⚠️ Por favor selecciona una opción del menú:"
    
    data = {
        "messaging_product": "whatsapp",
        "to": 524611777249,
        "type": "interactive",
        "interactive": {
            "type": "button",
            "body": {
                "text": texto
            },
            "action": {
                "buttons": [
                    {"type": "reply", "reply": {"id": "op1", "title": "1️⃣ Informacion general"}},
                    {"type": "reply", "reply": {"id": "op2", "title": "2️⃣ Inscripción"}},
                    {"type": "reply", "reply": {"id": "op3", "title": "3️⃣ Costos y Promocciones"}},
                ]
            }
        }
    }
    enviar_peticion(data)

# -------------> Función - Boton de "regresar al menu" 

def enviar_boton_regreso(texto, numero):
    data = {
        "messaging_product": "whatsapp",
        "to": 524611777249,
        "type": "interactive",
        "interactive": {
            "type": "button",
            "body": {
                "text": texto
            },
            "action": {
                "buttons": [
                    {
                        "type": "reply",
                        "reply": {
                            "id": "menu",
                            "title": "🔙 Regresar al menú"
                        }
                    }
                ]
            }
        }
    }
    enviar_peticion(data)

# -------------> Configuracion para mandar mensaje

# Función para enviar mensajes de texto simples
def enviar_texto(numero, texto):
    data = {
        "messaging_product": "whatsapp",
        "to": 524611777249,
        "type": "text",
        "text": {
            "body": texto
        }
    }
    enviar_peticion(data)

#------------------ Envia peticion HTTP ------------------ 

# Función base que envía cualquier mensaje por API
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
        agregar_mensajes_log(error)
    finally:
        conn.close()

#------------------ Iniciar servidor ------------------ 
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
