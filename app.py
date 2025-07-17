# Importación de librerías necesarias
from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import requests # libreria - hacer peticiones HTTPS
import os
import json


#------------------ VARIABLES ------------------

TOKEN_VERIFICACION = "FARABOT" # Token validar webhook
ACCESS_TOKEN = os.getenv("EAAVPtixyt4QBPJUZBUbCJA1RMUrACVqYD5BMflsMRXmMNCx43oBcrZCqNSi7tCGaAK1cKoI9uGoCL3Q3PZClZBQBt19DZA975nhXVuRTNZBWOhFObWL9tS5uX9odNewXdIp9eNSaJKnE0zzFJvy9bdfanPOIKfuvwjqW10kddTrv9CboJs9n6vX0xGEAFLeP1um4HZA5HfI7on5AcBnrv5XtXbMLyihHIV3DDBRwFCDIKvlJ1oZD")
PHONE_NUMBER_IDE ="762799950241046" #Identificador del numero (del numero de faraday)
API_URL = f"https://graph.facebook.com/v22.0/762799950241046/messages" # Url de la app
numero = "524611777249" # borrar esta

# Botones del menú definidos una vez
BOTONES_MENU = [
    {"id": "op1", "title": "1️⃣ Información general"},
    {"id": "op2", "title": "2️⃣ Inscripción"},
    {"id": "op3", "title": "3️⃣ Costos y Promociones"},
    {"id": "op4", "title": "4️⃣ Asesor"},
    {"id": "op5", "title": "5️⃣ Otra pregunta"},
]
#------------------  Base de Datos Y Flask ------------------

