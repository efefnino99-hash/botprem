
import os
import hmac
import html
import logging
from typing import Any

import httpx
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse


# =========================================================
# LOGGING & FASTAPI
# =========================================================

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("am-premium-bot")

app = FastAPI(title="AM Premium Telegram Bot")


# =========================================================
# KONFIGURASI
# =========================================================

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
BOT_SECRET = os.getenv("BOT_WEBHOOK_SECRET", "").strip()

ADMIN_ID = str(
    os.getenv("TELEGRAM_ADMIN_ID", "392836663")
).strip()

SUPABASE_URL = os.getenv(
    "SUPABASE_URL", ""
).rstrip("/")

SUPABASE_KEY = os.getenv(
    "SUPABASE_SERVICE_ROLE_KEY", ""
).strip()

PRICE = int(os.getenv("PRICE_PER_UNIT", "10000"))
MIN_QUANTITY = int(os.getenv("MIN_QUANTITY", "1"))
MAX_QUANTITY = int(os.getenv("MAX_QUANTITY", "100"))

PRODUCT_NAME = "AM Premium"

PAYMENT_INSTRUCTIONS = os.getenv(
    "PAYMENT_INSTRUCTIONS",
    "Silakan bayar melalui QRIS yang dikirimkan."
)

PAYMENT_QR_IMAGE_URL = os.getenv(
    "PAYMENT_QR_IMAGE_URL", ""
).strip()

INFO_GROUP_URL = os.getenv(
    "INFO_GROUP_URL", "https://t.me/"
).strip()

ADMIN_USERNAME = os.getenv(
    "ADMIN_USERNAME", ""
).strip().lstrip("@")

TELEGRAM_API = (
    f"https://api.telegram.org/bot{BOT_TOKEN}"
    if BOT_TOKEN else ""
)


# =========================================================
# VALIDASI KONFIGURASI
# =========================================================

def check_config():
    missing = []

    required = {
        "TELEGRAM_BOT_TOKEN": BOT_TOKEN,
        "BOT_WEBHOOK_SECRET": BOT_SECRET,
        "SUPABASE_URL": SUPABASE_URL,
        "SUPABASE_SERVICE_ROLE_KEY": SUPABASE_KEY,
    }

    for name, value in required.items():
        if not value:
            missing.append(name)

    if missing:
        raise RuntimeError(
            "Environment variable belum diatur: "
            + ", ".join(missing)
        )


# =========================================================
# TELEGRAM API
# =========================================================

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
        raise RuntimeError(
            "Respons Telegram tidak valid"
        )

    if response.status_code != 200 or not result.get("ok"):
        raise RuntimeError(
            result.get(
                "description",
                "Telegram API gagal"
            )
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
        "parse_mode": "HTML",
        "disable_web_page_preview": True
    }

    if reply_markup:
        payload["reply_markup"] = reply_markup

    return await telegram(
        "sendMessage",
        payload
    )


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

    return await telegram(
        "sendPhoto",
        payload
    )


async def answer_callback(
    callback_id: str,
    text: str = "Diproses..."
):
    return await telegram(
        "answerCallbackQuery",
        {
            "callback_query_id": callback_id,
            "text": text
        }
    )


# =========================================================
# SUPABASE DATABASE
# =========================================================

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
        logger.error(
            "Supabase error [%s]: %s",
            response.status_code,
            response.text
        )

        raise RuntimeError(
            "Database Supabase mengalami kesalahan"
        )

    if not response.text:
        return []

    return response.json()


async def db_rpc(
    function_name: str,
    body: dict
):
    check_config()

    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json"
    }

    async with httpx.AsyncClient(timeout=60) as client:
        response = await client.post(
            f"{SUPABASE_URL}/rest/v1/rpc/{function_name}",
            json=body,
            headers=headers
        )

    if response.status_code >= 400:
        logger.error(
            "Supabase RPC error [%s]: %s",
            response.status_code,
            response.text
        )

        raise RuntimeError(
            "Proses database gagal"
        )

    if not response.text:
        return None

    return response.json()


# =========================================================
# WEBHOOK UPDATE PROTECTION
# =========================================================

