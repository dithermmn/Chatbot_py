from flask import request, jsonify
import json
from basedatos import agregar_mensajes_log
from mensaje import enviar_menu, enviar_opcion, enviar_texto

TOKEN_VERIFICACION = "FARABOT"

def manejar_webhook_get(req):
    token = req.args.get('hub.verify_token')
    challenge = req.args.get('hub.challenge')
    if challenge and token == TOKEN_VERIFICACION:
        return challenge
    return jsonify({'error': 'Token inválido'}), 401

def manejar_webhook_post(req):
    try:
        data = request.get_json()
        agregar_mensajes_log("JSON recibido:")
        agregar_mensajes_log(json.dumps(data, indent=2))

        messages = data['entry'][0]['changes'][0]['value'].get('messages')
        if messages:
            msg = messages[0]
            numero = msg['from']
            tipo = msg.get('type')

            if tipo == "interactive":
                btn_id = msg["interactive"]["button_reply"]["id"]
                if btn_id == "opt1":
                    enviar_opcion(numero, "ℹ️ Esta es la información de la opción 1.")
                elif btn_id == "opt2":
                    enviar_opcion(numero, "📄 Detalles completos de la opción 2.")
                elif btn_id == "opt3":
                    enviar_opcion(numero, "📦 Contenido exclusivo de la opción 3.")
                elif btn_id == "opt4":
                    enviar_opcion(numero, "🛠️ Servicios disponibles en la opción 4.")
                elif btn_id == "opt5":
                    enviar_texto(numero, "🤖 Esta opción está en desarrollo. Por favor espere a que una persona lo atienda.")
                elif btn_id == "menu":
                    enviar_menu(numero)

            elif tipo == "text":
                enviar_texto(numero, "🕐 Gracias por tu mensaje. Por favor espera a que una persona lo atienda.")
                enviar_menu(numero)

        return jsonify({'message': 'EVENT_RECEIVED'})
    except Exception as e:
        agregar_mensajes_log(f"❌ Error en webhook POST: {str(e)}")
        return jsonify({'message': 'ERROR'})