# Configuración De Flask
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///instance/metapython.db' # Base de datos local SQLite
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Modelo (tabla) guardar mensajes 
class Mensaje(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    numero = db.Column(db.String(20))
    mensaje = db.Column(db.Text)
    fecha = db.Column(db.DateTime, default=datetime.now) 
 

# Modelo (tabla) guardar logs
class Log(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    contenido = db.Column(db.Text)
    fecha = db.Column(db.DateTime, default=datetime.now)

# Crear la tabla en la base de datos si no existe
with app.app_context():
    db.create_all()

# -------------> FUNCIONES DE BD

# Función - guardar mensajes en la BD
def agregar_mensajes_log(texto):
    log = Log(contenido=texto)
    db.session.add(log)
    db.session.commit()

# -------------> HTML

# Ruta raíz que muestra los mensajes en HTML
@app.route('/')
def index():
    logs = Log.query.order_by(Log.fecha.desc()).all()
    return render_template('index.html', logs=logs)


#------------------ WEBHOOK ------------------ 
# ----> Configurcion del token para validacion

# Ruta principal del webhook 
@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    if request.method == 'GET':
        token = request.args.get("hub.verify_token") # verificcion del token
        challenge = request.args.get("hub.challenge")
        if token == TOKEN_VERIFICACION:
            return challenge
        return "Token inválido", 403

    if request.method == 'POST':
        data = request.get_json()
        try:
            agregar_mensajes_log("📩 Entrada:\n" + json.dumps(data))
            procesar_mensaje(data)
            return "OK", 200
        except Exception as e:
            error = f"❌ Error en webhook: {str(e)}"
            print(error)
            agregar_mensajes_log(error)
            return "Error", 500

#------------------ Codigo Del MENSAJE ------------------ 

# 1.- Procesar los mensajes recibidos desde WhatsApp

def procesar_mensaje(data):
    entry = data.get("entry", [{}])[0]
    changes = entry.get("changes", [{}])[0]
    value = changes.get("value", {})
    mensajes = value.get("messages")
    
    if mensajes:
        msg = mensajes[0]
        numero = msg.get("from", "").strip()

        # Guardar mensaje si es texto
        if msg.get("type") == "text":
            texto = msg.get("text", {}).get("body", "").strip()
            nuevo = Mensaje(numero=numero, mensaje=texto)
            db.session.add(nuevo)
            db.session.commit()
            agregar_mensajes_log(f"{numero}: {texto}")
            enviar_menu(numero)

        # Si el usuario presionó botón
        elif msg.get("type") == "interactive":
            opcion = msg.get("interactive", {}).get("button_reply", {}).get("id")
            if opcion:
                responder_seleccion(opcion, numero)
            else:
                enviar_menu(numero)

        else:
            # Otros tipos de mensaje
            enviar_menu(numero)
    else:
        # No hay mensajes, reenviar menú (posible timeout o interacción no reconocida)
        contactos = value.get("contacts", [{}])
        if contactos:
            numero = contactos[0].get("wa_id", "")
            if numero:
                enviar_menu(numero, recordar=True)

# ------------->  2.- Función De Respuestas

def responder_seleccion(opcion, numero):
    if opcion == "op1":
        texto = ("""📘 *Información general*:\n\n
                 
                🎓 Nuestro bachillerato en línea es ideal si buscas estudiar desde casa, a tu ritmo, sin exámenes presenciales.\n
                📌 Dura 2 años.\n
                📅 Puedes comenzar cuando quieras.\n
                🌐 Modalidad 100% en línea con apoyo académico continuo.\n
                💻 100% en línea, sin asistir a planteles.\n
                🕒 Estudias a tu ritmo y desde cualquier lugar.\n
                📅 Acceso 24/7 a la plataforma\n
                🧑‍🏫 Asesorías personalizadas por WhatsApp y correo\n\n\n
                 

                ✅ Para ingresar necesitas:\n
                - Tener secundaria terminada\n
                - Ser mayor de 15 años\n
                - Contar con acceso a internet\n\n\n
                 

                📁 Documentación:\n
                - Acta de nacimiento\n
                - CURP\n
                - Certificado de secundaria\n
                - Comprobante de domicilio\n\n\n
                 

                🏛️ Nuestro programa tiene validez oficial ante la SEP.\n
                - RVOE: xxxxxxxxxxxxx\n\n
                 
                Puedes consultarlo directamente en la página oficial:\n
                👉 Consultar RVOE en SEP\n\n
                 
                🏫 Al finalizar recibirás un certificado de bachillerato válido en todo México.\n\n\n
                 

                📄 Ver folleto informativo (PDF)\n\n""")
        enviar_boton_regreso(texto, numero)

    elif opcion == "op2":
        texto = ("""📋 *¿Cómo me inscribo?*\n\n
                 
                 ✍️ ¡El proceso es muy sencillo! Solo sigue estos pasos:\n\n

                1. Llena este formulario: 👉 Formulario de inscripción\n
                2. Realiza el pago de inscripción.\n
                3. Un asesor se pondrá en contacto contigo para verificar tu información.\n\n\n
                 

                📄 Documentos que necesitas:\n\n
                 
                - Acta de nacimiento\n
                - CURP\n
                - Comprobante de domicilio\n
                - Certificado de secundaria\n\n""")
        enviar_boton_regreso(texto, numero)

    elif opcion == "op3":
        texto = ("💰 *Costos y promociones*:\n\n" \
        ""
                 """💰 Nuestro modelo es accesible y sin pagos ocultos.\n
                🔹 Inscripción Y Reinscripciones: $XXX MXN\n
                🔹 Mensualidad: $XXX MXN\n\n\n


                🎁 Promoción actual: Inscripción con 50% de descuento.\n\n\n


                📆 Aceptamos pagos por:\n
                - Transferencia\n
                - OXXO\n
                - PayPal\n""")
        enviar_boton_regreso(texto, numero)

    elif opcion == "op4":
        texto = ("🧑‍💼 *Hablar con asesor*:\n\n"
                 """🕘 Horarios de atención:\n
                - Lunes a Viernes de 9:00 a.m. a 6:00 p.m.\n
                - Sábados de 10:00 a.m. a 2:00 p.m.\n\n""")
        enviar_boton_regreso(texto, numero)

    elif opcion == "op5":
        texto = ("🕐 *Otra pregunta*:\n\n"
                 """✏️ Por favor escribe tu pregunta y haré lo posible por ayudarte.\n
                Si no puedo resolverla, te contactaré con un asesor humano.\n\n""")
        enviar_texto(numero, texto)

    elif opcion == "menu":
        enviar_menu(numero)
    else:
        enviar_menu(numero)


# -------------> Funcion Envio - MENU PRINCIPAL 

def enviar_menu(numero, recordar=False):
    texto = "👋 Hola, soy Farabot.\nSelecciona una opción para continuar:" if not recordar else "⚠️ Por favor selecciona una opción del menú:"
    botones = [{"type": "reply", "reply": {"id": b["id"], "title": b["title"]}} for b in BOTONES_MENU]

    data = {
        "messaging_product": "whatsapp",
        "to": 524611777249,
        "type": "interactive",
        "interactive": {
            "type": "button",
            "body": {"text": texto},
            "action": {"buttons": botones}
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
            "body": {"text": texto},
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
        "text": {"body": texto}
    }
    enviar_peticion(data)

#------------------ Envia peticion HTTP ------------------ 

# Función base que envía cualquier mensaje por API
def enviar_peticion(data):
    if not ACCESS_TOKEN:
        error = "⚠️ ACCESS_TOKEN no configurado. Establece la variable de entorno."
        print(error)
        agregar_mensajes_log(error)
        return

    try:
        response = requests.post(
            API_URL,
            headers={
                "Authorization": f"Bearer {ACCESS_TOKEN}",
                "Content-Type": "application/json"
            },
            json=data,
            timeout=10
        )
        response.raise_for_status()
        body = response.text
        print("📤 Enviado:", body)
        agregar_mensajes_log("Respuesta WhatsApp:\n" + body)
    except requests.exceptions.RequestException as e:
        error = f"Error al enviar mensaje: {str(e)}"
        print(error)
        agregar_mensajes_log(error)


#------------------ Iniciar servidor ------------------ 
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
