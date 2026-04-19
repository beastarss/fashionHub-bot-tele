import sqlite3
import os
from datetime import datetime

# Nama file database
DB_NAME = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "umkm.db")

def get_conn():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Membuat semua tabel dan seed data produk baju"""
    conn = get_conn()
    cursor = conn.cursor()

    # 1. Tabel Produk Baju
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS produk_baju (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nama TEXT NOT NULL,
            kategori TEXT NOT NULL,
            harga INTEGER NOT NULL,
            deskripsi TEXT,
            stok INTEGER DEFAULT 50,
            ukuran TEXT DEFAULT 'S,M,L,XL,XXL',
            bahan TEXT,
            warna TEXT
        )
    ''')

    # 2. Tabel Keranjang
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS keranjang (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            chat_id INTEGER NOT NULL,
            produk_id INTEGER NOT NULL,
            jumlah INTEGER DEFAULT 1,
            ukuran TEXT DEFAULT 'M',
            FOREIGN KEY (produk_id) REFERENCES produk_baju(id)
        )
    ''')

    # 3. Tabel Pesanan
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS pesanan (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nomor_pesanan TEXT UNIQUE NOT NULL,
            chat_id INTEGER NOT NULL,
            nama_pemesan TEXT NOT NULL,
            alamat TEXT NOT NULL,
            telepon TEXT NOT NULL,
            metode_bayar TEXT NOT NULL,
            status TEXT DEFAULT 'Menunggu Konfirmasi',
            total INTEGER NOT NULL,
            catatan TEXT,
            created_at TEXT DEFAULT (datetime('now', 'localtime')),
            updated_at TEXT DEFAULT (datetime('now', 'localtime'))
        )
    ''')

    # 4. Tabel Item Pesanan
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS item_pesanan (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pesanan_id INTEGER NOT NULL,
            produk_id INTEGER NOT NULL,
            nama_produk TEXT NOT NULL,
            jumlah INTEGER NOT NULL,
            ukuran TEXT NOT NULL,
            harga INTEGER NOT NULL,
            FOREIGN KEY (pesanan_id) REFERENCES pesanan(id),
            FOREIGN KEY (produk_id) REFERENCES produk_baju(id)
        )
    ''')

    # 5. Tabel Admin
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS admin_users (
            chat_id INTEGER PRIMARY KEY,
            is_admin INTEGER DEFAULT 0
        )
    ''')

    # 6. Tabel Info Toko
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS info (
            kunci TEXT PRIMARY KEY,
            isi TEXT
        )
    ''')

    # Seed info toko
    try:
        cursor.execute("INSERT OR IGNORE INTO info VALUES ('jam_kerja', '09:00 - 21:00 WIB (Senin - Sabtu)')")
        cursor.execute("INSERT OR IGNORE INTO info VALUES ('kontak', '📱 WhatsApp: 0812-3456-7890\n📧 Email: support@fashionhub.id\n📸 Instagram: @fashionhub.id')")
        cursor.execute("INSERT OR IGNORE INTO info VALUES ('alamat', 'Jl. Fashion Street No. 88, Jakarta Selatan')")
    except:
        pass

    # Seed 50 produk baju
    _seed_products(cursor)

    conn.commit()
    conn.close()

def _seed_products(cursor):
    """Insert 50+ produk baju ke database"""
    # Check if already seeded
    cursor.execute("SELECT COUNT(*) FROM produk_baju")
    if cursor.fetchone()[0] > 0:
        return

    products = [
        # ===== KAOS (8) =====
        ("Kaos Polos Premium", "Kaos", 89000, "Kaos polos premium cotton combed 30s, nyaman dipakai sehari-hari", 100, "S,M,L,XL,XXL", "Cotton Combed 30s", "Hitam, Putih, Navy, Abu-abu"),
        ("Kaos Oversize Street", "Kaos", 129000, "Kaos oversize street style dengan cutting boxy, trendy & kekinian", 75, "M,L,XL,XXL", "Cotton Combed 24s", "Hitam, Cream, Sage Green"),
        ("Kaos Grafis Urban", "Kaos", 149000, "Kaos dengan print grafis urban art, desain eksklusif limited edition", 50, "S,M,L,XL", "Cotton Combed 24s", "Hitam, Putih"),
        ("Kaos Tie Dye Vintage", "Kaos", 139000, "Kaos tie dye handmade dengan pola unik vintage, setiap piece berbeda", 40, "M,L,XL", "Cotton Combed 30s", "Multi Color"),
        ("Kaos Polo Classic", "Kaos", 179000, "Kaos polo kerah klasik, cocok untuk casual & semi-formal", 60, "S,M,L,XL,XXL", "Lacoste Cotton", "Hitam, Putih, Navy, Maroon"),
        ("Kaos Henley Casual", "Kaos", 159000, "Kaos henley dengan kancing depan, tampilan casual maskulin", 55, "S,M,L,XL", "Cotton Combed 24s", "Hitam, Abu-abu, Olive"),
        ("Kaos V-Neck Slim", "Kaos", 99000, "Kaos V-neck slim fit, siluet ramping dan modern", 80, "S,M,L,XL", "Cotton Spandex", "Hitam, Putih, Navy"),
        ("Kaos Crop Top Wanita", "Kaos", 109000, "Kaos crop top wanita, potongan trendy untuk tampilan stylish", 65, "S,M,L", "Cotton Combed 30s", "Putih, Pink, Lilac"),

        # ===== KEMEJA (7) =====
        ("Kemeja Flannel Classic", "Kemeja", 199000, "Kemeja flannel kotak-kotak klasik, hangat dan stylish", 45, "S,M,L,XL,XXL", "Cotton Flannel", "Merah-Hitam, Hijau-Hitam, Biru-Hitam"),
        ("Kemeja Denim Wash", "Kemeja", 229000, "Kemeja denim wash premium dengan detail jahitan rapi", 40, "S,M,L,XL", "Denim Cotton", "Light Blue, Dark Blue"),
        ("Kemeja Linen Tropical", "Kemeja", 249000, "Kemeja linen adem untuk cuaca tropis, breathable dan ringan", 35, "S,M,L,XL", "Linen", "Putih, Cream, Light Blue"),
        ("Kemeja Oxford Formal", "Kemeja", 219000, "Kemeja oxford button-down, cocok untuk kerja dan acara formal", 50, "S,M,L,XL,XXL", "Oxford Cotton", "Putih, Biru Muda, Pink"),
        ("Kemeja Hawaiian Vibes", "Kemeja", 189000, "Kemeja hawaiian motif tropis, perfect untuk liburan dan hangout", 30, "M,L,XL", "Rayon", "Multi Pattern"),
        ("Kemeja Batik Modern", "Kemeja", 279000, "Kemeja batik modern kontemporer, perpaduan tradisi dan gaya kekinian", 25, "S,M,L,XL,XXL", "Katun Batik", "Coklat, Navy, Hitam"),
        ("Kemeja Corduroy Retro", "Kemeja", 239000, "Kemeja corduroy bertekstur retro, cocok untuk layering musim hujan", 35, "S,M,L,XL", "Corduroy", "Coklat, Hijau Army, Maroon"),

        # ===== CELANA (8) =====
        ("Celana Jeans Slim Fit", "Celana", 259000, "Celana jeans slim fit stretch, nyaman dan fleksibel", 70, "28,29,30,31,32,33,34", "Denim Stretch", "Dark Blue, Black, Light Blue"),
        ("Celana Jeans Baggy 90s", "Celana", 279000, "Celana jeans baggy ala 90s, loose fit yang sedang tren", 50, "28,30,32,34", "Denim 14oz", "Medium Blue, Black"),
        ("Celana Chino Regular", "Celana", 229000, "Celana chino regular fit, versatile untuk casual & semi-formal", 60, "28,29,30,31,32,33,34", "Cotton Twill", "Khaki, Navy, Hitam, Abu-abu"),
        ("Celana Cargo Tactical", "Celana", 249000, "Celana cargo dengan banyak kantong praktis, gaya tactical", 45, "28,30,32,34,36", "Ripstop Cotton", "Hijau Army, Hitam, Khaki"),
        ("Celana Jogger Sporty", "Celana", 189000, "Celana jogger sporty dengan pinggang elastis, nyaman untuk aktivitas", 80, "S,M,L,XL,XXL", "Cotton Fleece", "Hitam, Abu-abu, Navy"),
        ("Celana Kulot Wide Leg", "Celana", 199000, "Celana kulot wide leg wanita, elegan dan nyaman", 55, "S,M,L,XL", "Scuba Premium", "Hitam, Cream, Coklat"),
        ("Celana Culottes Linen", "Celana", 219000, "Celana culottes bahan linen, adem dan berkelas", 40, "S,M,L,XL", "Linen Blend", "Putih, Beige, Sage"),
        ("Celana Pendek Cargo", "Celana", 169000, "Celana pendek cargo casual, cocok untuk musim panas", 65, "28,30,32,34", "Cotton Twill", "Khaki, Olive, Hitam"),

        # ===== JAKET (7) =====
        ("Jaket Bomber Classic", "Jaket", 349000, "Jaket bomber klasik dengan rib di lengan dan pinggang", 40, "S,M,L,XL,XXL", "Parasut Despo", "Hitam, Hijau Army, Navy"),
        ("Jaket Denim Trucker", "Jaket", 329000, "Jaket denim trucker vintage, makin bagus makin sering dipakai", 35, "S,M,L,XL", "Denim 12oz", "Medium Blue, Dark Blue, Black"),
        ("Jaket Windbreaker Sport", "Jaket", 279000, "Jaket windbreaker ringan dan tahan angin, cocok untuk outdoor", 50, "S,M,L,XL,XXL", "Taslan Waterproof", "Hitam, Navy, Merah"),
        ("Jaket Parka Winter", "Jaket", 399000, "Jaket parka dengan hoodie, tebal dan hangat untuk cuaca dingin", 30, "M,L,XL,XXL", "Cotton Canvas", "Hijau Army, Hitam, Cream"),
        ("Jaket Varsity Baseball", "Jaket", 319000, "Jaket varsity baseball dengan aksen huruf, gaya kampus Amerika", 45, "S,M,L,XL", "Fleece + PU Leather", "Hitam-Putih, Navy-Putih, Merah-Putih"),
        ("Jaket Coach Minimalis", "Jaket", 259000, "Jaket coach minimalis waterproof, simpel tapi stylish", 55, "S,M,L,XL,XXL", "Parasut", "Hitam, Navy, Olive"),
        ("Jaket Leather Biker", "Jaket", 499000, "Jaket kulit sintetis gaya biker, maskulin dan berkarakter", 20, "S,M,L,XL", "PU Leather Premium", "Hitam, Coklat Tua"),

        # ===== HOODIE (6) =====
        ("Hoodie Polos Essential", "Hoodie", 229000, "Hoodie polos essential, basic item yang wajib punya", 70, "S,M,L,XL,XXL", "Cotton Fleece 280gsm", "Hitam, Abu-abu, Cream, Maroon"),
        ("Hoodie Zip-Up Classic", "Hoodie", 249000, "Hoodie dengan resleting depan, praktis dan versatile", 55, "S,M,L,XL,XXL", "Cotton Fleece 280gsm", "Hitam, Abu-abu, Navy"),
        ("Hoodie Oversize Trendy", "Hoodie", 269000, "Hoodie oversize dengan potongan lebar, super nyaman", 45, "M,L,XL,XXL", "Cotton Fleece 320gsm", "Hitam, Cream, Sage Green, Lilac"),
        ("Hoodie Graphic Art", "Hoodie", 289000, "Hoodie dengan print grafis eksklusif di bagian depan dan belakang", 35, "S,M,L,XL", "Cotton Fleece 280gsm", "Hitam, Putih"),
        ("Hoodie Cropped Wanita", "Hoodie", 219000, "Hoodie cropped untuk wanita, potongan di pinggang untuk tampilan trendi", 40, "S,M,L", "Cotton Fleece 260gsm", "Pink, Lilac, Cream"),
        ("Hoodie Pullover Thick", "Hoodie", 299000, "Hoodie pullover super tebal, ideal untuk cuaca dingin", 30, "M,L,XL,XXL", "Cotton Fleece 350gsm", "Hitam, Navy, Maroon"),

        # ===== SWEATER (5) =====
        ("Sweater Rajut Cable", "Sweater", 269000, "Sweater rajut motif cable knit klasik, hangat dan elegan", 30, "S,M,L,XL", "Acrylic Knit", "Cream, Coklat, Abu-abu"),
        ("Sweater Crewneck Basic", "Sweater", 219000, "Sweater crewneck polos, layering essential untuk setiap outfit", 50, "S,M,L,XL,XXL", "Cotton French Terry", "Hitam, Abu-abu, Navy, Cream"),
        ("Cardigan Oversized", "Sweater", 289000, "Cardigan oversized dengan kancing depan, cozy dan fashionable", 35, "M,L,XL", "Knit Blend", "Cream, Coklat Muda, Abu Tua"),
        ("Sweater Turtleneck Slim", "Sweater", 249000, "Sweater turtleneck slim fit, tampilan sophisticated dan modern", 40, "S,M,L,XL", "Cotton Rib", "Hitam, Putih, Maroon, Olive"),
        ("Vest Sweater Preppy", "Sweater", 199000, "Vest sweater tanpa lengan gaya preppy, cocok untuk layering", 45, "S,M,L,XL", "Acrylic Knit", "Abu-abu, Navy, Cream"),

        # ===== DRESS (5) =====
        ("Dress Casual Daily", "Dress", 229000, "Dress casual harian yang nyaman, simpel & manis", 40, "S,M,L,XL", "Cotton Rayon", "Hitam, Dusty Pink, Sage"),
        ("Dress Midi Elegant", "Dress", 299000, "Dress midi elegan untuk acara semi-formal, anggun dan feminin", 30, "S,M,L,XL", "Scuba Premium", "Navy, Maroon, Hitam"),
        ("Dress Maxi Bohemian", "Dress", 329000, "Dress maxi dengan motif bohemian, flow dan dramatis", 25, "S,M,L", "Rayon Viscose", "Multi Pattern"),
        ("Shirt Dress Modern", "Dress", 259000, "Shirt dress dengan kerah dan kancing, bisa untuk kerja & hangout", 35, "S,M,L,XL", "Cotton Poplin", "Putih, Khaki, Light Blue"),
        ("Wrap Dress Feminine", "Dress", 279000, "Wrap dress dengan ikat pinggang, menonjolkan siluet tubuh", 30, "S,M,L", "Jersey Stretch", "Hitam, Merah, Emerald"),

        # ===== ROK (4) =====
        ("Rok A-Line Classic", "Rok", 189000, "Rok A-line klasik sepanjang lutut, timeless dan versatile", 45, "S,M,L,XL", "Cotton Twill", "Hitam, Navy, Khaki"),
        ("Rok Plisir Elegant", "Rok", 219000, "Rok plisir dengan lipatan halus, elegan bergerak saat berjalan", 35, "S,M,L,XL", "Chiffon Premium", "Hitam, Cream, Dusty Pink"),
        ("Rok Mini Denim", "Rok", 199000, "Rok mini denim casual, cocok dipadukan kaos atau kemeja", 40, "S,M,L", "Denim Stretch", "Light Blue, Dark Blue"),
        ("Rok Span Formal", "Rok", 209000, "Rok span formal untuk kerja, potongan pensil yang rapi", 50, "S,M,L,XL", "Scuba", "Hitam, Navy, Abu-abu"),
    ]

    for p in products:
        cursor.execute('''
            INSERT INTO produk_baju (nama, kategori, harga, deskripsi, stok, ukuran, bahan, warna)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', p)

def query_db(query, params=(), fetch=False):
    """Fungsi pembantu untuk menjalankan perintah SQL"""
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute(query, params)

    if fetch:
        result = cursor.fetchall()
    else:
        result = None
        conn.commit()

    conn.close()
    return result

# ==================== PRODUCT QUERIES ====================

def get_categories():
    """Get all unique categories"""
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT DISTINCT kategori FROM produk_baju ORDER BY kategori")
    result = [row['kategori'] for row in cur.fetchall()]
    conn.close()
    return result

def get_products_by_category(kategori, page=0, per_page=1):
    """Get products by category with pagination"""
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) as cnt FROM produk_baju WHERE kategori = ?", (kategori,))
    total = cur.fetchone()['cnt']

    cur.execute("SELECT * FROM produk_baju WHERE kategori = ? LIMIT ? OFFSET ?",
                (kategori, per_page, page * per_page))
    product = cur.fetchone()
    conn.close()
    return dict(product) if product else None, total

def get_product_by_id(produk_id):
    """Get single product by ID"""
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM produk_baju WHERE id = ?", (produk_id,))
    product = cur.fetchone()
    conn.close()
    return dict(product) if product else None

def search_products(keyword):
    """Search products by name or category"""
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""SELECT * FROM produk_baju 
                   WHERE nama LIKE ? OR kategori LIKE ? OR deskripsi LIKE ?
                   LIMIT 10""",
                (f"%{keyword}%", f"%{keyword}%", f"%{keyword}%"))
    results = [dict(row) for row in cur.fetchall()]
    conn.close()
    return results

