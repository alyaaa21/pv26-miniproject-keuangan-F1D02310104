# catatUang — personal finance tracker

aplikasi pencatat keuangan pribadi berbasis GUI menggunakan PySide6 dan SQLite.

## identitas

Nama: Alya Dwi Pangesti
NIM: F1D02310104
Kelas: Pemrograman Visual D

---

## deskripsi

CatatUang adalah aplikasi desktop untuk mencatat pemasukan dan pengeluaran pribadi. Pengguna dapat menambahkan transaksi dengan detail lengkap, melihat ringkasan keuangan secara real-time, serta mencari dan mengelola riwayat transaksi.

## cara menjalankan

### prasyarat

```bash
pip install PySide6
```

### jalankan aplikasi

```bash
python main.py
```

database `keuangan.db` akan dibuat secara otomatis saat pertama kali dijalankan.

---

## struktur project (separation of concerns)

```
pv26-miniproject-keuangan-F1D02310104/
├── main.py                             #entry point, load stylesheet dan jalankan app
├── database.py                         #semua fungsi akses database sqlite (CRUD)
├── keuangan.db                         #file database (dibuat otomatis)
├── controllers/
│   ├── __init__.py
│   └── transaction_controller.py      #logika bisnis dan validasi input
├── views/
│   ├── __init__.py
│   ├── main_window.py                 #jendela utama, tampilkan data dan tombol aksi
│   └── transaction_dialog.py          #dialog form tambah dan edit transaksi
├── styles/
│   └── style.qss                      #styling antarmuka dari file eksternal
└── README.md
```

## teknologi

- **Python 3.10+**
- **PySide6** — framework GUI
- **SQLite3** — database lokal persisten
- **QSS** — styling antarmuka dari file eksternal

## fitur

- tambah transaksi baru (form di dialog terpisah)
- edit transaksi yang sudah ada
- hapus transaksi dengan dialog konfirmasi
- pencarian real-time berdasarkan kategori, jenis, atau deskripsi
- ringkasan otomatis: total pemasukan, pengeluaran, dan saldo
- input tanggal dengan calendar popup
- tema pink dengan QSS dari file eksternal
- data tersimpan permanen di SQLite
