"""
FashionHub - Keyboard Builder Module
Semua InlineKeyboardMarkup untuk navigasi bot
"""
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# ==================== MENU UTAMA ====================

def menu_utama():
    """Keyboard menu utama beranda"""
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton("👕 Katalog Produk", callback_data="menu_katalog"),
        InlineKeyboardButton("🛒 Keranjang", callback_data="menu_keranjang"),
        InlineKeyboardButton("🤖 Chat AI Fashion", callback_data="menu_ai"),
        InlineKeyboardButton("ℹ️ Tentang Kami", callback_data="menu_tentang"),
        InlineKeyboardButton("📞 Kontak", callback_data="menu_kontak"),
        InlineKeyboardButton("🕒 Jam Kerja", callback_data="menu_jamkerja"),
        InlineKeyboardButton("📦 Cek Pesanan Saya", callback_data="menu_cekpesanan"),
        InlineKeyboardButton("🔍 Cari Produk", callback_data="menu_cari"),
        InlineKeyboardButton("🏦 Rekening Seller", callback_data="menu_rekening"),
        InlineKeyboardButton("📏 Panduan Ukuran", callback_data="menu_panduan_ukuran"),
    )
    return kb

def btn_kembali_menu():
    """Tombol kembali ke menu utama"""
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("🏠 Menu Utama", callback_data="menu_utama"))
    return kb

# ==================== KATALOG ====================

def kategori_menu():
    """Keyboard pilih kategori"""
    kb = InlineKeyboardMarkup(row_width=2)
    categories = [
        ("👕 Kaos", "kat_Kaos"),
        ("👔 Kemeja", "kat_Kemeja"),
        ("👖 Celana", "kat_Celana"),
        ("🧥 Jaket", "kat_Jaket"),
        ("🧤 Hoodie", "kat_Hoodie"),
        ("🧶 Sweater", "kat_Sweater"),
        ("👗 Dress", "kat_Dress"),
        ("💃 Rok", "kat_Rok"),
    ]
    buttons = [InlineKeyboardButton(text, callback_data=data) for text, data in categories]
    kb.add(*buttons)
    kb.add(InlineKeyboardButton("🏠 Menu Utama", callback_data="menu_utama"))
    return kb

def produk_navigation(kategori, page, total, produk_id):
    """Keyboard navigasi produk (prev/next + actions)"""
    kb = InlineKeyboardMarkup(row_width=3)

    # Navigation row
    nav_buttons = []
    if page > 0:
        nav_buttons.append(InlineKeyboardButton("◀️ Prev", callback_data=f"nav_{kategori}_{page-1}"))
    nav_buttons.append(InlineKeyboardButton(f"📄 {page+1}/{total}", callback_data="noop"))
    if page < total - 1:
        nav_buttons.append(InlineKeyboardButton("Next ▶️", callback_data=f"nav_{kategori}_{page+1}"))
    kb.row(*nav_buttons)

    # Action row
    kb.row(
        InlineKeyboardButton("📏 Pilih Ukuran & Pesan", callback_data=f"size_{produk_id}")
    )

    # Back row
    kb.row(
        InlineKeyboardButton("📂 Kategori", callback_data="menu_katalog"),
        InlineKeyboardButton("🏠 Menu Utama", callback_data="menu_utama")
    )
    return kb

def ukuran_menu(produk_id, sizes_str):
    """Keyboard pilih ukuran"""
    kb = InlineKeyboardMarkup(row_width=3)
    sizes = [s.strip() for s in sizes_str.split(',')]
    buttons = [InlineKeyboardButton(f"📏 {s}", callback_data=f"addcart_{produk_id}_{s}") for s in sizes]
    kb.add(*buttons)
    kb.row(InlineKeyboardButton("🔙 Kembali", callback_data=f"back_to_prod_{produk_id}"))
    return kb

# ==================== KERANJANG ====================

def keranjang_item(cart_id, idx):
    """Keyboard per item keranjang"""
    kb = InlineKeyboardMarkup(row_width=3)
    kb.add(
        InlineKeyboardButton("➖", callback_data=f"cartmin_{cart_id}"),
        InlineKeyboardButton("🗑️ Hapus", callback_data=f"cartdel_{cart_id}"),
        InlineKeyboardButton("➕", callback_data=f"cartplus_{cart_id}"),
    )
    return kb

def keranjang_actions():
    """Keyboard aksi keranjang"""
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton("📦 Checkout", callback_data="checkout_start"),
        InlineKeyboardButton("🗑️ Kosongkan", callback_data="cart_clear"),
        InlineKeyboardButton("👕 Lanjut Belanja", callback_data="menu_katalog"),
        InlineKeyboardButton("🏠 Menu Utama", callback_data="menu_utama"),
    )
    return kb

def keranjang_kosong():
    """Keyboard keranjang kosong"""
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton("👕 Belanja Sekarang", callback_data="menu_katalog"),
        InlineKeyboardButton("🏠 Menu Utama", callback_data="menu_utama"),
    )
    return kb

# ==================== PEMBAYARAN ====================

