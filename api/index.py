import os
import hmac
import requests

from fastapi import FastAPI, Request, Header, HTTPException

app = FastAPI()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
BOT_SECRET = os.getenv("BOT_WEBHOOK_SECRET", "")

INFO_GROUP = os.getenv("INFO_GROUP_URL", "")
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "")


def send_message(chat_id, text, keyboard=None):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML"
    }

    if keyboard:
        payload["reply_markup"] = keyboard

    response = requests.post(url, json=payload, timeout=15)
    response.raise_for_status()
    return response.json()


@app.get("/")
def home():
    return {"ok": True, "service": "AM Premium Bot"}


@app.post("/api/telegram")
async def telegram_webhook(
    request: Request,
    x_telegram_bot_api_secret_token: str = Header(default="")
):
    if not BOT_TOKEN or not BOT_SECRET:
        raise HTTPException(status_code=500, detail="Bot configuration missing")

    if not hmac.compare_digest(
        x_telegram_bot_api_secret_token,
        BOT_SECRET
    ):
        raise HTTPException(status_code=403, detail="Invalid secret")

    update = await request.json()

    message = update.get("message", {})
    chat = message.get("chat", {})
    chat_id = chat.get("id")
    text = message.get("text", "")

    if not chat_id:
        return {"ok": True}

    if text.startswith("/start"):
        keyboard = {
            "inline_keyboard": [
                [
                    {
                        "text": "🛒 Beli AM Prem",
                        "callback_data": "buy"
                    }
                ],
                [
                    {
                        "text": "📢 Grup Informasi",
                        "url": INFO_GROUP or "https://t.me/"
                    }
                ],
                [
                    {
                        "text": "👨‍💻 Admin CS",
                        "url": (
                            "https://t.me/" + ADMIN_USERNAME
                            if ADMIN_USERNAME
                            else "https://t.me/"
                        )
                    }
                ]
            ]
        }

        send_message(
            chat_id,
            "✨ <b>SELAMAT DATANG DI AM PREMIUM STORE</b>\n\n"
            "Selamat datang! Silakan pilih menu di bawah "
            "untuk melanjutkan.",
            keyboard
        )

    return {"ok": True}
