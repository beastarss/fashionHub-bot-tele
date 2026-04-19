"""
Gamelab Fashion Hub - Menu & Beranda Handler
Handles: /start, beranda, tentang kami, kontak, jam kerja
"""
import os
from database import query_db
from keyboards import menu_utama, btn_kembali_menu

ASSETS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'assets')

WELCOME_TEXT = """
✨ *Selamat Datang di Gamelab Fashion Hub!* ✨

🛍️ Toko fashion online terlengkap dengan koleksi terkini!

👕 *800+ Koleksi* dari 8 Kategori
💰 *Harga Terjangkau* mulai Rp 89.000
🚚 *Gratis Ongkir* untuk pembelian tertentu
💳 *3 Metode Bayar*: COD, QRIS, M-Banking

Silakan pilih menu di bawah ini 👇
"""

TENTANG_TEXT = """
ℹ️ *TENTANG GAMELAB FASHION HUB*

━━━━━━━━━━━━━━━━━━━━

🏪 *Profil Toko*
Gamelab Fashion Hub adalah toko fashion online yang menyediakan berbagai koleksi pakaian berkualitas dengan desain terkini. Kami berkomitmen menghadirkan fashion yang stylish, nyaman, dan terjangkau untuk semua kalangan.

━━━━━━━━━━━━━━━━━━━━

🎯 *Visi*
Menjadi platform fashion online terdepan yang menginspirasi gaya hidup modern masyarakat Indonesia.

🏆 *Misi*
• Menyediakan produk fashion berkualitas tinggi
• Memberikan pengalaman belanja yang mudah & menyenangkan
• Menghadirkan harga yang terjangkau tanpa mengorbankan kualitas
• Memberikan pelayanan terbaik kepada setiap pelanggan

━━━━━━━━━━━━━━━━━━━━

⭐ *Keunggulan Kami*
✅ Produk 100% Original
✅ Bahan Premium & Nyaman
✅ Desain Up-to-date
✅ Pengemasan Rapi & Aman
✅ Customer Service Responsif
✅ Garansi Tukar Ukuran
✅ COD, QRIS, & M-Banking
✅ Pengiriman Cepat ke Seluruh Indonesia

━━━━━━━━━━━━━━━━━━━━

👥 *Tim Kami*
Kami adalah tim muda yang passionate di bidang fashion dan teknologi. Setiap produk kami kurasi dengan cermat untuk memastikan kualitas terbaik sampai ke tangan Anda.

📍 Jl. Fashion Street No. 88, Jakarta Selatan
"""

