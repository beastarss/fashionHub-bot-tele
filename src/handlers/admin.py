"""
Gamelab Fashion Hub - Admin Panel Handler
Handles: admin login, dashboard, order management, product CRUD
Hidden menu accessed via /admin command
"""
import logging
from database import (
    is_admin, set_admin, get_order_stats, get_all_orders,
    get_order_by_number, update_order_status, get_all_products,
    get_product_by_id, add_product, update_product, delete_product
)
from keyboards import (
    admin_menu, admin_order_actions, btn_kembali_menu
)
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

ADMIN_PASSWORD = "admin123"

# Temp states
admin_states = {}


def register(bot):
    """Register admin handlers"""

    # ==================== ADMIN LOGIN ====================

    @bot.message_handler(commands=['admin'])
    def cmd_admin(message):
        chat_id = message.chat.id
        if is_admin(chat_id):
            _show_admin_panel(bot, chat_id)
            return

        msg = bot.send_message(
            chat_id,
            "🔐 *ADMIN LOGIN*\n\nMasukkan password admin:",
            parse_mode='Markdown'
        )
        bot.register_next_step_handler(msg, _process_admin_login)

    def _process_admin_login(message):
        chat_id = message.chat.id
        if message.text == ADMIN_PASSWORD:
            set_admin(chat_id)
            bot.send_message(chat_id, "✅ Login berhasil! Selamat datang, Admin.")
            _show_admin_panel(bot, chat_id)
        else:
            bot.send_message(chat_id, "❌ Password salah.", reply_markup=btn_kembali_menu())

    def _show_admin_panel(bot, chat_id):
        stats = get_order_stats()
        teks = f"""
🔐 *ADMIN PANEL - GAMELAB FASHION HUB*

━━━━━━━━━━━━━━━━━━━━

📊 *Dashboard Ringkas*

📋 Total Pesanan: *{stats['total_pesanan']}*
💰 Total Pendapatan: *Rp {stats['total_pendapatan']:,}*

⏳ Menunggu: *{stats['menunggu']}*
🔄 Diproses: *{stats['diproses']}*
🚚 Dikirim: *{stats['dikirim']}*
✅ Selesai: *{stats['selesai']}*
❌ Dibatalkan: *{stats['dibatalkan']}*

━━━━━━━━━━━━━━━━━━━━

Pilih aksi admin:
"""
        bot.send_message(chat_id, teks, parse_mode='Markdown', reply_markup=admin_menu())

    # ==================== ADMIN CALLBACKS ====================

    @bot.callback_query_handler(func=lambda c: c.data == 'adm_panel')
    def cb_admin_panel(call):
        bot.answer_callback_query(call.id)
        if not is_admin(call.message.chat.id):
            bot.answer_callback_query(call.id, "❌ Akses ditolak", show_alert=True)
            return
        _show_admin_panel(bot, call.message.chat.id)

    @bot.callback_query_handler(func=lambda c: c.data == 'adm_dashboard')
    def cb_dashboard(call):
        bot.answer_callback_query(call.id)
        if not is_admin(call.message.chat.id):
            return
        _show_admin_panel(bot, call.message.chat.id)

    # ==================== ORDER MANAGEMENT ====================

    @bot.callback_query_handler(func=lambda c: c.data == 'adm_orders')
    def cb_all_orders(call):
        bot.answer_callback_query(call.id)
        if not is_admin(call.message.chat.id):
            return
        _show_orders(bot, call.message.chat.id)

    @bot.callback_query_handler(func=lambda c: c.data.startswith('adm_filter_'))
    def cb_filter_orders(call):
        bot.answer_callback_query(call.id)
        if not is_admin(call.message.chat.id):
            return
        status = call.data[11:]  # Remove 'adm_filter_'
        _show_orders(bot, call.message.chat.id, status_filter=status)

    def _show_orders(bot, chat_id, status_filter=None):
        orders = get_all_orders(status_filter)

        if not orders:
            filter_text = f" ({status_filter})" if status_filter else ""
            bot.send_message(
                chat_id,
                f"📋 Tidak ada pesanan{filter_text}.",
                reply_markup=admin_menu()
            )
            return

        filter_text = f" - {status_filter}" if status_filter else " - Semua"
        teks = f"📋 *DAFTAR PESANAN{filter_text}*\n\n"

        STATUS_EMOJI = {
            'Menunggu Konfirmasi': '⏳', 'Diproses': '🔄',
            'Dikirim': '🚚', 'Selesai': '✅', 'Dibatalkan': '❌'
        }

        for order in orders[:15]:
            emoji = STATUS_EMOJI.get(order['status'], '📦')
            teks += (
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"📋 `{order['nomor_pesanan']}`\n"
                f"👤 {order['nama_pemesan']}\n"
                f"💰 Rp {order['total']:,} | 💳 {order['metode_bayar']}\n"
                f"{emoji} {order['status']}\n"
                f"📅 {order['created_at']}\n\n"
            )

        bot.send_message(chat_id, teks, parse_mode='Markdown')

        # Send action buttons for each order
        for order in orders[:10]:
            kb = InlineKeyboardMarkup(row_width=2)
            kb.add(
                InlineKeyboardButton(f"📋 Detail", callback_data=f"adm_detail_{order['nomor_pesanan']}"),
                InlineKeyboardButton(f"✏️ Update", callback_data=f"adm_update_{order['nomor_pesanan']}")
            )
            bot.send_message(
                chat_id,
                f"📋 `{order['nomor_pesanan']}` - {order['nama_pemesan']}",
                parse_mode='Markdown',
                reply_markup=kb
            )

        bot.send_message(chat_id, "⬆️ Pilih pesanan untuk detail/update:", reply_markup=admin_menu())

    @bot.callback_query_handler(func=lambda c: c.data.startswith('adm_detail_'))
    def cb_order_detail(call):
        bot.answer_callback_query(call.id)
        if not is_admin(call.message.chat.id):
            return

        nomor = call.data[11:]
        order = get_order_by_number(nomor)

        if not order:
            bot.send_message(call.message.chat.id, "❌ Pesanan tidak ditemukan.")
            return

        STATUS_EMOJI = {
            'Menunggu Konfirmasi': '⏳', 'Diproses': '🔄',
            'Dikirim': '🚚', 'Selesai': '✅', 'Dibatalkan': '❌'
        }
        emoji = STATUS_EMOJI.get(order['status'], '📦')

        teks = f"""
📦 *DETAIL PESANAN (ADMIN)*

━━━━━━━━━━━━━━━━━━━━

📋 No: `{order['nomor_pesanan']}`
👤 Nama: {order['nama_pemesan']}
📍 Alamat: {order['alamat']}
📱 Telepon: {order['telepon']}
💳 Bayar: {order['metode_bayar']}
{emoji} Status: *{order['status']}*
📅 Dibuat: {order['created_at']}
📅 Update: {order['updated_at']}

━━━━━━━━━━━━━━━━━━━━

📋 *Item Pesanan:*
"""
        if 'items' in order:
            for i, item in enumerate(order['items'], 1):
                subtotal = item['harga'] * item['jumlah']
                teks += f"  {i}. {item['nama_produk']} ({item['ukuran']}) x{item['jumlah']} = Rp {subtotal:,}\n"

        teks += f"\n━━━━━━━━━━━━━━━━━━━━\n💰 *TOTAL: Rp {order['total']:,}*"

        bot.send_message(
            call.message.chat.id,
            teks,
            parse_mode='Markdown',
            reply_markup=admin_order_actions(order['nomor_pesanan'])
        )

    @bot.callback_query_handler(func=lambda c: c.data.startswith('adm_update_'))
    def cb_update_order(call):
        bot.answer_callback_query(call.id)
        if not is_admin(call.message.chat.id):
            return

        nomor = call.data[11:]
        bot.send_message(
            call.message.chat.id,
            f"✏️ *Update Status Pesanan* `{nomor}`\n\nPilih status baru:",
            parse_mode='Markdown',
            reply_markup=admin_order_actions(nomor)
        )

    @bot.callback_query_handler(func=lambda c: c.data.startswith('adm_status_'))
    def cb_set_status(call):
        if not is_admin(call.message.chat.id):
            bot.answer_callback_query(call.id, "❌ Akses ditolak", show_alert=True)
            return

        # adm_status_FH2604xxxx_Diproses
        parts = call.data.split('_', 3)  # ['adm', 'status', 'FH...', 'StatusText']
        nomor = parts[2]
        new_status = parts[3]

        update_order_status(nomor, new_status)
        bot.answer_callback_query(call.id, f"✅ Status diupdate: {new_status}")

        # Notify user
        order = get_order_by_number(nomor)
        if order:
            STATUS_EMOJI = {
                'Menunggu Konfirmasi': '⏳', 'Diproses': '🔄',
                'Dikirim': '🚚', 'Selesai': '✅', 'Dibatalkan': '❌'
            }
            emoji = STATUS_EMOJI.get(new_status, '📦')

            try:
                from keyboards import user_status_update_kb
                bot.send_message(
                    order['chat_id'],
                    f"📢 *UPDATE PESANAN*\n\n📋 No: `{nomor}`\n{emoji} Status: *{new_status}*\n\n{'🎉 Pesanan Anda sudah selesai! Terima kasih!' if new_status == 'Selesai' else ''}",
                    parse_mode='Markdown',
                    reply_markup=user_status_update_kb(new_status, nomor)
                )
            except:
                pass

        # Stay on order detail page (reload with updated data)
        order = get_order_by_number(nomor)
        if order:
            STATUS_EMOJI_2 = {
                'Menunggu Konfirmasi': '⏳', 'Diproses': '🔄',
                'Dikirim': '🚚', 'Selesai': '✅', 'Dibatalkan': '❌'
            }
            emoji2 = STATUS_EMOJI_2.get(order['status'], '📦')
            teks = f"""
✅ *Status berhasil diupdate!*

━━━━━━━━━━━━━━━━━━━━

📋 No: `{order['nomor_pesanan']}`
👤 Nama: {order['nama_pemesan']}
📍 Alamat: {order['alamat']}
📱 Telepon: {order['telepon']}
💳 Bayar: {order['metode_bayar']}
{emoji2} Status: *{order['status']}*
📅 Dibuat: {order['created_at']}
📅 Update: {order['updated_at']}

━━━━━━━━━━━━━━━━━━━━

📋 *Item Pesanan:*
"""
            if 'items' in order:
                for i, item in enumerate(order['items'], 1):
                    subtotal = item['harga'] * item['jumlah']
                    teks += f"  {i}. {item['nama_produk']} ({item['ukuran']}) x{item['jumlah']} = Rp {subtotal:,}\n"

            teks += f"\n━━━━━━━━━━━━━━━━━━━━\n💰 *TOTAL: Rp {order['total']:,}*"

            # Show order detail with update buttons + back to admin panel
            kb = admin_order_actions(order['nomor_pesanan'])
            bot.send_message(call.message.chat.id, teks, parse_mode='Markdown', reply_markup=kb)
        else:
            bot.send_message(
                call.message.chat.id,
                f"✅ Status pesanan `{nomor}` diupdate menjadi *{new_status}*",
                parse_mode='Markdown',
                reply_markup=admin_menu()
            )

    # ==================== PRODUCT MANAGEMENT ====================

    @bot.callback_query_handler(func=lambda c: c.data == 'adm_allprod')
    def cb_all_products(call):
        bot.answer_callback_query(call.id)
        if not is_admin(call.message.chat.id):
            return

        products = get_all_products()
        teks = "📦 *SEMUA PRODUK*\n\n"

        current_kat = ""
        for p in products:
            if p['kategori'] != current_kat:
                current_kat = p['kategori']
                teks += f"\n━━ *{current_kat}* ━━\n"
            teks += f"  #{p['id']} {p['nama']} - Rp {p['harga']:,} (Stok: {p['stok']})\n"

        # Split if too long
        if len(teks) > 4000:
            parts = [teks[i:i+4000] for i in range(0, len(teks), 4000)]
            for part in parts:
                bot.send_message(call.message.chat.id, part, parse_mode='Markdown')
        else:
            bot.send_message(call.message.chat.id, teks, parse_mode='Markdown')

        bot.send_message(call.message.chat.id, "⬆️ Daftar semua produk", reply_markup=admin_menu())

    @bot.callback_query_handler(func=lambda c: c.data == 'adm_addprod')
    def cb_add_product(call):
        bot.answer_callback_query(call.id)
        if not is_admin(call.message.chat.id):
            return

        msg = bot.send_message(
            call.message.chat.id,
            "➕ *TAMBAH PRODUK BARU*\n\nKirim data produk dengan format:\n\n`Nama Produk, Kategori, Harga, Deskripsi, Stok, Ukuran, Bahan, Warna`\n\n_Contoh:_\n`Kaos Premium V2, Kaos, 129000, Kaos premium terbaru, 50, S M L XL, Cotton 30s, Hitam Putih`",
            parse_mode='Markdown'
        )
        bot.register_next_step_handler(msg, _process_add_product)

    def _process_add_product(message):
        if not is_admin(message.chat.id):
            return

        try:
            parts = [p.strip() for p in message.text.split(',')]
            if len(parts) < 4:
                bot.send_message(message.chat.id, "❌ Format salah. Minimal: Nama, Kategori, Harga, Deskripsi")
                return

            nama = parts[0]
            kategori = parts[1]
            harga = int(parts[2])
            deskripsi = parts[3]
            stok = int(parts[4]) if len(parts) > 4 else 50
            ukuran = parts[5] if len(parts) > 5 else 'S,M,L,XL,XXL'
            bahan = parts[6] if len(parts) > 6 else ''
            warna = parts[7] if len(parts) > 7 else ''

            add_product(nama, kategori, harga, deskripsi, stok, ukuran, bahan, warna)
            bot.send_message(
                message.chat.id,
                f"✅ Produk *{nama}* berhasil ditambahkan!\n\n📂 {kategori} | 💰 Rp {harga:,} | 📊 Stok: {stok}",
                parse_mode='Markdown',
                reply_markup=admin_menu()
            )
        except ValueError:
            bot.send_message(message.chat.id, "❌ Harga dan stok harus angka.", reply_markup=admin_menu())
        except Exception as e:
            bot.send_message(message.chat.id, f"❌ Error: {str(e)}", reply_markup=admin_menu())
            logging.error(f"Add Product Error: {e}")

    @bot.callback_query_handler(func=lambda c: c.data == 'adm_editprod')
    def cb_edit_product(call):
        bot.answer_callback_query(call.id)
        if not is_admin(call.message.chat.id):
            return

        msg = bot.send_message(
            call.message.chat.id,
            "✏️ *EDIT PRODUK*\n\nKirim dengan format:\n`ID_PRODUK, field=value`\n\n_Contoh:_\n`1, harga=99000`\n`5, stok=100`\n`3, nama=Kaos Baru Premium`\n\n_Fields: nama, kategori, harga, deskripsi, stok, ukuran, bahan, warna_",
            parse_mode='Markdown'
        )
        bot.register_next_step_handler(msg, _process_edit_product)

    def _process_edit_product(message):
        if not is_admin(message.chat.id):
            return

        try:
            parts = message.text.split(',', 1)
            produk_id = int(parts[0].strip())
            field_val = parts[1].strip()

            field, value = field_val.split('=', 1)
            field = field.strip()
            value = value.strip()

            if field in ('harga', 'stok'):
                value = int(value)

            product = get_product_by_id(produk_id)
            if not product:
                bot.send_message(message.chat.id, f"❌ Produk #{produk_id} tidak ditemukan.", reply_markup=admin_menu())
                return

            update_product(produk_id, **{field: value})
            bot.send_message(
                message.chat.id,
                f"✅ Produk #{produk_id} *{product['nama']}* berhasil diupdate!\n{field} = {value}",
                parse_mode='Markdown',
                reply_markup=admin_menu()
            )
        except Exception as e:
            bot.send_message(message.chat.id, f"❌ Format salah atau error: {str(e)}", reply_markup=admin_menu())

    @bot.callback_query_handler(func=lambda c: c.data == 'adm_delprod')
    def cb_delete_product(call):
        bot.answer_callback_query(call.id)
        if not is_admin(call.message.chat.id):
            return

        msg = bot.send_message(
            call.message.chat.id,
            "🗑️ *HAPUS PRODUK*\n\nMasukkan ID produk yang ingin dihapus:\n_(contoh: 5)_",
            parse_mode='Markdown'
        )
        bot.register_next_step_handler(msg, _process_delete_product)

    def _process_delete_product(message):
        if not is_admin(message.chat.id):
            return

        try:
            produk_id = int(message.text.strip())
            product = get_product_by_id(produk_id)

            if not product:
                bot.send_message(message.chat.id, f"❌ Produk #{produk_id} tidak ditemukan.", reply_markup=admin_menu())
                return

            delete_product(produk_id)
            bot.send_message(
                message.chat.id,
                f"🗑️ Produk #{produk_id} *{product['nama']}* berhasil dihapus!",
                parse_mode='Markdown',
                reply_markup=admin_menu()
            )
        except ValueError:
            bot.send_message(message.chat.id, "❌ ID harus berupa angka.", reply_markup=admin_menu())
        except Exception as e:
            bot.send_message(message.chat.id, f"❌ Error: {str(e)}", reply_markup=admin_menu())
