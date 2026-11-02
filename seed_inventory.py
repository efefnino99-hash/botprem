
import os
import httpx

from account import STOCK

SUPABASE_URL = os.environ["SUPABASE_URL"].rstrip("/")
SUPABASE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]

url = f"{SUPABASE_URL}/rest/v1/am_inventory"

headers = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "resolution=ignore-duplicates,return=representation"
}

payload = [
    {
        "email": item["email"],
        "login_url": item["login_url"],
        "expiry": item["expiry"],
        "status": "available"
    }
    for item in STOCK
]

response = httpx.post(
    url,
    params={"on_conflict": "email"},
    headers=headers,
    json=payload,
    timeout=60
)

response.raise_for_status()

print("Import inventaris berhasil.")
print("Akun baru dimasukkan:", len(response.json()))