def register(bot):
    """Register menu handlers"""

    @bot.message_handler(commands=['start', 'help'])
    def send_welcome(message):
        # Send welcome with photo
        logo_path = os.path.join(ASSETS_DIR, 'products', 'kaos.png')
        if os.path.exists(logo_path):
            with open(logo_path, 'rb') as photo:
                bot.send_photo(
                    message.chat.id,
                    photo,
                    caption=WELCOME_TEXT,
                    parse_mode='Markdown',
                    reply_markup=menu_utama()
                )
        else:
            bot.send_message(
                message.chat.id,
                WELCOME_TEXT,
                parse_mode='Markdown',
                reply_markup=menu_utama()
            )

    @bot.callback_query_handler(func=lambda c: c.data == 'menu_utama')
    def cb_menu_utama(call):
        bot.answer_callback_query(call.id)
        bot.send_message(
            call.message.chat.id,
            WELCOME_TEXT,
            parse_mode='Markdown',
            reply_markup=menu_utama()
        )

    @bot.callback_query_handler(func=lambda c: c.data == 'menu_tentang')
    def cb_tentang(call):
        bot.answer_callback_query(call.id)
        bot.send_message(
            call.message.chat.id,
            TENTANG_TEXT,
            parse_mode='Markdown',
            reply_markup=btn_kembali_menu()
        )

    @bot.callback_query_handler(func=lambda c: c.data == 'menu_kontak')
    def cb_kontak(call):
        bot.answer_callback_query(call.id)
        try:
            hasil = query_db("SELECT isi FROM info WHERE kunci='kontak'", fetch=True)
            kontak = hasil[0]['isi'] if hasil else "📱 0812-3456-7890"
        except:
            kontak = "📱 0812-3456-7890"

        teks = f"""
📞 *KONTAK GAMELAB FASHION HUB*

━━━━━━━━━━━━━━━━━━━━

{kontak}

📍 *Alamat:*
Jl. Fashion Street No. 88
Jakarta Selatan, DKI Jakarta

━━━━━━━━━━━━━━━━━━━━

💬 Atau chat langsung dengan AI kami untuk bantuan cepat!
"""
        bot.send_message(
            call.message.chat.id,
            teks,
            parse_mode='Markdown',
            reply_markup=btn_kembali_menu()
        )

    @bot.callback_query_handler(func=lambda c: c.data == 'menu_jamkerja')
    def cb_jamkerja(call):
        bot.answer_callback_query(call.id)
        try:
            hasil = query_db("SELECT isi FROM info WHERE kunci='jam_kerja'", fetch=True)
            jam = hasil[0]['isi'] if hasil else "09:00 - 21:00 WIB"
        except:
            jam = "09:00 - 21:00 WIB"

        teks = f"""
🕒 *JAM OPERASIONAL*

━━━━━━━━━━━━━━━━━━━━

📅 *Senin - Jumat:* {jam}
📅 *Sabtu:* 10:00 - 18:00 WIB
📅 *Minggu:* 10:00 - 15:00 WIB

━━━━━━━━━━━━━━━━━━━━

📦 *Pengiriman:*
Order sebelum jam 14:00 WIB akan dikirim di hari yang sama!

🎄 *Hari Libur Nasional:* Tutup
"""
        bot.send_message(
            call.message.chat.id,
            teks,
            parse_mode='Markdown',
            reply_markup=btn_kembali_menu()
        )

    @bot.callback_query_handler(func=lambda c: c.data == 'menu_rekening')
    def cb_rekening(call):
        bot.answer_callback_query(call.id)
        teks = """
🏦 *REKENING PEMBAYARAN RESMI*

━━━━━━━━━━━━━━━━━━━━

🏧 *BCA (Bank Central Asia)*
No. Rekening: 1234567890
A/N: Ainun

🏧 *BNI (Bank Negara Indonesia)*
No. Rekening: 0987654321
A/N: Gamelab Fashion Hub

🏧 *Mandiri*
No. Rekening: 1122334455
A/N: Gamelab Fashion Hub

🏧 *BRI (Bank Rakyat Indonesia)*
No. Rekening: 5566778899
A/N: Gamelab Fashion Hub

━━━━━━━━━━━━━━━━━━━━

⚠️ *Penting:*
• Transfer sesuai dengan total pesanan Anda.
• Simpan bukti transfer (struk/screenshot).
• Hindari transfer ke rekening selain yang tercantum di atas.
"""
        bot.send_message(
            call.message.chat.id,
            teks,
            parse_mode='Markdown',
            reply_markup=btn_kembali_menu()
        )

    @bot.callback_query_handler(func=lambda c: c.data == 'menu_panduan_ukuran')
    def cb_panduan_ukuran(call):
        bot.answer_callback_query(call.id)
        teks = """
📏 *PANDUAN UKURAN GAMELAB FASHION HUB*

━━━━━━━━━━━━━━━━━━━━

👕 *BAJU / KEMEJA / KAOS / JAKET*
_*(Lebar Dada x Panjang Baju)*_
• *S* : 48 cm x 66 cm (Estimasi BB: 45 - 55 kg)
• *M* : 50 cm x 68 cm (Estimasi BB: 55 - 65 kg)
• *L* : 52 cm x 70 cm (Estimasi BB: 65 - 75 kg)
• *XL* : 54 cm x 72 cm (Estimasi BB: 75 - 85 kg)
• *XXL* : 56 cm x 74 cm (Estimasi BB: 85 - 95 kg)

━━━━━━━━━━━━━━━━━━━━

👖 *CELANA / ROK*
_*(Lingkar Panggul/Pinggang)*_
• *28 (S)* : 72 cm - 74 cm
• *29-30 (M)* : 76 cm - 78 cm
• *31-32 (L)* : 80 cm - 82 cm
• *33-34 (XL)* : 84 cm - 86 cm
• *35-36 (XXL)*: 88 cm - 92 cm

━━━━━━━━━━━━━━━━━━━━

💡 *Tips Memilih Ukuran:*
1. Jika ukuran Anda di antara dua size, disarankan memilih ukuran yang *lebih besar*.
2. Anda juga bisa berkonsultasi dengan *Chat AI Fashion* untuk rekomendasi.
"""
        bot.send_message(
            call.message.chat.id,
            teks,
            parse_mode='Markdown',
            reply_markup=btn_kembali_menu()
        )

    @bot.callback_query_handler(func=lambda c: c.data == 'noop')
    def cb_noop(call):
        bot.answer_callback_query(call.id)
