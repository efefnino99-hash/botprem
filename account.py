"""
INVENTARIS RESELLER AM PREMIUM
Data dimuat dari daftar yang diberikan pengguna.
Simpan file ini secara privat. Jangan unggah ke repository publik,
jangan kirim ke orang yang tidak berwenang, dan jangan letakkan API key di sini.

Field:
- email: identitas akun stok
- login_url: portal yang tercantum pada daftar sumber
- expiry: masa berlaku yang tercantum pada daftar sumber
- status: available / reserved / sold

Pastikan izin reseller mencakup distribusi email dan metode login.
"""

PRODUCT_NAME = "AM Premium"
UNIT_PRICE = 10000
MIN_ORDER = 1
MAX_ORDER = 100

STOCK = [
    {'email': 'nadia376@alightmotion.website', 'login_url': 'https://am.sekalipay.com', 'expiry': '01 Sep 2027', 'status': 'available'},
    {'email': 'oscarvina95@alightmotion.website', 'login_url': 'https://am.sekalipay.com', 'expiry': '01 Sep 2027', 'status': 'available'},
    {'email': 'hana662@alightmotion.website', 'login_url': 'https://am.sekalipay.com', 'expiry': '01 Sep 2027', 'status': 'available'},
    {'email': 'kevin126@alightmotion.website', 'login_url': 'https://am.sekalipay.com', 'expiry': '01 Sep 2027', 'status': 'available'},
    {'email': 'rafibagas693@alightmotion.website', 'login_url': 'https://am.sekalipay.com', 'expiry': '01 Sep 2027', 'status': 'available'},
    {'email': 'vito32@alightmotion.website', 'login_url': 'https://am.sekalipay.com', 'expiry': '01 Sep 2027', 'status': 'available'},
    {'email': 'umarcahya545@alightmotion.website', 'login_url': 'https://am.sekalipay.com', 'expiry': '01 Sep 2027', 'status': 'available'},
    {'email': 'ekailham881@alightmotion.website', 'login_url': 'https://am.sekalipay.com', 'expiry': '01 Sep 2027', 'status': 'available'},
    {'email': 'cahya406@alightmotion.website', 'login_url': 'https://am.sekalipay.com', 'expiry': '01 Sep 2027', 'status': 'available'},
    {'email': 'hendradinda442@alightmotion.website', 'login_url': 'https://am.sekalipay.com', 'expiry': '01 Sep 2027', 'status': 'available'},
    {'email': 'yudhanaufal647@alightmotion.website', 'login_url': 'https://am.sekalipay.com', 'expiry': '01 Sep 2027', 'status': 'available'},
    {'email': 'angelokta272@alightmotion.website', 'login_url': 'https://am.sekalipay.com', 'expiry': '01 Sep 2027', 'status': 'available'},
    {'email': 'elsatania306@alightmotion.website', 'login_url': 'https://am.sekalipay.com', 'expiry': '01 Sep 2027', 'status': 'available'},
    {'email': 'kaylakevin783@alightmotion.website', 'login_url': 'https://am.sekalipay.com', 'expiry': '01 Sep 2027', 'status': 'available'},
    {'email': 'zahrabagas702@alightmotion.website', 'login_url': 'https://am.sekalipay.com', 'expiry': '01 Sep 2027', 'status': 'available'},
    {'email': 'citrakevan904@alightmotion.website', 'login_url': 'https://am.sekalipay.com', 'expiry': '01 Sep 2027', 'status': 'available'},
    {'email': 'kevan892@alightmotion.website', 'login_url': 'https://am.sekalipay.com', 'expiry': '01 Sep 2027', 'status': 'available'},
    {'email': 'raka162@alightmotion.website', 'login_url': 'https://am.sekalipay.com', 'expiry': '01 Sep 2027', 'status': 'available'},
    {'email': 'lukashendra987@alightmotion.website', 'login_url': 'https://am.sekalipay.com', 'expiry': '01 Sep 2027', 'status': 'available'},
    {'email': 'aureldevi300@alightmotion.website', 'login_url': 'https://am.sekalipay.com', 'expiry': '01 Sep 2027', 'status': 'available'},
    {'email': 'rizkybella612@alightmotion.website', 'login_url': 'https://am.sekalipay.com', 'expiry': '01 Sep 2027', 'status': 'available'},
    {'email': 'oktaprita764@alightmotion.website', 'login_url': 'https://am.sekalipay.com', 'expiry': '01 Sep 2027', 'status': 'available'},
    {'email': 'sabrinacandra887@alightmotion.website', 'login_url': 'https://am.sekalipay.com', 'expiry': '01 Sep 2027', 'status': 'available'},
    {'email': 'yoga649@alightmotion.website', 'login_url': 'https://am.sekalipay.com', 'expiry': '01 Sep 2027', 'status': 'available'},
    {'email': 'bagaspandu924@alightmotion.website', 'login_url': 'https://am.sekalipay.com', 'expiry': '01 Sep 2027', 'status': 'available'},
    {'email': 'hendradinda432@alightmotion.website', 'login_url': 'https://am.sekalipay.com', 'expiry': '01 Sep 2027', 'status': 'available'},
    {'email': 'salsa637@alightmotion.website', 'login_url': 'https://am.sekalipay.com', 'expiry': '01 Sep 2027', 'status': 'available'},
    {'email': 'mikail617@alightmotion.website', 'login_url': 'https://am.sekalipay.com', 'expiry': '01 Sep 2027', 'status': 'available'},
    {'email': 'cahya106@alightmotion.website', 'login_url': 'https://am.sekalipay.com', 'expiry': '01 Sep 2027', 'status': 'available'},
    {'email': 'bellaprita940@alightmotion.website', 'login_url': 'https://am.sekalipay.com', 'expiry': '01 Sep 2027', 'status': 'available'},
    {'email': 'gilangbagas347@alightmotion.website', 'login_url': 'https://am.sekalipay.com', 'expiry': '01 Sep 2027', 'status': 'available'},
    {'email': 'bellaangel94@alightmotion.website', 'login_url': 'https://am.sekalipay.com', 'expiry': '01 Sep 2027', 'status': 'available'},
    {'email': 'bungavito47@alightmotion.website', 'login_url': 'https://am.sekalipay.com', 'expiry': '01 Sep 2027', 'status': 'available'},
    {'email': 'wulanfarel692@alightmotion.website', 'login_url': 'https://am.sekalipay.com', 'expiry': '01 Sep 2027', 'status': 'available'},
    {'email': 'sintaangel117@alightmotion.website', 'login_url': 'https://am.sekalipay.com', 'expiry': '01 Sep 2027', 'status': 'available'},
    {'email': 'pandufikri884@alightmotion.website', 'login_url': 'https://am.sekalipay.com', 'expiry': '01 Sep 2027', 'status': 'available'},
    {'email': 'wulanyoga830@alightmotion.website', 'login_url': 'https://am.sekalipay.com', 'expiry': '01 Sep 2027', 'status': 'available'},
    {'email': 'mikailokta705@alightmotion.website', 'login_url': 'https://am.sekalipay.com', 'expiry': '01 Sep 2027', 'status': 'available'},
    {'email': 'jokokevin535@alightmotion.website', 'login_url': 'https://am.sekalipay.com', 'expiry': '01 Sep 2027', 'status': 'available'},
    {'email': 'kevan941@alightmotion.website', 'login_url': 'https://am.sekalipay.com', 'expiry': '01 Sep 2027', 'status': 'available'},
    {'email': 'umarcandra367@alightmotion.website', 'login_url': 'https://am.sekalipay.com', 'expiry': '01 Sep 2027', 'status': 'available'},
    {'email': 'naufalvina531@alightmotion.website', 'login_url': 'https://am.sekalipay.com', 'expiry': '01 Sep 2027', 'status': 'available'},
    {'email': 'bungazaki209@alightmotion.website', 'login_url': 'https://am.sekalipay.com', 'expiry': '01 Sep 2027', 'status': 'available'},
    {'email': 'mikail407@alightmotion.website', 'login_url': 'https://am.sekalipay.com', 'expiry': '01 Sep 2027', 'status': 'available'},
    {'email': 'gilang520@alightmotion.website', 'login_url': 'https://am.sekalipay.com', 'expiry': '01 Sep 2027', 'status': 'available'},
    {'email': 'aureloscar589@alightmotion.website', 'login_url': 'https://am.sekalipay.com', 'expiry': '01 Sep 2027', 'status': 'available'},
    {'email': 'ilhamjoko966@alightmotion.website', 'login_url': 'https://am.sekalipay.com', 'expiry': '01 Sep 2027', 'status': 'available'},
    {'email': 'lukas193@alightmotion.website', 'login_url': 'https://am.sekalipay.com', 'expiry': '01 Sep 2027', 'status': 'available'},
    {'email': 'miranadia153@alightmotion.website', 'login_url': 'https://am.sekalipay.com', 'expiry': '01 Sep 2027', 'status': 'available'},
    {'email': 'ilhamindah598@alightmotion.website', 'login_url': 'https://am.sekalipay.com', 'expiry': '01 Sep 2027', 'status': 'available'},
    {'email': 'suryaintan199@alightmotion.website', 'login_url': 'https://am.sekalipay.com', 'expiry': '01 Sep 2027', 'status': 'available'},
    {'email': 'cahya774@alightmotion.website', 'login_url': 'https://am.sekalipay.com', 'expiry': '01 Sep 2027', 'status': 'available'},
    {'email': 'arifjihan574@alightmotion.website', 'login_url': 'https://am.sekalipay.com', 'expiry': '01 Sep 2027', 'status': 'available'},
    {'email': 'aldibrian59@alightmotion.website', 'login_url': 'https://am.sekalipay.com', 'expiry': '01 Sep 2027', 'status': 'available'},
    {'email': 'yogasinta650@alightmotion.website', 'login_url': 'https://am.sekalipay.com', 'expiry': '01 Sep 2027', 'status': 'available'},
    {'email': 'gitamira220@alightmotion.website', 'login_url': 'https://am.sekalipay.com', 'expiry': '01 Sep 2027', 'status': 'available'},
    {'email': 'rendidiaz224@alightmotion.website', 'login_url': 'https://am.sekalipay.com', 'expiry': '01 Sep 2027', 'status': 'available'},
    {'email': 'miragilang644@alightmotion.website', 'login_url': 'https://am.sekalipay.com', 'expiry': '01 Sep 2027', 'status': 'available'},
    {'email': 'mayadinda916@alightmotion.website', 'login_url': 'https://am.sekalipay.com', 'expiry': '01 Sep 2027', 'status': 'available'},
    {'email': 'bella448@alightmotion.website', 'login_url': 'https://am.sekalipay.com', 'expiry': '01 Sep 2027', 'status': 'available'},
    {'email': 'citra752@alightmotion.website', 'login_url': 'https://am.sekalipay.com', 'expiry': '01 Sep 2027', 'status': 'available'},
    {'email': 'citraoscar202@alightmotion.website', 'login_url': 'https://am.sekalipay.com', 'expiry': '01 Sep 2027', 'status': 'available'},
    {'email': 'vito850@alightmotion.website', 'login_url': 'https://am.sekalipay.com', 'expiry': '01 Sep 2027', 'status': 'available'},
    {'email': 'mikail50@alightmotion.website', 'login_url': 'https://am.sekalipay.com', 'expiry': '01 Sep 2027', 'status': 'available'},
    {'email': 'diazbagas961@alightmotion.website', 'login_url': 'https://am.sekalipay.com', 'expiry': '01 Sep 2027', 'status': 'available'},
    {'email': 'putridevi892@alightmotion.website', 'login_url': 'https://am.sekalipay.com', 'expiry': '01 Sep 2027', 'status': 'available'},
    {'email': 'yudhacahya584@alightmotion.website', 'login_url': 'https://am.sekalipay.com', 'expiry': '01 Sep 2027', 'status': 'available'},
    {'email': 'rezafikri44@alightmotion.website', 'login_url': 'https://am.sekalipay.com', 'expiry': '01 Sep 2027', 'status': 'available'},
    {'email': 'yogadimas839@alightmotion.website', 'login_url': 'https://am.sekalipay.com', 'expiry': '01 Sep 2027', 'status': 'available'},
    {'email': 'lukas523@alightmotion.website', 'login_url': 'https://am.sekalipay.com', 'expiry': '01 Sep 2027', 'status': 'available'},
    {'email': 'gita949@alightmotion.website', 'login_url': 'https://am.sekalipay.com', 'expiry': '01 Sep 2027', 'status': 'available'},
    {'email': 'indahkevan54@alightmotion.website', 'login_url': 'https://am.sekalipay.com', 'expiry': '01 Sep 2027', 'status': 'available'},
    {'email': 'ekakevin571@alightmotion.website', 'login_url': 'https://am.sekalipay.com', 'expiry': '01 Sep 2027', 'status': 'available'},
    {'email': 'diaz223@alightmotion.website', 'login_url': 'https://am.sekalipay.com', 'expiry': '01 Sep 2027', 'status': 'available'},
    {'email': 'jokozaki539@alightmotion.website', 'login_url': 'https://am.sekalipay.com', 'expiry': '01 Sep 2027', 'status': 'available'},
    {'email': 'aurel177@alightmotion.website', 'login_url': 'https://am.sekalipay.com', 'expiry': '01 Sep 2027', 'status': 'available'},
    {'email': 'prita643@alightmotion.website', 'login_url': 'https://am.sekalipay.com', 'expiry': '01 Sep 2027', 'status': 'available'},
    {'email': 'usmanprita745@alightmotion.website', 'login_url': 'https://am.sekalipay.com', 'expiry': '01 Sep 2027', 'status': 'available'},
    {'email': 'rakasabrina339@alightmotion.website', 'login_url': 'https://am.sekalipay.com', 'expiry': '01 Sep 2027', 'status': 'available'},
    {'email': 'gilangyudha537@alightmotion.website', 'login_url': 'https://am.sekalipay.com', 'expiry': '01 Sep 2027', 'status': 'available'},
    {'email': 'kevanjihan89@alightmotion.website', 'login_url': 'https://am.sekalipay.com', 'expiry': '01 Sep 2027', 'status': 'available'},
    {'email': 'mayareza194@alightmotion.website', 'login_url': 'https://am.sekalipay.com', 'expiry': '01 Sep 2027', 'status': 'available'},
    {'email': 'oscareka309@alightmotion.website', 'login_url': 'https://am.sekalipay.com', 'expiry': '01 Sep 2027', 'status': 'available'},
    {'email': 'maya245@alightmotion.website', 'login_url': 'https://am.sekalipay.com', 'expiry': '01 Sep 2027', 'status': 'available'},
    {'email': 'angela515@alightmotion.website', 'login_url': 'https://am.sekalipay.com', 'expiry': '01 Sep 2027', 'status': 'available'},
    {'email': 'cahya45@alightmotion.website', 'login_url': 'https://am.sekalipay.com', 'expiry': '01 Sep 2027', 'status': 'available'},
    {'email': 'cahyafikri969@alightmotion.website', 'login_url': 'https://am.sekalipay.com', 'expiry': '01 Sep 2027', 'status': 'available'},
    {'email': 'kevanyoga435@alightmotion.website', 'login_url': 'https://am.sekalipay.com', 'expiry': '01 Sep 2027', 'status': 'available'},
    {'email': 'salsalukas970@alightmotion.website', 'login_url': 'https://am.sekalipay.com', 'expiry': '01 Sep 2027', 'status': 'available'},
    {'email': 'tiozahra32@alightmotion.website', 'login_url': 'https://am.sekalipay.com', 'expiry': '01 Sep 2027', 'status': 'available'},
    {'email': 'bungahana902@alightmotion.website', 'login_url': 'https://am.sekalipay.com', 'expiry': '01 Sep 2027', 'status': 'available'},
    {'email': 'wawan411@alightmotion.website', 'login_url': 'https://am.sekalipay.com', 'expiry': '01 Sep 2027', 'status': 'available'},
    {'email': 'vitokevin207@alightmotion.website', 'login_url': 'https://am.sekalipay.com', 'expiry': '01 Sep 2027', 'status': 'available'},
    {'email': 'sinta882@alightmotion.website', 'login_url': 'https://am.sekalipay.com', 'expiry': '01 Sep 2027', 'status': 'available'},
    {'email': 'dindaarif982@alightmotion.website', 'login_url': 'https://am.sekalipay.com', 'expiry': '01 Sep 2027', 'status': 'available'},
    {'email': 'putridinda84@alightmotion.website', 'login_url': 'https://am.sekalipay.com', 'expiry': '01 Sep 2027', 'status': 'available'},
    {'email': 'putri608@alightmotion.website', 'login_url': 'https://am.sekalipay.com', 'expiry': '01 Sep 2027', 'status': 'available'},
    {'email': 'ekawawan552@alightmotion.website', 'login_url': 'https://am.sekalipay.com', 'expiry': '01 Sep 2027', 'status': 'available'},
    {'email': 'jihanbrian705@alightmotion.website', 'login_url': 'https://am.sekalipay.com', 'expiry': '01 Sep 2027', 'status': 'available'},
    {'email': 'ilham62@alightmotion.website', 'login_url': 'https://am.sekalipay.com', 'expiry': '01 Sep 2027', 'status': 'available'},
]

def available_stock():
    """Mengembalikan stok yang masih tersedia."""
    return [item for item in STOCK if item["status"] == "available"]

def available_count():
    return len(available_stock())