async def claim_telegram_update(
    update_id: int
) -> bool:

    result = await db_rpc(
        "claim_telegram_update",
        {
            "p_update_id": update_id
        }
    )

    return result is True


async def release_telegram_update(
    update_id: int
):
    return await db_rpc(
        "release_telegram_update",
        {
            "p_update_id": update_id
        }
    )


# =========================================================
# ORDER MANAGEMENT
# =========================================================

async def create_order(
    user_id: str,
    username: str,
    quantity: int
):
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
        raise RuntimeError(
            "Pesanan gagal dibuat"
        )

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


async def latest_waiting_order(
    user_id: str
):
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


async def available_inventory_count():
    rows = await db_request(
        "GET",
        "am_inventory",
        params={
            "status": "eq.available",
            "select": "id",
            "limit": str(MAX_QUANTITY)
        }
    )

    return len(rows)


# =========================================================
# MENU UTAMA
# =========================================================

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
                        if ADMIN_USERNAME
                        else "https://t.me/"
                    )
                }
            ]
        ]
    }

    await send_message(
        chat_id,
        "<b>✨ AM PREMIUM STORE</b>\n\n"
        "Selamat datang di toko AM Premium.\n\n"
        f"🛍️ <b>Produk:</b> {PRODUCT_NAME}\n"
        f"💰 <b>Harga:</b> Rp{PRICE:,} / akun\n"
        "📦 Pilih menu di bawah untuk mulai memesan.",
        keyboard
    )


# =========================================================
# MENU PEMBELIAN
# =========================================================

