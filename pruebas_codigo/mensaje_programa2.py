import requests

ACCESS_TOKEN = "EAAVPtixyt4QBPEpSC5NKIYsLqcMqM4TZBEb8Yi61JnZAseUZAz5SgyiCty5tXuBe5sZB75fQw8QbBcYeihpasWnGk5Rur3MmCkLaLv6xw0g1W1S2pX04bSebHPM4axbZBZBT0lUyzjZAxt0HcGbWADytJdcO9o4rhc5CBZBPJFxDzjgEsRPxP6okEYjtEtRx01n89yzRR7PeqjRtf7ZCI4vCOrrUBV7o6nd3F30QbJJ6iWB62tCEZD"
PHONE_NUMBER_ID = "762799950241046"
API_URL = f"https://graph.facebook.com/v22.0/762799950241046/messages"
number = "524611777249" # borrar esta linea

HEADERS = {
    "Authorization": f"Bearer {ACCESS_TOKEN}",
    "Content-Type": "application/json"
}

def enviar_menu(numero):
    data = {
        "messaging_product": "whatsapp",
        "to": 524611777249,
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
        "to": 524611777249,
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
        "to": 524611777249,
        "type": "text",
        "text": {"body": texto}
    }
    requests.post(API_URL, headers=HEADERS, json=data)
