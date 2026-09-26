import os
import requests
from flask import Flask, request
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")
PAGE_ACCESS_TOKEN = os.getenv("PAGE_ACCESS_TOKEN")


# Verificação do Webhook da Meta
@app.route("/webhook", methods=["GET"])
def verify_webhook():
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        print("Webhook verificado!")
        return challenge, 200

    return "Token inválido", 403


# Receber mensagens
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()

    if data.get("object") == "page":
        for entry in data.get("entry", []):
            for event in entry.get("messaging", []):

                sender_id = event.get("sender", {}).get("id")
                message = event.get("message", {})

                if sender_id and "text" in message:
                    texto = message["text"]

                    print(f"Mensagem recebida: {texto}")

                    responder(sender_id, texto)

        return "EVENT_RECEIVED", 200

    return "IGNORED", 200


def enviar_mensagem(destinatario, texto):
    url = "https://graph.facebook.com/v23.0/me/messages"

    payload = {
        "recipient": {
            "id": destinatario
        },
        "message": {
            "text": texto
        },
        "access_token": PAGE_ACCESS_TOKEN
    }

    resposta = requests.post(url, json=payload)

    print("Resposta da Meta:", resposta.text)


def responder(sender_id, texto):
    texto = texto.lower().strip()

    if any(palavra in texto for palavra in ["oi", "olá", "ola", "bom dia", "boa tarde", "boa noite"]):
        resposta = (
            "Olá! 👋 Seja bem-vindo!\n\n"
            "Como posso ajudar?\n"
            "🚗 Ver veículos\n"
            "💰 Financiamento\n"
            "🔄 Refinanciamento\n"
            "📍 Endereço"
        )

    elif "financiamento" in texto:
        resposta = (
            "💰 Trabalhamos com financiamento de veículos.\n\n"
            "Me envie o veículo que você tem interesse e posso te orientar."
        )

    elif "refinanciamento" in texto:
        resposta = (
            "🚗 Trabalhamos com refinanciamento de veículos.\n\n"
            "Me diga o que você precisa e vamos te orientar."
        )

    elif "endereço" in texto or "endereco" in texto:
        resposta = "📍 Em breve colocaremos aqui o endereço da loja."

    elif "preço" in texto or "preco" in texto or "valor" in texto:
        resposta = (
            "💰 Qual veículo você viu no anúncio?\n"
            "Me mande o nome ou uma foto dele."
        )

    else:
        resposta = (
            "Entendi! 👍\n\n"
            "Pode me explicar um pouco melhor o que você está procurando?"
        )

    enviar_mensagem(sender_id, resposta)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)