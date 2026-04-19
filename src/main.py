"""
🛍️ GAMELAB FASHION HUB - Telegram Bot
Toko Baju Online dengan fitur lengkap:
- Katalog 50+ produk (8 kategori)
- Keranjang belanja
- Checkout & Pembayaran (COD, QRIS, M-Banking)
- AI Fashion Advisor
- Admin Panel (tersembunyi via /admin)
"""
import sys
import os
import logging
import telebot
from groq import Groq
from dotenv import load_dotenv

# Fix path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import init_db
from error_notifier import init_notifier, send_error_notification, notify_info
from handlers import menu, katalog, keranjang, pesanan, ai_chat, admin

# --- KONFIGURASI ---
load_dotenv()
log_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'error_log.txt')
logging.basicConfig(
    level=logging.ERROR,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_path),
        logging.StreamHandler()
    ]
)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_AI")  # Match .env key name

if not TELEGRAM_TOKEN:
    print("❌ ERROR: TELEGRAM_TOKEN tidak ditemukan di .env")
    sys.exit(1)

bot = telebot.TeleBot(TELEGRAM_TOKEN)
groq_client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None

# Initialize Error Notifier
init_notifier(bot)

# --- INISIALISASI DATABASE ---
try:
    # Delete old db to recreate with new schema
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "umkm.db")
    if os.path.exists(db_path):
        import sqlite3
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='produk_baju'")
        if not cur.fetchone():
            conn.close()
            os.remove(db_path)
            print("🔄 Database lama dihapus, akan dibuat ulang...")
        else:
            conn.close()
    
    init_db()
    print("✅ Database siap!")
except Exception as e:
    print(f"⚠️ Database Warning: {e}")
    send_error_notification(e, context="Database Initialization")

# --- REGISTER SEMUA HANDLER ---
# Urutan penting! Command handlers harus didaftarkan duluan.

# 1. Menu & Beranda (/start, /help, beranda, tentang, kontak, jam_kerja)
menu.register(bot)

# 2. Admin Panel (/admin) - harus sebelum katalog
admin.register(bot)

# 3. AI Chat (/ai, /stop)
if groq_client:
    handle_ai_message, is_ai_active = ai_chat.register(bot, groq_client)
else:
    handle_ai_message = None
    is_ai_active = lambda chat_id: False
    print("⚠️ GROQ_API_KEY tidak ditemukan, AI Chat dinonaktifkan")

# 4. Katalog (kategori, produk, search, ukuran)
katalog.register(bot)

# 5. Keranjang
keranjang.register(bot)

# 6. Pesanan (checkout, payment, tracking)
pesanan.register(bot)


# --- FALLBACK TEXT HANDLER (PALING BAWAH) ---
@bot.message_handler(func=lambda message: True)
def handle_all_text(message):
    """Handle semua pesan teks - cek AI mode dulu"""
    # Check if this is a test error command
    if message.text == '/tes_error':
        try:
            # Sengaja buat error "Division by Zero"
            _ = 1 / 0
        except Exception as e:
            from error_notifier import send_error_notification
            send_error_notification(e, context="Test Error Command (/tes_error)")
            bot.reply_to(message, "✅ Percobaan error berhasil dibuat! Cek pesan dari bot di akun Telegram admin Anda.")
        return

    # Skip commands lainnya (hindari nabrak command valid)
    if message.text and message.text.startswith('/'):
        return

    # Check AI mode
    if handle_ai_message and is_ai_active(message.chat.id):
        handle_ai_message(message)
    else:
        # User kirim teks tapi bukan AI mode
        from keyboards import menu_utama
        bot.send_message(
            message.chat.id,
            "👋 Halo! Silakan gunakan menu di bawah ini untuk berbelanja:",
            reply_markup=menu_utama()
        )


# --- RUN ---
print("=" * 50)
print("🛍️  GAMELAB FASHION HUB BOT")
print("=" * 50)
print("📦 50+ produk di 8 kategori")
print("🛒 Keranjang & Checkout")
print("💳 COD, QRIS, M-Banking")
print("🤖 AI Fashion Advisor")
print("🔐 Admin: /admin (password: admin123)")
print("=" * 50)
print("Bot berjalan... Tekan Ctrl+C untuk berhenti")
print("=" * 50)

# Notify admin that bot started
notify_info("🚀 *GAMELAB FASHION HUB BOT START*\nBot berhasil dinyalakan dan siap menerima pesanan!")

try:
    bot.infinity_polling(timeout=10, long_polling_timeout=5)
except Exception as e:
    send_error_notification(e, context="Infinity Polling Terhenti")