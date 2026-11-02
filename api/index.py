
import os
import hmac
import logging
from decimal import Decimal
from typing import Any

import httpx
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("am-premium-bot")

app = FastAPI(title="AM Premium Telegram Bot")


@app.get("/api/telegram")
async def telegram_test():
    return {
        "ok": True,
        "message": "Endpoint Telegram aktif"
    }


BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
BOT_SECRET = os.getenv("BOT_WEBHOOK_SECRET", "").strip()
ADMIN_ID = str(os.getenv("TELEGRAM_ADMIN_ID", "392836663")).strip()

SUPABASE_URL = os.getenv("SUPABASE_URL", "").rstrip("/")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "").strip()

PRICE = int(os.getenv("PRICE_PER_UNIT", "5000"))
MIN_QUANTITY = int(os.getenv("MIN_QUANTITY", "1"))
MAX_QUANTITY = int(os.getenv("MAX_QUANTITY", "100"))

PAYMENT_INSTRUCTIONS = os.getenv(
    "PAYMENT_INSTRUCTIONS",
    "Silakan bayar melalui QRIS yang dikirimkan."
)
PAYMENT_QR_IMAGE_URL = os.getenv("PAYMENT_QR_IMAGE_URL", "").strip()
INFO_GROUP_URL = os.getenv("INFO_GROUP_URL", "https://t.me/").strip()
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "").strip().lstrip("@")

TELEGRAM_API = (
    f"https://api.telegram.org/bot{BOT_TOKEN}"
    if BOT_TOKEN else ""
)


def check_config():
    missing = []

    for name, value in [
        ("TELEGRAM_BOT_TOKEN", BOT_TOKEN),
        ("BOT_WEBHOOK_SECRET", BOT_SECRET),
        ("SUPABASE_URL", SUPABASE_URL),
        ("SUPABASE_SERVICE_ROLE_KEY", SUPABASE_KEY),
    ]:
        if not value:
            missing.append(name)

    if missing:
        raise RuntimeError(
            "Environment variable belum diatur: " + ", ".join(missing)
        )


async def telegram(method: str, payload: dict):
    check_config()

    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.post(
            f"{TELEGRAM_API}/{method}",
            json=payload
        )

    try:
        result = response.json()
    except Exception:
        raise RuntimeError("Respons Telegram tidak valid")

    if response.status_code != 200 or not result.get("ok"):
        raise RuntimeError(
            result.get("description", "Telegram API gagal")
        )

    return result.get("result")


async def send_message(
    chat_id: Any,
    text: str,
    reply_markup: dict | None = None
):
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML"
    }

    if reply_markup:
        payload["reply_markup"] = reply_markup

    return await telegram("sendMessage", payload)


async def send_photo(
    chat_id: Any,
    photo: str,
    caption: str = "",
    reply_markup: dict | None = None
):
    payload = {
        "chat_id": chat_id,
        "photo": photo,
        "caption": caption,
        "parse_mode": "HTML"
    }

    if reply_markup:
        payload["reply_markup"] = reply_markup

    return await telegram("sendPhoto", payload)


async def answer_callback(callback_id: str, text: str):
    return await telegram(
        "answerCallbackQuery",
        {
            "callback_query_id": callback_id,
            "text": text
        }
    )


async def db_request(
    method: str,
    table: str,
    params: dict | None = None,
    body: dict | list | None = None,
    prefer: str = "return=representation"
):
    check_config()

    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": prefer
    }

    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.request(
            method,
            f"{SUPABASE_URL}/rest/v1/{table}",
            params=params,
            json=body,
            headers=headers
        )

    if response.status_code >= 400:
        logger.error("Supabase error: %s", response.text)
        raise RuntimeError("Database Supabase mengalami kesalahan")

    if not response.text:
        return []

    return response.json()


async def db_rpc(function_name: str, body: dict):
    check_config()

    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json"
    }

    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.post(
            f"{SUPABASE_URL}/rest/v1/rpc/{function_name}",
            json=body,
            headers=headers
        )

    if response.status_code >= 400:
        logger.error("Supabase RPC error: %s", response.text)
        raise RuntimeError("Proses database gagal")

    if not response.text:
        return None

    return response.json()


async def claim_telegram_update(update_id: int) -> bool:
    result = await db_rpc(
        "claim_telegram_update",
        {"p_update_id": update_id}
    )
    return result is True


async def release_telegram_update(update_id: int):
    return await db_rpc(
        "release_telegram_update",
        {"p_update_id": update_id}
    )


