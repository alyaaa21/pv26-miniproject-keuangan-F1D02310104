from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLabel, QLineEdit, QComboBox, QDateEdit, QTextEdit,
    QPushButton, QMessageBox
)
from PySide6.QtCore import Qt, QDate
from controllers import transaction_controller as ctrl

class TransactionDialog(QDialog):
    #dialog untuk tambah transaksi baru atau edit transaksi yang sudah ada
    #transaction_id = None berarti mode tambah, ada nilai berarti mode edit

    def __init__(self, parent=None, transaction_id=None):
        super().__init__(parent)
        self.transaction_id = transaction_id
        self.setWindowTitle("Tambah Transaksi" if transaction_id is None else "Edit Transaksi")
        self.setMinimumWidth(450)
        self.setModal(True)
        self._build_ui()
        #kalau mode edit, isi form dengan data yang sudah ada
        if self.transaction_id is not None:
            self._load_existing_data()

    def _build_ui(self):
        #bangun tampilan form dialog
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(16)
        main_layout.setContentsMargins(24, 24, 24, 24)

        #judul di bagian atas dialog
        title_label = QLabel(
            "✏️ Edit Transaksi" if self.transaction_id else "➕ Tambah Transaksi Baru"
        )
        title_label.setObjectName("dialogTitle")
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)

        #form layout agar label dan field input rapi berdampingan
        form_layout = QFormLayout()
        form_layout.setSpacing(12)
        form_layout.setLabelAlignment(Qt.AlignRight)

        #field 1 - tanggal transaksi dengan calendar popup
        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDate(QDate.currentDate())
        self.date_edit.setDisplayFormat("dd/MM/yyyy")
        self.date_edit.setObjectName("formField")
        form_layout.addRow("📅 Tanggal:", self.date_edit)

        #field 2 - jenis transaksi pemasukan atau pengeluaran
        self.jenis_combo = QComboBox()
        self.jenis_combo.addItems(["Pemasukan", "Pengeluaran"])
        self.jenis_combo.setObjectName("formField")
        #signal: saat jenis berubah, otomatis update pilihan kategori
        self.jenis_combo.currentTextChanged.connect(self._on_jenis_changed)
        form_layout.addRow("💱 Jenis:", self.jenis_combo)

        #field 3 - kategori transaksi, bisa pilih atau ketik sendiri
        self.kategori_combo = QComboBox()
        self.kategori_combo.setEditable(True)
        self.kategori_combo.setObjectName("formField")
        self._populate_kategori("Pemasukan")
        form_layout.addRow("🏷️ Kategori:", self.kategori_combo)

        #field 4 - jumlah uang dalam rupiah
        self.jumlah_input = QLineEdit()
        self.jumlah_input.setPlaceholderText("Contoh: 150000")
        self.jumlah_input.setObjectName("formField")
        form_layout.addRow("💰 Jumlah (Rp):", self.jumlah_input)

        #field 5 - metode pembayaran
        self.metode_combo = QComboBox()
        self.metode_combo.addItems([
            "Transfer Bank", "Tunai", "QRIS", "Kartu Debit",
            "Kartu Kredit", "Dompet Digital", "Lainnya"
        ])
        self.metode_combo.setObjectName("formField")
        form_layout.addRow("💳 Metode:", self.metode_combo)

        #field 6 - deskripsi atau catatan tambahan, boleh kosong
        self.deskripsi_input = QTextEdit()
        self.deskripsi_input.setPlaceholderText("Keterangan tambahan (opsional)...")
        self.deskripsi_input.setMaximumHeight(80)
        self.deskripsi_input.setObjectName("formField")
        form_layout.addRow("📝 Deskripsi:", self.deskripsi_input)

        main_layout.addLayout(form_layout)

        #tombol batal dan simpan di bagian bawah
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(12)

        self.btn_cancel = QPushButton("Batal")
        self.btn_cancel.setObjectName("btnSecondary")
        #signal: klik batal -> tutup dialog tanpa simpan
        self.btn_cancel.clicked.connect(self.reject)

        self.btn_save = QPushButton("Simpan")
        self.btn_save.setObjectName("btnPrimary")
        #signal: klik simpan -> jalankan validasi dan simpan data
        self.btn_save.clicked.connect(self._on_save_clicked)

        btn_layout.addWidget(self.btn_cancel)
        btn_layout.addWidget(self.btn_save)
        main_layout.addLayout(btn_layout)

    def _on_jenis_changed(self, jenis):
        #slot: update isi dropdown kategori sesuai jenis yang dipilih
        self.kategori_combo.clear()
        self._populate_kategori(jenis)

    def _populate_kategori(self, jenis):
        #isi pilihan kategori berdasarkan jenis transaksi
        if jenis == "Pemasukan":
            kategori_list = ["Gaji", "Freelance", "Investasi", "Hadiah", "Penjualan", "Lainnya"]
        else:
            kategori_list = [
                "Makanan & Minuman", "Transportasi", "Belanja",
                "Kesehatan", "Pendidikan", "Hiburan",
                "Tagihan & Utilitas", "Tabungan", "Lainnya"
            ]
        self.kategori_combo.addItems(kategori_list)

    def _load_existing_data(self):
        #isi semua field dengan data transaksi yang ada, dipakai saat mode edit
        data = ctrl.ambil_transaksi_by_id(self.transaction_id)
        if not data:
            return
        #parse tanggal dari format yyyy-mm-dd lalu set ke widget tanggal
        tanggal_parts = data["tanggal"].split("-")
        if len(tanggal_parts) == 3:
            qdate = QDate(int(tanggal_parts[0]), int(tanggal_parts[1]), int(tanggal_parts[2]))
            self.date_edit.setDate(qdate)
        #set jenis, ini akan otomatis trigger _on_jenis_changed
        idx_jenis = self.jenis_combo.findText(data["jenis"])
        if idx_jenis >= 0:
            self.jenis_combo.setCurrentIndex(idx_jenis)
        #set kategori, kalau tidak ada di list maka ketikkan langsung
        idx_kat = self.kategori_combo.findText(data["kategori"])
        if idx_kat >= 0:
            self.kategori_combo.setCurrentIndex(idx_kat)
        else:
            self.kategori_combo.setEditText(data["kategori"])
        self.jumlah_input.setText(str(data["jumlah"]))
        idx_metode = self.metode_combo.findText(data["metode"])
        if idx_metode >= 0:
            self.metode_combo.setCurrentIndex(idx_metode)
        self.deskripsi_input.setPlainText(data["deskripsi"] or "")

    def _on_save_clicked(self):
        #slot: ambil semua nilai dari form, validasi, lalu simpan ke database
        tanggal    = self.date_edit.date().toString("yyyy-MM-dd")
        jenis      = self.jenis_combo.currentText()
        kategori   = self.kategori_combo.currentText().strip()
        jumlah_str = self.jumlah_input.text().strip()
        metode     = self.metode_combo.currentText()
        deskripsi  = self.deskripsi_input.toPlainText().strip()

        if self.transaction_id is None:
            #mode tambah: kirim ke controller untuk disimpan
            ok, result = ctrl.tambah_transaksi(tanggal, kategori, jenis, jumlah_str, deskripsi, metode)
        else:
            #mode edit: kirim ke controller untuk diupdate
            ok, result = ctrl.edit_transaksi(
                self.transaction_id, tanggal, kategori, jenis, jumlah_str, deskripsi, metode
            )

        if not ok:
            #tampilkan pesan error kalau validasi gagal
            QMessageBox.warning(self, "Input Tidak Valid", result)
            return
        #tutup dialog dengan status berhasil
        self.accept()