async def handle_buy(chat_id: int):

    try:
        stock = await available_inventory_count()
    except Exception:
        logger.exception(
            "Gagal membaca stok inventaris"
        )

        return await send_message(
            chat_id,
            "⚠️ Stok sedang tidak dapat diperiksa.\n"
            "Silakan coba beberapa saat lagi."
        )

    if stock < MIN_QUANTITY:
        return await send_message(
            chat_id,
            "❌ <b>STOK SEDANG HABIS</b>\n\n"
            "Silakan hubungi admin untuk informasi stok."
        )

    quick_quantities = [1, 2, 5, 10, 20, 50]

    available = [
        quantity
        for quantity in quick_quantities
        if MIN_QUANTITY <= quantity <= min(
            MAX_QUANTITY,
            stock
        )
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

    buttons.append([
        {
            "text": "✍️ Masukkan jumlah lain",
            "callback_data": "quantity_custom"
        }
    ])

    buttons.append([
        {
            "text": "⬅️ Kembali ke Menu",
            "callback_data": "home"
        }
    ])

    keyboard = {
        "inline_keyboard": buttons
    }

    await send_message(
        chat_id,
        "<b>🛒 PEMBELIAN AM PREMIUM</b>\n\n"
        f"💰 Harga per akun: <b>Rp{PRICE:,}</b>\n"
        f"📦 Minimal pembelian: <b>{MIN_QUANTITY}</b>\n"
        f"📦 Maksimal pembelian: <b>{min(MAX_QUANTITY, stock)}</b>\n"
        f"📊 Stok tersedia: <b>{stock}</b>\n\n"
        "Pilih jumlah akun melalui tombol di bawah.",
        keyboard
    )


# =========================================================
# MEMBUAT PESANAN
# =========================================================

async def handle_quantity(message: dict):

    chat_id = message["chat"]["id"]

    user = message.get("from", {})

    user_id = str(user.get("id", ""))

    username = user.get("username", "")

    text = (
        message.get("text") or ""
    ).strip()

    if not text.isdigit():
        return await send_message(
            chat_id,
            "Kirim jumlah dalam angka.\n"
            "Contoh: <code>2</code>"
        )

    quantity = int(text)

    if quantity < MIN_QUANTITY or quantity > MAX_QUANTITY:
        return await send_message(
            chat_id,
            f"Jumlah harus antara {MIN_QUANTITY} "
            f"sampai {MAX_QUANTITY}."
        )

    try:
        stock = await available_inventory_count()
    except Exception:
        logger.exception(
            "Gagal memeriksa stok"
        )

        return await send_message(
            chat_id,
            "⚠️ Tidak dapat memeriksa stok saat ini."
        )

    if quantity > stock:
        return await send_message(
            chat_id,
            "❌ <b>STOK TIDAK MENCUKUPI</b>\n\n"
            f"Permintaan: {quantity} akun\n"
            f"Stok tersedia: {stock} akun\n\n"
            "Silakan pilih jumlah yang lebih kecil."
        )

    try:
        order = await create_order(
            user_id,
            username,
            quantity
        )
    except Exception:
        logger.exception(
            "Gagal membuat pesanan"
        )

        return await send_message(
            chat_id,
            "⚠️ Pesanan gagal dibuat.\n"
            "Silakan coba kembali."
        )

    total = int(order["total"])

    order_id = str(order["id"])

    safe_username = html.escape(
        username or "Tidak tersedia"
    )

    # Notifikasi pesanan kepada admin.
    try:
        await send_message(
            ADMIN_ID,
            "<b>🔔 PESANAN BARU AM PREMIUM</b>\n\n"
            f"🆔 ID Pesanan: <code>{html.escape(order_id)}</code>\n"
            f"👤 Username: @{safe_username}\n"
            f"🪪 User ID: <code>{user_id}</code>\n"
            f"📦 Jumlah akun: <b>{quantity}</b>\n"
            f"💰 Harga per akun: <b>Rp{PRICE:,}</b>\n"
            f"🧮 Total: <b>Rp{total:,}</b>\n\n"
            "<i>Status: Menunggu pembayaran.</i>"
        )
    except Exception:
        logger.exception(
            "Gagal mengirim notifikasi pesanan kepada admin"
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
                        if ADMIN_USERNAME
                        else "https://t.me/"
                    )
                }
            ]
        ]
    }

    await send_message(
        chat_id,
        "<b>🧾 DETAIL PESANAN</b>\n\n"
        f"🆔 ID Pesanan: <code>{html.escape(order_id)}</code>\n"
        f"📦 Jumlah akun: <b>{quantity}</b>\n"
        f"💰 Harga per akun: <b>Rp{PRICE:,}</b>\n"
        f"🧮 Total pembayaran: <b>Rp{total:,}</b>\n\n"
        "<b>💳 CARA PEMBAYARAN</b>\n"
        f"{html.escape(PAYMENT_INSTRUCTIONS)}\n\n"
        "Silakan lakukan pembayaran sesuai total.\n"
        "Setelah membayar, tekan tombol "
        "<b>Saya Sudah Bayar</b> dan kirim foto bukti pembayaran.",
        keyboard
    )

    if PAYMENT_QR_IMAGE_URL:
        try:
            await send_photo(
                chat_id,
                PAYMENT_QR_IMAGE_URL,
                "📷 <b>QRIS PEMBAYARAN</b>\n\n"
                "Scan QRIS dan bayar sesuai total pesanan."
            )
        except Exception:
            logger.exception(
                "Gagal mengirim foto QRIS"
            )


# =========================================================
# TOMBOL SAYA SUDAH BAYAR
# =========================================================

async def handle_paid(
    callback: dict,
    order_id: str
):

    user_id = str(
        callback["from"]["id"]
    )

    chat_id = callback["message"]["chat"]["id"]

    order = await get_order(order_id)

    if not order:
        return await send_message(
            chat_id,
            "Pesanan tidak ditemukan."
        )

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
            f"ID Pesanan: <code>{html.escape(order_id)}</code>\n"
            "Bukti pembayaran sedang diperiksa admin."
        )

    if status == "rejected":
        return await send_message(
            chat_id,
            "❌ <b>PESANAN DITOLAK</b>\n\n"
            "Silakan hubungi admin untuk informasi lebih lanjut."
        )

    if status != "waiting_payment":
        return await send_message(
            chat_id,
            "ℹ️ Pesanan sudah diproses atau tidak "
            "menunggu pembayaran.\n"
            f"Status: <code>{html.escape(str(status))}</code>"
        )

    await send_message(
        chat_id,
        "📤 <b>KIRIM BUKTI PEMBAYARAN</b>\n\n"
        "Silakan kirim foto bukti pembayaran di chat ini.\n"
        "Pastikan nominal dan status pembayaran terlihat jelas."
    )


# =========================================================
# MENERIMA FOTO BUKTI PEMBAYARAN
# =========================================================

