"""
Gamelab Fashion Hub - Katalog Handler
Handles: kategori, produk browse, product list, search, pilih ukuran
"""
import os
from database import (
    get_products_by_category, get_product_by_id,
    search_products, add_to_cart, get_conn
)
from keyboards import (
    kategori_menu, produk_navigation, ukuran_menu,
    btn_kembali_menu, menu_utama, search_result_btn
)
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

ASSETS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'assets')

# Map kategori to emoji
KATEGORI_EMOJI = {
    'Kaos': '👕', 'Kemeja': '👔', 'Celana': '👖', 'Jaket': '🧥',
    'Hoodie': '🧤', 'Sweater': '🧶', 'Dress': '👗', 'Rok': '💃'
}

# Map kategori to image file
KATEGORI_IMG = {
    'Kaos': 'kaos.png', 'Kemeja': 'kemeja.png', 'Celana': 'celana.png',
    'Jaket': 'jaket.png', 'Hoodie': 'hoodie.png', 'Sweater': 'sweater.png',
    'Dress': 'dress.png', 'Rok': 'rok.png'
}

def _format_product_text(p):
    """Format product info text"""
    emoji = KATEGORI_EMOJI.get(p['kategori'], '🏷️')
    stok_status = "✅ Ready" if p['stok'] > 0 else "❌ Habis"

    return f"""
{emoji} *{p['nama']}*

━━━━━━━━━━━━━━━━━━━━
📂 Kategori: {p['kategori']}
💰 Harga: *Rp {p['harga']:,}*
📊 Stok: {p['stok']} ({stok_status})
📏 Ukuran: {p['ukuran']}
🎨 Warna: {p['warna']}
🧵 Bahan: {p['bahan']}

📝 {p['deskripsi']}
━━━━━━━━━━━━━━━━━━━━
"""


def _get_all_in_category(kategori):
    """Get all products in a category"""
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM produk_baju WHERE kategori = ? ORDER BY id", (kategori,))
    results = [dict(row) for row in cur.fetchall()]
    conn.close()
    return results


def _send_product_detail(bot, chat_id, produk_id):
    """Send single product detail with photo"""
    product = get_product_by_id(produk_id)
    if not product:
        bot.send_message(chat_id, "😕 Produk tidak ditemukan.", reply_markup=kategori_menu())
        return

    text = _format_product_text(product)
    kategori = product['kategori']

    # Build keyboard: size select + back to list + menu
    kb = InlineKeyboardMarkup(row_width=1)
    kb.add(
        InlineKeyboardButton("📏 Pilih Ukuran & Pesan", callback_data=f"size_{produk_id}"),
        InlineKeyboardButton(f"📋 Kembali ke Daftar {kategori}", callback_data=f"kat_{kategori}"),
        InlineKeyboardButton("📂 Semua Kategori", callback_data="menu_katalog"),
        InlineKeyboardButton("🏠 Menu Utama", callback_data="menu_utama"),
    )

    # Send with category image
    img_file = KATEGORI_IMG.get(kategori, 'kaos.png')
    img_path = os.path.join(ASSETS_DIR, 'products', img_file)

    if os.path.exists(img_path):
        with open(img_path, 'rb') as photo:
            bot.send_photo(chat_id, photo, caption=text, parse_mode='Markdown', reply_markup=kb)
    else:
        bot.send_message(chat_id, text, parse_mode='Markdown', reply_markup=kb)