async def create_order(user_id: str, username: str, quantity: int):
    total = quantity * PRICE

    rows = await db_request(
        "POST",
        "orders",
        body={
            "user_id": user_id,
            "username": username or None,
            "quantity": quantity,
            "total": total,
            "status": "waiting_payment"
        }
    )

    if not rows:
        raise RuntimeError("Pesanan gagal dibuat")

    return rows[0]


async def get_order(order_id: str):
    rows = await db_request(
        "GET",
        "orders",
        params={
            "id": f"eq.{order_id}",
            "select": "*",
            "limit": "1"
        }
    )

    return rows[0] if rows else None


# Mencari pesanan aktif, termasuk yang sedang menunggu verifikasi.
async def latest_waiting_order(user_id: str):
    rows = await db_request(
        "GET",
        "orders",
        params={
            "user_id": f"eq.{user_id}",
            "status": "in.(waiting_payment,waiting_review)",
            "select": "*",
            "order": "created_at.desc",
            "limit": "1"
        }
    )

    return rows[0] if rows else None


async def handle_start(chat_id: int):
    keyboard = {
        "inline_keyboard": [
            [
                {
                    "text": "🛒 Beli AM Premium",
                    "callback_data": "buy"
                }
            ],
            [
                {
                    "text": "📢 Grup Informasi",
                    "url": INFO_GROUP_URL
                }
            ],
            [
                {
                    "text": "💬 Admin CS",
                    "url": (
                        f"https://t.me/{ADMIN_USERNAME}"
                        if ADMIN_USERNAME else "https://t.me/"
                    )
                }
            ]
        ]
    }

    await send_message(
        chat_id,
        "<b>✨ AM PREMIUM STORE</b>\n\n"
        "Selamat datang di toko AM Premium.\n\n"
        "🛍️ <b>Produk:</b> AM Premium\n"
        f"💰 <b>Harga:</b> Rp{PRICE:,} / akun\n"
        "📦 Pilih menu di bawah untuk mulai memesan.",
        keyboard
    )


async def handle_buy(chat_id: int):
    quick_quantities = [1, 2, 5, 10, 20, 50]
    available = [
        quantity for quantity in quick_quantities
        if MIN_QUANTITY <= quantity <= MAX_QUANTITY
    ]

    buttons = []
    row = []

    for quantity in available:
        row.append({
            "text": f"{quantity} akun",
            "callback_data": f"quantity_{quantity}"
        })

        if len(row) == 3:
            buttons.append(row)
            row = []

    if row:
        buttons.append(row)

    buttons.append([{
        "text": "✍️ Masukkan jumlah lain",
        "callback_data": "quantity_custom"
    }])

    buttons.append([{
        "text": "⬅️ Kembali ke Menu",
        "callback_data": "home"
    }])

    keyboard = {"inline_keyboard": buttons}

    await send_message(
        chat_id,
        "<b>🛒 PEMBELIAN AM PREMIUM</b>\n\n"
        f"💰 Harga per akun: <b>Rp{PRICE:,}</b>\n"
        f"📦 Minimal pembelian: <b>{MIN_QUANTITY} akun</b>\n"
        f"📦 Maksimal pembelian: <b>{MAX_QUANTITY} akun</b>\n\n"
        "Pilih jumlah akun melalui tombol di bawah.\n"
        "Jika jumlah yang diinginkan tidak tersedia, tekan "
        "<b>Masukkan jumlah lain</b>.",
        keyboard
    )


