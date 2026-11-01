# Telegram Store — Pembayaran Manual

Template proyek toko Telegram dengan pembayaran manual (tanpa Midtrans).

## Alur pembayaran yang direncanakan
1. Pembeli tekan **Beli AM Prem** dan mengirim jumlah unit (1–100).
2. Bot menghitung total: jumlah × `PRICE_PER_UNIT`.
3. Bot menampilkan instruksi transfer/QRIS dari admin.
4. Pembeli mengirim foto bukti pembayaran.
5. Bot meneruskan bukti dan detail pesanan ke admin Telegram.
6. Admin memeriksa mutasi/rekening/QRIS melalui aplikasi penyedia pembayaran, lalu menyetujui atau menolak pesanan.
7. Setelah disetujui, sistem mengambil stok yang tersedia dan mengirim pesanan serta tanda terima kepada pembeli.

**Tidak ada deteksi pembayaran otomatis.** Bot tidak boleh menganggap foto/screenshot sebagai bukti bahwa uang benar-benar masuk. Admin wajib memeriksa transaksi pada aplikasi rekening/penyedia QRIS sebelum menekan tombol konfirmasi.

## Konfigurasi
Salin `.env.example` menjadi `.env` untuk pengujian lokal. Di Vercel buka:
Project → Settings → Environment Variables.

Isi:
- `TELEGRAM_BOT_TOKEN`: token dari BotFather.
- `BOT_WEBHOOK_SECRET`: secret acak untuk mengamankan webhook Telegram.
- `TELEGRAM_ADMIN_ID`: ID Telegram admin.
- `SUPABASE_URL`: Project URL Supabase.
- `SUPABASE_SERVICE_ROLE_KEY`: service role key Supabase. Rahasiakan.
- `PAYMENT_METHOD`: contoh `QRIS`, `TRANSFER BANK`, atau metode manual lain.
- `PAYMENT_INSTRUCTIONS`: instruksi pembayaran yang ditampilkan kepada pembeli.
- `PAYMENT_QR_IMAGE_URL`: URL gambar QR pembayaran (opsional; gunakan URL gambar yang dapat diakses bot).
- `INFO_GROUP_URL`: tautan grup informasi.
- `ADMIN_USERNAME`: username CS tanpa tanda @.
- `PRICE_PER_UNIT`: harga satu unit, default 10000.
- `MIN_QUANTITY`: minimum pembelian, default 1.
- `MAX_QUANTITY`: maksimum pembelian, default 100.

**Tidak diperlukan Midtrans Server Key maupun konfigurasi Midtrans.**

## Lokasi file
- `account.py`: inventaris reseller yang disertakan dalam arsip ini. Jangan unggah ke repository publik atau bagikan kepada pihak lain.
- `database/schema.sql`: skema awal tabel produk, stok, pesanan, dan bukti pembayaran.
- `api/index.py`: titik masuk backend FastAPI. Periksa catatan status implementasi di bawah.

## Status implementasi
Arsip ini adalah starter konfigurasi, bukan bot pembayaran siap produksi. Endpoint webhook dan proses berikut masih perlu diimplementasikan serta diuji sebelum dipakai menerima uang:
- validasi secret webhook Telegram;
- percakapan pemilihan kuantitas dan pembuatan pesanan;
- menerima dan meneruskan bukti pembayaran ke admin;
- tombol admin untuk menyetujui/menolak pesanan;
- penguncian stok secara atomik agar stok tidak terkirim ganda;
- pengiriman barang dan tanda terima, termasuk mekanisme retry jika Telegram gagal mengirim.

Sebelum digunakan, uji seluruh alur dengan pesanan percobaan dan pastikan admin selalu memverifikasi uang masuk dari aplikasi penyedia pembayaran, bukan hanya dari gambar bukti.