def register(bot):
    """Register katalog handlers"""

    @bot.callback_query_handler(func=lambda c: c.data == 'menu_katalog')
    def cb_katalog(call):
        bot.answer_callback_query(call.id)
        teks = """
👕 *KATALOG GAMELAB FASHION HUB*

━━━━━━━━━━━━━━━━━━━━
Pilih kategori untuk melihat koleksi kami:
"""
        bot.send_message(
            call.message.chat.id,
            teks,
            parse_mode='Markdown',
            reply_markup=kategori_menu()
        )

    @bot.callback_query_handler(func=lambda c: c.data.startswith('kat_'))
    def cb_kategori(call):
        """Show product LIST for a category (buttons with name + price)"""
        bot.answer_callback_query(call.id, "⏳ Memuat produk...")
        kategori = call.data[4:]
        emoji = KATEGORI_EMOJI.get(kategori, '🏷️')

        products = _get_all_in_category(kategori)
        if not products:
            bot.send_message(call.message.chat.id, "😕 Belum ada produk di kategori ini.",
                           reply_markup=kategori_menu())
            return

        # Build text summary
        teks = f"{emoji} *KOLEKSI {kategori.upper()}*\n\n"
        teks += f"━━━━━━━━━━━━━━━━━━━━\n"
        teks += f"📦 {len(products)} produk tersedia\n"
        teks += f"💰 Rp {min(p['harga'] for p in products):,} - Rp {max(p['harga'] for p in products):,}\n"
        teks += f"━━━━━━━━━━━━━━━━━━━━\n\n"
        teks += "Pilih produk untuk melihat detail:\n"

        # Send category image with text
        img_file = KATEGORI_IMG.get(kategori, 'kaos.png')
        img_path = os.path.join(ASSETS_DIR, 'products', img_file)

        if os.path.exists(img_path):
            with open(img_path, 'rb') as photo:
                bot.send_photo(call.message.chat.id, photo, caption=teks, parse_mode='Markdown')
        else:
            bot.send_message(call.message.chat.id, teks, parse_mode='Markdown')

        # Build product list as buttons (1 button per product with name + price)
        kb = InlineKeyboardMarkup(row_width=1)
        for p in products:
            stok_icon = "✅" if p['stok'] > 0 else "❌"
            btn_text = f"{stok_icon} {p['nama']} — Rp {p['harga']:,}"
            kb.add(InlineKeyboardButton(btn_text, callback_data=f"detail_{p['id']}"))

        # Add navigation buttons
        kb.row(
            InlineKeyboardButton("📂 Semua Kategori", callback_data="menu_katalog"),
            InlineKeyboardButton("🏠 Menu Utama", callback_data="menu_utama")
        )

        bot.send_message(call.message.chat.id, "👇 *Pilih produk:*", parse_mode='Markdown', reply_markup=kb)

    @bot.callback_query_handler(func=lambda c: c.data.startswith('detail_'))
    def cb_product_detail(call):
        """Show full product detail"""
        bot.answer_callback_query(call.id, "⏳ Memuat detail...")
        produk_id = int(call.data[7:])
        _send_product_detail(bot, call.message.chat.id, produk_id)

    @bot.callback_query_handler(func=lambda c: c.data.startswith('view_'))
    def cb_view_product(call):
        """View product from search results"""
        bot.answer_callback_query(call.id)
        produk_id = int(call.data[5:])
        _send_product_detail(bot, call.message.chat.id, produk_id)

    @bot.callback_query_handler(func=lambda c: c.data.startswith('size_'))
    def cb_size_select(call):
        bot.answer_callback_query(call.id)
        produk_id = int(call.data[5:])
        product = get_product_by_id(produk_id)
        if not product:
            bot.send_message(call.message.chat.id, "❌ Produk tidak ditemukan.")
            return

        if product['stok'] <= 0:
            bot.answer_callback_query(call.id, "❌ Maaf, stok habis!", show_alert=True)
            return

        teks = f"📏 *Pilih ukuran untuk {product['nama']}:*\n💰 Rp {product['harga']:,}"
        bot.send_message(
            call.message.chat.id,
            teks,
            parse_mode='Markdown',
            reply_markup=ukuran_menu(produk_id, product['ukuran'])
        )

    @bot.callback_query_handler(func=lambda c: c.data.startswith('addcart_'))
    def cb_add_to_cart(call):
        parts = call.data.split('_')
        produk_id = int(parts[1])
        ukuran = parts[2]

        product = get_product_by_id(produk_id)
        if not product:
            bot.answer_callback_query(call.id, "❌ Produk tidak ditemukan", show_alert=True)
            return

        add_to_cart(call.message.chat.id, produk_id, ukuran)
        bot.answer_callback_query(call.id, f"✅ {product['nama']} (Size {ukuran}) ditambahkan ke keranjang!", show_alert=True)

        kb = InlineKeyboardMarkup(row_width=2)
        kb.add(
            InlineKeyboardButton("🛒 Lihat Keranjang", callback_data="menu_keranjang"),
            InlineKeyboardButton("👕 Lanjut Belanja", callback_data="menu_katalog"),
        )
        bot.send_message(
            call.message.chat.id,
            f"✅ *Berhasil ditambahkan!*\n\n📦 {product['nama']}\n📏 Ukuran: {ukuran}\n💰 Rp {product['harga']:,}",
            parse_mode='Markdown',
            reply_markup=kb
        )

    @bot.callback_query_handler(func=lambda c: c.data.startswith('back_to_prod_'))
    def cb_back_to_prod(call):
        bot.answer_callback_query(call.id)
        produk_id = int(call.data[13:])
        _send_product_detail(bot, call.message.chat.id, produk_id)

    # Search
    @bot.callback_query_handler(func=lambda c: c.data == 'menu_cari')
    def cb_search(call):
        bot.answer_callback_query(call.id)
        msg = bot.send_message(
            call.message.chat.id,
            "🔍 *Cari Produk*\n\nKetik nama produk, kategori, atau kata kunci:\n_(contoh: kaos polos, hoodie, denim)_",
            parse_mode='Markdown',
            reply_markup=btn_kembali_menu()
        )
        bot.register_next_step_handler(msg, process_search)

    def process_search(message):
        keyword = message.text
        if not keyword or keyword.startswith('/'):
            return

        results = search_products(keyword)
        if not results:
            bot.send_message(
                message.chat.id,
                f"😕 Tidak ditemukan produk untuk *\"{keyword}\"*\nCoba kata kunci lain.",
                parse_mode='Markdown',
                reply_markup=btn_kembali_menu()
            )
            return

        teks = f"🔍 *Hasil Pencarian:* \"{keyword}\"\nDitemukan {len(results)} produk:\n"

        # Build result buttons
        kb = InlineKeyboardMarkup(row_width=1)
        for p in results[:10]:
            emoji = KATEGORI_EMOJI.get(p['kategori'], '🏷️')
            stok_icon = "✅" if p['stok'] > 0 else "❌"
            btn_text = f"{stok_icon} {p['nama']} — Rp {p['harga']:,}"
            kb.add(InlineKeyboardButton(btn_text, callback_data=f"detail_{p['id']}"))

        kb.row(
            InlineKeyboardButton("🔍 Cari Lagi", callback_data="menu_cari"),
            InlineKeyboardButton("🏠 Menu Utama", callback_data="menu_utama")
        )

        bot.send_message(message.chat.id, teks, parse_mode='Markdown', reply_markup=kb)