async def handle_quantity(message: dict):
    chat_id = message["chat"]["id"]
    user = message.get("from", {})
    user_id = str(user.get("id", ""))
    username = user.get("username", "")

    text = (message.get("text") or "").strip()

    if not text.isdigit():
        return await send_message(
            chat_id,
            "Kirim jumlah dalam angka. Contoh: <code>2</code>"
        )

    quantity = int(text)

    if quantity < MIN_QUANTITY or quantity > MAX_QUANTITY:
        return await send_message(
            chat_id,
            f"Jumlah harus antara {MIN_QUANTITY} sampai {MAX_QUANTITY}."
        )

    order = await create_order(user_id, username, quantity)

    total = int(order["total"])
    order_id = order["id"]

    # Notifikasi pesanan baru kepada admin.
    try:
        await send_message(
            ADMIN_ID,
            "<b>🔔 PESANAN BARU AM PREMIUM</b>\n\n"
            f"🆔 ID Pesanan: <code>{order_id}</code>\n"
            f"👤 Username: "
            f"@{username if username else 'Tidak tersedia'}\n"
            f"🪪 User ID: <code>{user_id}</code>\n"
            f"📦 Jumlah akun: <b>{quantity}</b>\n"
            f"💰 Harga per akun: <b>Rp{PRICE:,}</b>\n"
            f"🧮 Total pembayaran: <b>Rp{total:,}</b>\n\n"
            "<i>Status: Menunggu pembayaran dan bukti transfer.</i>"
        )
    except Exception:
        logger.exception(
            "Gagal mengirim notifikasi pesanan baru ke admin"
        )

    keyboard = {
        "inline_keyboard": [
            [
                {
                    "text": "📤 Saya Sudah Bayar",
                    "callback_data": f"paid_{order_id}"
                }
            ],
            [
                {
                    "text": "💬 Hubungi Admin",
                    "url": (
                        f"https://t.me/{ADMIN_USERNAME}"
                        if ADMIN_USERNAME else "https://t.me/"
                    )
                }
            ]
        ]
    }

    await send_message(
        chat_id,
        "<b>🧾 DETAIL PESANAN</b>\n\n"
        f"🆔 ID Pesanan: <code>{order_id}</code>\n"
        f"📦 Jumlah akun: <b>{quantity}</b>\n"
        f"💰 Harga per akun: <b>Rp{PRICE:,}</b>\n"
        f"🧮 Total pembayaran: <b>Rp{total:,}</b>\n\n"
        "<b>💳 CARA PEMBAYARAN</b>\n"
        f"{PAYMENT_INSTRUCTIONS}\n\n"
        "Silakan lakukan pembayaran sesuai total di atas.\n"
        "Setelah membayar, tekan tombol <b>Saya Sudah Bayar</b> "
        "dan kirim foto bukti pembayaran.",
        keyboard
    )

    if PAYMENT_QR_IMAGE_URL:
        try:
            await send_photo(
                chat_id,
                PAYMENT_QR_IMAGE_URL,
                "📷 <b>QRIS PEMBAYARAN</b>\n\n"
                "Scan QRIS ini dan bayar sesuai total pesanan."
            )
        except Exception:
            logger.exception("Gagal mengirim foto QRIS")
            await send_message(
                chat_id,
                "⚠️ Foto QRIS gagal dikirim. "
                "Silakan hubungi admin."
            )


# PERBAIKAN: Pemeriksaan status pesanan ketika tombol pembayaran ditekan.
async def handle_paid(callback: dict, order_id: str):
    user_id = str(callback["from"]["id"])
    chat_id = callback["message"]["chat"]["id"]

    order = await get_order(order_id)

    if not order:
        return await send_message(chat_id, "Pesanan tidak ditemukan.")

    if str(order["user_id"]) != user_id:
        return await send_message(
            chat_id,
            "Pesanan ini bukan milik akun Anda."
        )

    status = order.get("status")

    if status == "waiting_review":
        return await send_message(
            chat_id,
            "✅ <b>BUKTI PEMBAYARAN SUDAH DITERIMA</b>\n\n"
            f"🆔 ID Pesanan: <code>{order_id}</code>\n"
            "Bukti pembayaran Anda sedang diperiksa admin.\n"
            "Mohon tunggu hasil verifikasi."
        )

    if status == "rejected":
        return await send_message(
            chat_id,
            "❌ <b>PESANAN DITOLAK</b>\n\n"
            f"🆔 ID Pesanan: <code>{order_id}</code>\n"
            "Pembayaran pesanan ini belum diterima oleh admin.\n"
            "Silakan hubungi admin jika ingin mendapatkan bantuan."
        )

    if status != "waiting_payment":
        return await send_message(
            chat_id,
            "ℹ️ <b>STATUS PESANAN</b>\n\n"
            f"🆔 ID Pesanan: <code>{order_id}</code>\n"
            "Pesanan ini sudah diproses atau tidak lagi "
            "menunggu pembayaran.\n"
            f"Status saat ini: <code>{status}</code>"
        )

    await send_message(
        chat_id,
        "📤 <b>KIRIM BUKTI PEMBAYARAN</b>\n\n"
        "Silakan kirim <b>foto bukti pembayaran</b> di chat ini.\n"
        "Pastikan nominal dan status pembayaran terlihat jelas."
    )


# PERBAIKAN: Penerimaan foto dan pencegahan bukti ganda.

