import database

def tambah_transaksi(tanggal, kategori, jenis, jumlah_str, deskripsi, metode):
    #validasi input lalu simpan transaksi baru ke database
    #cek apakah semua field wajib sudah diisi
    if not tanggal or not kategori or not jenis or not metode:
        return False, "Semua field wajib diisi!"
    #cek apakah jumlah berupa angka dan lebih dari nol
    try:
        jumlah = float(jumlah_str.replace(",", "."))
        if jumlah <= 0:
            return False, "Jumlah harus lebih dari 0!"
    except ValueError:
        return False, "Jumlah harus berupa angka!"
    last_id = database.insert_transaction(tanggal, kategori, jenis, jumlah, deskripsi, metode)
    return True, last_id

def edit_transaksi(transaction_id, tanggal, kategori, jenis, jumlah_str, deskripsi, metode):
    #validasi input lalu update transaksi yang sudah ada
    #cek apakah semua field wajib sudah diisi
    if not tanggal or not kategori or not jenis or not metode:
        return False, "Semua field wajib diisi!"
    #cek apakah jumlah berupa angka dan lebih dari nol
    try:
        jumlah = float(jumlah_str.replace(",", "."))
        if jumlah <= 0:
            return False, "Jumlah harus lebih dari 0!"
    except ValueError:
        return False, "Jumlah harus berupa angka!"
    database.update_transaction(transaction_id, tanggal, kategori, jenis, jumlah, deskripsi, metode)
    return True, None

def hapus_transaksi(transaction_id):
    #hapus transaksi berdasarkan id
    database.delete_transaction(transaction_id)

def ambil_semua_transaksi():
    #ambil semua transaksi dari database
    return database.get_all_transactions()

def ambil_transaksi_by_id(transaction_id):
    #ambil satu transaksi berdasarkan id
    return database.get_transaction_by_id(transaction_id)

def cari_transaksi(keyword):
    #cari transaksi berdasarkan kata kunci
    return database.search_transactions(keyword)

def ambil_ringkasan():
    #ambil ringkasan total masuk, keluar, dan saldo
    return database.get_summary()

def format_rupiah(angka):
    #ubah angka jadi format rupiah, contoh: 150000 -> Rp 150.000
    return f"Rp {angka:,.0f}".replace(",", ".")