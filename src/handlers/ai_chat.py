"""
Gamelab Fashion Hub - AI Chat Handler
Handles: AI fashion advisor mode using Groq API
Includes real product data from database for accurate recommendations
"""
import logging
from database import get_all_products, get_categories
from keyboards import ai_chat_menu, ai_stop_btn, btn_kembali_menu
from error_notifier import send_error_notification

# Track which users have AI mode active
user_ai_sessions = {}


def _build_product_context():
    """Build product catalog string from database for AI context"""
    try:
        products = get_all_products()
        if not products:
            return "Belum ada produk tersedia."

        catalog = ""
        current_kat = ""
        for p in products:
            if p['kategori'] != current_kat:
                current_kat = p['kategori']
                catalog += f"\n=== {current_kat} ===\n"
            catalog += (
                f"- {p['nama']} | Rp {p['harga']:,} | "
                f"Bahan: {p['bahan']} | Warna: {p['warna']} | "
                f"Ukuran: {p['ukuran']} | Stok: {p['stok']} | "
                f"Deskripsi: {p['deskripsi']}\n"
            )
        return catalog
    except Exception as e:
        logging.error(f"Build context error: {e}")
        return "Data produk sedang tidak tersedia."


def _get_system_prompt():
    """Generate system prompt with real product data"""
    product_catalog = _build_product_context()

    return f"""
Kamu adalah Asisten Fashion AI dari 'Gamelab Fashion Hub', toko baju online Indonesia.
Gaya bicaramu: Ramah, fun, informatif, dan menggunakan emoji yang relevan.

TUGASMU:
1. Memberikan rekomendasi outfit dan fashion tips berdasarkan KATALOG PRODUK KAMI yang tersedia
2. Menjawab pertanyaan tentang bahan, ukuran, dan perawatan pakaian
3. Membantu mix & match outfit dari produk yang kami jual
4. Memberikan saran style sesuai acara (casual, formal, hangout, olahraga, dll)
5. Merekomendasikan produk SPESIFIK dari katalog kami beserta harga dan detail
6. Membantu user memilih ukuran yang tepat

ATURAN PENTING:
- SELALU rekomendasikan produk dari katalog kami (jangan rekomendasikan brand lain)
- Sebutkan NAMA PRODUK, HARGA, BAHAN, dan WARNA yang tersedia
- Jika user tanya produk yang tidak ada, arahkan ke produk serupa yang tersedia
- Jawab dengan ringkas (maksimal 3-4 paragraf)
- Akhiri dengan ajakan untuk mengecek katalog atau menambahkan ke keranjang via bot
- Jika ditanya stok, sebutkan berdasarkan data katalog

FORMAT JAWABAN (Telegram Markdown):
- JANGAN merekomendasikan dalam bentuk tabel. Selalu gunakan format list.
- Untuk list/poin, SELALU gunakan tanda hubung tunggal "-" (JANGAN gunakan bintang * untuk list).
- Untuk menebalkan teks (nama produk & harga), gunakan satu bintang mengapit teks: *teks tebal*.
- CONTOH FORMAT YANG BENAR: 
- *Kaos Polos Premium* (Rp 89.000)
- *Jaket Bomber Classic* (Rp 349.000)
- Berikan spasi baris kosong (enter) antar item rekomendasi agar tidak menumpuk.
- MINIMALKAN EMOJI: Hanya gunakan emoji maksimal 1-2 buah di kalimat pembuka atau penutup. JANGAN beri emoji di list item produk.
- JANGAN gunakan heading (#), gunakan teks biasa saja.

KATALOG PRODUK GAMELAB FASHION HUB:
{product_catalog}

PANDUAN UKURAN UMUM:
- S: Lebar Dada 48cm, Panjang 66cm (BB 45-55kg)
- M: Lebar Dada 50cm, Panjang 68cm (BB 55-65kg)
- L: Lebar Dada 52cm, Panjang 70cm (BB 65-75kg)
- XL: Lebar Dada 54cm, Panjang 72cm (BB 75-85kg)
- XXL: Lebar Dada 56cm, Panjang 74cm (BB 85-95kg)
- Untuk celana: 28(S), 29-30(M), 31-32(L), 33-34(XL), 36(XXL)

TIPS PERAWATAN UMUM:
- Cotton: Cuci dengan air dingin, jangan gunakan pemutih, jemur di tempat teduh
- Denim: Cuci balik, air dingin, hindari mesin pengering
- Linen: Cuci tangan atau dry clean, setrika saat lembab
- Fleece/Hoodie: Cuci air dingin, jangan gunakan pelembut, keringkan angin
- Rajut/Knit: Cuci tangan, jangan diperas, keringkan datar
"""