async def handle_photo(message: dict):
    chat_id = message["chat"]["id"]
    user_id = str(message["from"]["id"])

    photos = message.get("photo", [])

    if not photos:
        return await send_message(
            chat_id,
            "Foto bukti tidak ditemukan."
        )

    file_id = photos[-1]["file_id"]

    order = await latest_waiting_order(user_id)

    if not order:
        return await send_message(
            chat_id,
            "Tidak ada pesanan aktif yang menunggu pembayaran.\n\n"
            "Silakan buat pesanan baru melalui menu /start."
        )

    order_id = order["id"]
    status = order.get("status")

    # Jika sudah menunggu verifikasi, coba kirim ulang
    # bukti yang tersimpan ke admin.
    if status == "waiting_review":
        saved_file_id = order.get("proof_file_id") or file_id

        if not order.get("proof_file_id"):
            await db_request(
                "PATCH",
                "orders",
                params={
                    "id": f"eq.{order_id}",
                    "status": "eq.waiting_review"
                },
                body={"proof_file_id": saved_file_id}
            )

        file_id = saved_file_id

    elif status == "waiting_payment":
        # Ubah status hanya jika masih menunggu pembayaran.
        updated_rows = await db_request(
            "PATCH",
            "orders",
            params={
                "id": f"eq.{order_id}",
                "user_id": f"eq.{user_id}",
                "status": "eq.waiting_payment"
            },
            body={
                "status": "waiting_review",
                "proof_file_id": file_id
            }
        )

        if not updated_rows:
            latest_order = await get_order(str(order_id))

            if not latest_order:
                return await send_message(
                    chat_id,
                    "Pesanan tidak ditemukan."
                )

            if latest_order.get("status") == "waiting_review":
                file_id = latest_order.get("proof_file_id") or file_id
                order = latest_order
            else:
                return await send_message(
                    chat_id,
                    "Status pesanan berubah. Silakan hubungi admin."
                )
        else:
            order = updated_rows[0]

    else:
        return await send_message(
            chat_id,
            "Pesanan ini tidak sedang menunggu pembayaran.\n"
            "Silakan hubungi admin jika status pesanan tidak sesuai."
        )

    keyboard = {
        "inline_keyboard": [
            [
                {
                    "text": "💰 DANA MASUK",
                    "callback_data": f"approve_{order_id}"
                },
                {
                    "text": "❌ DANA TIDAK MASUK",
                    "callback_data": f"reject_{order_id}"
                }
            ]
        ]
    }

    try:
        await send_photo(
            ADMIN_ID,
            file_id,
            "<b>🔔 BUKTI PEMBAYARAN AM PREMIUM</b>\n\n"
            f"🆔 ID Pesanan: <code>{order_id}</code>\n"
            f"👤 Username: "
            f"@{message.get('from', {}).get('username', 'Tidak tersedia')}\n"
            f"🪪 User ID: <code>{user_id}</code>\n"
            f"📦 Jumlah akun: <b>{order['quantity']}</b>\n"
            f"💰 Total pembayaran: "
            f"<b>Rp{int(order['total']):,}</b>\n\n"
            "<i>Silakan periksa bukti transfer sebelum memilih keputusan.</i>",
            keyboard
        )

    except Exception as e:
        logger.exception(
            "Gagal mengirim bukti ke admin. Order ID: %s",
            order_id
        )

        return await send_message(
            chat_id,
            "⚠️ <b>Bukti transfer sudah tersimpan.</b>\n\n"
            "Namun bot belum berhasil mengirim notifikasi ke admin.\n"
            "Silakan pastikan admin sudah menekan /start pada bot.\n\n"
            "Anda boleh kirim ulang foto bukti transfer untuk "
            "mencoba mengirim notifikasi kembali."
        )

    await send_message(
        chat_id,
        "✅ <b>Bukti pembayaran berhasil dikirim.</b>\n\n"
        "Bukti sudah diteruskan kepada admin.\n"
        "Admin akan memeriksa pembayaran Anda.\n"
        "Mohon tunggu verifikasi."
    )


    if status != "waiting_payment":
        return await send_message(
            chat_id,
            "Pesanan ini tidak sedang menunggu pembayaran.\n"
            "Silakan hubungi admin jika status pesanan tidak sesuai."
        )

    # Update hanya jika status masih waiting_payment.
    updated_rows = await db_request(
        "PATCH",
        "orders",
        params={
            "id": f"eq.{order_id}",
            "user_id": f"eq.{user_id}",
            "status": "eq.waiting_payment"
        },
        body={
            "status": "waiting_review",
            "proof_file_id": file_id
        }
    )

    # Jika update tidak berhasil, periksa status terbaru.
    if not updated_rows:
        latest_order = await get_order(str(order_id))

        if latest_order and latest_order.get("status") == "waiting_review":
            return await send_message(
                chat_id,
                "✅ <b>BUKTI PEMBAYARAN SUDAH DITERIMA</b>\n\n"
                "Pesanan Anda sedang diperiksa admin.\n"
                "Mohon tunggu verifikasi."
            )

        return await send_message(
            chat_id,
            "⚠️ Status pesanan berubah sehingga bukti belum dapat "
            "diproses. Silakan hubungi admin."
        )

    # Gunakan data hasil update.
    order = updated_rows[0]

    keyboard = {
        "inline_keyboard": [
            [
                {
                    "text": "💰 DANA MASUK",
                    "callback_data": f"approve_{order_id}"
                },
                {
                    "text": "❌ DANA TIDAK MASUK",
                    "callback_data": f"reject_{order_id}"
                }
            ]
        ]
    }

    try:
        await send_photo(
            ADMIN_ID,
            file_id,
            "<b>🔔 BUKTI PEMBAYARAN BARU</b>\n\n"
            f"🆔 ID Pesanan: <code>{order_id}</code>\n"
            f"👤 Username: "
            f"@{message.get('from', {}).get('username', 'Tidak tersedia')}\n"
            f"🪪 User ID: <code>{user_id}</code>\n"
            f"📦 Jumlah akun: <b>{order['quantity']}</b>\n"
            f"💰 Total pembayaran: "
            f"<b>Rp{int(order['total']):,}</b>\n\n"
            "<i>Silakan periksa bukti transfer sebelum memilih keputusan.</i>",
            keyboard
        )
    except Exception:
        logger.exception(
            "Gagal mengirim bukti transfer ke admin untuk pesanan %s",
            order_id
        )

        await send_message(
            chat_id,
            "⚠️ Bukti tersimpan, tetapi notifikasi ke admin gagal dikirim.\n"
            "Silakan hubungi admin agar bukti Anda diperiksa."
        )
        raise

    await send_message(
        chat_id,
        "✅ <b>Bukti pembayaran berhasil dikirim.</b>\n\n"
        "Admin akan memeriksa pembayaran Anda.\n"
        "Mohon tunggu verifikasi."
    )