def metode_bayar():
    """Keyboard pilih metode pembayaran"""
    kb = InlineKeyboardMarkup(row_width=1)
    kb.add(
        InlineKeyboardButton("💵 COD (Bayar di Tempat)", callback_data="bayar_COD"),
        InlineKeyboardButton("📱 QRIS (Scan QR)", callback_data="bayar_QRIS"),
        InlineKeyboardButton("🏦 M-Banking (Transfer Bank)", callback_data="bayar_MBANKING"),
    )
    kb.row(InlineKeyboardButton("🔙 Kembali", callback_data="menu_keranjang"))
    return kb

def konfirmasi_pesanan():
    """Keyboard konfirmasi pesanan"""
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton("✅ Konfirmasi Pesan", callback_data="confirm_order"),
        InlineKeyboardButton("❌ Batalkan", callback_data="cancel_order"),
    )
    return kb

def setelah_pesan():
    """Keyboard setelah pesanan berhasil"""
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton("📦 Cek Pesanan Saya", callback_data="menu_cekpesanan"),
        InlineKeyboardButton("👕 Belanja Lagi", callback_data="menu_katalog"),
        InlineKeyboardButton("🏠 Menu Utama", callback_data="menu_utama"),
    )
    return kb

def user_status_update_kb(status, nomor_pesanan):
    """Keyboard notifikasi update status untuk user"""
    kb = InlineKeyboardMarkup(row_width=1)
    if status == 'Selesai':
        kb.add(InlineKeyboardButton("🖨️ Cetak Struk Pembelian", callback_data=f"struk_{nomor_pesanan}"))
    kb.row(
        InlineKeyboardButton("📦 Pesanan Saya", callback_data="my_orders"),
        InlineKeyboardButton("🏠 Beranda", callback_data="menu_utama")
    )
    return kb

# ==================== AI CHAT ====================

def ai_chat_menu():
    """Keyboard AI chat"""
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton("🟢 Mulai Chat AI", callback_data="ai_start"),
        InlineKeyboardButton("🔴 Stop Chat AI", callback_data="ai_stop"),
        InlineKeyboardButton("🏠 Menu Utama", callback_data="menu_utama"),
    )
    return kb

def ai_stop_btn():
    """Tombol stop AI"""
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("🔴 Stop Chat AI", callback_data="ai_stop"))
    return kb

# ==================== ADMIN ====================

def admin_menu():
    """Keyboard admin panel"""
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton("📊 Dashboard", callback_data="adm_dashboard"),
        InlineKeyboardButton("📋 Semua Pesanan", callback_data="adm_orders"),
        InlineKeyboardButton("⏳ Pesanan Baru", callback_data="adm_filter_Menunggu Konfirmasi"),
        InlineKeyboardButton("🔄 Diproses", callback_data="adm_filter_Diproses"),
        InlineKeyboardButton("🚚 Dikirim", callback_data="adm_filter_Dikirim"),
        InlineKeyboardButton("✅ Selesai", callback_data="adm_filter_Selesai"),
        InlineKeyboardButton("➕ Tambah Produk", callback_data="adm_addprod"),
        InlineKeyboardButton("📝 Edit Produk", callback_data="adm_editprod"),
        InlineKeyboardButton("🗑️ Hapus Produk", callback_data="adm_delprod"),
        InlineKeyboardButton("📦 Semua Produk", callback_data="adm_allprod"),
        InlineKeyboardButton("🏠 Menu Utama", callback_data="menu_utama"),
    )
    return kb

def admin_order_actions(nomor_pesanan):
    """Keyboard update status pesanan"""
    kb = InlineKeyboardMarkup(row_width=2)
    statuses = [
        ("⏳ Menunggu", f"adm_status_{nomor_pesanan}_Menunggu Konfirmasi"),
        ("🔄 Proses", f"adm_status_{nomor_pesanan}_Diproses"),
        ("🚚 Kirim", f"adm_status_{nomor_pesanan}_Dikirim"),
        ("✅ Selesai", f"adm_status_{nomor_pesanan}_Selesai"),
        ("❌ Batalkan", f"adm_status_{nomor_pesanan}_Dibatalkan"),
    ]
    buttons = [InlineKeyboardButton(text, callback_data=data) for text, data in statuses]
    kb.add(*buttons)
    kb.row(InlineKeyboardButton("🔙 Admin Panel", callback_data="adm_panel"))
    return kb

def admin_order_detail_btn(nomor_pesanan):
    """Button to view order detail"""
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton(f"📋 Detail {nomor_pesanan}", callback_data=f"adm_detail_{nomor_pesanan}"))
    return kb

# ==================== MISC ====================

def cek_pesanan_input():
    """Keyboard cek pesanan"""
    kb = InlineKeyboardMarkup(row_width=1)
    kb.add(
        InlineKeyboardButton("📋 Riwayat Pesanan Saya", callback_data="my_orders"),
        InlineKeyboardButton("🔍 Cek via Nomor Pesanan", callback_data="input_order_num"),
        InlineKeyboardButton("🏠 Menu Utama", callback_data="menu_utama"),
    )
    return kb

def search_result_btn(produk_id, nama):
    """Button for search result item"""
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton(f"👀 Lihat {nama[:30]}", callback_data=f"view_{produk_id}"))
    return kb
