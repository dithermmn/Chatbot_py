from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# Tokens de Meta API
ACCESS_TOKEN = "EAAVPtixyt4QBPKqrUQVLa2YaaZBkYwszDc3ZC5z0J05gdqpW01jpvFiPZA8FwEZAAY7lzrt3doVMDgCJh9DKVoOSYFEc03xynpsha0BfiK8OUXhEtCzbhoH0BxpEmRagC634WIeFrfi05qMQn7ZCddP9ZCSMwBEVZCeyWDgolEWTl3ecpPf8WUfxibKs3cO15fXhVPhQXPFXyq5zS9Syz1K35zBblZCPmQJlOvHEEuGTpL4dwz8ZD"
PHONE_NUMBER_ID = "762799950241046"
VERIFY_TOKEN = "FARABOT" #token webhook
API_URL = f"https://graph.facebook.com/v22.0/762799950241046/messages"

user_id = "524611777249" # borrar esta 

# Menú principal
def send_menu(user_id):
    body = {
        "messaging_product": "whatsapp",
        "to": user_id,
        "type": "interactive",
        "interactive": {
            "type": "button",
            "body": {"text": "📋 *Menú Principal:* Elige una opción:"},
            "action": {
                "buttons": [
                    {"type": "reply", "reply": {"id": "opt1", "title": "Opción 1"}},
                    {"type": "reply", "reply": {"id": "opt2", "title": "Opción 2"}},
                    {"type": "reply", "reply": {"id": "opt3", "title": "Opción 3"}},
                    {"type": "reply", "reply": {"id": "opt4", "title": "Opción 4"}},
                    {"type": "reply", "reply": {"id": "opt5", "title": "Hablar con IA 🤖"}}
                ]
            }
        }
    }
    requests.post(API_URL, headers={
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }, json=body)

# Función para enviar mensajes con botón de regreso
def send_option(user_id, text):
    body = {
        "messaging_product": "whatsapp",
        "to": user_id,
        "type": "interactive",
        "interactive": {
            "type": "button",
            "body": {"text": text},
            "action": {
                "buttons": [
                    {"type": "reply", "reply": {"id": "menu", "title": "🔙 Regresar al menú"}}
                ]
            }
        }
    }
    requests.post(API_URL, headers={
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }, json=body)

# Función para enviar texto simple
def send_text(user_id, text):
    body = {
        "messaging_product": "whatsapp",
        "to": user_id,
        "type": "text",
        "text": {"body": text}
    }
    requests.post(API_URL, headers={
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }, json=body)

# Webhook para validación inicial con Meta
@app.route("/webhook", methods=["GET"])
def verify():
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")
    if mode == "subscribe" and token == VERIFY_TOKEN:
        return challenge, 200
    return "Unauthorized", 403

# Webhook de recepción de mensajes
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()
    print("🔔 Webhook recibido:", data)

    try:
        entry = data["entry"][0]["changes"][0]["value"]
        messages = entry.get("messages")
        if messages:
            msg = messages[0]
            user_id = msg["from"]
            msg_type = msg.get("type")

            # Si es mensaje interactivo (botón)
            if msg_type == "interactive":
                btn_id = msg["interactive"]["button_reply"]["id"]

                if btn_id == "opt1":
                    send_option(user_id, "ℹ️ Información sobre la Opción 1")
                elif btn_id == "opt2":
                    send_option(user_id, "📄 Detalles de la Opción 2")
                elif btn_id == "opt3":
                    send_option(user_id, "📦 Contenido exclusivo de la Opción 3")
                elif btn_id == "opt4":
                    send_option(user_id, "🔧 Servicios de la Opción 4")
                elif btn_id == "opt5":
                    send_text(user_id, "🤖 Esta opción está en desarrollo. Por favor, espere a que una persona lo atienda.")
                elif btn_id == "menu":
                    send_menu(user_id)

            # Si es mensaje de texto normal
            elif msg_type == "text":
                text = msg["text"]["body"].strip().lower()
                # Si ya se envió el menú, pero no se presiona botón
                send_text(user_id, "👤 Por favor, espere a que una persona lo atienda.")
                # También puedes guardar estado por usuario con una base de datos si quieres algo más complejo
                send_menu(user_id)
    except Exception as e:
        print("❌ Error en el webhook:", e)

    return "OK", 200

if __name__ == "__main__":
    app.run(port=5000, debug=True)
