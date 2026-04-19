# Gamelab Fashion Hub Bot 🛍️

Bot Telegram e-commerce fashion yang memudahkan pelanggan berbelanja langsung dari chat — mulai dari lihat katalog, pilih produk, sampai proses bayar. Dilengkapi AI Fashion Advisor berbasis Groq (Llama 3.3) dan panel admin tersendiri untuk pengelolaan toko.

---

## Apa yang Bisa Dilakukan Bot Ini?

### Katalog Produk
Bot menampilkan lebih dari 50 produk yang dikelompokkan dalam 8 kategori seperti Kaos, Kemeja, Celana, Jaket, dan lainnya. Setiap produk bisa dilihat detailnya langsung di dalam chat.

### Keranjang Belanja
Pelanggan bisa menambah produk ke keranjang, mengubah kuantitas, dan melihat total harga sebelum lanjut ke proses pembelian — semua dilakukan interaktif lewat tombol inline Telegram.

### Proses Checkout
Alur checkout dibuat sederhana dan terstruktur dalam 3 langkah: bot akan meminta Nama, Alamat pengiriman, dan Nomor Telepon secara berurutan.

### Metode Pembayaran
Mendukung tiga opsi pembayaran:
- **COD** — bayar saat barang tiba
- **QRIS** — scan barcode langsung dari chat
- **M-Banking** — transfer via mobile banking

Setelah transaksi selesai, pelanggan mendapat struk pembelian otomatis di chat.

### AI Fashion Advisor
Fitur konsultasi berbasis AI yang bisa membantu pelanggan memilih outfit, merekomendasikan ukuran, dan memberi saran gaya — semua berdasarkan katalog produk yang tersedia di toko secara real-time.

### Panel Admin
Admin memiliki akses ke dashboard khusus via perintah `/admin` yang mencakup:
- Memonitor semua riwayat pesanan masuk
- Mengubah status pengiriman secara langsung
- Menambah atau menghapus produk dari katalog

### Notifikasi Error Otomatis
Kalau bot mengalami masalah, sistem akan mencatat error ke file `error_log.txt` sekaligus mengirim notifikasi langsung ke akun Telegram pribadi admin — sehingga masalah operasional bisa ditangani dengan cepat.

---

## Struktur Proyek

```
python/
├── src/
│   ├── main.py             # Entry point — jalankan file ini untuk memulai bot
│   ├── database.py         # Konfigurasi SQLite: schema tabel dan query
│   ├── keyboards.py        # Komponen tombol navigasi inline
│   ├── error_notifier.py   # Modul pencatatan dan notifikasi error
│   ├── assets/             # Foto produk dan gambar QRIS
│   └── handlers/           # Logika fitur dipisah per modul
│       ├── menu.py         # Navigasi statis (Home, Tentang, Kontak)
│       ├── katalog.py      # Daftar produk dan detail per kategori
│       ├── keranjang.py    # Kelola isi keranjang belanja
│       ├── pesanan.py      # Alur checkout dan validasi order
│       ├── ai_chat.py      # Konsultasi fashion via AI
│       └── admin.py        # Panel admin: kelola produk dan pesanan
├── .env.example            # Template konfigurasi environment
├── .gitignore              # File dan folder yang dikecualikan dari Git
└── requirements.txt        # Daftar dependency Python yang dibutuhkan
```

---

## Yang Perlu Disiapkan Sebelum Mulai

- **Python 3.X**
- **Token Bot Telegram** — dapatkan dari [@BotFather](https://t.me/BotFather)
- **Groq API Key** — daftar dan ambil key di [console.groq.com](https://console.groq.com) untuk fitur AI Advisor
- **Admin Chat ID** — Telegram ID pribadi Anda, digunakan untuk hak akses admin dan penerimaan notifikasi error

---

## Cara Instalasi dan Menjalankan Bot

**1. Clone repositori**

Download source code ke direktori kerja Anda.

**2. Buat virtual environment**

Ini agar library proyek tidak bercampur dengan instalasi Python sistem.
```bash
python3 -m venv venv
source venv/bin/activate
```

**3. Install semua dependency**

```bash
pip install -r requirements.txt
```

**4. Konfigurasi file environment**

Salin file `.env.example` menjadi `.env`, lalu isi dengan kredensial asli Anda:
```env
TELEGRAM_TOKEN=123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11
GROQ_AI=gsk_randomapikey12345
ADMIN_CHAT_ID=1122334455
```

**5. Jalankan bot**

```bash
python3 src/main.py
```

Saat pertama kali dijalankan, database `umkm.db` akan dibuat secara otomatis beserta seluruh tabel yang dibutuhkan.

---

## Catatan Pengujian

Untuk memverifikasi bahwa notifikasi error ke Telegram berfungsi, kirim perintah berikut langsung ke bot saat bot sedang berjalan:

```
/tes_error
```

Perintah ini akan memicu exception yang disengaja. Jika konfigurasi sudah benar, Anda akan menerima notifikasi di Telegram dan error tercatat di `error_log.txt`.

---

