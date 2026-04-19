"""
Gamelab Fashion Hub - Pesanan (Order) Handler
Handles: checkout flow, payment methods, order tracking
"""
import os
from database import (
    get_cart, get_cart_total, create_order,
    get_order_by_number, get_orders_by_chat
)
from keyboards import (
    metode_bayar, konfirmasi_pesanan, setelah_pesan,
    cek_pesanan_input, btn_kembali_menu
)

ASSETS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'assets')

# Temporary storage for checkout data
checkout_data = {}

STATUS_EMOJI = {
    'Menunggu Konfirmasi': '⏳',
    'Diproses': '🔄',
    'Dikirim': '🚚',
    'Selesai': '✅',
    'Dibatalkan': '❌'
}

MBANKING_INFO = """
🏦 *TRANSFER M-BANKING*

━━━━━━━━━━━━━━━━━━━━

🏧 *BCA*
No. Rekening: 1234567890
A/N: Ainun

🏧 *BNI*
No. Rekening: 0987654321
A/N: Gamelab Fashion Hub

🏧 *Mandiri*
No. Rekening: 1122334455
A/N: Gamelab Fashion Hub

🏧 *BRI*
No. Rekening: 5566778899
A/N: Gamelab Fashion Hub

━━━━━━━━━━━━━━━━━━━━

⚠️ *Penting:*
• Transfer sesuai total pesanan
• Simpan bukti transfer
• Konfirmasi ke admin setelah transfer
"""