def get_all_products():
    """Get all products"""
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM produk_baju ORDER BY kategori, nama")
    results = [dict(row) for row in cur.fetchall()]
    conn.close()
    return results

# ==================== CART QUERIES ====================

def add_to_cart(chat_id, produk_id, ukuran='M', jumlah=1):
    """Add item to cart"""
    conn = get_conn()
    cur = conn.cursor()
    # Check if already in cart with same size
    cur.execute("SELECT id, jumlah FROM keranjang WHERE chat_id = ? AND produk_id = ? AND ukuran = ?",
                (chat_id, produk_id, ukuran))
    existing = cur.fetchone()
    if existing:
        cur.execute("UPDATE keranjang SET jumlah = jumlah + ? WHERE id = ?", (jumlah, existing['id']))
    else:
        cur.execute("INSERT INTO keranjang (chat_id, produk_id, jumlah, ukuran) VALUES (?, ?, ?, ?)",
                    (chat_id, produk_id, jumlah, ukuran))
    conn.commit()
    conn.close()

def get_cart(chat_id):
    """Get user's cart items"""
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""SELECT k.id, k.produk_id, k.jumlah, k.ukuran, 
                          p.nama, p.harga, p.kategori
                   FROM keranjang k 
                   JOIN produk_baju p ON k.produk_id = p.id 
                   WHERE k.chat_id = ?""", (chat_id,))
    items = [dict(row) for row in cur.fetchall()]
    conn.close()
    return items

def update_cart_qty(cart_id, delta):
    """Update cart item quantity"""
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("UPDATE keranjang SET jumlah = MAX(1, jumlah + ?) WHERE id = ?", (delta, cart_id))
    conn.commit()
    conn.close()

def remove_from_cart(cart_id):
    """Remove item from cart"""
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM keranjang WHERE id = ?", (cart_id,))
    conn.commit()
    conn.close()

def clear_cart(chat_id):
    """Clear user's cart"""
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM keranjang WHERE chat_id = ?", (chat_id,))
    conn.commit()
    conn.close()