async def handle_photo(message: dict):

    chat_id = message["chat"]["id"]

    user_id = str(
        message["from"]["id"]
    )

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
            "Silakan buat pesanan baru melalui /start."
        )

    order_id = str(order["id"])

    status = order.get("status")

    # Jika bukti sudah tersimpan, gunakan bukti lama.
    if status == "waiting_review":

        saved_file_id = order.get("proof_file_id")

        if not saved_file_id:
            return await send_message(
                chat_id,
                "Bukti sebelumnya belum tercatat dengan benar. "
                "Silakan hubungi admin."
            )

        file_id = saved_file_id

    elif status == "waiting_payment":

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
            latest = await get_order(order_id)

            if (
                latest
                and latest.get("status") == "waiting_review"
                and latest.get("proof_file_id")
            ):
                order = latest
                file_id = latest["proof_file_id"]
            else:
                return await send_message(
                    chat_id,
                    "Status pesanan berubah. "
                    "Silakan hubungi admin."
                )

        else:
            order = updated_rows[0]

    else:
        return await send_message(
            chat_id,
            "Pesanan tidak sedang menunggu pembayaran."
        )

    username = (
        message.get("from", {}).get("username")
        or "Tidak tersedia"
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
            f"🆔 ID Pesanan: <code>{html.escape(order_id)}</code>\n"
            f"👤 Username: @{html.escape(username)}\n"
            f"🪪 User ID: <code>{user_id}</code>\n"
            f"📦 Jumlah akun: <b>{order['quantity']}</b>\n"
            f"💰 Total: <b>Rp{int(order['total']):,}</b>\n\n"
            "<i>Periksa pembayaran sebelum mengambil keputusan.</i>",
            keyboard
        )

    except Exception:
        logger.exception(
            "Gagal mengirim bukti kepada admin: %s",
            order_id
        )

        return await send_message(
            chat_id,
            "⚠️ <b>Bukti pembayaran sudah tersimpan.</b>\n\n"
            "Namun notifikasi ke admin gagal dikirim.\n"
            "Silakan hubungi admin agar bukti diperiksa."
        )

    await send_message(
        chat_id,
        "✅ <b>BUKTI PEMBAYARAN BERHASIL DIKIRIM</b>\n\n"
        "Bukti sudah diteruskan kepada admin.\n"
        "Mohon tunggu verifikasi pembayaran."
    )


# =========================================================
# PENGIRIMAN DATA AKUN KEPADA PEMBELI
# =========================================================

async def send_order_accounts(
    user_id: str,
    order_id: str,
    accounts: list
):
    if not accounts:
        raise RuntimeError(
            "Data akun kosong"
        )

    await send_message(
        user_id,
        "<b>✅ PEMBAYARAN BERHASIL DIVERIFIKASI</b>\n\n"
        f"🆔 ID Pesanan: <code>{html.escape(order_id)}</code>\n"
        f"📦 Jumlah akun: <b>{len(accounts)}</b>\n\n"
        "Berikut detail akun AM Premium Anda."
    )

    # Maksimal 8 akun dalam satu pesan.
    for start in range(0, len(accounts), 8):

        chunk = accounts[start:start + 8]

        lines = []

        for index, item in enumerate(chunk, start=start + 1):

            email = html.escape(
                str(item.get("email", ""))
            )

            login_url = html.escape(
                str(item.get("login_url", "")),
                quote=True
            )

            expiry = html.escape(
                str(item.get("expiry", ""))
            )

            lines.append(
                f"<b>📦 AKUN {index}</b>\n"
                f"📧 Email: <code>{email}</code>\n"
                f"🌐 Login: {login_url}\n"
                f"📅 Berlaku sampai: <b>{expiry}</b>"
            )

        await send_message(
            user_id,
            "<b>DETAIL AKUN AM PREMIUM</b>\n\n"
            + "\n\n".join(lines)
        )

    await send_message(
        user_id,
        "🎉 <b>PESANAN SELESAI</b>\n\n"
        "Seluruh data akun telah dikirim.\n"
        "Terima kasih telah berbelanja."
    )


# =========================================================
# ADMIN: DANA MASUK / DANA TIDAK MASUK
# =========================================================