def register(bot, groq_client):
    """Register AI chat handlers"""

    @bot.callback_query_handler(func=lambda c: c.data == 'menu_ai')
    def cb_ai_menu(call):
        bot.answer_callback_query(call.id)
        status = "🟢 Aktif" if user_ai_sessions.get(call.message.chat.id) else "🔴 Nonaktif"

        teks = f"""
🤖 *AI FASHION ADVISOR*

━━━━━━━━━━━━━━━━━━━━

Status: {status}

Fitur AI Chat:
• 💡 Rekomendasi outfit dari katalog kami
• 👕 Info bahan, ukuran & perawatan
• 🎨 Mix & match style
• 🎯 Saran fashion sesuai acara
• 📏 Panduan ukuran
• 💰 Info harga & stok real-time

━━━━━━━━━━━━━━━━━━━━

Aktifkan AI lalu ketik pertanyaan Anda!

_Contoh pertanyaan:_
• "Rekomendasi outfit casual weekend"
• "Bahan apa yang adem untuk cuaca panas?"
• "Padankan jaket bomber dengan apa?"
• "Ukuran L cocok untuk BB berapa?"
"""
        bot.send_message(
            call.message.chat.id,
            teks,
            parse_mode='Markdown',
            reply_markup=ai_chat_menu()
        )

    @bot.callback_query_handler(func=lambda c: c.data == 'ai_start')
    def cb_ai_start(call):
        user_ai_sessions[call.message.chat.id] = True
        bot.answer_callback_query(call.id, "🟢 AI Chat Aktif!")
        bot.send_message(
            call.message.chat.id,
            "🤖 *Mode AI Fashion Advisor AKTIF!*\n\n"
            "Saya punya akses ke seluruh katalog Gamelab Fashion Hub.\n"
            "Silakan tanya apapun tentang fashion! 👇\n\n"
            "_Contoh: \"Rekomendasikan outfit untuk interview kerja\"_\n\n"
            "Ketik /stop atau tekan tombol Stop untuk keluar.",
            parse_mode='Markdown',
            reply_markup=ai_stop_btn()
        )

    @bot.callback_query_handler(func=lambda c: c.data == 'ai_stop')
    def cb_ai_stop(call):
        user_ai_sessions[call.message.chat.id] = False
        bot.answer_callback_query(call.id, "🔴 AI Chat Dinonaktifkan")
        bot.send_message(
            call.message.chat.id,
            "🔴 *Mode AI dinonaktifkan.*\n\n"
            "Terima kasih sudah menggunakan Fashion Advisor! 😊\n"
            "Jangan lupa cek katalog untuk produk rekomendasi tadi ya!",
            parse_mode='Markdown',
            reply_markup=btn_kembali_menu()
        )

    @bot.message_handler(commands=['ai'])
    def cmd_ai_start(message):
        user_ai_sessions[message.chat.id] = True
        bot.reply_to(
            message,
            "🤖 *Mode AI Fashion Advisor AKTIF!*\n\n"
            "Ketik pertanyaan fashion Anda.\n"
            "Ketik /stop untuk keluar.",
            parse_mode='Markdown',
            reply_markup=ai_stop_btn()
        )

    @bot.message_handler(commands=['stop'])
    def cmd_ai_stop(message):
        user_ai_sessions[message.chat.id] = False
        bot.reply_to(message, "🔴 Mode AI dinonaktifkan.", reply_markup=btn_kembali_menu())

    def is_ai_active(chat_id):
        return user_ai_sessions.get(chat_id, False)

    def handle_ai_message(message):
        """Process AI message - called from main handler"""
        chat_id = message.chat.id
        if not is_ai_active(chat_id):
            return False

        pertanyaan = message.text
        bot.send_chat_action(chat_id, 'typing')

        try:
            # Build fresh system prompt with current product data
            system_prompt = _get_system_prompt()

            chat_completion = groq_client.chat.completions.create(
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": pertanyaan}
                ],
                model="llama-3.3-70b-versatile",
                max_tokens=1024,
                temperature=0.7,
            )
            jawaban = chat_completion.choices[0].message.content

            # Try sending with Markdown formatting
            try:
                bot.reply_to(message, jawaban, parse_mode='Markdown', reply_markup=ai_stop_btn())
            except Exception:
                # Fallback: if markdown fails (unbalanced chars), send as plain text
                bot.reply_to(message, jawaban, reply_markup=ai_stop_btn())

        except Exception as e:
            bot.reply_to(
                message,
                "⚠️ AI sedang gangguan. Coba lagi nanti ya!\n"
                "Sementara itu, cek katalog kami langsung di menu utama.",
                reply_markup=btn_kembali_menu()
            )
            send_error_notification(e, context="AI Chat (Groq API)")

        return True

    # Expose the handler function
    return handle_ai_message, is_ai_active