def register(bot):
    """Register pesanan handlers"""

    # ==================== CHECKOUT FLOW ====================

    @bot.callback_query_handler(func=lambda c: c.data == 'checkout_start')
    def cb_checkout(call):
        bot.answer_callback_query(call.id)
        chat_id = call.message.chat.id

        items = get_cart(chat_id)
        if not items:
            bot.send_message(chat_id, "🛒 Keranjang kosong! Belanja dulu ya.",
                           reply_markup=btn_kembali_menu())
            return

        total = get_cart_total(chat_id)
        checkout_data[chat_id] = {'total': total, 'items': items}

        teks = f"""
📦 *CHECKOUT PESANAN*

━━━━━━━━━━━━━━━━━━━━

📋 *Ringkasan Pesanan:*
"""
        for i, item in enumerate(items, 1):
            subtotal = item['harga'] * item['jumlah']
            teks += f"{i}. {item['nama']} (Size {item['ukuran']}) x{item['jumlah']} = Rp {subtotal:,}\n"

        teks += f"""
━━━━━━━━━━━━━━━━━━━━
💰 *TOTAL: Rp {total:,}*
━━━━━━━━━━━━━━━━━━━━

📝 *Langkah 1/3:* Masukkan Nama Lengkap Anda:
"""
        msg = bot.send_message(chat_id, teks, parse_mode='Markdown')
        bot.register_next_step_handler(msg, _get_nama)

    def _get_nama(message):
        chat_id = message.chat.id
        if chat_id not in checkout_data:
            return
        checkout_data[chat_id]['nama'] = message.text

        msg = bot.send_message(
            chat_id,
            "📝 *Langkah 2/3:* Masukkan Alamat Lengkap Pengiriman:\n_(RT/RW, Kelurahan, Kecamatan, Kota, Kode Pos)_",
            parse_mode='Markdown'
        )
        bot.register_next_step_handler(msg, _get_alamat)

    def _get_alamat(message):
        chat_id = message.chat.id
        if chat_id not in checkout_data:
            return
        checkout_data[chat_id]['alamat'] = message.text

        msg = bot.send_message(
            chat_id,
            "📝 *Langkah 3/3:* Masukkan Nomor HP/WhatsApp:\n_(contoh: 08123456789)_",
            parse_mode='Markdown'
        )
        bot.register_next_step_handler(msg, _get_telepon)

    def _get_telepon(message):
        chat_id = message.chat.id
        if chat_id not in checkout_data:
            return
        checkout_data[chat_id]['telepon'] = message.text

        # Show payment method selection
        data = checkout_data[chat_id]
        teks = f"""
💳 *PILIH METODE PEMBAYARAN*

━━━━━━━━━━━━━━━━━━━━

👤 Nama: {data['nama']}
📍 Alamat: {data['alamat']}
📱 Telepon: {data['telepon']}
💰 Total: *Rp {data['total']:,}*

━━━━━━━━━━━━━━━━━━━━

Pilih metode pembayaran:
"""
        bot.send_message(chat_id, teks, parse_mode='Markdown', reply_markup=metode_bayar())

    # ==================== PAYMENT METHODS ====================

    @bot.callback_query_handler(func=lambda c: c.data.startswith('bayar_'))
    def cb_payment(call):
        bot.answer_callback_query(call.id)
        chat_id = call.message.chat.id
        metode = call.data[6:]  # COD, QRIS, MBANKING

        if chat_id not in checkout_data:
            bot.send_message(chat_id, "⚠️ Sesi checkout sudah expired. Silakan mulai lagi.",
                           reply_markup=btn_kembali_menu())
            return

        checkout_data[chat_id]['metode'] = metode

        if metode == 'COD':
            _show_confirmation(bot, chat_id, "💵 COD (Bayar di Tempat)")

        elif metode == 'QRIS':
            # Send QRIS image
            qris_path = os.path.join(ASSETS_DIR, 'qris.png')
            if os.path.exists(qris_path):
                with open(qris_path, 'rb') as photo:
                    bot.send_photo(
                        chat_id,
                        photo,
                        caption=f"📱 *PEMBAYARAN QRIS*\n\n💰 Total: *Rp {checkout_data[chat_id]['total']:,}*\n\nScan QR code di atas menggunakan aplikasi e-wallet (GoPay, OVO, DANA, ShopeePay, LinkAja) atau M-Banking.",
                        parse_mode='Markdown'
                    )
            _show_confirmation(bot, chat_id, "📱 QRIS")

        elif metode == 'MBANKING':
            bot.send_message(chat_id, MBANKING_INFO, parse_mode='Markdown')
            _show_confirmation(bot, chat_id, "🏦 M-Banking (Transfer)")

    def _show_confirmation(bot, chat_id, metode_text):
        data = checkout_data[chat_id]
        teks = f"""
✅ *KONFIRMASI PESANAN*

━━━━━━━━━━━━━━━━━━━━

👤 *Pemesan:* {data['nama']}
📍 *Alamat:* {data['alamat']}
📱 *Telepon:* {data['telepon']}
💳 *Pembayaran:* {metode_text}

📋 *Item:*
"""
        for i, item in enumerate(data['items'], 1):
            subtotal = item['harga'] * item['jumlah']
            teks += f"  {i}. {item['nama']} ({item['ukuran']}) x{item['jumlah']} = Rp {subtotal:,}\n"

        teks += f"""
━━━━━━━━━━━━━━━━━━━━
💰 *TOTAL BAYAR: Rp {data['total']:,}*
━━━━━━━━━━━━━━━━━━━━

Apakah Anda yakin ingin memesan?
"""
        bot.send_message(chat_id, teks, parse_mode='Markdown', reply_markup=konfirmasi_pesanan())

    # ==================== CONFIRM / CANCEL ====================

    @bot.callback_query_handler(func=lambda c: c.data == 'confirm_order')
    def cb_confirm(call):
        bot.answer_callback_query(call.id, "⏳ Memproses pesanan...")
        chat_id = call.message.chat.id

        if chat_id not in checkout_data:
            bot.send_message(chat_id, "⚠️ Sesi checkout sudah expired.",
                           reply_markup=btn_kembali_menu())
            return

        data = checkout_data[chat_id]

        # Map payment method
        metode_map = {'COD': 'COD', 'QRIS': 'QRIS', 'MBANKING': 'M-Banking'}
        metode = metode_map.get(data['metode'], data['metode'])

        # Create order
        nomor = create_order(
            chat_id=chat_id,
            nama=data['nama'],
            alamat=data['alamat'],
            telepon=data['telepon'],
            metode_bayar=metode,
            total=data['total']
        )

        # Cleanup
        del checkout_data[chat_id]

        teks = f"""
🎉 *PESANAN BERHASIL!*

━━━━━━━━━━━━━━━━━━━━

📋 *Nomor Pesanan:* `{nomor}`
💳 *Metode Bayar:* {metode}
💰 *Total:* Rp {data['total']:,}
📊 *Status:* ⏳ Menunggu Konfirmasi

━━━━━━━━━━━━━━━━━━━━

📌 *Simpan nomor pesanan Anda!*
Gunakan menu "Cek Pesanan" untuk tracking.

{"💵 Siapkan uang pas saat kurir datang." if metode == "COD" else ""}
{"📱 Pastikan sudah scan & bayar via QRIS." if metode == "QRIS" else ""}
{"🏦 Segera transfer dan konfirmasi ke admin." if metode == "M-Banking" else ""}

Terima kasih sudah berbelanja di *Gamelab Fashion Hub*! 🛍️
"""
        bot.send_message(chat_id, teks, parse_mode='Markdown', reply_markup=setelah_pesan())

    @bot.callback_query_handler(func=lambda c: c.data == 'cancel_order')
    def cb_cancel(call):
        bot.answer_callback_query(call.id)
        chat_id = call.message.chat.id
        if chat_id in checkout_data:
            del checkout_data[chat_id]
        bot.send_message(
            chat_id,
            "❌ Pesanan dibatalkan.",
            reply_markup=btn_kembali_menu()
        )

    # ==================== CETAK STRUK ====================

    @bot.callback_query_handler(func=lambda c: c.data.startswith('struk_'))
    def cb_cetak_struk(call):
        bot.answer_callback_query(call.id, "🖨️ Mencetak struk...")
        nomor = call.data[6:]
        order = get_order_by_number(nomor)

        if not order:
            bot.send_message(call.message.chat.id, "❌ Pesanan tidak ditemukan.")
            return

        teks = f"""
================================
     GAMELAB FASHION HUB
     STRUK PEMBELIAN RESMI
================================

Nomor   : {order['nomor_pesanan']}
Tanggal : {order['created_at']}
Nama    : {order['nama_pemesan']}
Metode  : {order['metode_bayar']}

--------------------------------
"""
        if 'items' in order:
            for item in order['items']:
                subtotal = item['harga'] * item['jumlah']
                teks += f"{item['nama_produk']} (Size {item['ukuran']})\n"
                teks += f"  {item['jumlah']} x Rp {item['harga']:,} = Rp {subtotal:,}\n"

        teks += f"""--------------------------------
TOTAL BAYAR   : Rp {order['total']:,}
================================
    Terima Kasih Telah Belanja
    di Gamelab Fashion Hub!
================================
"""
        bot.send_message(
            call.message.chat.id, 
            f"```text\n{teks}```", 
            parse_mode='Markdown'
        )

    # ==================== CEK PESANAN ====================

    @bot.callback_query_handler(func=lambda c: c.data == 'menu_cekpesanan')
    def cb_cekpesanan(call):
        bot.answer_callback_query(call.id)
        bot.send_message(
            call.message.chat.id,
            "📦 *CEK PESANAN*\n\nPilih cara cek pesanan:",
            parse_mode='Markdown',
            reply_markup=cek_pesanan_input()
        )

    @bot.callback_query_handler(func=lambda c: c.data == 'my_orders')
    def cb_my_orders(call):
        bot.answer_callback_query(call.id)
        orders = get_orders_by_chat(call.message.chat.id)

        if not orders:
            bot.send_message(
                call.message.chat.id,
                "📦 Anda belum memiliki pesanan.",
                reply_markup=btn_kembali_menu()
            )
            return

        teks = "📋 *RIWAYAT PESANAN ANDA*\n\n━━━━━━━━━━━━━━━━━━━━\n\n"
        for order in orders[:10]:
            emoji = STATUS_EMOJI.get(order['status'], '📦')
            teks += (
                f"📋 `{order['nomor_pesanan']}`\n"
                f"💰 Rp {order['total']:,}\n"
                f"💳 {order['metode_bayar']}\n"
                f"{emoji} Status: *{order['status']}*\n"
                f"📅 {order['created_at']}\n\n"
            )

        bot.send_message(call.message.chat.id, teks, parse_mode='Markdown',
                        reply_markup=btn_kembali_menu())

    @bot.callback_query_handler(func=lambda c: c.data == 'input_order_num')
    def cb_input_order(call):
        bot.answer_callback_query(call.id)
        msg = bot.send_message(
            call.message.chat.id,
            "🔍 Masukkan nomor pesanan Anda:\n_(contoh: FH2604xxxx)_",
            parse_mode='Markdown'
        )
        bot.register_next_step_handler(msg, _process_order_check)

    def _process_order_check(message):
        nomor = message.text.strip()
        order = get_order_by_number(nomor)

        if not order:
            bot.send_message(
                message.chat.id,
                f"❌ Pesanan `{nomor}` tidak ditemukan.\nPastikan nomor pesanan sudah benar.",
                parse_mode='Markdown',
                reply_markup=cek_pesanan_input()
            )
            return

        emoji = STATUS_EMOJI.get(order['status'], '📦')

        teks = f"""
📦 *DETAIL PESANAN*

━━━━━━━━━━━━━━━━━━━━

📋 No. Pesanan: `{order['nomor_pesanan']}`
👤 Nama: {order['nama_pemesan']}
📍 Alamat: {order['alamat']}
📱 Telepon: {order['telepon']}
💳 Metode Bayar: {order['metode_bayar']}
{emoji} Status: *{order['status']}*
📅 Tanggal: {order['created_at']}

━━━━━━━━━━━━━━━━━━━━

📋 *Item Pesanan:*
"""
        if 'items' in order:
            for i, item in enumerate(order['items'], 1):
                subtotal = item['harga'] * item['jumlah']
                teks += f"  {i}. {item['nama_produk']} ({item['ukuran']}) x{item['jumlah']} = Rp {subtotal:,}\n"

        teks += f"\n━━━━━━━━━━━━━━━━━━━━\n💰 *TOTAL: Rp {order['total']:,}*"

        bot.send_message(message.chat.id, teks, parse_mode='Markdown',
                        reply_markup=btn_kembali_menu())
