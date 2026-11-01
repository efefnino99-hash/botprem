import os
from fastapi import FastAPI, Header, HTTPException, Request

app = FastAPI(title="Telegram Store - Manual Payment")

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
BOT_SECRET = os.getenv("BOT_WEBHOOK_SECRET", "")
ADMIN_ID = os.getenv("TELEGRAM_ADMIN_ID", "392836663")

@app.get("/")
def health():
    return {
        "ok": True,
        "service": "telegram-store-manual-payment",
        "payment_mode": "manual",
        "midtrans_enabled": False,
        "implementation_status": "starter_not_production_ready"
    }

@app.post("/api/telegram")
async def telegram_webhook(
    request: Request,
    x_telegram_bot_api_secret_token: str = Header(default="")
):
    if not BOT_SECRET or x_telegram_bot_api_secret_token != BOT_SECRET:
        raise HTTPException(status_code=403, detail="Invalid Telegram webhook secret")

    update = await request.json()

    # TODO: Implementasikan handler /start, /beli, pilihan jumlah 1-100,
    # instruksi pembayaran manual, dan penerimaan foto bukti pembayaran.
    # Bukti harus diteruskan ke ADMIN_ID untuk pemeriksaan manual.
    # Jangan menandai pesanan paid hanya karena pembeli mengirim foto.
    return {"ok": True, "received": bool(update)}

@app.post("/api/admin/approve")
async def admin_approve(request: Request):
    # TODO: Batasi endpoint ini dengan secret admin terpisah dan validasi
    # identitas admin. Setelah admin memastikan dana benar-benar masuk,
    # lakukan transaksi database atomik untuk klaim stok dan membuat delivery.
    raise HTTPException(status_code=501, detail="Admin approval flow belum diimplementasikan")

@app.post("/api/admin/reject")
async def admin_reject(request: Request):
    # TODO: Implementasikan penolakan pesanan dan pemberitahuan pembeli.
    raise HTTPException(status_code=501, detail="Admin rejection flow belum diimplementasikan")
