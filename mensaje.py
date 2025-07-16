import requests

ACCESS_TOKEN = "TU_ACCESS_TOKEN"
PHONE_NUMBER_ID = "TU_PHONE_NUMBER_ID"
API_URL = f"https://graph.facebook.com/v18.0/{PHONE_NUMBER_ID}/messages"

HEADERS = {
    "Authorization": f"Bearer {ACCESS_TOKEN}",
    "Content-Type": "application/json"
}

def enviar_menu(numero):
    data = {
        "messaging_product": "whatsapp",
        "to": numero,
        "type": "interactive",
        "interactive": {
            "type": "button",
            "body": {
                "text": "📋 *Menú Principal:* Elige una opción:"
            },
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
    requests.post(API_URL, headers=HEADERS, json=data)

def enviar_opcion(numero, texto):
    data = {
        "messaging_product": "whatsapp",
        "to": numero,
        "type": "interactive",
        "interactive": {
            "type": "button",
            "body": {"text": texto},
            "action": {
                "buttons": [
                    {"type": "reply", "reply": {"id": "menu", "title": "🔙 Regresar al menú"}}
                ]
            }
        }
    }
    requests.post(API_URL, headers=HEADERS, json=data)

def enviar_texto(numero, texto):
    data = {
        "messaging_product": "whatsapp",
        "to": numero,
        "type": "text",
        "text": {"body": texto}
    }
    requests.post(API_URL, headers=HEADERS, json=data)
