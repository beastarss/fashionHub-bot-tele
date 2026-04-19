"""
Gamelab Fashion Hub - Error Notifier
Mencatat error ke error_log.txt DAN mengirim notifikasi ke admin via Telegram
"""
import os
import logging
import traceback
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
ADMIN_CHAT_ID = os.getenv("ADMIN_CHAT_ID")

# Setup file logging to root directory
LOG_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'error_log.txt')

logger = logging.getLogger('fashionhub_errors')
logger.setLevel(logging.ERROR)

# File handler - tulis ke error_log.txt
file_handler = logging.FileHandler(LOG_FILE, encoding='utf-8')
file_handler.setLevel(logging.ERROR)
file_handler.setFormatter(logging.Formatter(
    '%(asctime)s | %(levelname)s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
))
logger.addHandler(file_handler)

# Console handler (Railway logs visibility)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.ERROR)
console_handler.setFormatter(logging.Formatter(
    '%(asctime)s | %(levelname)s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
))
logger.addHandler(console_handler)

# Bot instance (will be set from main.py)
_bot = None


def init_notifier(bot_instance):
    """Initialize with bot instance from main.py"""
    global _bot
    _bot = bot_instance


def send_error_notification(error_message, context=""):
    """
    Log error ke file DAN kirim ke admin via Telegram.
    
    Args:
        error_message: Pesan error atau Exception
        context: Konteks tambahan (misal: nama handler, fungsi)
    """
    # 1. Format pesan
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    if isinstance(error_message, Exception):
        tb = traceback.format_exception(type(error_message), error_message, error_message.__traceback__)
        error_detail = ''.join(tb)
        error_short = f"{type(error_message).__name__}: {str(error_message)}"
    else:
        error_detail = str(error_message)
        error_short = str(error_message)[:200]

    # 2. Tulis ke error_log.txt
    log_entry = f"[{context}] {error_short}" if context else error_short
    logger.error(log_entry)
    logger.error(f"Detail: {error_detail}")
    logger.error("─" * 50)

    # 3. Kirim ke admin via Telegram
    if _bot and ADMIN_CHAT_ID:
        try:
            teks = (
                f"🚨 *ERROR TERDETEKSI*\n"
                f"━━━━━━━━━━━━━━━━━━━━\n\n"
                f"⏰ *Waktu:* {timestamp}\n"
            )
            if context:
                teks += f"📍 *Lokasi:* {context}\n"
            
            teks += (
                f"\n❌ *Error:*\n"
                f"`{error_short[:500]}`\n\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"📝 Detail lengkap tersimpan di error\\_log.txt"
            )

            _bot.send_message(
                int(ADMIN_CHAT_ID),
                teks,
                parse_mode='Markdown'
            )
        except Exception as e:
            # Jangan sampai error notifier sendiri crash
            logger.error(f"Gagal kirim notifikasi ke admin: {e}")


def notify_warning(warning_message, context=""):
    """Kirim warning (bukan error) ke admin"""
    if _bot and ADMIN_CHAT_ID:
        try:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            teks = (
                f"⚠️ *WARNING*\n"
                f"━━━━━━━━━━━━━━━━━━━━\n\n"
                f"⏰ {timestamp}\n"
            )
            if context:
                teks += f"📍 {context}\n"
            teks += f"\n{warning_message}"

            _bot.send_message(
                int(ADMIN_CHAT_ID),
                teks,
                parse_mode='Markdown'
            )
        except:
            pass


def notify_info(info_message):
    """Kirim info ke admin (bot start, dll)"""
    if _bot and ADMIN_CHAT_ID:
        try:
            _bot.send_message(
                int(ADMIN_CHAT_ID),
                f"ℹ️ {info_message}",
                parse_mode='Markdown'
            )
        except:
            pass