async def handle_admin_decision(
    callback: dict,
    approve: bool,
    order_id: str
):

    admin_id = str(
        callback["from"]["id"]
    )

    chat_id = callback["message"]["chat"]["id"]

    # Validasi ID admin.
    if admin_id != ADMIN_ID:
        return await send_message(
            chat_id,
            "⛔ Akses ditolak. Anda bukan admin."
        )

    order = await get_order(order_id)

    if not order:
        return await send_message(
            chat_id,
            "Pesanan tidak ditemukan."
        )

    # =====================================================
    # DANA TIDAK MASUK
    # =====================================================

    if not approve:

        if order.get("status") != "waiting_review":
            return await send_message(
                chat_id,
                "Pesanan sudah diproses atau "
                "tidak menunggu verifikasi."
            )

        updated_rows = await db_request(
            "PATCH",
            "orders",
            params={
                "id": f"eq.{order_id}",
                "status": "eq.waiting_review"
            },
            body={
                "status": "rejected"
            }
        )

        if not updated_rows:
            return await send_message(
                chat_id,
                "Pesanan sudah berubah status."
            )

        await send_message(
            order["user_id"],
            "<b>❌ PEMBAYARAN BELUM DITERIMA</b>\n\n"
            f"🆔 ID Pesanan: <code>{html.escape(order_id)}</code>\n"
            "Admin belum menerima pembayaran.\n"
            "Silakan hubungi admin jika ada kesalahan."
        )

        return await send_message(
            chat_id,
            "❌ <b>DANA TIDAK MASUK</b>\n\n"
            f"ID Pesanan: <code>{html.escape(order_id)}</code>\n"
            "Status pesanan berhasil diperbarui."
        )

    # =====================================================
    # DANA MASUK
    # =====================================================

    try:

        result = await db_rpc(
            "approve_order_from_inventory",
            {
                "p_order_id": str(order_id)
            }
        )

        # Antisipasi hasil RPC berbentuk list.
        if isinstance(result, list):
            result = result[0] if result else None

    except Exception:
        logger.exception(
            "RPC alokasi inventaris gagal: %s",
            order_id
        )

        return await send_message(
            chat_id,
            "⚠️ <b>GAGAL MEMPROSES PESANAN</b>\n\n"
            "Database tidak berhasil mengalokasikan stok.\n"
            "Silakan periksa log Vercel dan Supabase."
        )

    if not isinstance(result, dict):
        return await send_message(
            chat_id,
            "⚠️ Respons database tidak valid."
        )

    if not result.get("success"):

        reason = result.get(
            "message",
            "Proses persetujuan gagal"
        )

        return await send_message(
            chat_id,
            "❌ <b>GAGAL MEMPROSES PESANAN</b>\n\n"
            f"{html.escape(str(reason))}"
        )

    accounts = result.get("accounts", [])

    if not accounts:
        return await send_message(
            chat_id,
            "⚠️ Data akun kosong.\n"
            "Silakan periksa tabel am_inventory."
        )

    # Pastikan jumlah akun sesuai pesanan.
    if len(accounts) != int(order["quantity"]):
        logger.error(
            "Jumlah akun tidak sesuai. Order=%s",
            order_id
        )

        return await send_message(
            chat_id,
            "⚠️ Jumlah akun yang dialokasikan tidak sesuai "
            "dengan jumlah pesanan. Hubungi pengelola."
        )

    # =====================================================
    # KIRIM AKUN KE PEMBELI
    # =====================================================

    try:

        await send_order_accounts(
            str(order["user_id"]),
            order_id,
            accounts
        )

    except Exception:

        logger.exception(
            "Pengiriman akun gagal untuk order %s",
            order_id
        )

        return await send_message(
            chat_id,
            "⚠️ <b>STOK SUDAH DIALOKASIKAN</b>\n\n"
            f"ID Pesanan: <code>{html.escape(order_id)}</code>\n"
            "Namun pengiriman Telegram kepada pembeli gagal.\n\n"
            "Data alokasi tetap tersimpan di Supabase. "
            "Jangan membuat alokasi stok baru untuk pesanan ini.\n"
            "Periksa koneksi Telegram dan lakukan pengiriman ulang "
            "dengan prosedur pemulihan."
        )

    # =====================================================
    # KONFIRMASI ADMIN
    # =====================================================

    return await send_message(
        chat_id,
        "✅ <b>DANA MASUK - PESANAN BERHASIL</b>\n\n"
        f"🆔 ID Pesanan: <code>{html.escape(order_id)}</code>\n"
        f"📦 Jumlah akun: <b>{len(accounts)}</b>\n"
        "📨 Data akun berhasil dikirim kepada pembeli.\n"
        "📌 Status: <b>COMPLETED</b>"
    )


