"""
Gamelab Fashion Hub - Keranjang (Cart) Handler
Handles: view cart, update qty, remove item, clear cart
"""
from database import get_cart, update_cart_qty, remove_from_cart, clear_cart, get_cart_total
from keyboards import keranjang_item, keranjang_actions, keranjang_kosong

def register(bot):
    """Register keranjang handlers"""

    @bot.callback_query_handler(func=lambda c: c.data == 'menu_keranjang')
    def cb_keranjang(call):
        bot.answer_callback_query(call.id)
        _show_cart(bot, call.message.chat.id)

    def _show_cart(bot, chat_id):
        items = get_cart(chat_id)

        if not items:
            bot.send_message(
                chat_id,
                "🛒 *KERANJANG BELANJA*\n\n━━━━━━━━━━━━━━━━━━━━\n\n😕 Keranjang Anda masih kosong.\nAyo mulai belanja! 🛍️",
                parse_mode='Markdown',
                reply_markup=keranjang_kosong()
            )
            return

        total = get_cart_total(chat_id)

        teks = "🛒 *KERANJANG BELANJA*\n\n━━━━━━━━━━━━━━━━━━━━\n\n"

        for i, item in enumerate(items, 1):
            subtotal = item['harga'] * item['jumlah']
            teks += (
                f"*{i}. {item['nama']}*\n"
                f"   📏 Ukuran: {item['ukuran']}\n"
                f"   💰 Rp {item['harga']:,} x {item['jumlah']} = *Rp {subtotal:,}*\n\n"
            )

        teks += f"━━━━━━━━━━━━━━━━━━━━\n💰 *TOTAL: Rp {total:,}*\n━━━━━━━━━━━━━━━━━━━━"

        bot.send_message(chat_id, teks, parse_mode='Markdown')

        # Send individual item control buttons
        for i, item in enumerate(items):
            bot.send_message(
                chat_id,
                f"📦 {item['nama']} (Size {item['ukuran']}) — Qty: {item['jumlah']}",
                reply_markup=keranjang_item(item['id'], i)
            )

        # Send action buttons
        bot.send_message(
            chat_id,
            f"📝 *Total {len(items)} item* | 💰 *Rp {total:,}*\n\nPilih aksi:",
            parse_mode='Markdown',
            reply_markup=keranjang_actions()
        )

    @bot.callback_query_handler(func=lambda c: c.data.startswith('cartplus_'))
    def cb_cart_plus(call):
        cart_id = int(call.data[9:])
        update_cart_qty(cart_id, 1)
        bot.answer_callback_query(call.id, "➕ Jumlah ditambah!")
        _show_cart(bot, call.message.chat.id)

    @bot.callback_query_handler(func=lambda c: c.data.startswith('cartmin_'))
    def cb_cart_minus(call):
        cart_id = int(call.data[8:])
        update_cart_qty(cart_id, -1)
        bot.answer_callback_query(call.id, "➖ Jumlah dikurangi!")
        _show_cart(bot, call.message.chat.id)

    @bot.callback_query_handler(func=lambda c: c.data.startswith('cartdel_'))
    def cb_cart_delete(call):
        cart_id = int(call.data[8:])
        remove_from_cart(cart_id)
        bot.answer_callback_query(call.id, "🗑️ Item dihapus!")
        _show_cart(bot, call.message.chat.id)

    @bot.callback_query_handler(func=lambda c: c.data == 'cart_clear')
    def cb_cart_clear(call):
        clear_cart(call.message.chat.id)
        bot.answer_callback_query(call.id, "🗑️ Keranjang dikosongkan!")
        bot.send_message(
            call.message.chat.id,
            "🗑️ Keranjang telah dikosongkan.",
            reply_markup=keranjang_kosong()
        )