def get_cart_total(chat_id):
    """Get cart total"""
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""SELECT COALESCE(SUM(k.jumlah * p.harga), 0) as total
                   FROM keranjang k 
                   JOIN produk_baju p ON k.produk_id = p.id 
                   WHERE k.chat_id = ?""", (chat_id,))
    total = cur.fetchone()['total']
    conn.close()
    return total

# ==================== ORDER QUERIES ====================

def create_order(chat_id, nama, alamat, telepon, metode_bayar, total, catatan=''):
    """Create new order from cart"""
    import random, string
    nomor = 'FH' + datetime.now().strftime('%y%m%d') + ''.join(random.choices(string.digits, k=4))

    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""INSERT INTO pesanan (nomor_pesanan, chat_id, nama_pemesan, alamat, telepon, 
                   metode_bayar, total, catatan) VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (nomor, chat_id, nama, alamat, telepon, metode_bayar, total, catatan))
    pesanan_id = cur.lastrowid

    # Move cart items to order items
    cart_items = get_cart(chat_id)
    for item in cart_items:
        cur.execute("""INSERT INTO item_pesanan (pesanan_id, produk_id, nama_produk, jumlah, ukuran, harga)
                       VALUES (?, ?, ?, ?, ?, ?)""",
                    (pesanan_id, item['produk_id'], item['nama'], item['jumlah'], item['ukuran'], item['harga']))

    conn.commit()
    conn.close()

    # Clear cart
    clear_cart(chat_id)
    return nomor

def get_order_by_number(nomor):
    """Get order by order number"""
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM pesanan WHERE nomor_pesanan = ?", (nomor,))
    order = cur.fetchone()
    if order:
        order = dict(order)
        cur.execute("SELECT * FROM item_pesanan WHERE pesanan_id = ?", (order['id'],))
        order['items'] = [dict(row) for row in cur.fetchall()]
    conn.close()
    return order

def get_orders_by_chat(chat_id):
    """Get all orders for a user"""
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM pesanan WHERE chat_id = ? ORDER BY created_at DESC", (chat_id,))
    orders = [dict(row) for row in cur.fetchall()]
    conn.close()
    return orders

def get_all_orders(status_filter=None):
    """Get all orders (admin)"""
    conn = get_conn()
    cur = conn.cursor()
    if status_filter:
        cur.execute("SELECT * FROM pesanan WHERE status = ? ORDER BY created_at DESC", (status_filter,))
    else:
        cur.execute("SELECT * FROM pesanan ORDER BY created_at DESC")
    orders = [dict(row) for row in cur.fetchall()]
    conn.close()
    return orders

def update_order_status(nomor_pesanan, new_status):
    """Update order status"""
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("UPDATE pesanan SET status = ?, updated_at = datetime('now','localtime') WHERE nomor_pesanan = ?",
                (new_status, nomor_pesanan))
    conn.commit()
    conn.close()

def get_order_stats():
    """Get order statistics"""
    conn = get_conn()
    cur = conn.cursor()

    stats = {}
    cur.execute("SELECT COUNT(*) as cnt FROM pesanan")
    stats['total_pesanan'] = cur.fetchone()['cnt']

    cur.execute("SELECT COALESCE(SUM(total), 0) as rev FROM pesanan WHERE status != 'Dibatalkan'")
    stats['total_pendapatan'] = cur.fetchone()['rev']

    cur.execute("SELECT COUNT(*) as cnt FROM pesanan WHERE status = 'Menunggu Konfirmasi'")
    stats['menunggu'] = cur.fetchone()['cnt']

    cur.execute("SELECT COUNT(*) as cnt FROM pesanan WHERE status = 'Diproses'")
    stats['diproses'] = cur.fetchone()['cnt']

    cur.execute("SELECT COUNT(*) as cnt FROM pesanan WHERE status = 'Dikirim'")
    stats['dikirim'] = cur.fetchone()['cnt']

    cur.execute("SELECT COUNT(*) as cnt FROM pesanan WHERE status = 'Selesai'")
    stats['selesai'] = cur.fetchone()['cnt']

    cur.execute("SELECT COUNT(*) as cnt FROM pesanan WHERE status = 'Dibatalkan'")
    stats['dibatalkan'] = cur.fetchone()['cnt']

    conn.close()
    return stats

# ==================== ADMIN QUERIES ====================

def is_admin(chat_id):
    """Check if user is admin"""
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT is_admin FROM admin_users WHERE chat_id = ?", (chat_id,))
    result = cur.fetchone()
    conn.close()
    return bool(result and result['is_admin'])

def set_admin(chat_id):
    """Set user as admin"""
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("INSERT OR REPLACE INTO admin_users (chat_id, is_admin) VALUES (?, 1)", (chat_id,))
    conn.commit()
    conn.close()

# ==================== PRODUCT MANAGEMENT ====================

def update_product(produk_id, **kwargs):
    """Update product fields"""
    conn = get_conn()
    cur = conn.cursor()
    fields = []
    values = []
    for key, val in kwargs.items():
        if key in ('nama', 'kategori', 'harga', 'deskripsi', 'stok', 'ukuran', 'bahan', 'warna'):
            fields.append(f"{key} = ?")
            values.append(val)
    if fields:
        values.append(produk_id)
        cur.execute(f"UPDATE produk_baju SET {', '.join(fields)} WHERE id = ?", values)
        conn.commit()
    conn.close()

def delete_product(produk_id):
    """Delete a product"""
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM produk_baju WHERE id = ?", (produk_id,))
    conn.commit()
    conn.close()

def add_product(nama, kategori, harga, deskripsi, stok=50, ukuran='S,M,L,XL,XXL', bahan='', warna=''):
    """Add new product"""
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""INSERT INTO produk_baju (nama, kategori, harga, deskripsi, stok, ukuran, bahan, warna)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                (nama, kategori, harga, deskripsi, stok, ukuran, bahan, warna))
    conn.commit()
    conn.close()