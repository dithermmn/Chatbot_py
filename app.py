from flask import Flask, request, jsonify, render_template
from basedatos import db, Log, init_db, agregar_mensajes_log, marcar_menu_enviado, ya_envio_menu, reiniciar_estado
from mensaje import enviar_menu, enviar_opcion, enviar_texto
import json

TOKEN_VERIFICACION = "FARABOT"

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///metapython.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

init_db(app)

@app.route('/')
def index():
    registros = Log.query.order_by(Log.fecha_y_hora.desc()).all()
    return render_template('index.html', registros=registros)

@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    if request.method == 'GET':
        return verificar_token(request)
    elif request.method == 'POST':
        return recibir_mensajes()

def verificar_token(req):
    token = req.args.get('hub.verify_token')
    challenge = req.args.get('hub.challenge')
    if token == TOKEN_VERIFICACION and challenge:
        return challenge
    return jsonify({'error': 'Token inválido'}), 401

def recibir_mensajes():
    try:
        data = request.get_json()
        agregar_mensajes_log(json.dumps(data, indent=2))

        messages = data['entry'][0]['changes'][0]['value'].get('messages')
        if not messages:
            return jsonify({'message': 'NO_MESSAGES'})

        msg = messages[0]
        numero = msg['from']
        tipo = msg.get('type')

        # Botón presionado
        if tipo == "interactive":
            btn_id = msg["interactive"]["button_reply"]["id"]

            if btn_id == "opt1":
                enviar_opcion(numero, "📘 Esta es la información de la opción 1.")
            elif btn_id == "opt2":
                enviar_opcion(numero, "📗 Detalles completos de la opción 2.")
            elif btn_id == "opt3":
                enviar_opcion(numero, "📦 Contenido exclusivo de la opción 3.")
            elif btn_id == "opt4":
                enviar_opcion(numero, "🛠️ Servicios disponibles en la opción 4.")
            elif btn_id == "opt5":
                enviar_texto(numero, "🤖 Esta opción está en desarrollo. Por favor espere a que una persona lo atienda.")
            elif btn_id == "menu":
                enviar_menu(numero)

            reiniciar_estado(numero)

        # Mensaje de texto
        elif tipo == "text":
            if not ya_envio_menu(numero):
                enviar_menu(numero)
                marcar_menu_enviado(numero)
            else:
                enviar_texto(numero, "🕐 Gracias por tu mensaje. Por favor espere a que una persona lo atienda.")
                reiniciar_estado(numero)

        return jsonify({'message': 'EVENT_RECEIVED'})
    except Exception as e:
        agregar_mensajes_log(f"❌ Error en webhook: {str(e)}")
        return jsonify({'message': 'ERROR'})
        
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