async def handle_admin_decision(callback: dict, approve: bool, order_id: str):
    admin_id = str(callback["from"]["id"])
    chat_id = callback["message"]["chat"]["id"]

    if admin_id != ADMIN_ID:
        return await send_message(chat_id, "⛔ Akses ditolak.")

    order = await get_order(order_id)

    if not order:
        return await send_message(chat_id, "Pesanan tidak ditemukan.")

    if order["status"] != "waiting_review":
        return await send_message(
            chat_id,
            "Pesanan sudah diproses atau tidak menunggu verifikasi."
        )

    if not approve:
        updated_rows = await db_request(
            "PATCH",
            "orders",
            params={
                "id": f"eq.{order_id}",
                "status": "eq.waiting_review"
            },
            body={"status": "rejected"}
        )

        if not updated_rows:
            return await send_message(
                chat_id,
                "Pesanan sudah berubah status atau sudah diproses."
            )

        await send_message(
            order["user_id"],
            "❌ <b>PEMBAYARAN BELUM DITERIMA</b>\n\n"
            f"🆔 ID Pesanan: <code>{order_id}</code>\n"
            "Admin belum menerima pembayaran untuk pesanan ini.\n\n"
            "Silakan periksa kembali pembayaran atau hubungi admin."
        )

        return await send_message(
            chat_id,
            f"❌ Pesanan <code>{order_id}</code> "
            "ditandai DANA TIDAK MASUK."
        )

    result = await db_rpc(
        "approve_order",
        {"p_order_id": order_id}
    )

    if not result or not result.get("success"):
        reason = (
            result.get("message", "Stok tidak tersedia")
            if result else "Proses gagal"
        )
        return await send_message(chat_id, f"❌ {reason}")

    accounts = result.get("accounts", [])

    if not accounts:
        return await send_message(
            chat_id,
            "Pesanan diproses tetapi data stok kosong. Periksa database."
        )

    delivery = "\n".join(
        f"{index + 1}. <code>{item}</code>"
        for index, item in enumerate(accounts)
    )

    await send_message(
        order["user_id"],
        "<b>✅ PEMBAYARAN DISETUJUI</b>\n\n"
        f"🆔 ID Pesanan: <code>{order_id}</code>\n"
        f"📦 Jumlah akun: <b>{len(accounts)}</b>\n\n"
        "<b>📦 DATA PESANAN:</b>\n"
        f"{delivery}\n\n"
        "Terima kasih telah melakukan pembelian."
    )

    await send_message(
        chat_id,
        "✅ <b>DANA MASUK - PESANAN BERHASIL</b>\n\n"
        f"🆔 ID Pesanan: <code>{order_id}</code>\n"
        f"📦 Jumlah akun dikirim: <b>{len(accounts)}</b>\n"
        "Data pesanan berhasil dikirim kepada pembeli."
    )


