import sqlite3
import os

#path file database sqlite
DB_PATH = os.path.join(os.path.dirname(__file__), "keuangan.db")

def get_connection():
    #buat koneksi ke database dan kembalikan objeknya
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    #buat tabel jika belum ada, dipanggil saat aplikasi pertama kali jalan
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS transactions (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            tanggal     TEXT    NOT NULL,
            kategori    TEXT    NOT NULL,
            jenis       TEXT    NOT NULL,
            jumlah      REAL    NOT NULL,
            deskripsi   TEXT,
            metode      TEXT    NOT NULL,
            created_at  TEXT    DEFAULT (datetime('now','localtime'))
        )
    """)
    conn.commit()
    conn.close()

def insert_transaction(tanggal, kategori, jenis, jumlah, deskripsi, metode):
    #tambah data transaksi baru ke tabel
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO transactions (tanggal, kategori, jenis, jumlah, deskripsi, metode)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (tanggal, kategori, jenis, jumlah, deskripsi, metode))
    conn.commit()
    last_id = cursor.lastrowid
    conn.close()
    return last_id

def get_all_transactions():
    #ambil semua data transaksi, diurutkan dari yang terbaru
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, tanggal, kategori, jenis, jumlah, deskripsi, metode
        FROM transactions
        ORDER BY tanggal DESC, id DESC
    """)
    rows = cursor.fetchall()
    conn.close()
    return rows

def get_transaction_by_id(transaction_id):
    #ambil satu data transaksi berdasarkan id
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM transactions WHERE id = ?", (transaction_id,))
    row = cursor.fetchone()
    conn.close()
    return row

def get_summary():
    #hitung total pemasukan, pengeluaran, dan saldo dari semua transaksi
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT
            SUM(CASE WHEN jenis = 'Pemasukan'   THEN jumlah ELSE 0 END) AS total_masuk,
            SUM(CASE WHEN jenis = 'Pengeluaran' THEN jumlah ELSE 0 END) AS total_keluar
        FROM transactions
    """)
    row = cursor.fetchone()
    conn.close()
    total_masuk  = row["total_masuk"]  or 0.0
    total_keluar = row["total_keluar"] or 0.0
    saldo        = total_masuk - total_keluar
    return total_masuk, total_keluar, saldo

def search_transactions(keyword):
    #cari transaksi berdasarkan kata kunci di kolom deskripsi, kategori, atau jenis
    conn = get_connection()
    cursor = conn.cursor()
    like = f"%{keyword}%"
    cursor.execute("""
        SELECT id, tanggal, kategori, jenis, jumlah, deskripsi, metode
        FROM transactions
        WHERE deskripsi LIKE ? OR kategori LIKE ? OR jenis LIKE ?
        ORDER BY tanggal DESC, id DESC
    """, (like, like, like))
    rows = cursor.fetchall()
    conn.close()
    return rows

def update_transaction(transaction_id, tanggal, kategori, jenis, jumlah, deskripsi, metode):
    #ubah data transaksi yang sudah ada berdasarkan id
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE transactions
        SET tanggal = ?, kategori = ?, jenis = ?, jumlah = ?, deskripsi = ?, metode = ?
        WHERE id = ?
    """, (tanggal, kategori, jenis, jumlah, deskripsi, metode, transaction_id))
    conn.commit()
    conn.close()

def delete_transaction(transaction_id):
    #hapus data transaksi berdasarkan id
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM transactions WHERE id = ?", (transaction_id,))
    conn.commit()
    conn.close()