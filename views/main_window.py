from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QTableWidget, QTableWidgetItem,
    QLineEdit, QHeaderView, QMessageBox, QFrame, QSizePolicy
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QAction, QColor

import database
from controllers import transaction_controller as ctrl
from views.transaction_dialog import TransactionDialog

#identitas mahasiswa, tampil di header dan tidak bisa diedit pengguna
NAMA_MAHASISWA = "Alya Dwi Pangesti"
NIM_MAHASISWA  = "F1D02310104"

class MainWindow(QMainWindow):
    #jendela utama aplikasi, bertugas menampilkan data dan tombol aksi
    #logika bisnis ada di controller, akses database ada di database.py

    def __init__(self):
        super().__init__()
        self.setWindowTitle("CatatUang - Personal Finance Tracker")
        self.setMinimumSize(QSize(900, 620))
        #inisialisasi database saat pertama kali dijalankan
        database.init_db()
        self._build_menu_bar()
        self._build_ui()
        self._load_data()

    def _build_menu_bar(self):
        #buat menu bar dengan menu file dan tentang aplikasi
        menu_bar = self.menuBar()

        #menu file: refresh data dan keluar aplikasi
        file_menu = menu_bar.addMenu("&File")
        action_refresh = QAction("🔄 Refresh Data", self)
        action_refresh.setShortcut("F5")
        #signal: klik refresh -> load ulang semua data dari database
        action_refresh.triggered.connect(self._load_data)
        file_menu.addAction(action_refresh)
        file_menu.addSeparator()
        action_exit = QAction("❌ Keluar", self)
        action_exit.setShortcut("Ctrl+Q")
        action_exit.triggered.connect(self.close)
        file_menu.addAction(action_exit)

        #menu tentang: info aplikasi dan identitas mahasiswa
        about_menu = menu_bar.addMenu("&Tentang")
        action_about = QAction("ℹ️ Tentang Aplikasi", self)
        #signal: klik tentang -> tampilkan dialog info aplikasi
        action_about.triggered.connect(self._show_about)
        about_menu.addAction(action_about)

    def _build_ui(self):
        #bangun semua bagian tampilan jendela utama
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        root_layout = QVBoxLayout(central_widget)
        root_layout.setSpacing(0)
        root_layout.setContentsMargins(0, 0, 0, 0)

        #--- bagian header atas ---
        header = QWidget()
        header.setObjectName("appHeader")
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(24, 16, 24, 16)

        logo_title = QLabel("💸 CatatUang")
        logo_title.setObjectName("appTitle")
        subtitle = QLabel("Personal Finance Tracker")
        subtitle.setObjectName("appSubtitle")
        title_col = QVBoxLayout()
        title_col.setSpacing(2)
        title_col.addWidget(logo_title)
        title_col.addWidget(subtitle)

        #kotak identitas mahasiswa di pojok kanan, tidak bisa diedit
        identity_widget = QWidget()
        identity_widget.setObjectName("identityBox")
        identity_layout = QVBoxLayout(identity_widget)
        identity_layout.setContentsMargins(12, 8, 12, 8)
        identity_layout.setSpacing(2)
        nama_label = QLabel(f"👤 {NAMA_MAHASISWA}")
        nama_label.setObjectName("identityText")
        nim_label  = QLabel(f"🎓 {NIM_MAHASISWA}")
        nim_label.setObjectName("identityText")
        identity_layout.addWidget(nama_label)
        identity_layout.addWidget(nim_label)

        header_layout.addLayout(title_col)
        header_layout.addStretch()
        header_layout.addWidget(identity_widget)
        root_layout.addWidget(header)

        #--- bagian kartu ringkasan keuangan ---
        summary_bar = QWidget()
        summary_bar.setObjectName("summaryBar")
        summary_layout = QHBoxLayout(summary_bar)
        summary_layout.setContentsMargins(24, 16, 24, 16)
        summary_layout.setSpacing(16)
        self.card_masuk  = self._make_summary_card("💚 Total Pemasukan",  "Rp 0", "cardGreen")
        self.card_keluar = self._make_summary_card("❤️ Total Pengeluaran", "Rp 0", "cardRed")
        self.card_saldo  = self._make_summary_card("💗 Saldo",             "Rp 0", "cardPink")
        summary_layout.addWidget(self.card_masuk)
        summary_layout.addWidget(self.card_keluar)
        summary_layout.addWidget(self.card_saldo)
        root_layout.addWidget(summary_bar)

        #--- bagian konten utama: toolbar + tabel ---
        content = QWidget()
        content.setObjectName("contentArea")
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(24, 16, 24, 16)
        content_layout.setSpacing(12)

        #toolbar berisi kolom pencarian dan tombol-tombol aksi
        toolbar = QHBoxLayout()
        toolbar.setSpacing(10)
        search_label = QLabel("🔍")
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Cari transaksi (kategori, deskripsi, jenis)...")
        self.search_input.setObjectName("searchInput")
        #signal: setiap ketikan -> langsung filter data di tabel
        self.search_input.textChanged.connect(self._on_search)

        self.btn_tambah = QPushButton("＋ Tambah Transaksi")
        self.btn_tambah.setObjectName("btnPrimary")
        #signal: klik tambah -> buka dialog tambah transaksi baru
        self.btn_tambah.clicked.connect(self._on_tambah_clicked)

        self.btn_edit = QPushButton("✏️ Edit")
        self.btn_edit.setObjectName("btnSecondary")
        self.btn_edit.setEnabled(False)
        #signal: klik edit -> buka dialog edit transaksi yang dipilih
        self.btn_edit.clicked.connect(self._on_edit_clicked)

        self.btn_hapus = QPushButton("🗑 Hapus")
        self.btn_hapus.setObjectName("btnDanger")
        self.btn_hapus.setEnabled(False)
        #signal: klik hapus -> tampilkan konfirmasi lalu hapus data
        self.btn_hapus.clicked.connect(self._on_hapus_clicked)

        toolbar.addWidget(search_label)
        toolbar.addWidget(self.search_input, 1)
        toolbar.addWidget(self.btn_tambah)
        toolbar.addWidget(self.btn_edit)
        toolbar.addWidget(self.btn_hapus)
        content_layout.addLayout(toolbar)

        #tabel untuk menampilkan semua data transaksi
        self.table = QTableWidget()
        self.table.setObjectName("dataTable")
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "ID", "Tanggal", "Jenis", "Kategori", "Jumlah", "Metode", "Deskripsi"
        ])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeToContents)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        #tabel tidak bisa langsung diedit, harus lewat tombol edit
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        self.table.setSortingEnabled(True)
        #signal: saat baris dipilih -> aktifkan tombol edit dan hapus
        self.table.selectionModel().selectionChanged.connect(self._on_selection_changed)
        content_layout.addWidget(self.table)

        #label status di bawah tabel untuk info jumlah data
        self.status_label = QLabel("Memuat data...")
        self.status_label.setObjectName("statusLabel")
        content_layout.addWidget(self.status_label)

        root_layout.addWidget(content, 1)

    def _make_summary_card(self, title, value, obj_name):
        #buat satu kartu ringkasan dengan judul dan nilai
        card = QFrame()
        card.setObjectName(obj_name)
        card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        layout = QVBoxLayout(card)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(4)
        lbl_title = QLabel(title)
        lbl_title.setObjectName("cardTitle")
        lbl_value = QLabel(value)
        lbl_value.setObjectName("cardValue")
        layout.addWidget(lbl_title)
        layout.addWidget(lbl_value)
        #simpan referensi ke label nilai supaya bisa diupdate nanti
        card.value_label = lbl_value
        return card

    def _load_data(self, rows=None):
        #muat data ke tabel, kalau rows tidak dikirim maka ambil semua dari database
        if rows is None:
            rows = ctrl.ambil_semua_transaksi()
        #nonaktifkan sorting sementara saat mengisi data supaya tidak error
        self.table.setSortingEnabled(False)
        self.table.setRowCount(0)

        for row_data in rows:
            row_idx = self.table.rowCount()
            self.table.insertRow(row_idx)
            #kolom 0: id transaksi
            id_item = QTableWidgetItem(str(row_data["id"]))
            id_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row_idx, 0, id_item)
            #kolom 1: tanggal
            self.table.setItem(row_idx, 1, QTableWidgetItem(row_data["tanggal"]))
            #kolom 2: jenis transaksi, hijau untuk pemasukan dan merah untuk pengeluaran
            jenis_item = QTableWidgetItem(row_data["jenis"])
            jenis_item.setTextAlignment(Qt.AlignCenter)
            if row_data["jenis"] == "Pemasukan":
                jenis_item.setForeground(QColor("#2d8a4e"))
            else:
                jenis_item.setForeground(QColor("#c0392b"))
            self.table.setItem(row_idx, 2, jenis_item)
            #kolom 3: kategori
            self.table.setItem(row_idx, 3, QTableWidgetItem(row_data["kategori"]))
            #kolom 4: jumlah dalam format rupiah
            jumlah_item = QTableWidgetItem(ctrl.format_rupiah(row_data["jumlah"]))
            jumlah_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.table.setItem(row_idx, 4, jumlah_item)
            #kolom 5: metode pembayaran
            self.table.setItem(row_idx, 5, QTableWidgetItem(row_data["metode"]))
            #kolom 6: deskripsi, tampilkan strip kalau kosong
            self.table.setItem(row_idx, 6, QTableWidgetItem(row_data["deskripsi"] or "-"))

        self.table.setSortingEnabled(True)
        self._update_summary()
        total = self.table.rowCount()
        self.status_label.setText(f"Total: {total} transaksi ditampilkan")

    def _update_summary(self):
        #perbarui angka di kartu ringkasan berdasarkan data terbaru dari database
        masuk, keluar, saldo = ctrl.ambil_ringkasan()
        self.card_masuk.value_label.setText(ctrl.format_rupiah(masuk))
        self.card_keluar.value_label.setText(ctrl.format_rupiah(keluar))
        self.card_saldo.value_label.setText(ctrl.format_rupiah(saldo))
        #warna saldo hijau kalau positif, merah kalau minus
        color = "#2d8a4e" if saldo >= 0 else "#c0392b"
        self.card_saldo.value_label.setStyleSheet(f"color: {color};")

    def _get_selected_id(self):
        #ambil id transaksi yang sedang dipilih di tabel
        selected = self.table.selectedItems()
        if not selected:
            return None
        row = self.table.currentRow()
        return int(self.table.item(row, 0).text())

    def _on_tambah_clicked(self):
        #slot: buka dialog tambah transaksi baru
        dialog = TransactionDialog(parent=self)
        if dialog.exec():
            #kalau user klik simpan, refresh tabel
            self._load_data()

    def _on_edit_clicked(self):
        #slot: buka dialog edit untuk transaksi yang dipilih
        selected_id = self._get_selected_id()
        if selected_id is None:
            QMessageBox.information(self, "Pilih Data", "Pilih transaksi yang ingin diedit terlebih dahulu.")
            return
        dialog = TransactionDialog(parent=self, transaction_id=selected_id)
        if dialog.exec():
            self._load_data()

    def _on_hapus_clicked(self):
        #slot: tampilkan konfirmasi dulu sebelum hapus transaksi
        selected_id = self._get_selected_id()
        if selected_id is None:
            QMessageBox.information(self, "Pilih Data", "Pilih transaksi yang ingin dihapus terlebih dahulu.")
            return
        #dialog konfirmasi, default pilihan adalah tidak supaya tidak tidak sengaja terhapus
        reply = QMessageBox.question(
            self,
            "Konfirmasi Hapus",
            f"Yakin ingin menghapus transaksi ID #{selected_id}?\nData yang dihapus tidak dapat dikembalikan.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            ctrl.hapus_transaksi(selected_id)
            self._load_data()
            self.status_label.setText(f"✅ Transaksi #{selected_id} berhasil dihapus.")

    def _on_search(self, keyword):
        #slot: filter tabel setiap ada perubahan teks di kolom pencarian
        if keyword.strip():
            rows = ctrl.cari_transaksi(keyword.strip())
        else:
            rows = ctrl.ambil_semua_transaksi()
        self._load_data(rows)

    def _on_selection_changed(self):
        #slot: aktifkan tombol edit dan hapus kalau ada baris yang dipilih
        has_selection = bool(self.table.selectedItems())
        self.btn_edit.setEnabled(has_selection)
        self.btn_hapus.setEnabled(has_selection)

    def _show_about(self):
        #slot: tampilkan dialog tentang aplikasi
        QMessageBox.about(
            self,
            "Tentang CatatUang",
            f"""<div style='font-family: sans-serif;'>
            <h2 style='color:#c2185b;'>💸 CatatUang</h2>
            <p><b>Versi:</b> 1.0.0</p>
            <p><b>Deskripsi:</b><br>
            Aplikasi pencatat keuangan pribadi berbasis GUI dengan PySide6.<br>
            Memungkinkan pengguna mencatat pemasukan dan pengeluaran dengan mudah,<br>
            lengkap dengan ringkasan saldo dan riwayat transaksi.</p>
            <hr>
            <p><b>Developer:</b><br>
            👤 {NAMA_MAHASISWA}<br>
            🎓 {NIM_MAHASISWA}</p>
            <p><b>Teknologi:</b> PySide6, SQLite, Python 3</p>
            <p><b>Mata Kuliah:</b> Pemrograman Visual</p>
            </div>"""
        )