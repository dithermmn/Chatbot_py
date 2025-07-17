#---------------------------------
# codigo "acomodado" de programa 2 
#---------------------------------

#LIBRERIAS IMPORTADAS

#flask = programacion web en python, render_templates = template  html
from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import http.client
import json

################################

# Autentificacion

#Token de meta
ACCESS_TOKEN = "" 
PHONE_NUMBER_IDE ="" #Identificador del numero (del numero de faraday)
API_URL = f"https://graph.facebook.com/v22.0/762799950241046/messages" # Url de la app


############### BASE DE DATOS #################

# CONFIGURACION De La Base De Datos SQLite
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///metapython.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Modelo de la tabla log - base de datos
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
    return render_template('index.html', registros=registros_ordenados) #HTML

# Guardar en la base de datos
def agregar_mensajes_log(texto):
    nuevo_registro = Log(texto=texto)
    db.session.add(nuevo_registro)
    db.session.commit()

############### WEBHOOK #################

#Configurcion del token para validacion -- webhook

@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    if request.method == 'GET':
        return verificar_token(request)
    elif request.method == 'POST':
        return recibir_mensajes(request)

def verificar_token(req):
    token = req.args.get('hub.verify_token')
    challenge = req.args.get('hub.challenge')
    if challenge and token == ACCESS_TOKEN:
        return challenge
    else:
        return jsonify({'error': 'Token inválido'}), 401


################################

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

                #enviar_mensajes_whatsapp(text, numero)
                agregar_mensajes_log(f"{numero}: {text}")

        return jsonify({'message': 'EVENT_RECEIVED'})

    except Exception as e:
        error_msg = f"Error en recibir_mensajes: {str(e)}"
        print(error_msg)
        agregar_mensajes_log(error_msg)
        return jsonify({'message': 'EVENT_RECEIVED'})



#Enviar respuesta por WhatsApp -- Codigo Del Mensaje





# Ejecutar servidor Flask
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)