# =========================================================
# CALLBACK BUTTON HANDLER
# =========================================================

async def handle_callback(callback: dict):

    callback_id = callback["id"]

    data = callback.get("data", "")

    message = callback.get("message") or {}

    chat_id = message.get("chat", {}).get("id")

    try:
        await answer_callback(
            callback_id,
            "Diproses..."
        )
    except Exception:
        logger.exception(
            "Gagal menjawab callback Telegram"
        )

    if data == "buy":
        return await handle_buy(chat_id)

    if data == "home":
        return await handle_start(chat_id)

    if data == "quantity_custom":
        return await send_message(
            chat_id,
            "✍️ <b>MASUKKAN JUMLAH AKUN</b>\n\n"
            f"Ketik jumlah antara {MIN_QUANTITY} "
            f"sampai {MAX_QUANTITY}.\n"
            "Contoh: <code>3</code>"
        )

    if data.startswith("quantity_"):

        quantity = data[len("quantity_"):]

        if not quantity.isdigit():
            return await send_message(
                chat_id,
                "Jumlah tidak valid."
            )

        synthetic_message = {
            "chat": {"id": chat_id},
            "from": callback.get("from", {}),
            "text": quantity
        }

        return await handle_quantity(
            synthetic_message
        )

    if data.startswith("paid_"):

        return await handle_paid(
            callback,
            data[5:]
        )

    if data.startswith("approve_"):

        return await handle_admin_decision(
            callback,
            True,
            data[8:]
        )

    if data.startswith("reject_"):

        return await handle_admin_decision(
            callback,
            False,
            data[7:]
        )


# =========================================================
# PROCESS TELEGRAM UPDATE
# =========================================================

async def process_update(update: dict):

    if "callback_query" in update:
        return await handle_callback(
            update["callback_query"]
        )

    message = update.get("message")

    if not message:
        return

    if message.get("photo"):
        return await handle_photo(message)

    text = (
        message.get("text") or ""
    ).strip()

    chat_id = message["chat"]["id"]

    if text.startswith("/start"):
        return await handle_start(chat_id)

    if text.startswith("/beli"):
        return await handle_buy(chat_id)

    if text.isdigit():
        return await handle_quantity(message)


# =========================================================
# HEALTH CHECK
# =========================================================

@app.get("/")
async def home():

    return {
        "ok": True,
        "message": "AM Premium Bot API aktif",
        "product": PRODUCT_NAME
    }


@app.get("/api/telegram")
async def telegram_test():

    return {
        "ok": True,
        "message": "Endpoint Telegram aktif"
    }


# =========================================================
# TELEGRAM WEBHOOK
# =========================================================

@app.post("/")
@app.post("/api/telegram")
async def telegram_webhook(request: Request):

    received_secret = request.headers.get(
        "X-Telegram-Bot-Api-Secret-Token",
        ""
    ).strip()

    if not BOT_SECRET:
        logger.error(
            "BOT_WEBHOOK_SECRET belum diatur"
        )

        raise HTTPException(
            status_code=500,
            detail="BOT_WEBHOOK_SECRET belum diatur"
        )

    if not hmac.compare_digest(
        received_secret,
        BOT_SECRET
    ):
        logger.warning(
            "Webhook secret tidak cocok"
        )

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

            is_new = await claim_telegram_update(
                int(update_id)
            )

            if not is_new:
                logger.info(
                    "Update duplikat diabaikan: %s",
                    update_id
                )

                return JSONResponse({
                    "ok": True
                })

        await process_update(update)

        return JSONResponse({
            "ok": True
        })

    except Exception:

        logger.exception(
            "Gagal memproses update Telegram"
        )

        if update_id is not None:

            try:
                await release_telegram_update(
                    int(update_id)
                )

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
