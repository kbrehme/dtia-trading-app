
import requests

TELEGRAM_TOKEN = "7521010029:AAF87jAzPWf0Kjz9hdymPKnVbRamCVGmhZQ"
TELEGRAM_CHAT_ID = "6501591390"

def send_telegram_alert(message):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "HTML"
    }
    try:
        requests.post(url, data=payload)
    except Exception as e:
        print(f"Telegram Fehler: {e}")
