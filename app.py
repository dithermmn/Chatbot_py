#El primer mensaje del usuuario o si pone menu manda el menu y los posteriores pone que lo va a atender alguien 


# Importación de librerías necesarias
from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import http.client
import json


#------------------ VARIABLES ------------------

TOKEN_VERIFICACION = "FARABOT" # Token de seguridad para el webhook
ACCESS_TOKEN = "EAAVPtixyt4QBPJtIaw3fsg3oZBKQW1L99nh8CD8ZCLaLPn85RerUWZBiqTZCCeSbt4Or6RZCYe2LlA3eL4B5cO2vIQUtUDohVHc1BRImV1yVaa2wdZA59UViZAHm57eJ9ExmJXypXXLArLWlnWTRJ25VJijKvcUE6ZBdYnHjrPEduLIInsS8b60SGUseSsBDwJ75g7SsgcdYihvQZAKvTQLqwPQgs6T3IG9vg0JPiiZA8xhT730qQ7c7IZBsHrbneJpWgZDZD"
PHONE_NUMBER_IDE ="762799950241046" #Identificador del numero (del numero de faraday)

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
    telefono = db.Column(db.String(20))  # Guardar número
    

# Crear la tabla en la base de datos si no existe
with app.app_context():
    db.create_all()

# -------------> FUNCIONES DE BD

# Función - guardar mensajes en la BD
def agregar_mensajes_log(texto, telefono=None):
    nuevo_registro = Log(texto=texto, telefono=telefono)
    db.session.add(nuevo_registro)
    db.session.commit()

# Función auxiliar - ordenar mensajes por fecha descendente
def ordenar_por_fecha_y_hora(registros):
    return sorted(registros, key=lambda x: x.fecha_y_hora, reverse=True)

# Verificar si es primer mensaje para un número
def es_primer_mensaje(numero):
    return Log.query.filter_by(telefono=numero).count() == 0
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


#------------------Logica - Procesamiento Del MENSAJE ------------------ 

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
        else:
            agregar_mensajes_log("⚠️ No se recibió mensaje. Nada que responder.")

        return jsonify({'message': 'EVENT_RECEIVED'})

    except Exception as e:
        error = f"Error en webhook: {str(e)}"
        print(error)
        agregar_mensajes_log(error)
        return jsonify({'message': 'EVENT_RECEIVED'})

# ------------->  Función - Respuestas Segun el Boton

def responder_seleccion(opcion, numero):
    if opcion == "op1":
        texto = ("""📘 *Información general*:\n\n🎓 Nuestro bachillerato en línea es ideal si buscas estudiar desde casa, a tu ritmo, sin exámenes presenciales.\n\n📌 Dura 2 años.\n📅 Puedes comenzar cuando quieras.\n🌐 Modalidad 100% en línea con apoyo académico continuo.\n💻 100% en línea, sin asistir a planteles.\n🕒 Estudias a tu ritmo y desde cualquier lugar.\n📅 Acceso 24/7 a la plataforma\n🧑‍🏫 Asesorías personalizadas por WhatsApp y correo\n\n\n✅ Para ingresar necesitas:\n- Tener secundaria terminada\n- Ser mayor de 15 años\n- Contar con acceso a internet\n\n\n📁 Documentación:\n- Acta de nacimiento\n- CURP\n- Certificado de secundaria\n- Comprobante de domicilio\n\n\n🏛️ Nuestro programa tiene validez oficial ante la SEP.\n- RVOE: xxxxxxxxxxxxx\n\nPuedes consultarlo directamente en la página oficial:\n👉 Consultar RVOE en SEP\n\n🏫 Al finalizar recibirás un certificado de bachillerato válido en todo México.\n\n\n""")
        enviar_boton_regreso(texto, numero)

    elif opcion == "op2":
        texto = ("""📋 *¿Cómo me inscribo?*\n\n✍️ ¡El proceso es muy sencillo! Solo sigue estos pasos:\n\n1. Llena este formulario: 👉 Formulario de inscripción\n2. Realiza el pago de inscripción.\n3. Un asesor se pondrá en contacto contigo para verificar tu información.\n\n\n📄 Documentos que necesitas:\n\n- Acta de nacimiento\n- CURP\n- Comprobante de domicilio\n- Certificado de secundaria\n\n""")
        enviar_boton_regreso(texto, numero)

    elif opcion == "op3":
        texto = ("""💰 *Costos y promociones*:\n\n💰 Nuestro modelo es accesible y sin pagos ocultos.\n🔹 Inscripción Y Reinscripciones: $XXX MXN\n🔹 Mensualidad: $XXX MXN\n\n\n🎁 Promoción actual: Inscripción con 50% de descuento.\n\n\n📆 Aceptamos pagos por:\n- Transferencia\n- OXXO\n- PayPal\n""")
        enviar_boton_regreso(texto, numero)

    elif opcion == "enviar_menu":
        enviar_menu(numero)  # ✅ Esta línea activa el botón de regreso al menú

# -------------> Funcion Envio - MENU PRINCIPAL 

def enviar_menu(numero, recordar=False):
    numero = "524611777249" # borrar

    texto = "*Selecciona una opción para continuar:*\n" if not recordar else "⚠️ Por favor selecciona una opción del menú:"
    
    data = {
        "messaging_product": "whatsapp",
        "to": numero,
        "type": "interactive",
        "interactive": {
            "type": "button",
            "body": {
                "text": texto
            },
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


# -------------> Función - Boton de "regresar al menu" 

def enviar_boton_regreso(texto, numero):
    numero = "524611777249" # borrar
    data = {
        "messaging_product": "whatsapp",
        "to": numero,
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
                            "id": "enviar_menu",
                            "title": "🔙 Menú"
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
    numero = "524611777249" # borrar
    data = {
        "messaging_product": "whatsapp",
        "to": numero,
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