async def handle_callback(callback: dict):
    callback_id = callback["id"]
    data = callback.get("data", "")
    chat_id = callback["message"]["chat"]["id"]

    await answer_callback(callback_id, "Diproses...")

    if data == "buy":
        return await handle_buy(chat_id)

    if data == "home":
        return await handle_start(chat_id)

    if data == "quantity_custom":
        return await send_message(
            chat_id,
            "✍️ <b>MASUKKAN JUMLAH AKUN</b>\n\n"
            f"Ketik jumlah antara {MIN_QUANTITY} sampai {MAX_QUANTITY}.\n"
            "Contoh: <code>3</code>"
        )

    if data.startswith("quantity_"):
        quantity = data[len("quantity_"):]

        if not quantity.isdigit():
            return await send_message(chat_id, "Jumlah tidak valid.")

        synthetic_message = {
            "chat": {"id": chat_id},
            "from": callback.get("from", {}),
            "text": quantity
        }

        return await handle_quantity(synthetic_message)

    if data.startswith("paid_"):
        return await handle_paid(callback, data[5:])

    if data.startswith("approve_"):
        return await handle_admin_decision(
            callback, True, data[8:]
        )

    if data.startswith("reject_"):
        return await handle_admin_decision(
            callback, False, data[7:]
        )


async def process_update(update: dict):
    if "callback_query" in update:
        return await handle_callback(update["callback_query"])

    message = update.get("message")

    if not message:
        return

    if message.get("photo"):
        return await handle_photo(message)

    text = (message.get("text") or "").strip()

    if text.startswith("/start"):
        return await handle_start(message["chat"]["id"])

    if text.startswith("/beli"):
        return await handle_buy(message["chat"]["id"])

    if text.isdigit():
        return await handle_quantity(message)


@app.get("/")
async def home():
    return {
        "ok": True,
        "message": "AM Premium Bot API aktif"
    }


@app.post("/")
@app.post("/api/telegram")
async def telegram_webhook(request: Request):
    received_secret = request.headers.get(
        "X-Telegram-Bot-Api-Secret-Token", ""
    ).strip()

    logger.info(
        "Webhook masuk; secret_header_present=%s; secret_match=%s",
        bool(received_secret),
        bool(BOT_SECRET) and hmac.compare_digest(
            received_secret, BOT_SECRET
        )
    )

    if not BOT_SECRET:
        logger.error("BOT_WEBHOOK_SECRET belum diatur")
        raise HTTPException(
            status_code=500,
            detail="BOT_WEBHOOK_SECRET belum diatur"
        )

    if not hmac.compare_digest(received_secret, BOT_SECRET):
        logger.warning("Webhook secret tidak cocok")
        raise HTTPException(
            status_code=403,
            detail="Forbidden"
        )

    update_id = None

    try:
        update = await request.json()
        update_id = update.get("update_id")

        # Cegah update Telegram yang sama diproses dua kali.
        if update_id is not None:
            is_new = await claim_telegram_update(int(update_id))

            if not is_new:
                logger.info(
                    "Update duplikat diabaikan: %s",
                    update_id
                )
                return JSONResponse({"ok": True})

        await process_update(update)

        return JSONResponse({"ok": True})

    except Exception:
        logger.exception("Gagal memproses update Telegram")

        if update_id is not None:
            try:
                await release_telegram_update(int(update_id))
            except Exception:
                logger.exception(
                    "Gagal menghapus klaim update: %s",
                    update_id
                )

        return JSONResponse(
            {
                "ok": False,
                "error": "Internal server error"
            },
            status_code=500
        )
