# -*- coding: UTF-8 -*-
import wx
import datetime
from .logger import jk_log
import ui
import gui
import os
import api

class HelpDialog(wx.Dialog):
	def __init__(self, parent):
		super().__init__(parent, title="Panduan & Bantuan JadwalKu", size=(580, 460), style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)
		sizer = wx.BoxSizer(wx.VERTICAL)
		
		info_label = wx.StaticText(self, label="Gunakan Panah Atas/Bawah untuk membaca per baris, atau Panah Kiri/Kanan untuk mengeja teks:")
		sizer.Add(info_label, 0, wx.ALL, 8)
		
		help_text = (
			"=== PANDUAN PENGGUNAAN ADD-ON JADWALKU (Versi 1.7.6.3) ===\n\n"
			"1. DAFTAR SHORTCUT GLOBAL UTAMA:\n"
			"- NVDA + / : Masuk ke Mode Lapisan Perintah (Command Layer) JadwalKu.\n"
			"- NVDA + Shift + / : Membacakan Status Dinamis dari seluruh pewaktu yang sedang aktif.\n"
			"- NVDA + F12 (1, 2, 3, kali) : Membacakan Jam dan Tanggal serta perhitungan mundur ke akhir tahun saat ini.\n\n"
			"2. DAFTAR PERINTAH DALAM MODE JADWALKU (Setelah menekan NVDA + /):\n"
			"- O atau Enter atau P : Buka Dialog Utama Manajemen Jadwal.\n"
			"- J : Buka Pelacak Kebiasaan (Habit Tracker) untuk menandai jadwal.\n"
			"- L : Buka Papan Skor & Lencana Ketekunan (Badge Showcase).\n"
			"- 1 : Buka Manajer Timer Rutin (Buat, Jeda, Lanjutkan, atau Hentikan Timer).\n"
			"- 2 : Buka Manajer Alarm Sekali Pakai (Buat, Jeda, Lanjutkan, atau Hentikan Alarm).\n"
			"- 3 : Buka Pengaturan Pomodoro Timer (Fokus, Istirahat Pendek, Istirahat Panjang).\n"
			"- W : Bacakan jam saat ini dan status pengingat waktu berkala (Time Reminder).\n"
			"- K : Buka Kalender Bulanan & Daftar Hari Libur Nasional (Tanggal Merah).\n"
			"- D : Buka Jam Dunia & Kalkulator Konversi Zona Waktu.\n"
			"- H : Bacakan seluruh daftar agenda aktif hari ini.\n"
			"- I : Buka file log internal JadwalKu di Notepad.\n"
			"- A : Check / Uncheck (Nyalakan/Matikan) Pengingat Waktu Berkala secara cepat.\n"
			"- S : Buka Pengaturan Audio Manager (Memilih Speaker & Volume Independen, serta Lonceng Klasik).\n"
			"- T : Buka Pengaturan Mesin TTS Mandiri SAPI 5 untuk notifikasi latar belakang.\n"
			"- R : Buka Dialog Kirim Laporan, Kritik, Saran & Bug Fix (Terhubung ke Telegram Bot).\n"
			"- G : Bagikan Add-on (Salin tautan unduhan langsung / direct download ke clipboard).\n"
			"- U : Periksa pembaruan terbaru add-on secara langsung dari server.\n"
			"- V : Buka dialog catatan riwayat pembaruan (Changelog Read-Only).\n"
			"- Z : Tunda (Snooze) alarm yang sedang berbunyi selama 10 menit ke depan.\n"
			"- M : Aktifkan pemantauan Microphone (Untuk perintah suara).\n"
			"- Spasi : Hentikan suara notifikasi/chime atau matikan alarm weker yang sedang berdering.\n"
			"- B atau F1 : Buka dialog panduan bantuan ini (Mode Read-Only bisa dinavigasi panah).\n"
			"- Escape : Keluar/Batal dari mode perintah JadwalKu.\n\n"
			"3. TIPS FITUR TAMBAHAN:\n"
			"- JadwalKu kini memiliki Pelacak Kebiasaan (J) yang memberikan Lencana Ketekunan (L) untuk setiap konsistensi Anda.\n"
			"- Anda bisa menyalakan Lonceng Jam Klasik (Grandfather Clock) melalui pengaturan Audio Manager (S).\n"
			"- Saat menambah atau mengedit agenda, Anda dapat memilih 'Alarm Jam Weker', suara akan berdering terus-menerus tanpa henti sampai Anda mematikannya (Spasi) atau menundanya (Z).\n"
			"- Gunakan tombol 'Tes Suara' (Alt + T) saat menambah/mengedit agenda untuk mendengarkan sampel suara.\n"
		)
		
		self.textCtrl = wx.TextCtrl(self, value=help_text, style=wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_RICH2 | wx.HSCROLL)
		sizer.Add(self.textCtrl, 1, wx.EXPAND | wx.LEFT | wx.RIGHT, 8)
		
		btnSizer = wx.StdDialogButtonSizer()
		self.btnClose = wx.Button(self, wx.ID_CANCEL, label="&Tutup")
		self.btnClose.Bind(wx.EVT_BUTTON, lambda evt: self.EndModal(wx.ID_CANCEL))
		btnSizer.AddButton(self.btnClose)
		btnSizer.Realize()
		sizer.Add(btnSizer, 0, wx.ALIGN_RIGHT | wx.ALL, 12)
		
		self.SetSizer(sizer)
		self.Centre()
		self.textCtrl.SetFocus()


class ContextualHelpDialog(wx.Dialog):
	def __init__(self, parent, title, help_text):
		super().__init__(parent, title=title, size=(580, 460), style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)
		sizer = wx.BoxSizer(wx.VERTICAL)
		
		info_label = wx.StaticText(self, label="Gunakan Panah Atas/Bawah untuk membaca per baris, atau Panah Kiri/Kanan untuk mengeja teks:")
		sizer.Add(info_label, 0, wx.ALL, 8)
		
		self.textCtrl = wx.TextCtrl(self, value=help_text, style=wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_RICH2 | wx.HSCROLL)
		self.textCtrl.SetName("Gunakan Panah Atas/Bawah untuk membaca per baris, atau Panah Kiri/Kanan untuk mengeja teks:")
		self.textCtrl.SetToolTip("Gunakan Panah Atas/Bawah untuk membaca per baris, atau Panah Kiri/Kanan untuk mengeja teks:")
		sizer.Add(self.textCtrl, 1, wx.EXPAND | wx.LEFT | wx.RIGHT, 8)
		
		btnSizer = wx.StdDialogButtonSizer()
		self.btnClose = wx.Button(self, wx.ID_CANCEL, label="&Tutup")
		self.btnClose.Bind(wx.EVT_BUTTON, lambda evt: self.EndModal(wx.ID_CANCEL))
		btnSizer.AddButton(self.btnClose)
		btnSizer.Realize()
		sizer.Add(btnSizer, 0, wx.EXPAND | wx.ALL, 8)
		
		self.SetSizer(sizer)
		self.Layout()
		self.textCtrl.SetFocus()

class ChangelogDialog(wx.Dialog):
	def __init__(self, parent):
		super().__init__(parent, title="Catatan Riwayat Pembaruan JadwalKu (Changelog)", size=(620, 500), style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)
		sizer = wx.BoxSizer(wx.VERTICAL)
		
		info_label = wx.StaticText(self, label="Gunakan Panah Atas/Bawah untuk membaca riwayat pembaruan dari versi terbaru hingga terlama:")
		sizer.Add(info_label, 0, wx.ALL, 8)
		
		changelog_text = (
			"=== RIWAYAT PEMBARUAN JADWALKU ===\n\n"
			"[Versi 1.7.6.5]\n"
			"- Perbaikan Bug (Habit Tracker Bisu): Memperbaiki masalah pada penundaan jadwal 'Sekali Saja' yang gagal membunyikan alarm satu jam kemudian jika NVDA sempat dimuat ulang (restart) atau jika detak komputer meleset. Kini data penundaan (snooze) disimpan secara permanen!\n"
			"- Perbaikan Bug (Pengumuman Ganda): Memperbaiki anomali mesin Cache RAM yang mengulang nama jadwal pertama saat 2 jadwal aktif secara bersamaan, menjamin suara bacaan jadwal selalu otentik.\n"
			"- Pemadatan Irama Lonceng (Audio Engine): Beralih menggunakan target waktu absolut (milidetik presisi) pada mesin pemutar lonceng, sehingga ayunan 16.5 detik dan jeda 1.8 detik tidak lagi melar tertahan proses komputasi. Irama ketukan lonceng 100% presisi.\n"
			"- Penyempurnaan UX Laporan TTS (NVDA + / lalu W): Memangkas info 'Interval Waktu Berkala Aktif' pada pintasan waktu, sehingga laporan jam via TTS terasa jauh lebih ringkas, elegan, dan profesional (Terima kasih kepada Dedi Sanjaya atas laporannya).\n"
			"- Ketangguhan Mesin Suara (Anti-Freeze): Menambahkan batas waktu maksimal (timeout) 5 detik pada sintesis TTS. Kini jika Anda menggunakan SAPI5 Neural Voice online dan internet bermasalah, JadwalKu tidak akan lagi macet (hang) belasan detik, melainkan langsung menggunakan suara NVDA cadangan secara instan!\n"
			"- Perbaikan Bug (Jadwal Diedit): Memperbaiki anomali di mana jadwal (tanpa interval) yang sudah berbunyi hari ini tidak akan berbunyi lagi jika Anda hanya mengedit menit/jamnya. Kini, mengubah waktu jadwal akan me-reset status pemicunya sehingga bisa berbunyi lagi di hari yang sama!\n\n"
			"[Versi 1.7.6.4.3]\n"
			"- Perbaikan Kritis (Hotfix): Memperbaiki fitur Auto-Updater bawaan yang mogok dan gagal menampilkan jendela unduhan saat menemukan versi baru.\n\n"
			"[Versi 1.7.6.4.2]\n"
			"- Perbaikan Voice Pack (Bugfix): Memperbaiki bug RAM Cache di mana mesin memori salah memutar audio jam sebelumnya (misal \"0 menit\") saat jam berganti (misal \"30 menit\"). Kini mesin memori bisa membedakan file suara gabungan.\n\n"
			"[Versi 1.7.6.4.1]\n"
			"- Perbaikan Interaksi (Bugfix): Memperbaiki tombol Spasi dan Enter yang sebelumnya tidak merespon saat ditekan pada daftar Pelacak Kebiasaan (NVDA + / lalu J). Kini konteks menu pemilihan status (Selesai/Belum/Tunda) akan muncul dengan mulus. Menu ini juga mendukung klik kanan, klik ganda, dan tombol Aplikasi (Context Menu).\n\n"
			"[Versi 1.7.6.4]\n"
			"- Aksesibilitas Total: Menambal kelemahan antarmuka wxPython dengan membuang gaya visual slider (wx.SL_LABELS) yang merusak pohon hirarki MSAA Windows, serta menyematkan fitur .SetName() dan ToolTip otomatis pada 64 elemen kontrol (Slider, Kotak Teks, Kotak Kombo, dan List) di seluruh antarmuka JadwalKu. Kini saat bernavigasi menggunakan tombol Tab, NVDA akan membacakan nama fungsi elemen secara langsung tanpa memerlukan Object Navigation!\n"
			"- Ketangguhan Pelacak Kebiasaan (Habit Rollover): Merombak logika jadwal \"Sekali Waktu (Tanggal Spesifik)\". Kini jika jadwal tersebut diaktifkan sebagai Pelacak Kebiasaan (Habit Tracker) dan Anda mengabaikannya (tidak menekan tombol Belum/Tunda), jadwal tersebut tidak akan hangus! Ia akan terus mengulang dan menagih Anda di hari-hari berikutnya pada jam yang sama.\n"
			"- Teror Auto-Snooze: Selain itu, jadwal kebiasaan harian (tanpa interval) yang diabaikan kini akan otomatis menunda dirinya sendiri (Auto-Snooze) setiap 1 jam secara agresif, sampai Anda benar-benar mengeksekusi tombol \"Sudah Selesai\" via NVDA + / lalu J.\n"
			"- Performa Ekstrem (Audio Engine): Menyelamatkan NVDA dari kelambatan (lag) ketika jam klasik berbunyi panjang dengan menulis ulang kalkulator volume menggunakan library bahasa C (audioop.mul) serta mengadopsi memori tembolok (Memory Caching) untuk menghemat keausan hardisk. Selain itu, menyesuaikan kembali ritme interval ketukan jam (16.5 detik awal dan jeda 1.8 detik) yang sempat terpengaruh optimasi kecepatan komputasi, agar kembali mengayun elegan seperti aslinya.\n\n"
						"- Pembaruan Antarmuka Updater: Mengganti jendela konfirmasi pembaruan bawaan Windows (MessageBox) dengan jendela dialog khusus JadwalKu. Kini Anda dapat menelusuri dan mengeja catatan pembaruan (Changelog) baris demi baris menggunakan panah atas/bawah sebelum memutuskan untuk mengunduh versi baru.\n\n"
			"[Versi 1.7.6.3]\n"
			"- Fitur Baru (Log Terisolasi): Memisahkan seluruh catatan log internal JadwalKu agar tidak lagi menumpuk dan mengotori NVDA Log Viewer. Kini Anda dapat mengakses log khusus JadwalKu secara instan di Notepad dengan menekan shortcut NVDA + / lalu I.\n"
			"- Fitur Baru (Voice Command): Menambahkan umpan balik suara cerdas! Kini saat Anda bertanya \"What time?\" atau \"Jam berapa?\" ke mikrofon, JadwalKu akan memutar nada dering (WhatTimeRing) sesaat sebelum menjawab jamnya, persis seperti asisten virtual profesional (Saran dari Atikah Fina Wulandari).\n"
			"- Penyempurnaan Habit Tracker: Memperbaiki kendala (crash) gagal buka pada jendela Pelacak Kebiasaan, serta menyempurnakan logika jadwal \"Sekali Saja\". Kini jika Anda menekan \"Belum / Lewati\" atau \"Tunda\" pada Habit Tracker untuk jadwal yang tidak berulang, ia akan ditunda secara pintar dan mengingatkan Anda kembali.\n"
			"- Perbaikan Bug Super Langka (Race Condition): Memperbaiki isu di mana Voice Pack (Jam Bicara) mematikan paksa suara lonceng perempat jam (menit 15, 30, 45) secara prematur sebelum sempat terdengar.\n"
			"- Penyempurnaan Audio Overlap: Lonceng utama per jam (mulaiLonceng) kini dapat terdengar beriringan (tumpang-tindih) secara harmonis dengan suara peringatan Voice Pack, menghasilkan sensasi Grandfather Clock sesungguhnya tanpa potong-memotong audio.\n"
			"- Optimalisasi kestabilan thread mesin audio latar belakang JadwalKu.\n\n"
			"[Versi 1.7.6.2]\n"
			"- Penambahan Opsi Perempat Jam pada Lonceng Klasik: Kini lonceng dapat diatur untuk berbunyi setiap menit ke-15, 30, dan 45 menggunakan suara dentangan khusus!\n			- Perbaikan bug fatal pada menu bantuan di mana opsi '1' (Teks Panduan) gagal terbuka (Circular Import diselesaikan).\n"
			"- Menonaktifkan sementara opsi '2' (Simulasi Interaktif) ke mode Maintenance (Tahap Pengembangan).\n\n"
			"[Versi 1.7.6.1]\n"
			"- Penambahan Fitur Jam Lonceng Klasik (Grandfather Clock)! Nikmati sensasi jam kuno di rumah Anda dengan dentangan lonceng pada setiap pergantian jam dan opsi suara jarum detik di latar belakang. Dapat diatur hingga volume 1200% dan mengikuti perangkat audio favorit Anda (Akses via Pengaturan Agenda).\n"
			"- REVOLUSI BARU: JadwalKu kini menjadi Pelacak Kebiasaan (Habit Tracker)! Tekan NVDA + / lalu J untuk membuka panel daftar jadwal hari ini. Anda bisa menandai suatu jadwal 'Sudah Selesai', 'Lewati', atau 'Tunda (Snooze)'.\n"
			"- SISTEM LENCANA (GAMIFIKASI): JadwalKu kini akan mencatat runtutan hari (streak) kebiasaan Anda secara spesifik untuk setiap jadwal! Capai Lencana Perunggu (7 Hari), Perak (21 Hari), Emas (66 Hari) hingga Legenda (365 Hari).\n"
			"- ETALASE LENCANA: Tekan NVDA + / lalu L untuk membuka Etalase Lencana dan membaca riwayat/nostalgia panjang pencapaian ketekunan Anda.\n"
			"- Saat membuat atau mengedit jadwal, kini tersedia kotak centang baru: 'Jadikan ini sebagai Pelacak Kebiasaan'.\n"
			"- Fitur Snooze (Tunda) Cerdas: Jadwal berulang (interval) yang ditunda akan secara otomatis menyesuaikan dan menggeser sisa jadwal interval hari tersebut, agar ritme jaraknya (misal: tiap 2 jam) tetap konsisten.\n\n"
			"[Versi 1.7.6]\n"
			"- Fitur Baru: Menambahkan shortcut Status Dinamis (NVDA + Shift + /) untuk membacakan seluruh status pewaktu (Timer Rutin, Alarm, Pomodoro) secara bersamaan.\n"
			"- Fitur Baru: Antarmuka dinamis pada pembuatan Timer Rutin (NVDA + / lalu 1) dan Alarm (NVDA + / lalu 2). Jika Anda memiliki jadwal aktif, layar Manajer Pewaktu Aktif akan muncul, memungkinkan Anda untuk melakukan Jeda (Pause), Lanjutkan (Resume), atau Berhenti sepenuhnya pada tiap-tiap jadwal.\n"
			"- Perbaikan Pintasan: Memperbaiki tombol B (Bantuan) pada mode lapisan perintah (NVDA + / lalu B) yang sebelumnya tidak merespons.\n"
			"- Perbaikan Pomodoro: Memperbaiki masalah hitungan mundur (timer) yang bisa menjadi negatif dan memastikan Pomodoro berhenti otomatis setelah siklus terakhir (Istirahat Panjang) selesai.\n"
			"- Modul Simulasi Masterclass Diperluas: Latihan Jendela Utama (Tahap 1) dan Tahap Lanjutan (Tahap 2) telah direvitalisasi dan diperluas secara komprehensif.\n\n"
			"[Versi 1.7.4 & 1.7.3]\n"
			"- Perbaikan Auto-Update: Mengubah folder penyimpanan instalasi agar tidak diblokir oleh Windows dan mencegah file zip tidak lengkap.\n"
			"- Perbaikan Store: Memperbaiki masalah fatal di mana fungsi Hapus dengan Kata Sandi Master salah membaca ID pengguna.\n"
			"- Perbaikan Manifest: Memperbaiki kesalahan 'Duplicate keyword name' pada manifest.ini yang sebelumnya membatalkan instalasi.\n\n"
			"[Versi 1.7.2]\n"
			"- Pembaruan minor pada arsitektur update.\n"
		)
		
		self.textCtrl = wx.TextCtrl(self, value=changelog_text, style=wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_RICH2 | wx.HSCROLL)
		sizer.Add(self.textCtrl, 1, wx.EXPAND | wx.LEFT | wx.RIGHT, 8)
		
		btnSizer = wx.StdDialogButtonSizer()
		self.btnClose = wx.Button(self, wx.ID_CANCEL, label="&Tutup")
		self.btnClose.Bind(wx.EVT_BUTTON, lambda evt: self.EndModal(wx.ID_CANCEL))
		btnSizer.AddButton(self.btnClose)
		btnSizer.Realize()
		sizer.Add(btnSizer, 0, wx.ALIGN_RIGHT | wx.ALL, 12)
		
		self.SetSizer(sizer)
		self.Centre()
		self.textCtrl.SetFocus()


class FeedbackDialog(wx.Dialog):
	def __init__(self, parent, config_manager):
		super().__init__(parent, title="Kirim Laporan, Kritik, Saran & Bug Fix JadwalKu (Bot Telegram Aileen)", size=(680, 640), style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)
		self.config = config_manager
		sizer = wx.BoxSizer(wx.VERTICAL)
		
		info_label = wx.StaticText(self, label="Anda dapat mengirimkan ide fitur baru, kritik saran, atau melaporkan kesalahan (bug) langsung ke Bot Telegram pengembang.\nBatas pengiriman: 1 laporan per pengguna per hari (maksimal 10 laporan/hari dari seluruh pengguna).")
		sizer.Add(info_label, 0, wx.ALL, 8)
		
		# Kategori
		cat_sizer = wx.BoxSizer(wx.HORIZONTAL)
		cat_sizer.Add(wx.StaticText(self, label="&Kategori Laporan:"), 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 4)
		choices = ["Minta Fitur Baru / Ide Pengembangan", "Laporkan Kesalahan / Bug (Error)", "Kritik, Saran & Masukan Umum"]
		self.cb_category = wx.ComboBox(self, choices=choices, style=wx.CB_READONLY)
		self.cb_category.SetName("Kategori Laporan:")
		self.cb_category.SetToolTip("Kategori Laporan:")
		self.cb_category.SetSelection(0)
		self.cb_category.Bind(wx.EVT_COMBOBOX, self.onCategoryChange)
		cat_sizer.Add(self.cb_category, 1, wx.EXPAND | wx.ALL, 4)
		sizer.Add(cat_sizer, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 6)
		
		# Sub-Kategori Fitur (Untuk Bug Report)
		self.sub_sizer = wx.BoxSizer(wx.HORIZONTAL)
		self.lbl_sub_feature = wx.StaticText(self, label="&Pilih Fitur yang Mengalami Kesalahan:")
		self.sub_sizer.Add(self.lbl_sub_feature, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 4)
		sub_choices = [
			"Manajemen Agenda Rutin (Tambah/Edit/Hapus)",
			"Pengingat Waktu Berkala (Time Reminder)",
			"Mesin Suara TTS Mandiri SAPI 5",
			"Perintah Suara (Voice Command & Voice Pack)",
			"Audio Manager & Single-Open WinMM Relooping Engine",
			"Timer Mundur Cepat (Quick Timer)",
			"Alarm Sekali Pakai (One-Time Alarm & Snooze)",
			"Kalender Bulanan & Tanggal Merah",
			"Jam Dunia & Konversi Waktu",
			"Pemeriksa Pembaruan & Unduh Langsung (Update Checker)",
			"Lainnya / Kesalahan Umum Sistem NVDA"
		]
		self.cb_sub_feature = wx.ComboBox(self, choices=sub_choices, style=wx.CB_READONLY)
		self.cb_sub_feature.SetSelection(0)
		self.cb_sub_feature.Bind(wx.EVT_COMBOBOX, self.onSubFeatureChange)
		self.sub_sizer.Add(self.cb_sub_feature, 1, wx.EXPAND | wx.ALL, 4)
		sizer.Add(self.sub_sizer, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 6)
		
		# Judul
		title_sizer = wx.BoxSizer(wx.HORIZONTAL)
		title_sizer.Add(wx.StaticText(self, label="&Judul Laporan / Permintaan:"), 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 4)
		self.txt_title = wx.TextCtrl(self, value="Permintaan Fitur Baru JadwalKu")
		self.txt_title.SetName("Judul Laporan / Permintaan:")
		self.txt_title.SetToolTip("Judul Laporan / Permintaan:")
		title_sizer.Add(self.txt_title, 1, wx.EXPAND | wx.ALL, 4)
		sizer.Add(title_sizer, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 6)
		
		# Deskripsi
		sizer.Add(wx.StaticText(self, label="&Deskripsi Lengkap (Tuliskan detail ide permintaan atau kronologi error di sini):"), 0, wx.LEFT | wx.RIGHT | wx.TOP, 8)
		self.txt_desc = wx.TextCtrl(self, style=wx.TE_MULTILINE | wx.TE_RICH2)
		self.txt_desc.SetName("Deskripsi Lengkap (Tuliskan detail ide permintaan atau kronologi error di sini):")
		self.txt_desc.SetToolTip("Deskripsi Lengkap (Tuliskan detail ide permintaan atau kronologi error di sini):")
		sizer.Add(self.txt_desc, 1, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 8)
		
		# Log Diagnostik (Transparan dan Bisa Diedit)
		self.lbl_logs = wx.StaticText(self, label="&Log Deteksi Otomatis NVDA & JadwalKu (Akan dilampirkan transparan, dapat Anda periksa/edit):")
		sizer.Add(self.lbl_logs, 0, wx.LEFT | wx.RIGHT | wx.TOP, 8)
		self.txt_logs = wx.TextCtrl(self, style=wx.TE_MULTILINE | wx.TE_RICH2 | wx.HSCROLL)
		self.txt_logs.SetName("Log Deteksi Otomatis NVDA  JadwalKu (Akan dilampirkan transparan, dapat Anda periksa/edit):")
		self.txt_logs.SetToolTip("Log Deteksi Otomatis NVDA  JadwalKu (Akan dilampirkan transparan, dapat Anda periksa/edit):")
		sizer.Add(self.txt_logs, 1, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 8)
		
		# Sembunyikan Sub-Kategori & Log secara default (karena defaultnya adalah Permintaan Fitur Baru)
		self.lbl_sub_feature.Hide()
		self.cb_sub_feature.Hide()
		self.lbl_logs.Hide()
		self.txt_logs.Hide()
		
		# Tombol
		btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
		self.btn_send = wx.Button(self, label="&Kirim Laporan Sekarang")
		self.btn_send.Bind(wx.EVT_BUTTON, self.onSend)
		btn_sizer.Add(self.btn_send, 0, wx.ALL, 6)
		
		self.btn_cancel = wx.Button(self, wx.ID_CANCEL, label="&Batal")
		self.btn_cancel.Bind(wx.EVT_BUTTON, lambda evt: self.EndModal(wx.ID_CANCEL))
		btn_sizer.Add(self.btn_cancel, 0, wx.ALL, 6)
		
		sizer.Add(btn_sizer, 0, wx.ALIGN_RIGHT | wx.RIGHT | wx.BOTTOM, 8)
		
		self.SetSizer(sizer)
		self.Centre()

	def onCategoryChange(self, event):
		sel = self.cb_category.GetSelection()
		if sel == 1: # Bug Report
			self.lbl_sub_feature.Show()
			self.cb_sub_feature.Show()
			self.lbl_logs.Show()
			self.txt_logs.Show()
			if not self.txt_logs.GetValue():
				from .reportSender import extract_recent_logs
				self.txt_logs.SetValue(extract_recent_logs())
			sub_text = self.cb_sub_feature.GetStringSelection()
			self.txt_title.SetValue(f"Laporan Bug: {sub_text}")
		elif sel == 0: # Fitur Baru
			self.lbl_sub_feature.Hide()
			self.cb_sub_feature.Hide()
			self.lbl_logs.Hide()
			self.txt_logs.Hide()
			self.txt_title.SetValue("Permintaan Fitur Baru JadwalKu")
		else: # Kritik / Saran Masukan
			self.lbl_sub_feature.Hide()
			self.cb_sub_feature.Hide()
			self.lbl_logs.Hide()
			self.txt_logs.Hide()
			self.txt_title.SetValue("Kritik & Saran Masukan Umum JadwalKu")
		self.Layout()

	def onSubFeatureChange(self, event):
		if self.cb_category.GetSelection() == 1:
			sub_text = self.cb_sub_feature.GetStringSelection()
			self.txt_title.SetValue(f"Laporan Bug: {sub_text}")

	def onSend(self, event):
		desc = self.txt_desc.GetValue().strip()
		if not desc:
			ui.message("Mohon isi deskripsi lengkap laporan atau saran Anda sebelum mengirim.")
			self.txt_desc.SetFocus()
			return
		
		sel = self.cb_category.GetSelection()
		cat_map = {0: "Saran", 1: "Bug", 2: "Lainnya"}
		report_data = {
			"category": cat_map.get(sel, "Lainnya"),
			"sub_feature": self.cb_sub_feature.GetStringSelection() if sel == 1 else "-",
			"title": self.txt_title.GetValue().strip() or "Laporan JadwalKu",
			"description": desc,
			"logs": self.txt_logs.GetValue().strip() if sel == 1 else ""
		}
		
		self.btn_send.Disable()
		self.btn_cancel.Disable()
		ui.message("Mengirim laporan ke server JadwalKu...")
		
		from .reportSender import send_report_async
		def on_done(success, msg):
			ui.message(msg)
			if self and self.IsShown():
				if success:
					self.EndModal(wx.ID_OK)
				else:
					self.btn_send.Enable()
					self.btn_cancel.Enable()
					gui.messageBox(msg, "Pemberitahuan Laporan JadwalKu", wx.OK | wx.ICON_INFORMATION if "clipboard" in msg.lower() else wx.OK | wx.ICON_WARNING, self)
		
		send_report_async(self.config, report_data, on_done)


class CustomDaysDialog(wx.Dialog):
	def __init__(self, parent, current_days=None):
		super().__init__(parent, title="Pilih Gabungan Hari JadwalKu", size=(420, 380), style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)
		self.current_days = current_days or []
		
		sizer = wx.BoxSizer(wx.VERTICAL)
		sizer.Add(wx.StaticText(self, label="&Centang hari-hari saat jadwal ini akan berbunyi:"), 0, wx.ALL, 8)
		
		self.days = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"]
		self.checkboxes = {}
		for d in self.days:
			chk = wx.CheckBox(self, label=d)
			chk.SetValue(d in self.current_days)
			sizer.Add(chk, 0, wx.LEFT | wx.RIGHT | wx.TOP, 6)
			self.checkboxes[d] = chk
		
		btnSizer = wx.StdDialogButtonSizer()
		self.btnOk = wx.Button(self, wx.ID_OK, label="&Simpan")
		self.btnCancel = wx.Button(self, wx.ID_CANCEL, label="&Batal")
		btnSizer.AddButton(self.btnOk)
		btnSizer.AddButton(self.btnCancel)
		btnSizer.Realize()
		sizer.Add(btnSizer, 0, wx.ALIGN_RIGHT | wx.ALL, 15)
		
		self.SetSizer(sizer)
		self.Centre()
		self.checkboxes["Senin"].SetFocus()

	def get_selected_days(self):
		return [d for d in self.days if self.checkboxes[d].GetValue()]


class AudioManagerDialog(wx.Dialog):
	def __init__(self, parent, audio_manager, config_manager):
		super().__init__(parent, title="JadwalKu Audio Manager - Pengaturan Speaker & Suara", size=(560, 480), style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)
		self.audio = audio_manager
		self.config = config_manager
		
		sizer = wx.BoxSizer(wx.VERTICAL)
		
		# 1. Pilih Perangkat Output Audio (Speaker yang Berbeda)
		sizer.Add(wx.StaticText(self, label="&Pilih Perangkat Output Audio (Speaker / Kartu Suara):"), 0, wx.ALL, 6)
		device_names = self.audio.get_available_output_devices() if self.audio else ["Default (Microsoft Sound Mapper)"]
		
		self.cb_device = wx.ComboBox(self, choices=device_names, style=wx.CB_READONLY)
		self.cb_device.SetName("Pilih Perangkat Output Audio (Speaker / Kartu Suara):")
		self.cb_device.SetToolTip("Pilih Perangkat Output Audio (Speaker / Kartu Suara):")
		cur_dev = self.config.get_audio_device()
		if cur_dev in device_names:
			self.cb_device.SetValue(cur_dev)
		else:
			self.cb_device.SetSelection(0)
		sizer.Add(self.cb_device, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 6)
		
		self.btnTestDevice = wx.Button(self, label="&Tes Suara di Speaker Ini")
		self.btnTestDevice.Bind(wx.EVT_BUTTON, self.onTestDevice)
		sizer.Add(self.btnTestDevice, 0, wx.ALL, 6)
		
		# 2. Pengaturan Volume Audio (Maksimal 1200%)
		cur_vol = self.config.get_audio_volume() if self.config else 100
		self.lbl_volume = wx.StaticText(self, label=f"&Volume Audio Suara ({cur_vol}%):")
		sizer.Add(self.lbl_volume, 0, wx.ALL, 6)
		
		self.slider_volume = wx.Slider(self, value=cur_vol, minValue=1, maxValue=1200, style=wx.SL_HORIZONTAL | wx.SL_AUTOTICKS)
		self.slider_volume.Bind(wx.EVT_SLIDER, self.onVolumeScroll)
		sizer.Add(self.slider_volume, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 6)
		
		self.btnResetVolume = wx.Button(self, label="&Reset Volume ke Normal (100%)")
		self.btnResetVolume.Bind(wx.EVT_BUTTON, self.onResetVolume)
		sizer.Add(self.btnResetVolume, 0, wx.ALL, 6)
		
		# 3. Daftar Aset Suara & Alarm yang Tersedia
		sizer.Add(wx.StaticText(self, label="&Daftar File Suara di Folder Add-on:"), 0, wx.ALL, 6)
		self.lb_sounds = wx.ListBox(self)
		self.refresh_sounds_list()
		sizer.Add(self.lb_sounds, 1, wx.EXPAND | wx.LEFT | wx.RIGHT, 6)
		
		self.btnTestFile = wx.Button(self, label="T&es File Suara Terpilih")
		self.btnTestFile.Bind(wx.EVT_BUTTON, self.onTestFile)
		sizer.Add(self.btnTestFile, 0, wx.ALL, 6)
		
		# Tombol Simpan & Batal
		btnSizer = wx.StdDialogButtonSizer()
		self.btnOk = wx.Button(self, wx.ID_OK, label="&Simpan")
		self.btnCancel = wx.Button(self, wx.ID_CANCEL, label="&Batal")
		self.btnHelp = wx.Button(self, label="&Bantuan... (Alt+B)")
		self.btnHelp.Bind(wx.EVT_BUTTON, self.onContextualHelp)
		btnSizer.AddButton(self.btnOk)
		btnSizer.AddButton(self.btnCancel)
		btnSizer.AddButton(self.btnHelp)
		btnSizer.Realize()
		sizer.Add(btnSizer, 0, wx.ALIGN_RIGHT | wx.ALL, 12)
		
		self.SetSizer(sizer)
		self.Centre()
		self.cb_device.SetFocus()
		self.Bind(wx.EVT_CLOSE, self.onClose)

	def onContextualHelp(self, evt):
		text = "BANTUAN AUDIO MANAGER:\n\n- Audio Manager memungkinkan JadwalKu memutar suara alarm/chime melalui perangkat output/speaker yang BEDA dari suara Screen Reader (NVDA).\n- Anda bisa mengatur volume suara JadwalKu secara independen agar lebih keras dari suara NVDA.\n- Centang opsi Auto-Resume jika Anda ingin audio lain otomatis menyala kembali setelah alarm berbunyi."
		dlg = ContextualHelpDialog(self, "Bantuan: Audio Manager", text)
		dlg.ShowModal()
		dlg.Destroy()

	def onVolumeScroll(self, event):
		val = self.slider_volume.GetValue()
		self.lbl_volume.SetLabel(f"&Volume Audio Suara ({val}%):")
		if self.audio:
			self.audio._override_volume = val
		
		if not hasattr(self, "_volume_timer"):
			self._volume_timer = wx.Timer(self)
			self.Bind(wx.EVT_TIMER, self._onPlayVolumePreview, self._volume_timer)
		self._volume_timer.Start(150, wx.TIMER_ONE_SHOT)

	def _onPlayVolumePreview(self, event):
		if not self.audio:
			return
		sel = self.lb_sounds.GetStringSelection() if hasattr(self, "lb_sounds") else ""
		if not sel or sel == "Tanpa Suara Audio":
			sel = "chime.wav"
		sel_dev = self.cb_device.GetValue()
		old_dev = self.config.get_audio_device()
		try:
			self.config.set_audio_device(sel_dev)
			self.audio.stop_sound()
			self.audio.play_sound(sel)
		finally:
			self.config.set_audio_device(old_dev)

	def onResetVolume(self, event):
		self.slider_volume.SetValue(100)
		self.lbl_volume.SetLabel("&Volume Audio Suara (100%):")
		if self.audio:
			self.audio._override_volume = 100
			self.audio.stop_sound()
			self.audio.play_sound("chime.wav")
		ui.message("Volume direset ke 100%.")

	def onClose(self, event):
		if hasattr(self, "_volume_timer") and self._volume_timer.IsRunning():
			self._volume_timer.Stop()
		if hasattr(self, "_test_timer") and self._test_timer.IsRunning():
			self._test_timer.Stop()
		if self.audio and hasattr(self.audio, "_override_volume"):
			self.audio._override_volume = None
		if self.audio:
			self.audio.stop_sound()
		event.Skip()

	def refresh_sounds_list(self):
		self.lb_sounds.Clear()
		sounds_dir = os.path.join(os.path.dirname(__file__), "sounds")
		if os.path.exists(sounds_dir):
			files = sorted(os.listdir(sounds_dir))
			for f in files:
				if (f.lower().endswith(".wav") or f.lower().endswith(".mp3")) and f not in ["on.wav", "off.wav"]:
					self.lb_sounds.Append(f)

	def onTestDevice(self, event):
		if getattr(self, "_is_test_playing", False) or "Hentikan" in self.btnTestDevice.GetLabel():
			self.audio.stop_sound()
			self.btnTestDevice.SetLabel("&Tes Suara di Speaker Ini")
			self.btnTestFile.SetLabel("T&es File Suara Terpilih")
			self._is_test_playing = False
			if hasattr(self, "_test_timer"):
				self._test_timer.Stop()
			ui.message("Tes suara dihentikan.")
			return

		sel_dev = self.cb_device.GetValue()
		old_dev = self.config.get_audio_device()
		try:
			self.config.set_audio_device(sel_dev)
			ui.message(f"Menguji speaker: {sel_dev}")
			self.btnTestDevice.SetLabel("&Hentikan Tes di Speaker Ini")
			self._is_test_playing = True
			if self.audio:
				self.audio._override_volume = self.slider_volume.GetValue()
			self.audio.play_sound("chime.wav", allow_overlap=False)
			if not hasattr(self, "_test_timer"):
				self._test_timer = wx.Timer(self)
				self.Bind(wx.EVT_TIMER, self._onCheckTestStatus, self._test_timer)
			self._test_timer.Start(250)
		finally:
			self.config.set_audio_device(old_dev)

	def onTestFile(self, event):
		if getattr(self, "_is_test_playing", False) or "Hentikan" in self.btnTestFile.GetLabel():
			self.audio.stop_sound()
			self.btnTestDevice.SetLabel("&Tes Suara di Speaker Ini")
			self.btnTestFile.SetLabel("T&es File Suara Terpilih")
			self._is_test_playing = False
			if hasattr(self, "_test_timer"):
				self._test_timer.Stop()
			ui.message("Tes suara dihentikan.")
			return

		sel = self.lb_sounds.GetStringSelection()
		if not sel:
			ui.message("Pilih file suara dari daftar terlebih dahulu.")
			return
		sel_dev = self.cb_device.GetValue()
		old_dev = self.config.get_audio_device()
		try:
			self.config.set_audio_device(sel_dev)
			ui.message(f"Memutar {sel} di speaker {sel_dev}")
			self.btnTestFile.SetLabel("H&entikan Tes File Terpilih")
			self._is_test_playing = True
			if self.audio:
				self.audio._override_volume = self.slider_volume.GetValue()
			self.audio.play_sound(sel, allow_overlap=False)
			if not hasattr(self, "_test_timer"):
				self._test_timer = wx.Timer(self)
				self.Bind(wx.EVT_TIMER, self._onCheckTestStatus, self._test_timer)
			self._test_timer.Start(250)
		finally:
			self.config.set_audio_device(old_dev)

	def _onCheckTestStatus(self, event):
		if not self.audio or not self.audio.has_active_sounds():
			self.btnTestDevice.SetLabel("&Tes Suara di Speaker Ini")
			self.btnTestFile.SetLabel("T&es File Suara Terpilih")
			self._is_test_playing = False
			if hasattr(self, "_test_timer"):
				self._test_timer.Stop()

	def get_result(self):
		return {
			"audio_device": self.cb_device.GetValue(),
			"audio_volume": self.slider_volume.GetValue()
		}


class AgendaDialog(wx.Dialog):
	def __init__(self, parent, schedule_data=None, audio_manager=None):
		super().__init__(parent, title="Formulir Agenda JadwalKu", size=(520, 490), style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)
		self.schedule_data = schedule_data or {}
		self.audio_manager = audio_manager
		
		sizer = wx.BoxSizer(wx.VERTICAL)
		
		# 1. Nama Agenda
		sizer.Add(wx.StaticText(self, label="&Nama Agenda:"), 0, wx.ALL, 5)
		self.txt_name = wx.TextCtrl(self, value=self.schedule_data.get("name", ""))
		self.txt_name.SetName("Nama Agenda:")
		self.txt_name.SetToolTip("Nama Agenda:")
		sizer.Add(self.txt_name, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 5)
		
		self.custom_days = self.schedule_data.get("custom_days", [])
		
		# 2. Frekuensi / Hari & Tombol Pilih Hari
		sizer.Add(wx.StaticText(self, label="&Frekuensi / Hari:"), 0, wx.ALL, 5)
		freq_sizer = wx.BoxSizer(wx.HORIZONTAL)
		freq_choices = [
			"Setiap Hari", "Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu",
			"Hari Kerja (Senin - Jumat)", "Akhir Pekan (Sabtu - Minggu)",
			"Sesuaikan Hari (Pilih Hari Spesifik...)", "Sekali Waktu (Tanggal Spesifik)"
		]
		self.cb_freq = wx.ComboBox(self, choices=freq_choices, style=wx.CB_READONLY)
		self.cb_freq.SetName("Frekuensi / Hari:")
		self.cb_freq.SetToolTip("Frekuensi / Hari:")
		current_freq = self.schedule_data.get("frequency", "Setiap Hari")
		if current_freq in freq_choices or current_freq.startswith("Sesuaikan Hari"):
			if current_freq.startswith("Sesuaikan Hari"):
				if not self.custom_days and ":" in current_freq:
					self.custom_days = [d.strip() for d in current_freq.split(":", 1)[1].split(",") if d.strip()]
				self.cb_freq.SetValue(current_freq)
			else:
				self.cb_freq.SetValue(current_freq)
		else:
			self.cb_freq.SetSelection(0)
		freq_sizer.Add(self.cb_freq, 1, wx.EXPAND | wx.RIGHT, 5)
		
		self.btnCustomDays = wx.Button(self, label="&Pilih Hari (Checklist)...")
		self.btnCustomDays.Bind(wx.EVT_BUTTON, self.onSelectCustomDays)
		freq_sizer.Add(self.btnCustomDays, 0, wx.ALIGN_CENTER_VERTICAL)
		sizer.Add(freq_sizer, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 5)
		
		# 3. Tanggal Spesifik (jika pilih Sekali Waktu)
		sizer.Add(wx.StaticText(self, label="&Tanggal Spesifik (Format: YYYY-MM-DD, misal 2026-07-15):"), 0, wx.ALL, 5)
		self.txt_date = wx.TextCtrl(self, value=self.schedule_data.get("date", datetime.datetime.now().strftime("%Y-%m-%d")))
		self.txt_date.SetName("Tanggal Spesifik (Format: YYYY-MM-DD, misal 2026-07-15):")
		self.txt_date.SetToolTip("Tanggal Spesifik (Format: YYYY-MM-DD, misal 2026-07-15):")
		sizer.Add(self.txt_date, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 5)
		
		# 4. Waktu (Jam & Menit)
		time_sizer = wx.BoxSizer(wx.HORIZONTAL)
		time_sizer.Add(wx.StaticText(self, label="&Jam:"), 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)
		hours = [f"{i:02d}" for i in range(24)]
		self.cb_hour = wx.ComboBox(self, choices=hours, style=wx.CB_READONLY)
		self.cb_hour.SetName("Jam:")
		self.cb_hour.SetToolTip("Jam:")
		cur_hour = int(self.schedule_data.get("hour", 12))
		self.cb_hour.SetValue(f"{cur_hour:02d}")
		time_sizer.Add(self.cb_hour, 0, wx.ALL, 5)
		
		time_sizer.Add(wx.StaticText(self, label="&Menit:"), 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)
		minutes = [f"{i:02d}" for i in range(60)]
		self.cb_minute = wx.ComboBox(self, choices=minutes, style=wx.CB_READONLY)
		self.cb_minute.SetName("Menit:")
		self.cb_minute.SetToolTip("Menit:")
		cur_min = int(self.schedule_data.get("minute", 0))
		self.cb_minute.SetValue(f"{cur_min:02d}")
		time_sizer.Add(self.cb_minute, 0, wx.ALL, 5)
		sizer.Add(time_sizer, 0, wx.ALL, 5)
		
		# 5. Pengingat Berulang (Interval Jam Sekali)
		sizer.Add(wx.StaticText(self, label="&Ulangi Setiap (Interval Jam Sekali):"), 0, wx.ALL, 5)
		self.interval_values = [0, 1, 2, 3, 4, 6, 8, 12]
		interval_choices = [
			"Sekali Saja pada Jam & Menit Tersebut (Tidak Diulang)",
			"Setiap 1 Jam Sekali (Berulang dalam Hari Itu)",
			"Setiap 2 Jam Sekali (Berulang dalam Hari Itu)",
			"Setiap 3 Jam Sekali (Berulang dalam Hari Itu)",
			"Setiap 4 Jam Sekali (Berulang dalam Hari Itu)",
			"Setiap 6 Jam Sekali (Berulang dalam Hari Itu)",
			"Setiap 8 Jam Sekali (Berulang dalam Hari Itu)",
			"Setiap 12 Jam Sekali (Berulang dalam Hari Itu)"
		]
		self.cb_interval = wx.ComboBox(self, choices=interval_choices, style=wx.CB_READONLY)
		self.cb_interval.SetName("Ulangi Setiap (Interval Jam Sekali):")
		self.cb_interval.SetToolTip("Ulangi Setiap (Interval Jam Sekali):")
		cur_int = int(self.schedule_data.get("interval_hour", 0))
		if cur_int in self.interval_values:
			self.cb_interval.SetSelection(self.interval_values.index(cur_int))
		else:
			self.cb_interval.SetSelection(0)
		sizer.Add(self.cb_interval, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 5)
		
		# 6. Waktu Selesai Interval (Jam Selesai Perulangan)
		sizer.Add(wx.StaticText(self, label="&Waktu Selesai Interval (Jam Selesai Perulangan):"), 0, wx.ALL, 5)
		end_hours = [f"{i:02d} (Jam {i:02d}:00)" for i in range(24)]
		self.cb_interval_end = wx.ComboBox(self, choices=end_hours, style=wx.CB_READONLY)
		self.cb_interval_end.SetName("Waktu Selesai Interval (Jam Selesai Perulangan):")
		self.cb_interval_end.SetToolTip("Waktu Selesai Interval (Jam Selesai Perulangan):")
		cur_end = int(self.schedule_data.get("interval_end_hour", 23))
		if 0 <= cur_end <= 23:
			self.cb_interval_end.SetSelection(cur_end)
		else:
			self.cb_interval_end.SetSelection(23)
		sizer.Add(self.cb_interval_end, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 5)
		
		# 7. Mode Pemberitahuan (Chime vs Alarm Weker)
		sizer.Add(wx.StaticText(self, label="&Mode Pemberitahuan:"), 0, wx.ALL, 5)
		alarm_modes = [
			"Pemberitahuan Singkat (Sekali Bunyi / Chime)",
			"Alarm Jam Weker (Berdering Berulang + Fitur Tunda / Snooze)"
		]
		self.cb_alarm_mode = wx.ComboBox(self, choices=alarm_modes, style=wx.CB_READONLY)
		self.cb_alarm_mode.SetName("Mode Pemberitahuan:")
		self.cb_alarm_mode.SetToolTip("Mode Pemberitahuan:")
		if self.schedule_data.get("is_alarm", False) or self.schedule_data.get("alarm_mode") == alarm_modes[1]:
			self.cb_alarm_mode.SetSelection(1)
		else:
			self.cb_alarm_mode.SetSelection(0)
		sizer.Add(self.cb_alarm_mode, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 5)
		
		# 6. Suara Audio
		sizer.Add(wx.StaticText(self, label="&Suara Chime/Alarm:"), 0, wx.ALL, 5)
		audio_sizer = wx.BoxSizer(wx.HORIZONTAL)
		
		self.audio_files_map = []
		audio_choices = []
		
		# Aset standar
		std_items = [
			("chime.wav", "chime.wav (Chime Lembut)"),
			("bell.wav", "bell.wav (Bel Singkat)"),
			("alarm.wav", "alarm.wav (Alarm Nada Dering)"),
			("wind-up-clock-alarm-bell.mp3", "wind-up-clock-alarm-bell.mp3 (Alarm Jam Weker)")
		]
		for filename, label in std_items:
			self.audio_files_map.append(filename)
			audio_choices.append(label)
		
		# Scan tambahan dari folder sounds
		sounds_dir = os.path.join(os.path.dirname(__file__), "sounds")
		if os.path.exists(sounds_dir):
			for f in sorted(os.listdir(sounds_dir)):
				if (f.lower().endswith(".wav") or f.lower().endswith(".mp3")) and f not in ["on.wav", "off.wav"] and f not in self.audio_files_map:
					self.audio_files_map.append(f)
					audio_choices.append(f"{f} (Suara Kustom)")
		
		self.audio_files_map.append("")
		audio_choices.append("Tanpa Suara Audio")
		
		self.cb_audio = wx.ComboBox(self, choices=audio_choices, style=wx.CB_READONLY)
		cur_audio = self.schedule_data.get("audio_file", "chime.wav")
		if not self.schedule_data.get("audio_enabled", True) or not cur_audio:
			self.cb_audio.SetSelection(len(audio_choices) - 1)
		elif cur_audio in self.audio_files_map:
			self.cb_audio.SetSelection(self.audio_files_map.index(cur_audio))
		else:
			self.cb_audio.SetSelection(0)
		
		audio_sizer.Add(self.cb_audio, 1, wx.EXPAND | wx.RIGHT, 5)
		
		if self.audio_manager:
			self.btnTestSound = wx.Button(self, label="&Tes Suara")
			self.btnTestSound.Bind(wx.EVT_BUTTON, self.onTestSound)
			audio_sizer.Add(self.btnTestSound, 0, wx.ALIGN_CENTER_VERTICAL)
		
		sizer.Add(audio_sizer, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 5)
		
		# 6. Checkboxes
		self.chk_speech = wx.CheckBox(self, label="Bacakan pesan dengan &Suara NVDA (Speech)")
		self.chk_speech.SetValue(self.schedule_data.get("speech_enabled", True))
		sizer.Add(self.chk_speech, 0, wx.ALL, 8)
		
		self.chk_habit = wx.CheckBox(self, label="&Jadikan ini sebagai Pelacak Kebiasaan (Habit Tracker)")
		self.chk_habit.SetValue(self.schedule_data.get("is_habit", True))
		sizer.Add(self.chk_habit, 0, wx.ALL, 8)
		
		self.chk_active = wx.CheckBox(self, label="Status &Jadwal Aktif (Check)")
		self.chk_active.SetValue(self.schedule_data.get("active", True))
		sizer.Add(self.chk_active, 0, wx.ALL, 8)
		
		# Buttons
		btnSizer = wx.StdDialogButtonSizer()
		self.btnOk = wx.Button(self, wx.ID_OK, label="&Simpan")
		self.btnCancel = wx.Button(self, wx.ID_CANCEL, label="&Batal")
		btnSizer.AddButton(self.btnOk)
		btnSizer.AddButton(self.btnCancel)
		btnSizer.Realize()
		sizer.Add(btnSizer, 0, wx.ALIGN_RIGHT | wx.ALL, 15)
		
		self.SetSizer(sizer)
		self.Centre()
		self.txt_name.SetFocus()

	def onSelectCustomDays(self, event):
		dlg = CustomDaysDialog(self, getattr(self, "custom_days", []))
		if dlg.ShowModal() == wx.ID_OK:
			self.custom_days = dlg.get_selected_days()
			if self.custom_days:
				self.cb_freq.SetValue("Sesuaikan Hari: " + ", ".join(self.custom_days))
			else:
				self.cb_freq.SetValue("Setiap Hari")
		dlg.Destroy()

	def get_result(self):
		sel = self.cb_audio.GetSelection()
		if 0 <= sel < len(self.audio_files_map):
			audio_file = self.audio_files_map[sel]
		else:
			audio_file = "chime.wav"
		audio_enabled = bool(audio_file)
		
		is_alarm_sel = (self.cb_alarm_mode.GetSelection() == 1)
		interval_idx = self.cb_interval.GetSelection()
		interval_val = self.interval_values[interval_idx] if 0 <= interval_idx < len(self.interval_values) else 0
		end_idx = self.cb_interval_end.GetSelection()
		interval_end_val = end_idx if 0 <= end_idx <= 23 else 23
		alarm_modes = [
			"Pemberitahuan Singkat (Sekali Bunyi / Chime)",
			"Alarm Jam Weker (Berdering Berulang + Fitur Tunda / Snooze)"
		]
		
		new_hour = int(self.cb_hour.GetValue())
		new_minute = int(self.cb_minute.GetValue())
		
		# Reset trigger history if time was changed, so it can trigger again today
		last_trigger = self.schedule_data.get("last_triggered_date", "")
		old_hour = self.schedule_data.get("hour")
		old_minute = self.schedule_data.get("minute")
		if old_hour is not None and old_minute is not None:
			if old_hour != new_hour or old_minute != new_minute:
				last_trigger = ""
				
		return {
			"id": self.schedule_data.get("id", ""),
			"name": self.txt_name.GetValue().strip() or "Agenda Tanpa Nama",
			"frequency": self.cb_freq.GetValue(),
			"custom_days": getattr(self, "custom_days", []),
			"date": self.txt_date.GetValue().strip(),
			"hour": new_hour,
			"minute": new_minute,
			"interval_hour": interval_val,
			"interval_end_hour": interval_end_val,
			"audio_enabled": audio_enabled,
			"audio_file": audio_file,
			"speech_enabled": self.chk_speech.GetValue(),
			"active": self.chk_active.GetValue(),
			"is_alarm": is_alarm_sel,
			"alarm_mode": alarm_modes[1] if is_alarm_sel else alarm_modes[0],
			"is_habit": self.chk_habit.GetValue(),
			"last_triggered_date": last_trigger
		}

	def onTestSound(self, event):
		if not self.audio_manager:
			return
		if getattr(self, "_is_test_playing", False) or "Hentikan" in self.btnTestSound.GetLabel():
			self.audio_manager.stop_sound()
			self.btnTestSound.SetLabel("&Tes Suara")
			self._is_test_playing = False
			if hasattr(self, "_test_timer"):
				self._test_timer.Stop()
			ui.message("Suara tes dihentikan.")
			return

		sel = self.cb_audio.GetSelection()
		if 0 <= sel < len(self.audio_files_map) and self.audio_files_map[sel]:
			audio_file = self.audio_files_map[sel]
			ui.message(f"Memutar tes suara: {audio_file}")
			self.btnTestSound.SetLabel("&Hentikan Suara Tes")
			self._is_test_playing = True
			self.audio_manager.play_sound(audio_file)
			if not hasattr(self, "_test_timer"):
				self._test_timer = wx.Timer(self)
				self.Bind(wx.EVT_TIMER, self._onCheckTestStatus, self._test_timer)
			self._test_timer.Start(250)
		else:
			ui.message("Anda memilih opsi Tanpa Suara Audio.")

	def _onCheckTestStatus(self, event):
		if not self.audio_manager or not self.audio_manager.has_active_sounds():
			self.btnTestSound.SetLabel("&Tes Suara")
			self._is_test_playing = False
			if hasattr(self, "_test_timer"):
				self._test_timer.Stop()


class QuickTimerDialog(wx.Dialog):
	def __init__(self, parent, audio_manager=None):
		super().__init__(parent, title="Pasang Timer Mundur Cepat (Quick Timer)", size=(460, 320), style=wx.DEFAULT_DIALOG_STYLE)
		self.audio_manager = audio_manager
		
		sizer = wx.BoxSizer(wx.VERTICAL)
		
		# 1. Input Durasi Angka
		sizer.Add(wx.StaticText(self, label="&Durasi Waktu Angka:"), 0, wx.ALL, 5)
		self.txt_duration = wx.TextCtrl(self, value="10")
		self.txt_duration.SetName("Durasi Waktu Angka:")
		self.txt_duration.SetToolTip("Durasi Waktu Angka:")
		sizer.Add(self.txt_duration, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 5)
		
		# 2. Satuan Waktu (Dropdown: Detik, Menit, Jam)
		sizer.Add(wx.StaticText(self, label="&Satuan Waktu:"), 0, wx.ALL, 5)
		self.cb_unit = wx.ComboBox(self, choices=["Menit", "Detik", "Jam"], style=wx.CB_READONLY)
		self.cb_unit.SetName("Satuan Waktu:")
		self.cb_unit.SetToolTip("Satuan Waktu:")
		self.cb_unit.SetSelection(0)  # Default ke Menit
		sizer.Add(self.cb_unit, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 5)
		
		# 3. Detik Persiapan Sebelum Mulai (Hitung Mundur Awal)
		sizer.Add(wx.StaticText(self, label="&Detik Persiapan Sebelum Mulai (0 jika langsung):"), 0, wx.ALL, 5)
		self.txt_prep_seconds = wx.TextCtrl(self, value="0")
		self.txt_prep_seconds.SetName("Detik Persiapan Sebelum Mulai (0 jika langsung):")
		self.txt_prep_seconds.SetToolTip("Detik Persiapan Sebelum Mulai (0 jika langsung):")
		sizer.Add(self.txt_prep_seconds, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 5)
		
		# 4. Suara Audio
		sizer.Add(wx.StaticText(self, label="&Suara Timer:"), 0, wx.ALL, 5)
		audio_sizer = wx.BoxSizer(wx.HORIZONTAL)
		self.audio_files_map = []
		audio_choices = []
		std_items = [
			("wind-up-clock-alarm-bell.mp3", "wind-up-clock-alarm-bell.mp3 (Alarm Jam Weker)"),
			("alarm.wav", "alarm.wav (Alarm Nada Dering)"),
			("chime.wav", "chime.wav (Chime Lembut)"),
			("bell.wav", "bell.wav (Bel Singkat)")
		]
		for filename, label in std_items:
			self.audio_files_map.append(filename)
			audio_choices.append(label)
		if audio_manager and hasattr(audio_manager, "get_sound_path"):
			try:
				import os
				s_dir = os.path.join(os.path.dirname(__file__), "sounds")
				if os.path.exists(s_dir):
					for f in sorted(os.listdir(s_dir)):
						if f.lower().endswith(('.wav', '.mp3')) and f not in self.audio_files_map:
							self.audio_files_map.append(f)
							audio_choices.append(f)
			except Exception:
				pass
		self.cb_audio = wx.ComboBox(self, choices=audio_choices, style=wx.CB_READONLY)
		if self.cb_audio.GetCount() > 0:
			self.cb_audio.SetSelection(0)
		audio_sizer.Add(self.cb_audio, 1, wx.EXPAND | wx.RIGHT, 5)
		
		self.btnTestSound = wx.Button(self, label="&Tes Suara (Alt+T)")
		self.btnTestSound.Bind(wx.EVT_BUTTON, self.onTestSound)
		audio_sizer.Add(self.btnTestSound, 0)
		sizer.Add(audio_sizer, 0, wx.EXPAND | wx.ALL, 5)
		
		# Buttons
		btnSizer = wx.StdDialogButtonSizer()
		self.btnOk = wx.Button(self, wx.ID_OK, label="&Mulai Timer")
		self.btnCancel = wx.Button(self, wx.ID_CANCEL, label="&Batal")
		self.btnHelp = wx.Button(self, label="&Bantuan... (Alt+B)")
		self.btnHelp.Bind(wx.EVT_BUTTON, self.onContextualHelp)
		btnSizer.AddButton(self.btnOk)
		btnSizer.AddButton(self.btnCancel)
		btnSizer.AddButton(self.btnHelp)
		btnSizer.Realize()
		sizer.Add(btnSizer, 0, wx.ALIGN_RIGHT | wx.ALL, 15)
		
		self.SetSizer(sizer)
		self.Centre()
		self.txt_duration.SetFocus()

	def onContextualHelp(self, evt):
		text = "BANTUAN QUICK TIMER:\n\n- Quick Timer adalah cara tercepat untuk memasang hitung mundur (contoh: 10 menit).\n- Anda dapat Menjeda (Pause) dan Melanjutkan (Resume) timer kapan saja.\n- Pada 10 detik terakhir, JadwalKu akan memutar suara detak jam berdebar (ticking)."
		dlg = ContextualHelpDialog(self, "Bantuan: Quick Timer", text)
		dlg.ShowModal()
		dlg.Destroy()

	def onTestSound(self, event):
		if not self.audio_manager:
			return
		if getattr(self, "_is_test_playing", False) or "Hentikan" in self.btnTestSound.GetLabel():
			self.audio_manager.stop_sound()
			self.btnTestSound.SetLabel("&Tes Suara (Alt+T)")
			self._is_test_playing = False
			if hasattr(self, "_test_timer"):
				self._test_timer.Stop()
			ui.message("Suara tes dihentikan.")
			return

		sel = self.cb_audio.GetSelection()
		if 0 <= sel < len(self.audio_files_map) and self.audio_files_map[sel]:
			audio_file = self.audio_files_map[sel]
			ui.message(f"Memutar tes suara: {audio_file}")
			self.btnTestSound.SetLabel("&Hentikan Suara Tes (Alt+T)")
			self._is_test_playing = True
			self.audio_manager.play_sound(audio_file)
			if not hasattr(self, "_test_timer"):
				self._test_timer = wx.Timer(self)
				self.Bind(wx.EVT_TIMER, self._onCheckTestStatus, self._test_timer)
			self._test_timer.Start(250)

	def _onCheckTestStatus(self, event):
		if not self.audio_manager or not self.audio_manager.has_active_sounds():
			self.btnTestSound.SetLabel("&Tes Suara (Alt+T)")
			self._is_test_playing = False
			if hasattr(self, "_test_timer"):
				self._test_timer.Stop()

	def get_result(self):
		dur_str = self.txt_duration.GetValue().strip()
		try:
			dur = int(dur_str)
			if dur <= 0:
				dur = 1
		except Exception:
			dur = 10
		prep_str = self.txt_prep_seconds.GetValue().strip()
		try:
			prep = int(prep_str)
			if prep < 0:
				prep = 0
		except Exception:
			prep = 0
		sel = self.cb_audio.GetSelection()
		audio_file = self.audio_files_map[sel] if 0 <= sel < len(self.audio_files_map) else "alarm.wav"
		return {
			"duration": dur,
			"unit": self.cb_unit.GetValue() or "Menit",
			"audio_file": audio_file,
			"prep_seconds": prep
		}


class OneTimeAlarmDialog(wx.Dialog):
	def __init__(self, parent, audio_manager=None):
		super().__init__(parent, title="Pasang Alarm Sekali Pakai (One-Time Alarm)", size=(480, 360), style=wx.DEFAULT_DIALOG_STYLE)
		self.audio_manager = audio_manager
		import datetime
		now = datetime.datetime.now() + datetime.timedelta(minutes=5)
		
		sizer = wx.BoxSizer(wx.VERTICAL)
		
		# 1. Dropdown Jam
		sizer.Add(wx.StaticText(self, label="&Jam (00 - 23):"), 0, wx.ALL, 5)
		hours = [f"{h:02d}" for h in range(24)]
		self.cb_hour = wx.ComboBox(self, choices=hours, style=wx.CB_READONLY)
		self.cb_hour.SetName("Jam (00 - 23):")
		self.cb_hour.SetToolTip("Jam (00 - 23):")
		self.cb_hour.SetValue(f"{now.hour:02d}")
		sizer.Add(self.cb_hour, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 5)
		
		# 2. Dropdown Menit
		sizer.Add(wx.StaticText(self, label="&Menit (00 - 59):"), 0, wx.ALL, 5)
		minutes = [f"{m:02d}" for m in range(60)]
		self.cb_minute = wx.ComboBox(self, choices=minutes, style=wx.CB_READONLY)
		self.cb_minute.SetName("Menit (00 - 59):")
		self.cb_minute.SetToolTip("Menit (00 - 59):")
		self.cb_minute.SetValue(f"{now.minute:02d}")
		sizer.Add(self.cb_minute, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 5)
		
		# 3. Dropdown Detik
		sizer.Add(wx.StaticText(self, label="&Detik (00 - 59):"), 0, wx.ALL, 5)
		seconds = [f"{s:02d}" for s in range(60)]
		self.cb_second = wx.ComboBox(self, choices=seconds, style=wx.CB_READONLY)
		self.cb_second.SetName("Detik (00 - 59):")
		self.cb_second.SetToolTip("Detik (00 - 59):")
		self.cb_second.SetValue("00")
		sizer.Add(self.cb_second, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 5)
		
		# 4. Mode Alarm / Snooze
		sizer.Add(wx.StaticText(self, label="&Fitur Mode Alarm & Snooze:"), 0, wx.ALL, 5)
		alarm_modes = [
			"Alarm Jam Weker (Berdering Berulang + Fitur Tunda / Snooze 10m)",
			"Pemberitahuan Singkat (Sekali Bunyi / Chime)"
		]
		self.cb_alarm_mode = wx.ComboBox(self, choices=alarm_modes, style=wx.CB_READONLY)
		self.cb_alarm_mode.SetName("Fitur Mode Alarm  Snooze:")
		self.cb_alarm_mode.SetToolTip("Fitur Mode Alarm  Snooze:")
		self.cb_alarm_mode.SetSelection(0)
		sizer.Add(self.cb_alarm_mode, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 5)
		
		# 5. Suara Audio & Tombol Tes
		sizer.Add(wx.StaticText(self, label="&Suara Alarm:"), 0, wx.ALL, 5)
		audio_sizer = wx.BoxSizer(wx.HORIZONTAL)
		self.audio_files_map = []
		audio_choices = []
		std_items = [
			("wind-up-clock-alarm-bell.mp3", "wind-up-clock-alarm-bell.mp3 (Alarm Jam Weker)"),
			("alarm.wav", "alarm.wav (Alarm Nada Dering)"),
			("chime.wav", "chime.wav (Chime Lembut)"),
			("bell.wav", "bell.wav (Bel Singkat)")
		]
		for filename, label in std_items:
			self.audio_files_map.append(filename)
			audio_choices.append(label)
		if audio_manager and hasattr(audio_manager, "get_sound_path"):
			try:
				import os
				s_dir = os.path.join(os.path.dirname(__file__), "sounds")
				if os.path.exists(s_dir):
					for f in sorted(os.listdir(s_dir)):
						if f.lower().endswith(('.wav', '.mp3')) and f not in self.audio_files_map:
							self.audio_files_map.append(f)
							audio_choices.append(f)
			except Exception:
				pass
		self.cb_audio = wx.ComboBox(self, choices=audio_choices, style=wx.CB_READONLY)
		if self.cb_audio.GetCount() > 0:
			self.cb_audio.SetSelection(0)
		audio_sizer.Add(self.cb_audio, 1, wx.EXPAND | wx.RIGHT, 5)
		
		self.btnTestSound = wx.Button(self, label="&Tes Suara (Alt+T)")
		self.btnTestSound.Bind(wx.EVT_BUTTON, self.onTestSound)
		audio_sizer.Add(self.btnTestSound, 0)
		sizer.Add(audio_sizer, 0, wx.EXPAND | wx.ALL, 5)
		
		# Buttons
		btnSizer = wx.StdDialogButtonSizer()
		self.btnOk = wx.Button(self, wx.ID_OK, label="&Pasang Alarm")
		self.btnCancel = wx.Button(self, wx.ID_CANCEL, label="&Batal")
		self.btnHelp = wx.Button(self, label="&Bantuan... (Alt+B)")
		self.btnHelp.Bind(wx.EVT_BUTTON, self.onContextualHelp)
		btnSizer.AddButton(self.btnOk)
		btnSizer.AddButton(self.btnCancel)
		btnSizer.AddButton(self.btnHelp)
		btnSizer.Realize()
		sizer.Add(btnSizer, 0, wx.ALIGN_RIGHT | wx.ALL, 15)
		
		self.SetSizer(sizer)
		self.Centre()
		self.cb_hour.SetFocus()

	def onContextualHelp(self, evt):
		text = "BANTUAN ALARM SEKALI PAKAI:\n\n- Fitur ini berguna untuk menyetel weker (alarm berdering terus-menerus) pada jam dan menit tertentu hari ini.\n- Anda dapat Menjeda (Pause) alarm sebelum waktunya tiba.\n- Jika alarm sedang berdering, tekan Spasi untuk mematikan atau Z untuk menunda (Snooze 10 menit)."
		dlg = ContextualHelpDialog(self, "Bantuan: Alarm Sekali Pakai", text)
		dlg.ShowModal()
		dlg.Destroy()

	def onTestSound(self, event):
		if not self.audio_manager:
			return
		if getattr(self, "_is_test_playing", False) or "Hentikan" in self.btnTestSound.GetLabel():
			self.audio_manager.stop_sound()
			self.btnTestSound.SetLabel("&Tes Suara (Alt+T)")
			self._is_test_playing = False
			if hasattr(self, "_test_timer"):
				self._test_timer.Stop()
			ui.message("Suara tes dihentikan.")
			return

		sel = self.cb_audio.GetSelection()
		if 0 <= sel < len(self.audio_files_map) and self.audio_files_map[sel]:
			audio_file = self.audio_files_map[sel]
			ui.message(f"Memutar tes suara: {audio_file}")
			self.btnTestSound.SetLabel("&Hentikan Suara Tes (Alt+T)")
			self._is_test_playing = True
			self.audio_manager.play_sound(audio_file)
			if not hasattr(self, "_test_timer"):
				self._test_timer = wx.Timer(self)
				self.Bind(wx.EVT_TIMER, self._onCheckTestStatus, self._test_timer)
			self._test_timer.Start(250)

	def _onCheckTestStatus(self, event):
		if not self.audio_manager or not self.audio_manager.has_active_sounds():
			self.btnTestSound.SetLabel("&Tes Suara (Alt+T)")
			self._is_test_playing = False
			if hasattr(self, "_test_timer"):
				self._test_timer.Stop()

	def get_result(self):
		sel = self.cb_audio.GetSelection()
		audio_file = self.audio_files_map[sel] if 0 <= sel < len(self.audio_files_map) else "alarm.wav"
		is_alarm_sel = (self.cb_alarm_mode.GetSelection() == 0)
		return {
			"hour": int(self.cb_hour.GetValue()),
			"minute": int(self.cb_minute.GetValue()),
			"second": int(self.cb_second.GetValue()),
			"audio_file": audio_file,
			"is_alarm": is_alarm_sel,
			"alarm_mode": self.cb_alarm_mode.GetValue()
		}


class TTSManagerDialog(wx.Dialog):
	def __init__(self, parent, tts_manager, config_manager):
		super().__init__(parent, title="Pengaturan Suara TTS Mandiri (Notifikasi Latar Belakang)", size=(540, 460), style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)
		self.tts_manager = tts_manager
		self.config = config_manager
		self.cfg = self.config.get_tts_config() if self.config else {}
		
		sizer = wx.BoxSizer(wx.VERTICAL)
		
		# Checkbox Aktif
		self.chk_enabled = wx.CheckBox(self, label="&Aktifkan Suara TTS Mandiri Terpisah untuk Notifikasi Latar Belakang")
		self.chk_enabled.SetValue(self.cfg.get("enabled", False))
		sizer.Add(self.chk_enabled, 0, wx.ALL, 10)
		
		# Daftar Suara
		sizer.Add(wx.StaticText(self, label="&Pilih Suara / Mesin SAPI 5:"), 0, wx.ALL, 5)
		self.voices_list = self.tts_manager.get_available_voices() if self.tts_manager else []
		choices = [v["name"] for v in self.voices_list]
		if not choices:
			choices = ["(Suara SAPI 5 tidak ditemukan / tidak tersedia)"]
			self.voices_list = [{"id": 0, "name": choices[0]}]
		
		self.cb_voices = wx.ComboBox(self, choices=choices, style=wx.CB_READONLY)
		self.cb_voices.SetName("Pilih Suara / Mesin SAPI 5:")
		self.cb_voices.SetToolTip("Pilih Suara / Mesin SAPI 5:")
		cur_id = int(self.cfg.get("voice_id", 0))
		found_idx = 0
		for idx, v in enumerate(self.voices_list):
			if v["id"] == cur_id:
				found_idx = idx
				break
		self.cb_voices.SetSelection(found_idx)
		sizer.Add(self.cb_voices, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 5)
		
		# Slider Rate (Kecepatan)
		sizer.Add(wx.StaticText(self, label="&Kecepatan Pengucapan (Rate: -10 lambat s/d +10 cepat):"), 0, wx.ALL, 5)
		self.slider_rate = wx.Slider(self, value=int(self.cfg.get("rate", 0)), minValue=-10, maxValue=10, style=wx.SL_HORIZONTAL | wx.SL_AUTOTICKS)
		self.slider_rate.SetName("Kecepatan Pengucapan (Rate: -10 lambat s/d +10 cepat):")
		self.slider_rate.SetToolTip("Kecepatan Pengucapan (Rate: -10 lambat s/d +10 cepat):")
		sizer.Add(self.slider_rate, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 5)
		
		# Slider Volume
		sizer.Add(wx.StaticText(self, label="&Volume Suara TTS (0% s/d 100%):"), 0, wx.ALL, 5)
		self.slider_volume = wx.Slider(self, value=int(self.cfg.get("volume", 100)), minValue=0, maxValue=100, style=wx.SL_HORIZONTAL | wx.SL_AUTOTICKS)
		self.slider_volume.SetName("Volume Suara TTS (0% s/d 100%):")
		self.slider_volume.SetToolTip("Volume Suara TTS (0% s/d 100%):")
		sizer.Add(self.slider_volume, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 5)
		
		# Tombol Tes Suara
		self.btnTest = wx.Button(self, label="&Tes Suara TTS Mandiri")
		self.btnTest.Bind(wx.EVT_BUTTON, self.onTest)
		sizer.Add(self.btnTest, 0, wx.ALL | wx.ALIGN_CENTER_HORIZONTAL, 10)
		
		# Buttons Simpan & Batal
		btnSizer = wx.StdDialogButtonSizer()
		self.btnOk = wx.Button(self, wx.ID_OK, label="&Simpan")
		self.btnCancel = wx.Button(self, wx.ID_CANCEL, label="&Batal")
		self.btnHelp = wx.Button(self, label="&Bantuan... (Alt+B)")
		self.btnHelp.Bind(wx.EVT_BUTTON, self.onContextualHelp)
		btnSizer.AddButton(self.btnOk)
		btnSizer.AddButton(self.btnCancel)
		btnSizer.AddButton(self.btnHelp)
		btnSizer.Realize()
		sizer.Add(btnSizer, 0, wx.ALIGN_RIGHT | wx.ALL, 15)
		
		self.SetSizer(sizer)
		self.Centre()
		self.chk_enabled.SetFocus()

	def onContextualHelp(self, evt):
		text = "BANTUAN MESIN TTS MANDIRI:\n\n- JadwalKu dapat membacakan notifikasi suara latar belakang menggunakan SAPI5 (suara bawaan Windows) alih-alih suara synthesizer NVDA.\n- Ini memungkinkan suara NVDA dan suara JadwalKu menjadi berbeda.\n- Anda dapat mengatur kecepatan (Rate) dan volume khusus untuk TTS JadwalKu."
		dlg = ContextualHelpDialog(self, "Bantuan: TTS Manager", text)
		dlg.ShowModal()
		dlg.Destroy()

	def onTest(self, event):
		if not self.tts_manager:
			return
		sel = self.cb_voices.GetSelection()
		v_id = self.voices_list[sel]["id"] if sel >= 0 and sel < len(self.voices_list) else 0
		rate = self.slider_rate.GetValue()
		vol = self.slider_volume.GetValue()
		self.tts_manager.test_voice(v_id, rate, vol)

	def get_result(self):
		sel = self.cb_voices.GetSelection()
		v_id = self.voices_list[sel]["id"] if sel >= 0 and sel < len(self.voices_list) else 0
		v_name = self.voices_list[sel]["name"] if sel >= 0 and sel < len(self.voices_list) else ""
		return {
			"enabled": self.chk_enabled.GetValue(),
			"voice_id": v_id,
			"voice_name": v_name,
			"rate": self.slider_rate.GetValue(),
			"volume": self.slider_volume.GetValue()
		}


class TimeReminderDialog(wx.Dialog):
	def __init__(self, parent, time_config=None, tts_manager=None, config_manager=None):
		super().__init__(parent, title="Pengaturan Pengingat Waktu Berkala (Time Reminder)", size=(520, 460), style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)
		self.cfg = time_config or {}
		self.tts_manager = tts_manager
		self.config = config_manager
		
		sizer = wx.BoxSizer(wx.VERTICAL)
		
		# Checkbox Aktif
		self.chk_enabled = wx.CheckBox(self, label="&Aktifkan Pengingat Waktu Berkala")
		self.chk_enabled.SetValue(self.cfg.get("enabled", False))
		sizer.Add(self.chk_enabled, 0, wx.ALL, 10)
		
		# Interval
		sizer.Add(wx.StaticText(self, label="&Interval Waktu Pengingat:"), 0, wx.ALL, 5)
		interval_map = [
			("5 menit sekali", 5),
			("10 menit sekali", 10),
			("15 menit sekali", 15),
			("30 menit sekali", 30),
			("1 jam sekali (Setiap Jam)", 60)
		]
		self.interval_values = [v for k, v in interval_map]
		self.cb_interval = wx.ComboBox(self, choices=[k for k, v in interval_map], style=wx.CB_READONLY)
		self.cb_interval.SetName("Interval Waktu Pengingat:")
		self.cb_interval.SetToolTip("Interval Waktu Pengingat:")
		cur_val = int(self.cfg.get("interval", 60))
		if cur_val in self.interval_values:
			self.cb_interval.SetSelection(self.interval_values.index(cur_val))
		else:
			self.cb_interval.SetSelection(4) # Default 60 menit
		sizer.Add(self.cb_interval, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 5)
		
		# Mode Suara
		sizer.Add(wx.StaticText(self, label="&Mode Notifikasi Waktu:"), 0, wx.ALL, 5)
		mode_choices = [
			("Bicara Waktu via NVDA & Putar Chime", "both"),
			("Hanya Bicara Waktu via NVDA", "speech"),
			("Hanya Putar Suara Chime", "audio")
		]
		self.mode_values = [v for k, v in mode_choices]
		self.cb_mode = wx.ComboBox(self, choices=[k for k, v in mode_choices], style=wx.CB_READONLY)
		self.cb_mode.SetName("Mode Notifikasi Waktu:")
		self.cb_mode.SetToolTip("Mode Notifikasi Waktu:")
		cur_mode = self.cfg.get("mode", "both")
		if cur_mode in self.mode_values:
			self.cb_mode.SetSelection(self.mode_values.index(cur_mode))
		else:
			self.cb_mode.SetSelection(0)
		sizer.Add(self.cb_mode, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 5)
		
		# Gaya Pengucapan Waktu
		sizer.Add(wx.StaticText(self, label="&Gaya Pengucapan Waktu Pengingat:"), 0, wx.ALL, 5)
		speech_style_choices = [
			("Sekarang jam [Jam]:[Menit] (Contoh: Sekarang jam 09:00 tepat / Sekarang jam 09:15)", "default"),
			("Mengikuti format & gaya pengucapan NVDA+F12", "follow_f12"),
			("[Jam]:[Menit] waktu sekarang (Contoh: 09:00 waktu sekarang)", "waktu_sekarang"),
			("Hanya [Jam]:[Menit] (Contoh: 09:00 atau 09:00 AM)", "only_time"),
			("Waktu sekarang pukul [Jam]:[Menit] (Contoh: Waktu sekarang pukul 09:00)", "prefix_pukul"),
			("Pukul [Jam]:[Menit] tepat (Contoh: Pukul 09:00 tepat / Pukul 09:15)", "pukul_tepat"),
			("Jam [Jam] lewat [Menit] menit (Contoh: Jam 09 lewat 15 menit)", "jam_lewat_menit"),
			("Jam [Jam] lewat [Menit] menit [Detik] detik (Contoh: Jam 09 lewat 15 menit 30 detik)", "jam_lewat_menit_detik")
		]
		self.speech_style_values = [v for k, v in speech_style_choices]
		self.cb_speech_style = wx.ComboBox(self, choices=[k for k, v in speech_style_choices], style=wx.CB_READONLY)
		self.cb_speech_style.SetName("Gaya Pengucapan Waktu Pengingat:")
		self.cb_speech_style.SetToolTip("Gaya Pengucapan Waktu Pengingat:")
		cur_style = self.cfg.get("speech_style", "default")
		if cur_style in self.speech_style_values:
			self.cb_speech_style.SetSelection(self.speech_style_values.index(cur_style))
		else:
			self.cb_speech_style.SetSelection(0)
		sizer.Add(self.cb_speech_style, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 5)
		
		# Format Jam Pengingat (12 / 24 Jam)
		sizer.Add(wx.StaticText(self, label="&Format Jam Pengingat (12/24 Jam):"), 0, wx.ALL, 5)
		format_choices = [
			("24 Jam (Contoh: 14:00 atau 16:30)", "24"),
			("12 Jam AM/PM (Contoh: 02:00 PM atau 04:30 PM)", "12"),
			("Mengikuti Format Jam NVDA+F12", "follow_f12")
		]
		self.format_values = [v for k, v in format_choices]
		self.cb_time_format = wx.ComboBox(self, choices=[k for k, v in format_choices], style=wx.CB_READONLY)
		self.cb_time_format.SetName("Format Jam Pengingat (12/24 Jam):")
		self.cb_time_format.SetToolTip("Format Jam Pengingat (12/24 Jam):")
		cur_fmt = self.cfg.get("time_format", "24")
		if cur_fmt in self.format_values:
			self.cb_time_format.SetSelection(self.format_values.index(cur_fmt))
		else:
			self.cb_time_format.SetSelection(0)
		sizer.Add(self.cb_time_format, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 5)
		
		# Jam Mulai & Jam Selesai
		time_sizer = wx.BoxSizer(wx.HORIZONTAL)
		hours_start = [f"{i:02d}:00" for i in range(24)]
		hours_end = [f"{i:02d}:00" for i in range(24)] + ["23:59 (Sepanjang Hari / 24 Jam)"]
		
		time_sizer.Add(wx.StaticText(self, label="Jam &Mulai Aktif:"), 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)
		self.cb_start = wx.ComboBox(self, choices=hours_start, style=wx.CB_READONLY)
		self.cb_start.SetName("Jam Mulai Aktif:")
		self.cb_start.SetToolTip("Jam Mulai Aktif:")
		cur_start = int(self.cfg.get("start_hour", 0))
		self.cb_start.SetSelection(cur_start if 0 <= cur_start <= 23 else 0)
		time_sizer.Add(self.cb_start, 0, wx.ALL, 5)
		
		time_sizer.Add(wx.StaticText(self, label="Jam &Selesai Aktif:"), 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)
		self.cb_end = wx.ComboBox(self, choices=hours_end, style=wx.CB_READONLY)
		self.cb_end.SetName("Jam Selesai Aktif:")
		self.cb_end.SetToolTip("Jam Selesai Aktif:")
		cur_end = int(self.cfg.get("end_hour", 24))
		self.cb_end.SetSelection(cur_end if 0 <= cur_end <= 24 else 24)
		time_sizer.Add(self.cb_end, 0, wx.ALL, 5)
		sizer.Add(time_sizer, 0, wx.ALL, 5)
		
		# Tombol Pengaturan Suara TTS Mandiri
		self.btnOpenTTS = wx.Button(self, label="&Pengaturan Suara TTS Mandiri (Notifikasi Latar)...")
		self.btnOpenTTS.Bind(wx.EVT_BUTTON, self.onOpenTTS)
		sizer.Add(self.btnOpenTTS, 0, wx.ALL | wx.ALIGN_LEFT, 10)
		
		# Buttons
		btnSizer = wx.StdDialogButtonSizer()
		self.btnOk = wx.Button(self, wx.ID_OK, label="&Simpan")
		self.btnCancel = wx.Button(self, wx.ID_CANCEL, label="&Batal")
		self.btnHelp = wx.Button(self, label="&Bantuan... (Alt+B)")
		self.btnHelp.Bind(wx.EVT_BUTTON, self.onContextualHelp)
		btnSizer.AddButton(self.btnOk)
		btnSizer.AddButton(self.btnCancel)
		btnSizer.AddButton(self.btnHelp)
		btnSizer.Realize()
		sizer.Add(btnSizer, 0, wx.ALIGN_RIGHT | wx.ALL, 15)
		
		self.SetSizer(sizer)
		self.Centre()
		self.chk_enabled.SetFocus()

	def onOpenTTS(self, event):
		if self.tts_manager and self.config:
			dlg = TTSManagerDialog(self, self.tts_manager, self.config)
			if dlg.ShowModal() == wx.ID_OK:
				self.config.update_tts_config(dlg.get_result())
				status = "Aktif" if dlg.get_result()["enabled"] else "Nonaktif"
				ui.message(f"Pengaturan TTS Mandiri berhasil disimpan ({status}).")
			dlg.Destroy()
		else:
			ui.message("Fitur TTS Mandiri tidak tersedia.")

	def onContextualHelp(self, evt):
		text = "BANTUAN PENGINGAT WAKTU BERKALA:\n\n- Fitur ini membuat JadwalKu berbunyi (chime) secara otomatis setiap jam.\n- Anda bisa memilih untuk tidak membunyikan pengingat pada jam istirahat (misal: 23:00 - 05:00) agar tidur Anda tidak terganggu.\n- Anda juga bisa memilih suara bel kustom (chime) dan memutuskan apakah JadwalKu harus membacakan waktu secara lisan."
		dlg = ContextualHelpDialog(self, "Bantuan: Pengingat Waktu Berkala", text)
		dlg.ShowModal()
		dlg.Destroy()

	def get_result(self):
		idx_int = self.cb_interval.GetSelection()
		idx_mod = self.cb_mode.GetSelection()
		idx_stl = self.cb_speech_style.GetSelection()
		idx_fmt = self.cb_time_format.GetSelection()
		return {
			"enabled": self.chk_enabled.GetValue(),
			"interval": self.interval_values[idx_int if idx_int >= 0 else 4],
			"mode": self.mode_values[idx_mod if idx_mod >= 0 else 0],
			"speech_style": self.speech_style_values[idx_stl if idx_stl >= 0 else 0],
			"time_format": self.format_values[idx_fmt if idx_fmt >= 0 else 0],
			"start_hour": self.cb_start.GetSelection(),
			"end_hour": self.cb_end.GetSelection(),
			"last_triggered_minute": self.cfg.get("last_triggered_minute", "")
		}


class JadwalKuDialog(wx.Dialog):
	def __init__(self, parent, config_manager, audio_manager, updater=None, tts_manager=None):
		super().__init__(parent, title="JadwalKu - Manajemen Agenda & Pengingat", size=(680, 520), style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)
		self.config = config_manager
		self.audio = audio_manager
		self.updater = updater
		self.tts_manager = tts_manager
		
		main_sizer = wx.BoxSizer(wx.VERTICAL)
		
		self.notebook = wx.Notebook(self)
		
		# ==================== TAB 1: MANAJEMEN AGENDA & JADWAL ====================
		self.panel_tab1 = wx.Panel(self.notebook)
		sizer_tab1 = wx.BoxSizer(wx.VERTICAL)
		
		sizer_tab1.Add(wx.StaticText(self.panel_tab1, label="Daftar Agenda JadwalKu (Tekan Spasi untuk Check/Uncheck, Shift+Tab ke Tab):"), 0, wx.ALL, 8)
		
		self.listBox = wx.ListBox(self.panel_tab1, style=wx.LB_SINGLE)
		self.listBox.Bind(wx.EVT_KEY_DOWN, self.onListKeyDown)
		self.listBox.Bind(wx.EVT_LISTBOX_DCLICK, self.onEdit)
		sizer_tab1.Add(self.listBox, 1, wx.EXPAND | wx.LEFT | wx.RIGHT, 8)
		
		btnSizer1 = wx.BoxSizer(wx.HORIZONTAL)
		self.btnAdd = wx.Button(self.panel_tab1, label="&Tambah Jadwal Baru...")
		self.btnAdd.Bind(wx.EVT_BUTTON, self.onAdd)
		btnSizer1.Add(self.btnAdd, 0, wx.ALL, 4)
		
		self.btnEdit = wx.Button(self.panel_tab1, label="&Edit Jadwal...")
		self.btnEdit.Bind(wx.EVT_BUTTON, self.onEdit)
		btnSizer1.Add(self.btnEdit, 0, wx.ALL, 4)
		
		self.btnDel = wx.Button(self.panel_tab1, label="&Hapus Jadwal")
		self.btnDel.Bind(wx.EVT_BUTTON, self.onDelete)
		btnSizer1.Add(self.btnDel, 0, wx.ALL, 4)
		
		self.btnToggle = wx.Button(self.panel_tab1, label="&Check / Uncheck Status")
		self.btnToggle.Bind(wx.EVT_BUTTON, self.onToggleActive)
		btnSizer1.Add(self.btnToggle, 0, wx.ALL, 4)
		sizer_tab1.Add(btnSizer1, 0, wx.ALIGN_LEFT | wx.LEFT | wx.RIGHT | wx.TOP, 4)
		
		btnSizer2 = wx.BoxSizer(wx.HORIZONTAL)
		self.btnTimeRemind = wx.Button(self.panel_tab1, label="&Pengaturan Pengingat Waktu Berkala...")
		self.btnTimeRemind.Bind(wx.EVT_BUTTON, self.onTimeReminder)
		btnSizer2.Add(self.btnTimeRemind, 0, wx.ALL, 4)
		
		self.btnLonceng = wx.Button(self.panel_tab1, label="&Pengingat Lonceng (Grandfather Clock)...")
		self.btnLonceng.Bind(wx.EVT_BUTTON, self.onLonceng)
		btnSizer2.Add(self.btnLonceng, 0, wx.ALL, 4)
		
		self.btnAudio = wx.Button(self.panel_tab1, label="Pengaturan &Audio Manager (Speaker)...")
		self.btnAudio.Bind(wx.EVT_BUTTON, self.onAudioManager)
		btnSizer2.Add(self.btnAudio, 0, wx.ALL, 4)
		
		self.btnHelp = wx.Button(self.panel_tab1, label="&Bantuan...")
		self.btnHelp.Bind(wx.EVT_BUTTON, self.onHelp)
		btnSizer2.Add(self.btnHelp, 0, wx.ALL, 4)
		
		if self.updater:
			self.btnCheckUp = wx.Button(self.panel_tab1, label="&Cek Pembaruan...")
			self.btnCheckUp.Bind(wx.EVT_BUTTON, self.onCheckUpdate)
			btnSizer2.Add(self.btnCheckUp, 0, wx.ALL, 4)
		
		sizer_tab1.Add(btnSizer2, 0, wx.ALIGN_LEFT | wx.LEFT | wx.RIGHT | wx.BOTTOM, 8)
		
		self.panel_tab1.SetSizer(sizer_tab1)
		
		# ==================== TAB 2: PENGATURAN WAKTU & KALENDER JADWALKU ====================
		self.panel_tab2 = wx.Panel(self.notebook)
		sizer_tab2 = wx.BoxSizer(wx.VERTICAL)
		
		time_cfg = self.config.get_time_settings()
		
		sizer_tab2.Add(wx.StaticText(self.panel_tab2, label="=== 1. Pengaturan Pelaporan Waktu (Tekan NVDA+F12 1x / NVDA+/, W) ==="), 0, wx.ALL, 6)
		
		self.chk_override_f12 = wx.CheckBox(self.panel_tab2, label="&Aktifkan Penggantian Pelaporan Waktu & Tanggal NVDA (NVDA + F12)")
		self.chk_override_f12.SetValue(time_cfg.get("override_nvda_f12", True))
		sizer_tab2.Add(self.chk_override_f12, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 6)
		
		fmt_sizer = wx.BoxSizer(wx.HORIZONTAL)
		fmt_sizer.Add(wx.StaticText(self.panel_tab2, label="&Format Jam:"), 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 4)
		fmt_choices = ["24 Jam (00:00 - 23:59)", "12 Jam (01:00 AM - 12:59 PM)"]
		self.cb_time_format = wx.ComboBox(self.panel_tab2, choices=fmt_choices, style=wx.CB_READONLY)
		self.cb_time_format.SetName("Format Jam:")
		self.cb_time_format.SetToolTip("Format Jam:")
		if time_cfg.get("time_format", "24") == "12":
			self.cb_time_format.SetSelection(1)
		else:
			self.cb_time_format.SetSelection(0)
		fmt_sizer.Add(self.cb_time_format, 0, wx.ALL, 4)
		sizer_tab2.Add(fmt_sizer, 0, wx.LEFT | wx.RIGHT, 6)
		
		sizer_tab2.Add(wx.StaticText(self.panel_tab2, label="&Gaya Pengucapan Waktu (Tekan NVDA+F12 1x atau NVDA+/, W):"), 0, wx.LEFT | wx.TOP, 6)
		time_style_choices = [
			"[Jam]:[Menit] waktu sekarang (Contoh: 09:15 waktu sekarang)",
			"Hanya [Jam]:[Menit] (Contoh: 09:15 atau 09:15 AM)",
			"Waktu sekarang pukul [Jam]:[Menit] (Contoh: Waktu sekarang pukul 09:15)",
			"Pukul [Jam]:[Menit] lewat [Detik] detik (Contoh: Pukul 09:15 lewat 30 detik)",
			"Waktu sekarang pukul [Jam]:[Menit]:[Detik] (Contoh: Waktu sekarang pukul 09:15:30)",
			"Jam [Jam] lewat [Menit] menit (Contoh: Jam 09 lewat 15 menit)",
			"Jam [Jam] lewat [Menit] menit [Detik] detik (Contoh: Jam 09 lewat 15 menit 30 detik)"
		]
		self.cb_time_speech_style = wx.ComboBox(self.panel_tab2, choices=time_style_choices, style=wx.CB_READONLY)
		self.cb_time_speech_style.SetName("Gaya Pengucapan Waktu (Tekan NVDA+F12 1x atau NVDA+/, W):")
		self.cb_time_speech_style.SetToolTip("Gaya Pengucapan Waktu (Tekan NVDA+F12 1x atau NVDA+/, W):")
		style_map = {"default": 0, "only_time": 1, "prefix_pukul": 2, "with_seconds": 3, "full_seconds": 4, "jam_lewat_menit": 5, "jam_lewat_menit_detik": 6}
		self.cb_time_speech_style.SetSelection(style_map.get(time_cfg.get("time_speech_style", "default"), 0))
		sizer_tab2.Add(self.cb_time_speech_style, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 6)
		
		self.chk_time_seconds = wx.CheckBox(self.panel_tab2, label="Sertakan bacaan &Detik pada pelaporan waktu standar")
		self.chk_time_seconds.SetValue(time_cfg.get("include_seconds", False))
		sizer_tab2.Add(self.chk_time_seconds, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 8)
		
		sizer_tab2.Add(wx.StaticText(self.panel_tab2, label="=== 2. Pengaturan Pelaporan Tanggal & Kalender (Tekan NVDA+F12 2x & 3x) ==="), 0, wx.LEFT | wx.TOP, 6)
		
		sizer_tab2.Add(wx.StaticText(self.panel_tab2, label="&Gaya Pengucapan Tanggal (Tekan NVDA+F12 2x):"), 0, wx.LEFT | wx.TOP, 6)
		date_style_choices = [
			"[Hari], [Tanggal] [Bulan] [Tahun] (Contoh: Kamis, 16 Juli 2026)",
			"Hari [Hari], tanggal [Tanggal] bulan [Bulan] tahun [Tahun]",
			"[Tanggal]/[Bulan Angka]/[Tahun] (Contoh: 16/07/2026)",
			"Tanggal [Tanggal] [Bulan] [Tahun] hari [Hari]"
		]
		self.cb_date_speech_style = wx.ComboBox(self.panel_tab2, choices=date_style_choices, style=wx.CB_READONLY)
		self.cb_date_speech_style.SetName("Gaya Pengucapan Tanggal (Tekan NVDA+F12 2x):")
		self.cb_date_speech_style.SetToolTip("Gaya Pengucapan Tanggal (Tekan NVDA+F12 2x):")
		date_style_map = {"default": 0, "prefix_hari": 1, "numeric": 2, "suffix_hari": 3}
		self.cb_date_speech_style.SetSelection(date_style_map.get(time_cfg.get("date_speech_style", "default"), 0))
		sizer_tab2.Add(self.cb_date_speech_style, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 6)
		
		sizer_tab2.Add(wx.StaticText(self.panel_tab2, label="&Gaya Pengucapan Lengkap & Akhir Tahun (Tekan NVDA+F12 3x):"), 0, wx.LEFT | wx.TOP, 6)
		full_style_choices = [
			"Lengkap dengan sisa hari & jam menuju akhir tahun (Contoh: Kamis, 16 Juli 2026, pukul 09:15. Sisa waktu menuju akhir tahun: 168 hari 14 jam lagi)",
			"Ringkas: Tanggal, waktu, dan sisa hari akhir tahun (Contoh: 16 Juli 2026 09:15. Akhir tahun kurang 168 hari)"
		]
		self.cb_full_speech_style = wx.ComboBox(self.panel_tab2, choices=full_style_choices, style=wx.CB_READONLY)
		self.cb_full_speech_style.SetName("Gaya Pengucapan Lengkap  Akhir Tahun (Tekan NVDA+F12 3x):")
		self.cb_full_speech_style.SetToolTip("Gaya Pengucapan Lengkap  Akhir Tahun (Tekan NVDA+F12 3x):")
		full_style_map = {"default": 0, "short": 1}
		self.cb_full_speech_style.SetSelection(full_style_map.get(time_cfg.get("full_speech_style", "default"), 0))
		sizer_tab2.Add(self.cb_full_speech_style, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)
		
		sizer_tab2.Add(wx.StaticText(self.panel_tab2, label="=== 3. Fitur Kalender & Jam Dunia ==="), 0, wx.LEFT | wx.TOP, 6)
		btnSizerTab2 = wx.BoxSizer(wx.HORIZONTAL)
		
		self.btnOpenCal = wx.Button(self.panel_tab2, label="&Lihat Kalender & Tanggal Merah (NVDA+/, K)...")
		self.btnOpenCal.Bind(wx.EVT_BUTTON, self.onOpenCalendar)
		btnSizerTab2.Add(self.btnOpenCal, 0, wx.ALL, 4)
		
		self.btnOpenWorld = wx.Button(self.panel_tab2, label="&Buka Jam Dunia & Konversi (NVDA+/, D)...")
		self.btnOpenWorld.Bind(wx.EVT_BUTTON, self.onOpenWorldClock)
		btnSizerTab2.Add(self.btnOpenWorld, 0, wx.ALL, 4)
		
		self.btnOpenTTS = wx.Button(self.panel_tab2, label="&Pengaturan Suara TTS Mandiri (NVDA+/, M)...")
		self.btnOpenTTS.Bind(wx.EVT_BUTTON, self.onOpenTTSManager)
		btnSizerTab2.Add(self.btnOpenTTS, 0, wx.ALL, 4)
		
		self.btnSaveTimeCfg = wx.Button(self.panel_tab2, label="&Simpan Pengaturan Waktu")
		self.btnSaveTimeCfg.Bind(wx.EVT_BUTTON, self.onSaveTimeSettings)
		btnSizerTab2.Add(self.btnSaveTimeCfg, 0, wx.ALL, 4)
		
		sizer_tab2.Add(btnSizerTab2, 0, wx.ALIGN_LEFT | wx.ALL, 6)
		self.panel_tab2.SetSizer(sizer_tab2)
		
		self.notebook.AddPage(self.panel_tab1, "1. Manajemen Agenda & Jadwal")
		self.notebook.AddPage(self.panel_tab2, "2. Pengaturan Waktu & Kalender JadwalKu")
		
		# --- Tab 3: Voice Pack Studio ---
		self.panel_tab3 = wx.Panel(self.notebook)
		sizer_tab3 = wx.BoxSizer(wx.VERTICAL)
		
		info_vp = wx.StaticText(self.panel_tab3, label="JadwalKu Voice Pack Studio memandu Anda merekam 70 kata kustom untuk dijadikan pengingat waktu tanpa bergantung pada TTS.\nAnda dapat membuat rekaman Anda sendiri dan membagikannya dalam format .jvp")
		sizer_tab3.Add(info_vp, 0, wx.ALL, 10)
		
		# Pilihan Voice Pack Aktif
		vp_hz_sizer = wx.BoxSizer(wx.HORIZONTAL)
		vp_hz_sizer.Add(wx.StaticText(self.panel_tab3, label="Paket Suara (&Voice Pack) Aktif:"), 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)
		
		from .voicePackManager import VoicePackManager
		add_on_dir = os.path.dirname(os.path.abspath(__file__))
		self.vp_mgr = VoicePackManager(add_on_dir)
		self.vp_list = [p for p in self.vp_mgr.get_available_packs() if not p.get("is_draft")]
		choices = ["(Bawaan SAPI 5 / TTS Standar)"] + [p["name"] for p in self.vp_list]
		
		self.cb_active_vp = wx.ComboBox(self.panel_tab3, choices=choices, style=wx.CB_READONLY)
		self.cb_active_vp.SetName("Paket Suara (Voice Pack) Aktif:")
		self.cb_active_vp.SetToolTip("Paket Suara (Voice Pack) Aktif:")
		# Load from config
		active_vp_file = self.config.get_time_reminder_config().get("active_voice_pack", "")
		sel_idx = 0
		for i, p in enumerate(self.vp_list):
			if p["id"] == active_vp_file:
				sel_idx = i + 1
				break
		self.cb_active_vp.SetSelection(sel_idx)
		self.cb_active_vp.Bind(wx.EVT_COMBOBOX, self.onVoicePackChanged)
		vp_hz_sizer.Add(self.cb_active_vp, 1, wx.EXPAND | wx.ALL, 5)
		
		sizer_tab3.Add(vp_hz_sizer, 0, wx.EXPAND | wx.ALL, 5)
		
		# Slider Volume Khusus Voice Pack
		vp_vol_sizer = wx.BoxSizer(wx.HORIZONTAL)
		vp_vol_sizer.Add(wx.StaticText(self.panel_tab3, label="Volume Voice Pack Kustom (0 - 1200%):"), 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)
		vp_vol_val = self.config.get_time_reminder_config().get("voice_pack_volume", 100)
		self.sld_vp_vol = wx.Slider(self.panel_tab3, value=vp_vol_val, minValue=0, maxValue=1200, style=wx.SL_HORIZONTAL | wx.SL_AUTOTICKS)
		self.sld_vp_vol.SetName("Volume Voice Pack Kustom (0 - 1200%):")
		self.sld_vp_vol.SetToolTip("Volume Voice Pack Kustom (0 - 1200%):")
		self.sld_vp_vol.Bind(wx.EVT_SLIDER, self.onVoicePackVolumeChanged)
		vp_vol_sizer.Add(self.sld_vp_vol, 1, wx.EXPAND | wx.ALL, 5)
		sizer_tab3.Add(vp_vol_sizer, 0, wx.EXPAND | wx.ALL, 5)
		
		self.btnOpenVoiceStudio = wx.Button(self.panel_tab3, label="Buka &Studio Rekaman Suara JadwalKu...")
		self.btnOpenVoiceStudio.Bind(wx.EVT_BUTTON, self.onOpenVoiceStudio)
		sizer_tab3.Add(self.btnOpenVoiceStudio, 0, wx.ALL | wx.ALIGN_LEFT, 10)
		
		self.btnOpenStore = wx.Button(self.panel_tab3, label="Buka &Toko Voice Pack (JadwalKu Store)...")
		self.btnOpenStore.Bind(wx.EVT_BUTTON, self.onOpenVoicePackStore)
		sizer_tab3.Add(self.btnOpenStore, 0, wx.ALL | wx.ALIGN_LEFT, 10)
		
		self.panel_tab3.SetSizer(sizer_tab3)
		self.notebook.AddPage(self.panel_tab3, "3. Voice Pack & Studio Suara")
		
		# --- Tab 4: Voice Command ---
		self.panel_tab4 = wx.Panel(self.notebook)
		sizer_tab4 = wx.BoxSizer(wx.VERTICAL)
		
		info_vc = wx.StaticText(self.panel_tab4, label="Perintah Suara (Voice Command) memungkinkan Anda bertanya 'Jam berapa sekarang' ke mikrofon.\nModul AI (Vosk) akan berjalan 100% offline dan membalas melalui suara.")
		sizer_tab4.Add(info_vc, 0, wx.ALL, 10)
		
		from .voiceCommandManager import VoiceCommandManager
		self.vc_mgr = VoiceCommandManager(None)
		
		if not self.vc_mgr.is_module_installed():
			warn_text = wx.StaticText(self.panel_tab4, label="Modul Perintah Suara (AI Offline) belum terpasang di perangkat Anda.")
			sizer_tab4.Add(warn_text, 0, wx.ALL, 10)
			
			self.btnDownloadVC = wx.Button(self.panel_tab4, label="&Unduh & Pasang Modul (±45 MB)")
			self.btnDownloadVC.Bind(wx.EVT_BUTTON, self.onDownloadVCModule)
			sizer_tab4.Add(self.btnDownloadVC, 0, wx.ALL, 10)
		else:
			vc_cfg = self.config.get_voice_command()
			
			self.chk_vc_enabled = wx.CheckBox(self.panel_tab4, label="&Aktifkan Pemantauan Mikrofon Latar Belakang (Shortcut: NVDA+/, M)")
			self.chk_vc_enabled.SetValue(vc_cfg.get("enabled", False))
			sizer_tab4.Add(self.chk_vc_enabled, 0, wx.ALL, 10)
			
			# Input Device
			lbl_vc_in_dev = wx.StaticText(self.panel_tab4, label="Perangkat &Mikrofon (Input):")
			sizer_tab4.Add(lbl_vc_in_dev, 0, wx.LEFT | wx.RIGHT | wx.TOP, 6)
			self.vc_in_devs = self.vc_mgr.get_input_devices()
			in_dev_names = [d[1] for d in self.vc_in_devs]
			self.cb_vc_in_dev = wx.ComboBox(self.panel_tab4, choices=in_dev_names, style=wx.CB_READONLY)
			self.cb_vc_in_dev.SetName("Perangkat Mikrofon (Input):")
			self.cb_vc_in_dev.SetToolTip("Perangkat Mikrofon (Input):")
			cur_in_dev = vc_cfg.get("input_device", "Default (Microsoft Sound Mapper)")
			if cur_in_dev in in_dev_names:
				self.cb_vc_in_dev.SetSelection(in_dev_names.index(cur_in_dev))
			else:
				self.cb_vc_in_dev.SetSelection(0)
			sizer_tab4.Add(self.cb_vc_in_dev, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 6)
			
			# Output Engine
			lbl_vc_engine = wx.StaticText(self.panel_tab4, label="Mesin Penjawab (&Output Engine):")
			sizer_tab4.Add(lbl_vc_engine, 0, wx.LEFT | wx.RIGHT | wx.TOP, 6)
			engine_choices = ["NVDA Default", "TTS Standar (SAPI 5)", "Voice Pack Kustom"]
			self.cb_vc_engine = wx.ComboBox(self.panel_tab4, choices=engine_choices, style=wx.CB_READONLY)
			self.cb_vc_engine.SetName("Mesin Penjawab (Output Engine):")
			self.cb_vc_engine.SetToolTip("Mesin Penjawab (Output Engine):")
			cur_engine = vc_cfg.get("tts_engine", "NVDA Default")
			if cur_engine in engine_choices:
				self.cb_vc_engine.SetSelection(engine_choices.index(cur_engine))
			else:
				self.cb_vc_engine.SetSelection(0)
			sizer_tab4.Add(self.cb_vc_engine, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 6)
			
			# Output Device (only relevant if not NVDA Default)
			lbl_vc_out_dev = wx.StaticText(self.panel_tab4, label="Perangkat S&peaker (Khusus SAPI 5 / Voice Pack):")
			sizer_tab4.Add(lbl_vc_out_dev, 0, wx.LEFT | wx.RIGHT | wx.TOP, 6)
			out_dev_names = self.audio.get_available_output_devices() if hasattr(self, 'audio') else ["Default (Microsoft Sound Mapper)"]
			self.cb_vc_out_dev = wx.ComboBox(self.panel_tab4, choices=out_dev_names, style=wx.CB_READONLY)
			self.cb_vc_out_dev.SetName("Perangkat Speaker (Khusus SAPI 5 / Voice Pack):")
			self.cb_vc_out_dev.SetToolTip("Perangkat Speaker (Khusus SAPI 5 / Voice Pack):")
			cur_out_dev = vc_cfg.get("output_device", "Default (Microsoft Sound Mapper)")
			if cur_out_dev in out_dev_names:
				self.cb_vc_out_dev.SetSelection(out_dev_names.index(cur_out_dev))
			else:
				self.cb_vc_out_dev.SetSelection(0)
			sizer_tab4.Add(self.cb_vc_out_dev, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 6)
			
			# Time Format
			lbl_vc_format = wx.StaticText(self.panel_tab4, label="F&ormat Waktu:")
			sizer_tab4.Add(lbl_vc_format, 0, wx.LEFT | wx.RIGHT | wx.TOP, 6)
			fmt_choices = [("Format 24 Jam (Contoh: 15:30)", "24"), ("Format 12 Jam AM/PM (Contoh: 3:30 PM)", "12")]
			self.vc_fmt_values = [v for k, v in fmt_choices]
			self.cb_vc_format = wx.ComboBox(self.panel_tab4, choices=[k for k,v in fmt_choices], style=wx.CB_READONLY)
			self.cb_vc_format.SetName("Format Waktu:")
			self.cb_vc_format.SetToolTip("Format Waktu:")
			cur_fmt = vc_cfg.get("time_format", "24")
			if cur_fmt in self.vc_fmt_values:
				self.cb_vc_format.SetSelection(self.vc_fmt_values.index(cur_fmt))
			else:
				self.cb_vc_format.SetSelection(0)
			sizer_tab4.Add(self.cb_vc_format, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 6)
			
			vc_style_choices = [
				("Gunakan Gaya Pengucapan Default", "default"),
				("Jam [Jam] lewat [Menit] menit", "jam_lewat_menit"),
				("Jam [Jam] lewat [Menit] menit [Detik] detik", "jam_lewat_menit_detik")
			]
			self.vc_style_values = [v for k, v in vc_style_choices]
			
			lbl_vc_style = wx.StaticText(self.panel_tab4, label="Gaya Pengucapan Jawaban Waktu:")
			sizer_tab4.Add(lbl_vc_style, 0, wx.LEFT | wx.RIGHT | wx.TOP, 6)
			self.cb_vc_style = wx.ComboBox(self.panel_tab4, choices=[k for k,v in vc_style_choices], style=wx.CB_READONLY)
			self.cb_vc_style.SetName("Gaya Pengucapan Jawaban Waktu:")
			self.cb_vc_style.SetToolTip("Gaya Pengucapan Jawaban Waktu:")
			cur_vc_style = vc_cfg.get("speech_style", "jam_lewat_menit")
			if cur_vc_style in self.vc_style_values:
				self.cb_vc_style.SetSelection(self.vc_style_values.index(cur_vc_style))
			else:
				self.cb_vc_style.SetSelection(0)
			sizer_tab4.Add(self.cb_vc_style, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 6)
			
			self.chk_vc_mute = wx.CheckBox(self.panel_tab4, label="D&iamkan NVDA jika Mesin Penjawab Kustom (SAPI/Voice Pack) berhasil bersuara")
			self.chk_vc_mute.SetValue(vc_cfg.get("mute_nvda_fallback", True))
			sizer_tab4.Add(self.chk_vc_mute, 0, wx.ALL, 10)
			
			# Volume Output
			sizer_tab4.Add(wx.StaticText(self.panel_tab4, label="&Volume Keluaran Voice Command (10% - 1200%):"), 0, wx.LEFT | wx.RIGHT | wx.TOP, 6)
			self.sld_vc_volume = wx.Slider(self.panel_tab4, value=vc_cfg.get("vc_volume", 100), minValue=10, maxValue=1200, style=wx.SL_HORIZONTAL | wx.SL_AUTOTICKS)
			self.sld_vc_volume.SetName("Volume Keluaran Voice Command (10% - 1200%):")
			self.sld_vc_volume.SetToolTip("Volume Keluaran Voice Command (10% - 1200%):")
			sizer_tab4.Add(self.sld_vc_volume, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 6)
			
			# Mic Boost
			sizer_tab4.Add(wx.StaticText(self.panel_tab4, label="S&ensitivitas Mikrofon / Boost (100% - 1200%):"), 0, wx.LEFT | wx.RIGHT | wx.TOP, 6)
			self.sld_mic_boost = wx.Slider(self.panel_tab4, value=vc_cfg.get("mic_boost", 100), minValue=100, maxValue=1200, style=wx.SL_HORIZONTAL | wx.SL_AUTOTICKS)
			self.sld_mic_boost.SetName("Sensitivitas Mikrofon / Boost (100% - 1200%):")
			self.sld_mic_boost.SetToolTip("Sensitivitas Mikrofon / Boost (100% - 1200%):")
			sizer_tab4.Add(self.sld_mic_boost, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 6)
			
			self.btnSaveVC = wx.Button(self.panel_tab4, label="&Simpan Pengaturan Perintah Suara")
			self.btnSaveVC.Bind(wx.EVT_BUTTON, self.onSaveVCConfig)
			sizer_tab4.Add(self.btnSaveVC, 0, wx.ALL, 10)

		self.panel_tab4.SetSizer(sizer_tab4)
		self.notebook.AddPage(self.panel_tab4, "4. Perintah Suara (Voice Command)")
		
		main_sizer.Add(self.notebook, 1, wx.EXPAND | wx.ALL, 6)
		
		bottom_btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
		self.btnClose = wx.Button(self, wx.ID_CANCEL, label="&Tutup Dialog")
		bottom_btn_sizer.Add(self.btnClose, 0, wx.ALL, 6)
		
		self.btnContextHelp = wx.Button(self, label="&Bantuan... (Alt+B)")
		self.btnContextHelp.Bind(wx.EVT_BUTTON, self.onContextualHelp)
		bottom_btn_sizer.Add(self.btnContextHelp, 0, wx.ALL, 6)
		main_sizer.Add(bottom_btn_sizer, 0, wx.ALIGN_RIGHT | wx.RIGHT | wx.BOTTOM, 6)
		
		self.SetSizer(main_sizer)
		self.Centre()
		self.refreshList()
		self.listBox.SetFocus()

	def onContextualHelp(self, evt):
		tab = self.notebook.GetSelection()
		if tab == 0:
			title = "Bantuan: Manajemen Agenda & Jadwal"
			text = "TAB MANAJEMEN AGENDA:\n\n- Gunakan panah atas/bawah untuk menelusuri daftar agenda.\n- Tekan SPASI pada agenda yang disorot untuk mengaktifkan (centang) atau menonaktifkannya.\n- Tekan tombol 'Tambah Jadwal Baru' untuk membuat alarm weker atau chime (pemberitahuan singkat) pada jam tertentu.\n- Tombol 'Pengaturan Pengingat Waktu Berkala' berguna untuk menyalakan bunyi lonceng setiap pergantian jam layaknya jam dinding."
		elif tab == 1:
			title = "Bantuan: Pengaturan Waktu & Kalender"
			text = "TAB PENGATURAN WAKTU:\n\n- Format Waktu: Anda dapat memilih membaca jam dalam format 12 jam (AM/PM) atau 24 jam.\n- Format Tanggal: Tersedia berbagai susunan pengucapan tanggal (contoh: 17 Agustus 1945).\n- Gaya Pengucapan: Menentukan seberapa ringkas NVDA membacakan waktu.\n- Tombol Kalender: Menampilkan kalender bulan ini beserta daftar Tanggal Merah (Libur Nasional) di Indonesia."
		elif tab == 2:
			title = "Bantuan: Voice Pack & Studio Suara"
			text = "TAB VOICE PACK & STUDIO SUARA:\n\n- Voice Pack adalah paket suara rekaman asli manusia (atau AI) yang menggantikan suara mesin TTS saat membacakan jam (Misal: 'Jam setengah sembilan lewat lima menit').\n- Anda bisa merekam paket suara Anda sendiri melalui 'Studio Rekaman Suara JadwalKu' lalu membagikannya (.jvp).\n- Jika ada Voice Pack yang aktif, sistem secara otomatis akan menggunakan rekaman tersebut daripada suara SAPI5/NVDA."
		else:
			title = "Bantuan: Perintah Suara (Voice Command)"
			text = "TAB PERINTAH SUARA:\n\n- Jika Anda mencentang 'Aktifkan Pemantauan Mikrofon', Anda dapat bertanya 'Jam berapa sekarang?' secara lisan (menggunakan mikrofon).\n- Fitur ini berjalan 100% offline (menggunakan model Vosk) sehingga tidak butuh internet.\n- Anda dapat menyesuaikan Sensitivitas Mikrofon (Boost) jika suara Anda kurang terdengar."
		
		dlg = ContextualHelpDialog(self, title, text)
		dlg.ShowModal()
		dlg.Destroy()

	def refreshList(self, select_index=0):
		self.listBox.Clear()
		self.schedules = self.config.get_schedules()
		for item in self.schedules:
			status_mark = "[V]" if item.get("active", False) else "[ ]"
			int_h = int(item.get("interval_hour", 0))
			if int_h > 0:
				end_h = int(item.get("interval_end_hour", 23))
				repeat_str = f", Tiap {int_h} Jam s.d. Jam {end_h:02d}:00"
			else:
				repeat_str = ""
			time_str = f"{int(item.get('hour', 0)):02d}:{int(item.get('minute', 0)):02d}{repeat_str}"
			freq_str = item.get("frequency", "Setiap Hari")
			name_str = item.get("name", "Tanpa Nama")
			display_text = f"{status_mark} {time_str} - {name_str} ({freq_str})"
			self.listBox.Append(display_text)
		
		if self.schedules:
			if 0 <= select_index < len(self.schedules):
				self.listBox.SetSelection(select_index)
			else:
				self.listBox.SetSelection(len(self.schedules) - 1)

	def onListKeyDown(self, event):
		if event.GetKeyCode() == wx.WXK_SPACE:
			self.onToggleActive(None)
		elif event.GetKeyCode() == wx.WXK_TAB and event.ShiftDown():
			self.notebook.SetFocus()
		else:
			event.Skip()

	def onAdd(self, event):
		gui.mainFrame.prePopup()
		try:
			dlg = AgendaDialog(self, {}, audio_manager=self.audio)
			res = dlg.ShowModal()
			if res == wx.ID_OK:
				new_data = dlg.get_result()
				self.config.add_schedule(new_data)
				ui.message("Jadwal baru berhasil ditambahkan.")
				self.refreshList(select_index=len(self.config.get_schedules()) - 1)
			dlg.Destroy()
		finally:
			gui.mainFrame.postPopup()

	def onEdit(self, event):
		sel = self.listBox.GetSelection()
		if sel == wx.NOT_FOUND or sel >= len(self.schedules):
			ui.message("Pilih jadwal yang ingin diedit terlebih dahulu.")
			return
		
		item = self.schedules[sel]
		gui.mainFrame.prePopup()
		try:
			dlg = AgendaDialog(self, item.copy(), audio_manager=self.audio)
			res = dlg.ShowModal()
			if res == wx.ID_OK:
				updated = dlg.get_result()
				
				# Jika waktu diubah, batalkan penundaan (snooze) yang sedang berjalan
				if updated.get("last_triggered_date") == "":
					overrides = self.config.data.get("daily_overrides", {})
					if item["id"] in overrides:
						del overrides[item["id"]]
						self.config.save_data()
						
				self.config.update_schedule(item["id"], updated)
				ui.message("Jadwal berhasil diperbarui.")
				self.refreshList(select_index=sel)
			dlg.Destroy()
		finally:
			gui.mainFrame.postPopup()

	def onDelete(self, event):
		sel = self.listBox.GetSelection()
		if sel == wx.NOT_FOUND or sel >= len(self.schedules):
			ui.message("Pilih jadwal yang ingin dihapus terlebih dahulu.")
			return
		
		item = self.schedules[sel]
		gui.mainFrame.prePopup()
		try:
			confirm = wx.MessageBox(f"Apakah Anda yakin ingin menghapus jadwal '{item.get('name')}'?", "Konfirmasi Hapus JadwalKu", wx.YES_NO | wx.ICON_QUESTION, self)
			if confirm == wx.YES:
				self.config.delete_schedule(item["id"])
				ui.message("Jadwal berhasil dihapus.")
				self.refreshList(select_index=max(0, sel - 1))
		finally:
			gui.mainFrame.postPopup()

	def onToggleActive(self, event):
		sel = self.listBox.GetSelection()
		if sel == wx.NOT_FOUND or sel >= len(self.schedules):
			ui.message("Pilih jadwal terlebih dahulu.")
			return
		
		item = self.schedules[sel]
		new_status = self.config.toggle_schedule_active(item["id"])
		status_text = "Diaktifkan (Check)" if new_status else "Dinonaktifkan (Uncheck)"
		ui.message(f"Jadwal '{item.get('name')}' sekarang {status_text}.")
		self.refreshList(select_index=sel)

	def onTimeReminder(self, event):
		gui.mainFrame.prePopup()
		try:
			cfg = self.config.get_time_reminder_config()
			dlg = TimeReminderDialog(self, cfg.copy(), getattr(self, "tts_manager", None), self.config)
			res = dlg.ShowModal()
			if res == wx.ID_OK:
				updated = dlg.get_result()
				self.config.update_time_reminder_config(updated)
				status = "Aktif" if updated["enabled"] else "Nonaktif"
				ui.message(f"Pengaturan pengingat waktu berkala berhasil disimpan ({status}, tiap {updated['interval']} menit).")
			dlg.Destroy()
		finally:
			gui.mainFrame.postPopup()

	def onVoicePackChanged(self, event):
		sel = self.cb_active_vp.GetSelection()
		filename = ""
		if sel > 0 and sel - 1 < len(self.vp_list):
			filename = self.vp_list[sel - 1]["id"]
			
		time_cfg = self.config.get_time_reminder_config()
		time_cfg["active_voice_pack"] = filename
		self.config.update_time_reminder_config(time_cfg)
		ui.message("Paket suara aktif berhasil diubah.")

	def onVoicePackVolumeChanged(self, event):
		vol = self.sld_vp_vol.GetValue()
		
		if not hasattr(self, "_vp_vol_timer"):
			self._vp_vol_timer = wx.Timer(self)
			self.Bind(wx.EVT_TIMER, self._onSaveVoicePackVolume, self._vp_vol_timer)
		self._vp_vol_timer.Start(200, wx.TIMER_ONE_SHOT)
		
	def _onSaveVoicePackVolume(self, event):
		vol = self.sld_vp_vol.GetValue()
		time_cfg = self.config.get_time_reminder_config()
		time_cfg["voice_pack_volume"] = vol
		self.config.update_time_reminder_config(time_cfg)
		if hasattr(self, "audio") and self.audio:
			active_vp = time_cfg.get("active_voice_pack", "")
			if active_vp:
				import os, datetime
				pack_path = os.path.join(self.vp_mgr.pack_dir, active_vp)
				if os.path.exists(pack_path):
					temp_dir = self.vp_mgr.extract_pack_to_temp(pack_path)
					if temp_dir:
						now = datetime.datetime.now()
						h_12 = now.hour % 12 or 12
						words = ["waktu", "sekarang", str(now.hour), str(now.minute)]
						vp_files = []
						for w in words:
							wav_path = os.path.join(temp_dir, f"{w}.wav")
							if os.path.exists(wav_path):
								vp_files.append(wav_path)
						if vp_files:
							self.audio.play_voice_pack_sequence(vp_files, volume_override=vol)

	def onOpenVoiceStudio(self, event):
		gui.mainFrame.prePopup()
		try:
			from . import voicePackManager
			# add_on_dir is the jadwalku directory
			add_on_dir = os.path.dirname(os.path.abspath(__file__))
			try:
				dlg = VoicePackManagementDialog(self, add_on_dir, audio_manager=self.audio)
				dlg.ShowModal()
			except Exception as e:
				import traceback
				err = traceback.format_exc()
				import ui
				ui.message(f"Error opening Studio: {e}")
				from .logger import jk_log
				jk_log.error(f"JadwalKu Studio Error: {err}")
		finally:
			gui.mainFrame.postPopup()

	def onOpenVoicePackStore(self, event):
		gui.mainFrame.prePopup()
		try:
			from . import guiVoicePackStore
			from . import voicePackManager
			add_on_dir = os.path.dirname(os.path.abspath(__file__))
			vp_mgr = voicePackManager.VoicePackManager(add_on_dir)
			try:
				dlg = guiVoicePackStore.VoicePackStoreDialog(self, add_on_dir, vp_manager=vp_mgr)
				dlg.ShowModal()
			except Exception as e:
				import traceback
				err = traceback.format_exc()
				import ui
				ui.message(f"Error opening Store: {e}")
				from .logger import jk_log
				jk_log.error(f"JadwalKu Store Error: {err}")
		finally:
			gui.mainFrame.postPopup()

	def onOpenTTSManager(self, event):
		gui.mainFrame.prePopup()
		try:
			dlg = TTSManagerDialog(self, getattr(self, "tts_manager", None), self.config)
			if dlg.ShowModal() == wx.ID_OK:
				self.config.update_tts_config(dlg.get_result())
				status = "Aktif" if dlg.get_result()["enabled"] else "Nonaktif"
				ui.message(f"Pengaturan TTS Mandiri berhasil disimpan ({status}).")
			dlg.Destroy()
		finally:
			gui.mainFrame.postPopup()

	def onLonceng(self, event):
		dlg = LoncengDialog(self, self.config, self.audio)
		dlg.ShowModal()
		dlg.Destroy()
		
	def onCheckUpdate(self, event):
		if self.updater:
			ui.message("Memeriksa pembaruan ke server...")
			self.updater.check_update_manual()

	def onAudioManager(self, event):
		gui.mainFrame.prePopup()
		try:
			dlg = AudioManagerDialog(self, self.audio, self.config)
			res = dlg.ShowModal()
			if res == wx.ID_OK:
				updated = dlg.get_result()
				self.config.set_audio_device(updated["audio_device"])
				self.config.set_audio_volume(updated.get("audio_volume", 100))
				ui.message(f"Speaker ({updated['audio_device']}) & Volume ({updated.get('audio_volume', 100)}%) disimpan.")
			if hasattr(self.audio, "_override_volume"):
				self.audio._override_volume = None
			dlg.Destroy()
		finally:
			gui.mainFrame.postPopup()

	def onHelp(self, event):
		gui.mainFrame.prePopup()
		try:
			dlg = HelpDialog(self)
			dlg.ShowModal()
			dlg.Destroy()
		finally:
			gui.mainFrame.postPopup()

	def onOpenCalendar(self, event):
		gui.mainFrame.prePopup()
		try:
			dlg = CalendarDialog(self)
			dlg.ShowModal()
			dlg.Destroy()
		finally:
			gui.mainFrame.postPopup()

	def onOpenWorldClock(self, event):
		gui.mainFrame.prePopup()
		try:
			dlg = WorldClockDialog(self)
			dlg.ShowModal()
			dlg.Destroy()
		finally:
			gui.mainFrame.postPopup()

	def onSaveTimeSettings(self, event):
		t_style_inv = {0: "default", 1: "only_time", 2: "prefix_pukul", 3: "with_seconds", 4: "full_seconds", 5: "jam_lewat_menit", 6: "jam_lewat_menit_detik"}
		d_style_inv = {0: "default", 1: "prefix_hari", 2: "numeric", 3: "suffix_hari"}
		f_style_inv = {0: "default", 1: "short"}
		
		updated = {
			"override_nvda_f12": self.chk_override_f12.GetValue(),
			"time_format": "12" if self.cb_time_format.GetSelection() == 1 else "24",
			"time_speech_style": t_style_inv.get(self.cb_time_speech_style.GetSelection(), "default"),
			"include_seconds": self.chk_time_seconds.GetValue(),
			"date_speech_style": d_style_inv.get(self.cb_date_speech_style.GetSelection(), "default"),
			"full_speech_style": f_style_inv.get(self.cb_full_speech_style.GetSelection(), "default")
		}
		self.config.update_time_settings(updated)
		ui.message("Pengaturan pelaporan waktu dan kalender JadwalKu berhasil disimpan!")

	def onDownloadVCModule(self, event):
		import urllib.request
		import zipfile
		import tempfile
		import threading
		
		dlg = wx.ProgressDialog("Mengunduh Modul", "Menyambung ke server...", 100, self, wx.PD_AUTO_HIDE | wx.PD_APP_MODAL | wx.PD_CAN_ABORT)
		
		def download_thread():
			import sys
			is_64bit = sys.maxsize > 2**32
			if is_64bit:
				url = "https://github.com/RajuLaini/JadwalKu-NVDA/releases/download/voice-module-v1/jadwalku_voice_module.zip"
			else:
				url = "https://github.com/RajuLaini/JadwalKu-NVDA/releases/download/voice-module-v1/jadwalku_voice_module_32.zip"
			temp_dir = tempfile.mkdtemp()
			local_zip = os.path.join(temp_dir, "jadwalku_voice_module.zip")
			try:
				req = urllib.request.urlopen(url)
				total_size = int(req.info().get('Content-Length', 0))
				downloaded = 0
				block_size = 8192
				with open(local_zip, 'wb') as f:
					while True:
						buffer = req.read(block_size)
						if not buffer:
							break
						f.write(buffer)
						downloaded += len(buffer)
						if total_size > 0:
							percent = int(downloaded * 100 / total_size)
							# Update UI thread
							wx.CallAfter(dlg.Update, percent, f"Mengunduh... {percent}%")
				
				wx.CallAfter(dlg.Update, 100, "Mengekstrak...")
				
				from .voiceCommandManager import VoiceCommandManager
				mgr = VoiceCommandManager(None)
				if not os.path.isdir(mgr.module_path):
					os.makedirs(mgr.module_path)
				
				with zipfile.ZipFile(local_zip, 'r') as zip_ref:
					zip_ref.extractall(mgr.module_path)
					
				wx.CallAfter(dlg.Destroy)
				wx.CallAfter(wx.MessageBox, "Modul Perintah Suara berhasil dipasang dari Cloud! Silakan tutup dialog ini dan buka kembali pengaturan (NVDA+/, P) untuk melihat menu baru.", "Sukses", wx.OK | wx.ICON_INFORMATION, self)
			except Exception as e:
				wx.CallAfter(dlg.Destroy)
				wx.CallAfter(wx.MessageBox, f"Gagal mengunduh modul: {str(e)}", "Error", wx.OK | wx.ICON_ERROR, self)
			finally:
				try:
					if os.path.exists(local_zip):
						os.remove(local_zip)
					os.rmdir(temp_dir)
				except:
					pass
					
		threading.Thread(target=download_thread, daemon=True).start()
			
	def onSaveVCConfig(self, event):
		enabled = self.chk_vc_enabled.GetValue()
		in_dev = self.cb_vc_in_dev.GetStringSelection()
		engine = self.cb_vc_engine.GetStringSelection()
		out_dev = self.cb_vc_out_dev.GetStringSelection()
		t_fmt = self.vc_fmt_values[self.cb_vc_format.GetSelection()]
		style = self.vc_style_values[self.cb_vc_style.GetSelection()]
		mute = self.chk_vc_mute.GetValue()
		vol = self.sld_vc_volume.GetValue()
		boost = self.sld_mic_boost.GetValue()
		
		self.config.update_voice_command({
			"enabled": enabled,
			"input_device": in_dev,
			"tts_engine": engine,
			"output_device": out_dev,
			"time_format": t_fmt,
			"speech_style": style,
			"mute_nvda_fallback": mute,
			"vc_volume": vol,
			"mic_boost": boost
		})
		
		import globalVars
		try:
			plugin = globalVars.extensionManager.getGlobalPlugin("jadwalku")
			if plugin:
				if enabled:
					plugin.script_toggleVoiceCommand(None) # Call toggle logic to apply settings properly
					if plugin.vc_manager and not plugin.vc_manager.is_listening:
						# If toggle disabled it, re-enable it because we want it enabled. 
						plugin.script_toggleVoiceCommand(None)
				else:
					if plugin.vc_manager and plugin.vc_manager.is_listening:
						plugin.script_toggleVoiceCommand(None)
		except Exception:
			pass
		
		ui.message("Pengaturan Perintah Suara berhasil disimpan!")


def get_indonesian_holidays(year):
	holidays = {
		datetime.date(year, 1, 1): "Tahun Baru Masehi",
		datetime.date(year, 5, 1): "Hari Buruh Internasional",
		datetime.date(year, 6, 1): "Hari Lahir Pancasila",
		datetime.date(year, 8, 17): f"Hari Kemerdekaan Republik Indonesia ke-{year - 1945}",
		datetime.date(year, 12, 25): "Hari Raya Natal"
	}
	if year == 2026:
		holidays.update({
			datetime.date(2026, 2, 8): "Isra Mi'raj Nabi Muhammad SAW",
			datetime.date(2026, 2, 10): "Tahun Baru Imlek 2577 Kongzili",
			datetime.date(2026, 3, 11): "Hari Suci Nyepi Tahun Baru Saka 1948",
			datetime.date(2026, 3, 20): "Hari Raya Idul Fitri 1447 Hijriah (Hari Pertama)",
			datetime.date(2026, 3, 21): "Hari Raya Idul Fitri 1447 Hijriah (Hari Kedua)",
			datetime.date(2026, 4, 3): "Wafat Yesus Kristus",
			datetime.date(2026, 5, 14): "Kenaikan Yesus Kristus",
			datetime.date(2026, 5, 27): "Hari Raya Idul Adha 1447 Hijriah",
			datetime.date(2026, 5, 31): "Hari Raya Waisak 2570 BE",
			datetime.date(2026, 6, 16): "Tahun Baru Islam 1448 Hijriah",
			datetime.date(2026, 8, 25): "Maulid Nabi Muhammad SAW"
		})
	elif year == 2025:
		holidays.update({
			datetime.date(2025, 1, 27): "Isra Mi'raj Nabi Muhammad SAW",
			datetime.date(2025, 1, 29): "Tahun Baru Imlek 2576 Kongzili",
			datetime.date(2025, 3, 29): "Hari Suci Nyepi Tahun Baru Saka 1947",
			datetime.date(2025, 3, 31): "Hari Raya Idul Fitri 1446 Hijriah (Hari Pertama)",
			datetime.date(2025, 4, 1): "Hari Raya Idul Fitri 1446 Hijriah (Hari Kedua)",
			datetime.date(2025, 4, 18): "Wafat Yesus Kristus",
			datetime.date(2025, 5, 12): "Hari Raya Waisak 2569 BE",
			datetime.date(2025, 5, 29): "Kenaikan Yesus Kristus",
			datetime.date(2025, 6, 6): "Hari Raya Idul Adha 1446 Hijriah",
			datetime.date(2025, 6, 27): "Tahun Baru Islam 1447 Hijriah",
			datetime.date(2025, 9, 5): "Maulid Nabi Muhammad SAW"
		})
	elif year == 2024:
		holidays.update({
			datetime.date(2024, 2, 8): "Isra Mi'raj Nabi Muhammad SAW",
			datetime.date(2024, 2, 10): "Tahun Baru Imlek 2575 Kongzili",
			datetime.date(2024, 3, 11): "Hari Suci Nyepi Tahun Baru Saka 1946",
			datetime.date(2024, 3, 29): "Wafat Yesus Kristus",
			datetime.date(2024, 4, 10): "Hari Raya Idul Fitri 1445 Hijriah (Hari Pertama)",
			datetime.date(2024, 4, 11): "Hari Raya Idul Fitri 1445 Hijriah (Hari Kedua)",
			datetime.date(2024, 5, 9): "Kenaikan Yesus Kristus",
			datetime.date(2024, 5, 23): "Hari Raya Waisak 2568 BE",
			datetime.date(2024, 6, 17): "Hari Raya Idul Adha 1445 Hijriah",
			datetime.date(2024, 7, 7): "Tahun Baru Islam 1446 Hijriah",
			datetime.date(2024, 9, 16): "Maulid Nabi Muhammad SAW"
		})
	return holidays


class CalendarDialog(wx.Dialog):
	def __init__(self, parent):
		super().__init__(parent, title="Kalender & Daftar Tanggal Merah Indonesia", size=(620, 500), style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)
		
		self.now = datetime.datetime.now()
		self.current_year = self.now.year
		self.current_month = self.now.month
		
		sizer = wx.BoxSizer(wx.VERTICAL)
		sizer.Add(wx.StaticText(self, label="=== Kalender Bulanan & Tanggal Merah JadwalKu ==="), 0, wx.ALL, 8)
		
		# Pemilihan Bulan & Tahun
		filter_sizer = wx.BoxSizer(wx.HORIZONTAL)
		filter_sizer.Add(wx.StaticText(self, label="&Bulan:"), 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 4)
		self.months_list = ["Januari", "Februari", "Maret", "April", "Mei", "Juni", "Juli", "Agustus", "September", "Oktober", "November", "Desember"]
		self.cb_month = wx.ComboBox(self, choices=self.months_list, style=wx.CB_READONLY)
		self.cb_month.SetName("Bulan:")
		self.cb_month.SetToolTip("Bulan:")
		self.cb_month.SetSelection(self.current_month - 1)
		self.cb_month.Bind(wx.EVT_COMBOBOX, self.onMonthYearChanged)
		filter_sizer.Add(self.cb_month, 0, wx.ALL, 4)
		
		filter_sizer.Add(wx.StaticText(self, label="&Tahun:"), 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 4)
		self.years_list = [str(y) for y in range(2024, 2036)]
		self.cb_year = wx.ComboBox(self, choices=self.years_list, style=wx.CB_READONLY)
		self.cb_year.SetName("Tahun:")
		self.cb_year.SetToolTip("Tahun:")
		if str(self.current_year) in self.years_list:
			self.cb_year.SetSelection(self.years_list.index(str(self.current_year)))
		else:
			self.cb_year.SetSelection(2)
		self.cb_year.Bind(wx.EVT_COMBOBOX, self.onMonthYearChanged)
		filter_sizer.Add(self.cb_year, 0, wx.ALL, 4)
		sizer.Add(filter_sizer, 0, wx.LEFT | wx.RIGHT, 8)
		
		# Daftar Hari
		self.lbl_list = wx.StaticText(self, label="Daftar Hari dalam Bulan Terpilih (Gunakan Panah Atas/Bawah):")
		sizer.Add(self.lbl_list, 0, wx.LEFT | wx.RIGHT | wx.TOP, 8)
		
		self.listBox = wx.ListBox(self, style=wx.LB_SINGLE)
		self.listBox.Bind(wx.EVT_LISTBOX_DCLICK, self.onItemDClick)
		sizer.Add(self.listBox, 1, wx.EXPAND | wx.ALL, 8)
		
		# Tombol-tombol Aksi & Filter Tanggal Merah
		btnSizer1 = wx.BoxSizer(wx.HORIZONTAL)
		self.btnShowHolidays = wx.Button(self, label="&Tampilkan Seluruh Tanggal Merah Tahun Ini")
		self.btnShowHolidays.Bind(wx.EVT_BUTTON, self.onShowAllHolidays)
		btnSizer1.Add(self.btnShowHolidays, 0, wx.ALL, 4)
		
		self.btnMonthView = wx.Button(self, label="&Kembali ke Kalender Bulanan")
		self.btnMonthView.Bind(wx.EVT_BUTTON, self.onMonthView)
		btnSizer1.Add(self.btnMonthView, 0, wx.ALL, 4)
		
		self.btnCountdown = wx.Button(self, label="&Cek Akhir Tahun")
		self.btnCountdown.Bind(wx.EVT_BUTTON, self.onCheckYearEnd)
		btnSizer1.Add(self.btnCountdown, 0, wx.ALL, 4)
		sizer.Add(btnSizer1, 0, wx.ALIGN_LEFT | wx.LEFT | wx.RIGHT, 4)
		
		btnSizer2 = wx.BoxSizer(wx.HORIZONTAL)
		self.btnClose = wx.Button(self, wx.ID_CANCEL, label="&Tutup")
		btnSizer2.Add(self.btnClose, 0, wx.ALL, 6)
		self.btnHelp = wx.Button(self, label="&Bantuan... (Alt+B)")
		self.btnHelp.Bind(wx.EVT_BUTTON, self.onContextualHelp)
		btnSizer2.Add(self.btnHelp, 0, wx.ALL, 6)
		sizer.Add(btnSizer2, 0, wx.ALIGN_RIGHT | wx.RIGHT | wx.BOTTOM, 6)
		
		self.SetSizer(sizer)
		self.Centre()
		self.refreshMonthCalendar()
		self.listBox.SetFocus()

	def onContextualHelp(self, evt):
		text = "BANTUAN KALENDER & TANGGAL MERAH:\n\n- Kalender ini sudah terintegrasi dengan daftar libur nasional / tanggal merah Indonesia.\n- Tanggal merah akan ditandai dengan tulisan '(Libur)' saat Anda menggunakan panah atas/bawah.\n- Anda juga bisa mengecek sisa waktu mundur ke akhir tahun dengan tombol Cek Akhir Tahun."
		dlg = ContextualHelpDialog(self, "Bantuan: Kalender JadwalKu", text)
		dlg.ShowModal()
		dlg.Destroy()

	def onMonthYearChanged(self, event):
		self.refreshMonthCalendar()

	def refreshMonthCalendar(self):
		self.listBox.Clear()
		year = int(self.cb_year.GetStringSelection())
		month = self.cb_month.GetSelection() + 1
		holidays = get_indonesian_holidays(year)
		
		# Hitung hari dalam bulan
		if month == 12:
			next_m = datetime.date(year + 1, 1, 1)
		else:
			next_m = datetime.date(year, month + 1, 1)
		days_in_month = (next_m - datetime.date(year, month, 1)).days
		
		day_names = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"]
		month_name = self.months_list[month - 1]
		self.lbl_list.SetLabel(f"Daftar Hari di Bulan {month_name} {year}:")
		
		today = datetime.date.today()
		select_idx = 0
		for d in range(1, days_in_month + 1):
			curr_date = datetime.date(year, month, d)
			d_name = day_names[curr_date.weekday()]
			is_today = " (HARI INI)" if curr_date == today else ""
			
			if curr_date in holidays:
				status = f"[TANGGAL MERAH / LIBUR] {holidays[curr_date]}"
			elif curr_date.weekday() == 6:
				status = "(Akhir Pekan - Hari Minggu)"
			elif curr_date.weekday() == 5:
				status = "(Akhir Pekan - Hari Sabtu)"
			else:
				status = "(Hari Kerja Normal)"
			
			self.listBox.Append(f"{d_name}, {d} {month_name} {year}{is_today} - {status}")
			if curr_date == today:
				select_idx = d - 1
		
		if self.listBox.GetCount() > 0:
			self.listBox.SetSelection(min(select_idx, self.listBox.GetCount() - 1))

	def onShowAllHolidays(self, event):
		self.listBox.Clear()
		year = int(self.cb_year.GetStringSelection())
		holidays = get_indonesian_holidays(year)
		day_names = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"]
		self.lbl_list.SetLabel(f"Seluruh Daftar Tanggal Merah & Libur Nasional Tahun {year}:")
		
		sorted_dates = sorted(holidays.keys())
		for dt in sorted_dates:
			d_name = day_names[dt.weekday()]
			m_name = self.months_list[dt.month - 1]
			self.listBox.Append(f"{dt.day} {m_name} {year} ({d_name}) - [TANGGAL MERAH] {holidays[dt]}")
		
		if self.listBox.GetCount() > 0:
			self.listBox.SetSelection(0)
		ui.message(f"Menampilkan {len(sorted_dates)} tanggal merah di tahun {year}.")
		self.listBox.SetFocus()

	def onMonthView(self, event):
		self.refreshMonthCalendar()
		ui.message("Kembali menampilkan kalender bulanan.")
		self.listBox.SetFocus()

	def onCheckYearEnd(self, event):
		now = datetime.datetime.now()
		end_y = datetime.datetime(now.year + 1, 1, 1, 0, 0, 0)
		diff = end_y - now
		days = diff.days
		hours = diff.seconds // 3600
		ui.message(f"Sisa waktu menuju akhir tahun {now.year}: {days} hari dan {hours} jam lagi.")

	def onItemDClick(self, event):
		sel = self.listBox.GetStringSelection()
		if sel:
			ui.message(sel)


WORLD_CLOCKS_DATA = [
	{"country": "Indonesia Barat (WIB - Jakarta / Surabaya)", "region": "Asia & Timur Tengah", "offset": 0},
	{"country": "Indonesia Tengah (WITA - Bali / Makassar)", "region": "Asia & Timur Tengah", "offset": 1},
	{"country": "Indonesia Timur (WIT - Papua / Maluku)", "region": "Asia & Timur Tengah", "offset": 2},
	{"country": "Arab Saudi (Makkah / Madinah)", "region": "Asia & Timur Tengah", "offset": -4},
	{"country": "Jepang (Tokyo / Osaka)", "region": "Asia & Timur Tengah", "offset": 2},
	{"country": "Korea Selatan (Seoul)", "region": "Asia & Timur Tengah", "offset": 2},
	{"country": "Singapura & Malaysia (Kuala Lumpur)", "region": "Asia & Timur Tengah", "offset": 1},
	{"country": "Turki (Istanbul)", "region": "Asia & Timur Tengah", "offset": -4},
	{"country": "Jerman (Berlin / Frankfurt)", "region": "Eropa", "offset": -5},
	{"country": "Inggris (London)", "region": "Eropa", "offset": -6},
	{"country": "Belanda (Amsterdam)", "region": "Eropa", "offset": -5},
	{"country": "Prancis (Paris)", "region": "Eropa", "offset": -5},
	{"country": "Rusia (Moskow)", "region": "Eropa", "offset": -4},
	{"country": "Amerika Serikat (New York / Washington DC)", "region": "Amerika Utara & Selatan", "offset": -11},
	{"country": "Amerika Serikat (Los Angeles / San Francisco)", "region": "Amerika Utara & Selatan", "offset": -14},
	{"country": "Kanada (Toronto)", "region": "Amerika Utara & Selatan", "offset": -11},
	{"country": "Brasil (Sao Paulo)", "region": "Amerika Utara & Selatan", "offset": -10},
	{"country": "Australia (Sydney / Melbourne)", "region": "Australia & Pasifik", "offset": 3},
	{"country": "Australia (Perth)", "region": "Australia & Pasifik", "offset": 1},
	{"country": "Selandia Baru (Auckland)", "region": "Australia & Pasifik", "offset": 5},
	{"country": "Mesir (Kairo)", "region": "Afrika", "offset": -4},
	{"country": "Afrika Selatan (Cape Town)", "region": "Afrika", "offset": -5}
]


class WorldClockDialog(wx.Dialog):
	def __init__(self, parent):
		super().__init__(parent, title="Jam Dunia & Kalkulator Perbedaan Waktu JadwalKu", size=(680, 560), style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)
		
		self.notebook = wx.Notebook(self)
		
		# Tab 1: Daftar Jam Dunia
		self.panel_clocks = wx.Panel(self.notebook)
		sizer_c = wx.BoxSizer(wx.VERTICAL)
		
		filter_sizer = wx.BoxSizer(wx.HORIZONTAL)
		filter_sizer.Add(wx.StaticText(self.panel_clocks, label="&Filter Benua / Wilayah:"), 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 4)
		self.regions = ["Semua Negara & Kota", "Asia & Timur Tengah", "Eropa", "Amerika Utara & Selatan", "Australia & Pasifik", "Afrika"]
		self.cb_region = wx.ComboBox(self.panel_clocks, choices=self.regions, style=wx.CB_READONLY)
		self.cb_region.SetName("Filter Benua / Wilayah:")
		self.cb_region.SetToolTip("Filter Benua / Wilayah:")
		self.cb_region.SetSelection(0)
		self.cb_region.Bind(wx.EVT_COMBOBOX, self.onFilterChanged)
		filter_sizer.Add(self.cb_region, 0, wx.ALL, 4)
		sizer_c.Add(filter_sizer, 0, wx.LEFT | wx.RIGHT | wx.TOP, 8)
		
		sizer_c.Add(wx.StaticText(self.panel_clocks, label="Daftar Jam Dunia Langsung (Dibandingkan waktu Indonesia WIB saat ini):"), 0, wx.LEFT | wx.RIGHT | wx.TOP, 8)
		self.listBox_clocks = wx.ListBox(self.panel_clocks, style=wx.LB_SINGLE)
		self.listBox_clocks.Bind(wx.EVT_LISTBOX_DCLICK, self.onClockDClick)
		sizer_c.Add(self.listBox_clocks, 1, wx.EXPAND | wx.ALL, 8)
		
		btnSpeak = wx.Button(self.panel_clocks, label="&Bacakan Jam Terpilih")
		btnSpeak.Bind(wx.EVT_BUTTON, self.onSpeakClock)
		sizer_c.Add(btnSpeak, 0, wx.LEFT | wx.BOTTOM, 8)
		self.panel_clocks.SetSizer(sizer_c)
		
		# Tab 2: Kalkulator Konversi Waktu
		self.panel_conv = wx.Panel(self.notebook)
		sizer_v = wx.BoxSizer(wx.VERTICAL)
		sizer_v.Add(wx.StaticText(self.panel_conv, label="=== Kalkulator Konversi Waktu Antar Negara ==="), 0, wx.ALL, 8)
		
		# Negara Asal
		sizer_v.Add(wx.StaticText(self.panel_conv, label="1. Pilih Negara/Kota &Asal:"), 0, wx.LEFT | wx.TOP, 8)
		country_names = [item["country"] for item in WORLD_CLOCKS_DATA]
		self.cb_src_country = wx.ComboBox(self.panel_conv, choices=country_names, style=wx.CB_READONLY)
		self.cb_src_country.SetName("1. Pilih Negara/Kota Asal:")
		self.cb_src_country.SetToolTip("1. Pilih Negara/Kota Asal:")
		# Default Jerman jika ada
		jerman_idx = next((i for i, c in enumerate(country_names) if "Jerman" in c), 0)
		self.cb_src_country.SetSelection(jerman_idx)
		self.cb_src_country.Bind(wx.EVT_COMBOBOX, self.onCalculateConversion)
		sizer_v.Add(self.cb_src_country, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 8)
		
		# Jam & Menit Asal
		time_sizer = wx.BoxSizer(wx.HORIZONTAL)
		time_sizer.Add(wx.StaticText(self.panel_conv, label="&Jam di Negara Asal (00-23):"), 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 4)
		self.cb_src_hour = wx.ComboBox(self.panel_conv, choices=[f"{h:02d}" for h in range(24)], style=wx.CB_READONLY)
		self.cb_src_hour.SetName("Jam di Negara Asal (00-23):")
		self.cb_src_hour.SetToolTip("Jam di Negara Asal (00-23):")
		self.cb_src_hour.SetSelection(20) # Default Jam 20:00 seperti contoh user
		self.cb_src_hour.Bind(wx.EVT_COMBOBOX, self.onCalculateConversion)
		time_sizer.Add(self.cb_src_hour, 0, wx.ALL, 4)
		
		time_sizer.Add(wx.StaticText(self.panel_conv, label="&Menit:"), 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 4)
		self.cb_src_min = wx.ComboBox(self.panel_conv, choices=[f"{m:02d}" for m in range(60)], style=wx.CB_READONLY)
		self.cb_src_min.SetName("Menit:")
		self.cb_src_min.SetToolTip("Menit:")
		self.cb_src_min.SetSelection(0)
		self.cb_src_min.Bind(wx.EVT_COMBOBOX, self.onCalculateConversion)
		time_sizer.Add(self.cb_src_min, 0, wx.ALL, 4)
		sizer_v.Add(time_sizer, 0, wx.LEFT | wx.RIGHT, 8)
		
		# Negara Tujuan
		sizer_v.Add(wx.StaticText(self.panel_conv, label="2. Pilih Negara/Kota &Tujuan Konversi:"), 0, wx.LEFT | wx.TOP, 8)
		self.cb_tgt_country = wx.ComboBox(self.panel_conv, choices=country_names, style=wx.CB_READONLY)
		self.cb_tgt_country.SetName("2. Pilih Negara/Kota Tujuan Konversi:")
		self.cb_tgt_country.SetToolTip("2. Pilih Negara/Kota Tujuan Konversi:")
		# Default Indonesia WIB
		wib_idx = next((i for i, c in enumerate(country_names) if "WIB" in c), 0)
		self.cb_tgt_country.SetSelection(wib_idx)
		self.cb_tgt_country.Bind(wx.EVT_COMBOBOX, self.onCalculateConversion)
		sizer_v.Add(self.cb_tgt_country, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 8)
		
		# Tombol Hitung & Hasil
		self.btnCalc = wx.Button(self.panel_conv, label="&Hitung & Bacakan Hasil Konversi (Enter)")
		self.btnCalc.Bind(wx.EVT_BUTTON, self.onCalculateConversion)
		sizer_v.Add(self.btnCalc, 0, wx.LEFT | wx.RIGHT | wx.TOP, 8)
		
		self.txt_result = wx.TextCtrl(self.panel_conv, style=wx.TE_MULTILINE | wx.TE_READONLY)
		self.txt_result.SetName("2. Pilih Negara/Kota Tujuan Konversi:")
		self.txt_result.SetToolTip("2. Pilih Negara/Kota Tujuan Konversi:")
		sizer_v.Add(self.txt_result, 1, wx.EXPAND | wx.ALL, 8)
		self.panel_conv.SetSizer(sizer_v)
		
		self.notebook.AddPage(self.panel_clocks, "1. Jam Dunia & Selisih Waktu")
		self.notebook.AddPage(self.panel_conv, "2. Kalkulator Konversi Waktu Antar Negara")
		
		main_sizer = wx.BoxSizer(wx.VERTICAL)
		main_sizer.Add(self.notebook, 1, wx.EXPAND | wx.ALL, 6)
		
		bottom_btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
		self.btnClose = wx.Button(self, wx.ID_CANCEL, label="&Tutup Dialog")
		bottom_btn_sizer.Add(self.btnClose, 0, wx.ALL, 6)
		
		self.btnContextHelp = wx.Button(self, label="&Bantuan... (Alt+B)")
		self.btnContextHelp.Bind(wx.EVT_BUTTON, self.onContextualHelp)
		bottom_btn_sizer.Add(self.btnContextHelp, 0, wx.ALL, 6)
		main_sizer.Add(bottom_btn_sizer, 0, wx.ALIGN_RIGHT | wx.RIGHT | wx.BOTTOM, 6)
		
		self.SetSizer(main_sizer)
		self.Centre()
		self.refreshClocksList()
		self.onCalculateConversion(None, speak=False)
		self.listBox_clocks.SetFocus()

	def onContextualHelp(self, evt):
		tab = self.notebook.GetSelection()
		if tab == 0:
			text = "BANTUAN JAM DUNIA:\n\n- Menampilkan waktu saat ini di berbagai negara.\n- Anda dapat mengetik di kotak pencarian untuk memfilter negara."
		else:
			text = "BANTUAN KONVERSI WAKTU:\n\n- Memungkinkan Anda menghitung selisih waktu antara dua negara."
		dlg = ContextualHelpDialog(self, "Bantuan: Jam Dunia & Konversi", text)
		dlg.ShowModal()
		dlg.Destroy()

	def onFilterChanged(self, event):
		self.refreshClocksList()

	def refreshClocksList(self):
		self.listBox_clocks.Clear()
		sel_region = self.cb_region.GetStringSelection()
		now = datetime.datetime.now()
		
		for item in WORLD_CLOCKS_DATA:
			if sel_region != "Semua Negara & Kota" and item["region"] != sel_region:
				continue
			offset = item["offset"]
			# Hitung waktu target
			tgt_time = now + datetime.timedelta(hours=offset)
			
			if offset > 0:
				selisih_str = f"+{offset} jam dari WIB"
			elif offset < 0:
				selisih_str = f"{offset} jam dari WIB"
			else:
				selisih_str = "Sama dengan WIB (0 jam)"
			
			day_str = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"][tgt_time.weekday()]
			time_str = tgt_time.strftime("%H:%M")
			date_str = f"{tgt_time.day}/{tgt_time.month}"
			
			self.listBox_clocks.Append(f"{item['country']} | Pukul {time_str} ({day_str}, {date_str}) | Selisih: {selisih_str}")
		
		if self.listBox_clocks.GetCount() > 0:
			self.listBox_clocks.SetSelection(0)

	def onClockDClick(self, event):
		self.onSpeakClock(None)

	def onSpeakClock(self, event):
		sel = self.listBox_clocks.GetStringSelection()
		if sel:
			ui.message(sel)

	def onCalculateConversion(self, event, speak=True):
		src_idx = self.cb_src_country.GetSelection()
		tgt_idx = self.cb_tgt_country.GetSelection()
		if src_idx < 0 or tgt_idx < 0:
			return
		
		src_data = next((c for c in WORLD_CLOCKS_DATA if c["country"] == self.cb_src_country.GetStringSelection()), WORLD_CLOCKS_DATA[0])
		tgt_data = next((c for c in WORLD_CLOCKS_DATA if c["country"] == self.cb_tgt_country.GetStringSelection()), WORLD_CLOCKS_DATA[0])
		
		src_h = int(self.cb_src_hour.GetStringSelection())
		src_m = int(self.cb_src_min.GetStringSelection())
		
		diff_hours = tgt_data["offset"] - src_data["offset"]
		tgt_h_raw = src_h + diff_hours
		tgt_h = tgt_h_raw % 24
		day_shift = tgt_h_raw // 24
		
		if day_shift == 0:
			day_desc = "di Hari yang Sama"
		elif day_shift > 0:
			day_desc = f"Keesokan Harinya (+{day_shift} Hari)"
		else:
			day_desc = f"Hari Sebelumnya ({day_shift} Hari)"
		
		if diff_hours > 0:
			diff_str = f"+{diff_hours} jam"
		elif diff_hours < 0:
			diff_str = f"{diff_hours} jam"
		else:
			diff_str = "waktu yang sama"
		
		result_text = (
			f"=== HASIL KONVERSI WAKTU JADWALKU ===\n\n"
			f"Jika di {src_data['country']}:\n"
			f"Pukul {src_h:02d}:{src_m:02d}\n\n"
			f"Maka di {tgt_data['country']} adalah:\n"
			f"Pukul {tgt_h:02d}:{src_m:02d} ({day_desc})\n\n"
			f"Catatan: Selisih waktu adalah {diff_str}."
		)
		self.txt_result.SetValue(result_text)
		if speak and event is not None:
			speak_msg = f"Jika di {src_data['country']} pukul {src_h:02d}:{src_m:02d}, maka di {tgt_data['country']} adalah pukul {tgt_h:02d}:{src_m:02d} ({day_desc}, selisih {diff_str})."
			ui.message(speak_msg)





import wx
import os
import threading
from globalPlugins.jadwalku.voicePackManager import VoiceRecorder, VoicePackManager, trim_silence

WORDS_TO_RECORD = ["sekarang", "waktu", "pukul", "jam", "tepat", "lewat", "menit", "detik", "am", "pm"] + [str(i) for i in range(60)]



import hashlib
def hash_password(pwd):
	if not pwd: return ""
	return hashlib.sha256(pwd.encode('utf-8')).hexdigest()


class VoicePackManagementDialog(wx.Dialog):
	def __init__(self, parent, add_on_dir, audio_manager=None):
		super().__init__(parent, title="JadwalKu Voice Pack Manager", size=(600, 400), style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)
		self.add_on_dir = add_on_dir
		self.audio = audio_manager
		from .voicePackManager import VoicePackManager
		self.vp_manager = VoicePackManager(add_on_dir)
		
		sizer = wx.BoxSizer(wx.VERTICAL)
		
		lbl = wx.StaticText(self, label="Daftar Paket Suara (Voice Packs):")
		sizer.Add(lbl, 0, wx.ALL, 10)
		
		self.lst_packs = wx.ListCtrl(self, style=wx.LC_REPORT | wx.LC_SINGLE_SEL)
		self.lst_packs.SetName("Daftar Paket Suara (Voice Packs):")
		self.lst_packs.SetToolTip("Daftar Paket Suara (Voice Packs):")
		self.lst_packs.InsertColumn(0, "Nama Paket", width=200)
		self.lst_packs.InsertColumn(1, "Status", width=120)
		self.lst_packs.InsertColumn(2, "Privasi", width=100)
		self.lst_packs.InsertColumn(3, "Pembuat", width=150)
		sizer.Add(self.lst_packs, 1, wx.EXPAND | wx.ALL, 10)
		
		btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
		self.btn_new = wx.Button(self, label="&Buat Paket Baru")
		self.btn_new.Bind(wx.EVT_BUTTON, self.onNew)
		btn_sizer.Add(self.btn_new, 0, wx.ALL, 5)
		
		self.btn_edit = wx.Button(self, label="&Lanjutkan / Edit")
		self.btn_edit.Bind(wx.EVT_BUTTON, self.onEdit)
		btn_sizer.Add(self.btn_edit, 0, wx.ALL, 5)
		
		self.btn_del = wx.Button(self, label="&Hapus")
		self.btn_del.Bind(wx.EVT_BUTTON, self.onDelete)
		btn_sizer.Add(self.btn_del, 0, wx.ALL, 5)
		
		self.btn_close = wx.Button(self, id=wx.ID_CANCEL, label="&Tutup (Esc)")
		btn_sizer.Add(self.btn_close, 0, wx.ALL, 5)
		
		sizer.Add(btn_sizer, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.ALL, 10)
		
		self.SetSizer(sizer)
		self.refresh_list()
		self.lst_packs.SetFocus()

	def onContextualHelp(self, evt):
		text = "BANTUAN TOKO VOICE PACK:\n\n- Di sini Anda dapat memanajemen paket suara (Voice Pack).\n- JadwalKu dapat menggunakan rekaman suara asli manusia sebagai notifikasi jam."
		dlg = ContextualHelpDialog(self, "Bantuan: JadwalKu Store", text)
		dlg.ShowModal()
		dlg.Destroy()

	def refresh_list(self):
		self.lst_packs.DeleteAllItems()
		self.packs = self.vp_manager.get_available_packs()
		for i, p in enumerate(self.packs):
			status = "Draft ({}%)".format(int((p['recorded_words']/70)*100)) if p.get("is_draft") else "Selesai"
			privacy = "Terkunci" if p.get("password_hash") else "Publik"
			if p.get("is_permanent"):
				privacy += " (Permanen)"
			
			self.lst_packs.InsertItem(i, p["name"])
			self.lst_packs.SetItem(i, 1, status)
			self.lst_packs.SetItem(i, 2, privacy)
			self.lst_packs.SetItem(i, 3, p["author"])
			self.lst_packs.SetItemData(i, i)

	def onNew(self, evt):
		try:
			dlg = VoiceStudioDialog(self, self.add_on_dir, audio_manager=self.audio)
			dlg.ShowModal()
			dlg.Destroy()
			self.refresh_list()
		except Exception as e:
			import traceback
			import ui
			ui.message(f"Error onNew: {e}\n{traceback.format_exc().splitlines()[-1]}")

	def onEdit(self, evt):
		sel = self.lst_packs.GetFirstSelected()
		if sel < 0: return
		p = self.packs[self.lst_packs.GetItemData(sel)]
		
		pwd_hash = p.get("password_hash", "")
		if pwd_hash:
			import wx
			pwd_dlg = wx.TextEntryDialog(self, "Masukkan kata sandi untuk mengedit paket ini:", "Otorisasi Diperlukan", style=wx.TE_PASSWORD | wx.OK | wx.CANCEL)
			if pwd_dlg.ShowModal() == wx.ID_OK:
				inp = pwd_dlg.GetValue()
				if hash_password(inp) != pwd_hash:
					import ui
					ui.message("Kata sandi salah!")
					pwd_dlg.Destroy()
					return
			else:
				pwd_dlg.Destroy()
				return
			pwd_dlg.Destroy()
			
		# Ekstrak untuk edit
		import os
		pack_path = os.path.join(self.vp_manager.pack_dir, p["id"])
		meta = self.vp_manager.extract_for_edit(pack_path)
		if not meta:
			import ui
			ui.message("Gagal mengekstrak paket suara.")
			return
			
		try:
			dlg = VoiceStudioDialog(self, self.add_on_dir, audio_manager=self.audio, edit_meta=meta, edit_filename=p["id"])
			dlg.ShowModal()
			dlg.Destroy()
			self.refresh_list()
		except Exception as e:
			import traceback
			import ui
			ui.message(f"Error onEdit: {e}\n{traceback.format_exc().splitlines()[-1]}")

	def onDelete(self, evt):
		sel = self.lst_packs.GetFirstSelected()
		if sel < 0: return
		p = self.packs[self.lst_packs.GetItemData(sel)]
		
		if p.get("is_permanent"):
			import ui
			ui.message("Paket suara ini adalah contoh permanen dan tidak dapat dihapus.")
			return
			
		pwd_hash = p.get("password_hash", "")
		if pwd_hash:
			import wx
			pwd_dlg = wx.TextEntryDialog(self, "Masukkan kata sandi untuk menghapus paket ini:", "Otorisasi Diperlukan", style=wx.TE_PASSWORD | wx.OK | wx.CANCEL)
			if pwd_dlg.ShowModal() == wx.ID_OK:
				inp = pwd_dlg.GetValue()
				if hash_password(inp) != pwd_hash:
					import ui
					ui.message("Kata sandi salah!")
					pwd_dlg.Destroy()
					return
			else:
				pwd_dlg.Destroy()
				return
			pwd_dlg.Destroy()
			
		import wx
		confirm = wx.MessageDialog(self, f"Apakah Anda yakin ingin menghapus paket suara '{p['name']}'?", "Konfirmasi Hapus", wx.YES_NO | wx.ICON_WARNING)
		if confirm.ShowModal() == wx.ID_YES:
			import os
			pack_path = os.path.join(self.vp_manager.pack_dir, p["id"])
			try:
				os.remove(pack_path)
				import ui
				ui.message("Paket suara berhasil dihapus.")
				self.refresh_list()
			except Exception as e:
				import ui
				ui.message(f"Gagal menghapus: {e}")
		confirm.Destroy()

class VoiceStudioDialog(wx.Dialog):

	def __init__(self, parent, add_on_dir, audio_manager=None, edit_meta=None, edit_filename=None):
		super().__init__(parent, title="JadwalKu Voice Pack Studio", size=(650, 500), style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)
		self.add_on_dir = add_on_dir
		self.audio = audio_manager
		self.edit_meta = edit_meta
		self.edit_filename = edit_filename
		
		from .voicePackManager import VoicePackManager, VoiceRecorder
		self.vp_manager = VoicePackManager(add_on_dir)
		self.recorder = VoiceRecorder()
		if not edit_meta:
			self.session_dir = self.vp_manager.init_recording_session()
		else:
			self.session_dir = self.vp_manager.temp_session_dir
		
		self.current_step = 0 # 0: Test Mic, 1: Metadata, 2: Studio
		self.current_word_idx = 0
		
		self.main_sizer = wx.BoxSizer(wx.VERTICAL)
		
		# --- Panel 1: Tes Mikrofon (Langkah 1) ---
		self.pnl_step1 = wx.Panel(self)
		step1_sizer = wx.BoxSizer(wx.VERTICAL)
		
		step1_sizer.Add(wx.StaticText(self.pnl_step1, label="Langkah 1: Tes Kesiapan Mikrofon & Speaker"), 0, wx.ALL, 5)
		
		self.in_devices = self.recorder.get_input_devices()
		self.out_devices = self.recorder.get_output_devices()
		in_names = [d[1] for d in self.in_devices]
		out_names = [d[1] for d in self.out_devices]

		grid_audio = wx.FlexGridSizer(2, 2, 5, 5)
		grid_audio.AddGrowableCol(1)
		
		grid_audio.Add(wx.StaticText(self.pnl_step1, label="Pilih &Mikrofon:"), 0, wx.ALIGN_CENTER_VERTICAL)
		self.cbo_mic = wx.Choice(self.pnl_step1, choices=in_names)
		self.cbo_mic.SetName("Pilih Mikrofon:")
		self.cbo_mic.SetToolTip("Pilih Mikrofon:")
		self.cbo_mic.SetSelection(0)
		self.cbo_mic.Bind(wx.EVT_CHOICE, self.onChangeAudioDevice)
		grid_audio.Add(self.cbo_mic, 1, wx.EXPAND)
		
		grid_audio.Add(wx.StaticText(self.pnl_step1, label="Pilih &Speaker:"), 0, wx.ALIGN_CENTER_VERTICAL)
		self.cbo_spk = wx.Choice(self.pnl_step1, choices=out_names)
		self.cbo_spk.SetName("Pilih Speaker:")
		self.cbo_spk.SetToolTip("Pilih Speaker:")
		self.cbo_spk.SetSelection(0)
		self.cbo_spk.Bind(wx.EVT_CHOICE, self.onChangeAudioDevice)
		grid_audio.Add(self.cbo_spk, 1, wx.EXPAND)
		
		step1_sizer.Add(grid_audio, 0, wx.EXPAND | wx.ALL, 10)
		
		step1_sizer.Add(wx.StaticText(self.pnl_step1, label="Tekan tombol di bawah untuk merekam suara selama 3 detik. Pastikan tidak ada suara bising di sekitar Anda."), 0, wx.ALL, 5)
		
		btn_sizer_mic = wx.BoxSizer(wx.HORIZONTAL)
		self.btn_test_mic = wx.Button(self.pnl_step1, label="&Mulai Rekam 3 Detik")
		self.btn_test_mic.Bind(wx.EVT_BUTTON, self.onTestMic)
		btn_sizer_mic.Add(self.btn_test_mic, 0, wx.ALL, 5)
		
		self.btn_play_test = wx.Button(self.pnl_step1, label="&Putar Hasil Tes")
		self.btn_play_test.Bind(wx.EVT_BUTTON, self.onPlayTestMic)
		self.btn_play_test.Disable()
		btn_sizer_mic.Add(self.btn_play_test, 0, wx.ALL, 5)
		
		step1_sizer.Add(btn_sizer_mic, 0, wx.EXPAND | wx.ALL, 5)
		
		btn_sizer1 = wx.BoxSizer(wx.HORIZONTAL)
		self.btn_next_step1 = wx.Button(self.pnl_step1, label="Lanjut ke &Langkah 2")
		self.btn_next_step1.Bind(wx.EVT_BUTTON, self.onNextStep1)
		btn_sizer1.Add(self.btn_next_step1, 0, wx.ALL, 5)
		
		self.btn_close1 = wx.Button(self.pnl_step1, id=wx.ID_CANCEL, label="&Tutup")
		btn_sizer1.Add(self.btn_close1, 0, wx.ALL, 5)
		
		step1_sizer.Add(btn_sizer1, 0, wx.ALIGN_RIGHT | wx.ALL, 10)
		
		self.pnl_step1.SetSizer(step1_sizer)
		self.main_sizer.Add(self.pnl_step1, 1, wx.EXPAND)
		
		# --- Panel 2: Metadata Paket (Langkah 2) ---
		self.pnl_step2 = wx.Panel(self)
		step2_sizer = wx.BoxSizer(wx.VERTICAL)
		
		step2_sizer.Add(wx.StaticText(self.pnl_step2, label="Langkah 2: Identitas Paket Suara"), 0, wx.ALL, 5)
		
		grid = wx.FlexGridSizer(0, 2, 10, 10)
		grid.AddGrowableCol(1)
		
		grid.Add(wx.StaticText(self.pnl_step2, label="&Nama Paket Suara:"), 0, wx.ALIGN_CENTER_VERTICAL)
		self.txt_pack_name = wx.TextCtrl(self.pnl_step2, value="Suara Kustom")
		self.txt_pack_name.SetName("Nama Paket Suara:")
		self.txt_pack_name.SetToolTip("Nama Paket Suara:")
		grid.Add(self.txt_pack_name, 1, wx.EXPAND)
		
		grid.Add(wx.StaticText(self.pnl_step2, label="Nama &Pembuat:"), 0, wx.ALIGN_CENTER_VERTICAL)
		self.txt_author = wx.TextCtrl(self.pnl_step2, value="Pengguna JadwalKu")
		self.txt_author.SetName("Nama Pembuat:")
		self.txt_author.SetToolTip("Nama Pembuat:")
		grid.Add(self.txt_author, 1, wx.EXPAND)
		
		grid.Add(wx.StaticText(self.pnl_step2, label="&Deskripsi:"), 0, wx.ALIGN_CENTER_VERTICAL)
		self.txt_desc = wx.TextCtrl(self.pnl_step2, value="Paket suara buatanku.")
		self.txt_desc.SetName("Deskripsi:")
		self.txt_desc.SetToolTip("Deskripsi:")
		grid.Add(self.txt_desc, 1, wx.EXPAND)
		
		grid.Add(wx.StaticText(self.pnl_step2, label="&Kata Sandi (Opsional):"), 0, wx.ALIGN_CENTER_VERTICAL)
		self.txt_pwd = wx.TextCtrl(self.pnl_step2, style=wx.TE_PASSWORD)
		self.txt_pwd.SetName("Kata Sandi (Opsional):")
		self.txt_pwd.SetToolTip("Kata Sandi (Opsional):")
		grid.Add(self.txt_pwd, 1, wx.EXPAND)
		
		if self.edit_meta:
			self.txt_pack_name.SetValue(self.edit_meta.get("name", ""))
			self.txt_author.SetValue(self.edit_meta.get("author", ""))
			self.txt_desc.SetValue(self.edit_meta.get("description", ""))
			if self.edit_meta.get("password_hash"):
				self.txt_pwd.SetValue("********") # Dummy password representation
		
		step2_sizer.Add(grid, 0, wx.EXPAND | wx.ALL, 10)
		
		btn_sizer2 = wx.BoxSizer(wx.HORIZONTAL)
		self.btn_next_step2 = wx.Button(self.pnl_step2, label="&Lanjut ke Langkah 3 (Studio Rekaman)")
		self.btn_next_step2.Bind(wx.EVT_BUTTON, self.onNextStep2)
		btn_sizer2.Add(self.btn_next_step2, 0, wx.ALL, 5)
		
		self.btn_close2 = wx.Button(self.pnl_step2, id=wx.ID_CANCEL, label="&Tutup")
		btn_sizer2.Add(self.btn_close2, 0, wx.ALL, 5)
		
		step2_sizer.Add(btn_sizer2, 0, wx.ALIGN_RIGHT | wx.ALL, 10)
		
		self.pnl_step2.SetSizer(step2_sizer)
		self.main_sizer.Add(self.pnl_step2, 1, wx.EXPAND)
		
		# --- Panel 3: Studio Rekaman ---
		self.pnl_studio = wx.Panel(self)
		studio_sizer = wx.BoxSizer(wx.VERTICAL)
		
		self.lbl_progress = wx.StaticText(self.pnl_studio, label="")
		studio_sizer.Add(self.lbl_progress, 0, wx.ALL | wx.ALIGN_CENTER_HORIZONTAL, 10)
		
		studio_sizer.Add(wx.StaticText(self.pnl_studio, label="Kata/Frasa yang Harus Diucapkan:"), 0, wx.LEFT | wx.TOP, 10)
		
		self.txt_word = wx.TextCtrl(self.pnl_studio, style=wx.TE_CENTER)
		self.txt_word.SetName("Kata/Frasa yang Harus Diucapkan:")
		self.txt_word.SetToolTip("Kata/Frasa yang Harus Diucapkan:")
		self.txt_word.Bind(wx.EVT_CHAR, self.onWordChar)
		font = self.txt_word.GetFont()
		font.SetPointSize(18)
		font.SetWeight(wx.FONTWEIGHT_BOLD)
		self.txt_word.SetFont(font)
		studio_sizer.Add(self.txt_word, 0, wx.EXPAND | wx.ALL, 10)
		
		btn_sizer1 = wx.BoxSizer(wx.HORIZONTAL)
		self.btn_record = wx.Button(self.pnl_studio, label="&Mulai Rekam (Spasi)")
		self.btn_record.Bind(wx.EVT_BUTTON, self.onRecordToggle)
		btn_sizer1.Add(self.btn_record, 0, wx.ALL, 5)
		
		self.btn_play_result = wx.Button(self.pnl_studio, label="Putar &Hasil")
		self.btn_play_result.Bind(wx.EVT_BUTTON, self.onPlayResult)
		btn_sizer1.Add(self.btn_play_result, 0, wx.ALL, 5)
		
		self.btn_play_sample = wx.Button(self.pnl_studio, label="Putar &Contoh")
		self.btn_play_sample.Bind(wx.EVT_BUTTON, self.onPlaySample)
		btn_sizer1.Add(self.btn_play_sample, 0, wx.ALL, 5)
		
		studio_sizer.Add(btn_sizer1, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.ALL, 5)
		
		btn_sizer2 = wx.BoxSizer(wx.HORIZONTAL)
		self.btn_prev = wx.Button(self.pnl_studio, label="<- S&ebelumnya")
		self.btn_prev.Bind(wx.EVT_BUTTON, self.onPrevWord)
		btn_sizer2.Add(self.btn_prev, 0, wx.ALL, 5)
		
		self.btn_next = wx.Button(self.pnl_studio, label="Sela&njutnya ->")
		self.btn_next.Bind(wx.EVT_BUTTON, self.onNextWord)
		btn_sizer2.Add(self.btn_next, 0, wx.ALL, 5)
		
		studio_sizer.Add(btn_sizer2, 0, wx.ALIGN_CENTER_HORIZONTAL | wx.ALL, 5)
		
		btn_sizer3 = wx.BoxSizer(wx.HORIZONTAL)
		self.btn_draft = wx.Button(self.pnl_studio, label="Simpan P&rogress (Draft)")
		self.btn_draft.Bind(wx.EVT_BUTTON, lambda e: self.onFinish(e, is_draft=True))
		btn_sizer3.Add(self.btn_draft, 0, wx.ALL, 5)
		
		self.btn_finish = wx.Button(self.pnl_studio, label="&Simpan & Ekspor Paket Suara...")
		self.btn_finish.Bind(wx.EVT_BUTTON, lambda e: self.onFinish(e, is_draft=False))
		btn_sizer3.Add(self.btn_finish, 0, wx.ALL, 5)
		
		self.btn_close3 = wx.Button(self.pnl_studio, id=wx.ID_CANCEL, label="&Tutup (Esc)")
		btn_sizer3.Add(self.btn_close3, 0, wx.ALL, 5)
		
		studio_sizer.Add(btn_sizer3, 0, wx.ALIGN_RIGHT | wx.ALL, 10)
		
		self.pnl_studio.SetSizer(studio_sizer)
		self.main_sizer.Add(self.pnl_studio, 1, wx.EXPAND)
		
		self.pnl_step2.Hide()
		self.pnl_studio.Hide()
		self.SetSizer(self.main_sizer)
		self.btn_test_mic.SetFocus()

	def play_audio(self, filepath):
		if not os.path.exists(filepath):
			import ui
			ui.message("Audio belum direkam atau file tidak ditemukan.")
			return
		# Gunakan play_audio dari NativeAudioIO
		self.recorder.play_audio(filepath)

	def onChangeAudioDevice(self, evt):
		in_idx = self.cbo_mic.GetSelection()
		out_idx = self.cbo_spk.GetSelection()
		if in_idx >= 0 and in_idx < len(self.in_devices):
			self.recorder.set_input_device(self.in_devices[in_idx][0])
		if out_idx >= 0 and out_idx < len(self.out_devices):
			self.recorder.set_output_device(self.out_devices[out_idx][0])

	def onTestMic(self, evt):
		if self.recorder.is_recording():
			return
		self.btn_test_mic.Disable()
		self.btn_play_test.Disable()
		self.btn_next_step1.Disable()
		self.btn_test_mic.SetLabel("Merekam... (Bicara Sekarang!)")
		import ui
		ui.message("Mulai merekam. Silakan bicara sekarang selama 3 detik.")
		
		if self.recorder.start_recording():
			def record_task():
				import time
				time.sleep(3)
				import wx
				wx.CallAfter(self.finishTestMic)
			import threading
			t = threading.Thread(target=record_task)
			t.daemon = True
			t.start()
		else:
			ui.message("Gagal mengakses mikrofon.")
			self.btn_test_mic.Enable()
			self.btn_next_step1.Enable()
			self.btn_test_mic.SetLabel("&Mulai Rekam 3 Detik")
			
	def finishTestMic(self):
		import os
		test_wav = os.path.join(self.session_dir, "test_mic.wav")
		if self.recorder.stop_and_save(test_wav):
			import ui
			ui.message("Selesai merekam. Silakan tekan Putar Hasil Tes.")
			self.btn_play_test.Enable()
			self.btn_play_test.SetFocus()
		self.btn_test_mic.Enable()
		self.btn_next_step1.Enable()
		self.btn_test_mic.SetLabel("&Ulangi Rekam 3 Detik")
		
	def onPlayTestMic(self, evt):
		import os
		test_wav = os.path.join(self.session_dir, "test_mic.wav")
		self.play_audio(test_wav)

	def onNextStep1(self, evt):
		self.pnl_step1.Hide()
		self.pnl_step2.Show()
		self.Layout()
		self.txt_pack_name.SetFocus()
		
	def onNextStep2(self, evt):
		# Validasi
		if not self.txt_pack_name.GetValue().strip():
			import ui
			ui.message("Nama paket tidak boleh kosong.")
			return
		self.pnl_step2.Hide()
		self.pnl_studio.Show()
		self.Layout()
		
		if self.edit_meta:
			import os
			# Cari kata pertama yang belum direkam
			for i, w in enumerate(WORDS_TO_RECORD):
				if not os.path.exists(self.vp_manager.get_session_wav_path(w)):
					self.current_word_idx = i
					break
					
		self.updateStudioUI()
		self.btn_record.SetFocus()

	def onContextualHelp(self, evt):
		text = "BANTUAN STUDIO REKAMAN:\n\n- Anda akan dipandu untuk merekam 70 kata pendek yang dibutuhkan oleh JadwalKu untuk membentuk kalimat pembacaan jam.\n- Pastikan mikrofon berfungsi. Gunakan tombol Rekam/Stop (Spasi) untuk merekam."
		dlg = ContextualHelpDialog(self, "Bantuan: Studio Rekaman Suara", text)
		dlg.ShowModal()
		dlg.Destroy()

	def updateStudioUI(self):
		import os
		
		word = WORDS_TO_RECORD[self.current_word_idx]
		self.lbl_progress.SetLabel(f"Item {self.current_word_idx + 1} dari {len(WORDS_TO_RECORD)}")
		self.txt_word.SetValue(word)
		
		self.btn_prev.Enable(self.current_word_idx > 0)
		self.btn_next.Enable(self.current_word_idx < len(WORDS_TO_RECORD) - 1)
		
		# Cek apakah sudah direkam
		path = self.vp_manager.get_session_wav_path(word)
		if os.path.exists(path):
			self.btn_play_result.Enable(True)
		else:
			self.btn_play_result.Enable(False)

	def onWordChar(self, evt):
		key = evt.GetKeyCode()
		# Allow navigation keys (arrows, home, end) and Tab
		if key in (wx.WXK_LEFT, wx.WXK_RIGHT, wx.WXK_UP, wx.WXK_DOWN, wx.WXK_HOME, wx.WXK_END, wx.WXK_PAGEUP, wx.WXK_PAGEDOWN, wx.WXK_TAB):
			evt.Skip()

	def onRecordToggle(self, evt):
		import ui
		import os
		if not self.recorder.is_recording():
			# Stop NativeAudioIO playback if any
			# Since we are recording now, we don't need to purge winsound
			if self.recorder.start_recording():
				self.btn_record.SetLabel("&Berhenti Rekam (Spasi)")
				ui.message("Merekam...")
				self.btn_play_result.Disable()
				self.btn_play_sample.Disable()
				self.btn_prev.Disable()
				self.btn_next.Disable()
		else:
			from .voicePackManager import trim_silence
			word = WORDS_TO_RECORD[self.current_word_idx]
			raw_wav = self.vp_manager.get_session_wav_path(word + "_raw")
			final_wav = self.vp_manager.get_session_wav_path(word)
			
			if self.recorder.stop_and_save(raw_wav):
				# Trim hening
				trim_silence(raw_wav, final_wav)
				if os.path.exists(raw_wav): os.remove(raw_wav)
				
				# Putar otomatis
				ui.message("Disimpan.")
				self.play_audio(final_wav)
				
			self.btn_record.SetLabel("&Mulai Rekam (Spasi)")
			self.btn_play_sample.Enable(True)
			self.updateStudioUI()
			
	def onPlayResult(self, evt):
		
		word = WORDS_TO_RECORD[self.current_word_idx]
		path = self.vp_manager.get_session_wav_path(word)
		self.play_audio(path)
		
	def onPlaySample(self, evt):
		import os
		
		word = WORDS_TO_RECORD[self.current_word_idx]
		sample_path = os.path.join(self.add_on_dir, "voice_master", f"{word}.wav")
		if os.path.exists(sample_path):
			self.play_audio(sample_path)
		else:
			import ui
			ui.message("Suara contoh master belum tersedia.")
			
	def onPrevWord(self, evt):
		if self.current_word_idx > 0:
			self.current_word_idx -= 1
			self.updateStudioUI()
			self.txt_word.SetFocus()
			
	def onNextWord(self, evt):
		
		if self.current_word_idx < len(WORDS_TO_RECORD) - 1:
			self.current_word_idx += 1
			self.updateStudioUI()
			self.txt_word.SetFocus()
			
	def onFinish(self, evt, is_draft=False):
		import os
		
		if not is_draft:
			# Cek apakah semua 70 item sudah direkam
			missing = []
			for w in WORDS_TO_RECORD:
				if not os.path.exists(self.vp_manager.get_session_wav_path(w)):
					missing.append(w)
			
			if missing:
				import ui
				ui.message(f"Masih ada {len(missing)} item yang belum direkam. Silakan lengkapi terlebih dahulu, atau gunakan Simpan Progress (Draft).")
				return
				
		meta = {
			"name": self.txt_pack_name.GetValue().strip(),
			"author": self.txt_author.GetValue().strip(),
			"description": self.txt_desc.GetValue().strip(),
			"version": "1.0",
			"words": WORDS_TO_RECORD
		}
		
		pwd_input = self.txt_pwd.GetValue()
		if pwd_input != "********": # If it changed or is new
			pwd_hash = hash_password(pwd_input)
		else:
			pwd_hash = self.edit_meta.get("password_hash", "") if self.edit_meta else ""
			
		is_perm = self.edit_meta.get("is_permanent", False) if self.edit_meta else False
		
		safe_name = "".join(c for c in meta["name"] if c.isalnum() or c in " _-").strip().replace(" ", "_")
		if not safe_name: safe_name = "MyVoice"
		
		out_file = self.edit_filename if self.edit_filename else f"{safe_name}.jvp"
		try:
			path = self.vp_manager.export_pack(meta, out_file, is_draft=is_draft, password_hash=pwd_hash, is_permanent=is_perm)
			import ui
			if is_draft:
				ui.message(f"Progress disimpan sebagai draft!")
			else:
				ui.message(f"Berhasil! Paket suara telah diekspor dan siap digunakan.")
			self.Destroy()
		except Exception as e:
			import ui
			ui.message(f"Gagal mengekspor: {str(e)}")


class ActiveTimerManagerDialog(wx.Dialog):
	def __init__(self, parent, scheduler):
		super().__init__(parent, title="Manajer Timer Aktif")
		
		mainSizer = wx.BoxSizer(wx.VERTICAL)
		
		lbl = wx.StaticText(self, label="Pilih timer yang sedang berjalan:")
		mainSizer.Add(lbl, 0, wx.ALL, 5)
		
		self.timerList = wx.ListBox(self, choices=self.get_timer_choices())
		self.timerList.SetSelection(0)
		mainSizer.Add(self.timerList, 1, wx.ALL | wx.EXPAND, 5)
		
		btnSizer = wx.BoxSizer(wx.HORIZONTAL)
		
		self.pauseBtn = wx.Button(self, label="&Jeda / Lanjutkan")
		self.pauseBtn.Bind(wx.EVT_BUTTON, self.onPauseResume)
		btnSizer.Add(self.pauseBtn, 0, wx.ALL, 5)
		
		self.stopBtn = wx.Button(self, label="&Berhenti")
		self.stopBtn.Bind(wx.EVT_BUTTON, self.onStop)
		btnSizer.Add(self.stopBtn, 0, wx.ALL, 5)
		
		self.newBtn = wx.Button(self, label="Buat Timer &Baru")
		self.newBtn.Bind(wx.EVT_BUTTON, self.onNew)
		btnSizer.Add(self.newBtn, 0, wx.ALL, 5)
		
		self.closeBtn = wx.Button(self, id=wx.ID_CANCEL, label="Tutu&p")
		btnSizer.Add(self.closeBtn, 0, wx.ALL, 5)
		
		mainSizer.Add(btnSizer, 0, wx.ALIGN_RIGHT)
		
		self.SetSizerAndFit(mainSizer)
		self.CenterOnScreen()

	def get_timer_choices(self):
		import datetime
		now = datetime.datetime.now()
		choices = []
		for idx, t in enumerate(self.scheduler.quick_timers):
			state = t.get("state", "running")
			status = ""
			if state == "paused":
				status = " [DIJEDA]"
			elif state == "prep":
				status = " [Persiapan]"
			choices.append(f"{idx + 1}. Timer {t['duration']} {t['unit']}{status}")
		return choices

	def refresh_list(self):
		sel = self.timerList.GetSelection()
		self.timerList.Set(self.get_timer_choices())
		if sel != wx.NOT_FOUND and sel < self.timerList.GetCount():
			self.timerList.SetSelection(sel)
		elif self.timerList.GetCount() > 0:
			self.timerList.SetSelection(0)
		else:
			import ui
			ui.message("Semua timer telah dihentikan.")
			self.Destroy()

	def onPauseResume(self, event):
		sel = self.timerList.GetSelection()
		if sel != wx.NOT_FOUND:
			t = self.scheduler.quick_timers[sel]
			if t.get("state") == "paused":
				self.scheduler.resume_quick_timer(sel)
			else:
				self.scheduler.pause_quick_timer(sel)
			self.refresh_list()

	def onStop(self, event):
		sel = self.timerList.GetSelection()
		if sel != wx.NOT_FOUND:
			self.scheduler.stop_quick_timer(sel)
			self.refresh_list()

	def onNew(self, event):
		self.Destroy()
		import wx
		dlg = QuickTimerDialog(None, self.scheduler)
		dlg.Show()


class ActiveAlarmManagerDialog(wx.Dialog):
	def __init__(self, parent, scheduler):
		super().__init__(parent, title="Manajer Alarm Aktif")
		
		mainSizer = wx.BoxSizer(wx.VERTICAL)
		
		lbl = wx.StaticText(self, label="Pilih alarm yang sedang berjalan:")
		mainSizer.Add(lbl, 0, wx.ALL, 5)
		
		self.alarmList = wx.ListBox(self, choices=self.get_alarm_choices())
		self.alarmList.SetSelection(0)
		mainSizer.Add(self.alarmList, 1, wx.ALL | wx.EXPAND, 5)
		
		btnSizer = wx.BoxSizer(wx.HORIZONTAL)
		
		self.pauseBtn = wx.Button(self, label="&Jeda / Lanjutkan")
		self.pauseBtn.Bind(wx.EVT_BUTTON, self.onPauseResume)
		btnSizer.Add(self.pauseBtn, 0, wx.ALL, 5)
		
		self.stopBtn = wx.Button(self, label="&Berhenti")
		self.stopBtn.Bind(wx.EVT_BUTTON, self.onStop)
		btnSizer.Add(self.stopBtn, 0, wx.ALL, 5)
		
		self.newBtn = wx.Button(self, label="Buat Alarm &Baru")
		self.newBtn.Bind(wx.EVT_BUTTON, self.onNew)
		btnSizer.Add(self.newBtn, 0, wx.ALL, 5)
		
		self.closeBtn = wx.Button(self, id=wx.ID_CANCEL, label="Tutu&p")
		btnSizer.Add(self.closeBtn, 0, wx.ALL, 5)
		
		mainSizer.Add(btnSizer, 0, wx.ALIGN_RIGHT)
		
		self.SetSizerAndFit(mainSizer)
		self.CenterOnScreen()

	def get_alarm_choices(self):
		choices = []
		for idx, t in enumerate(self.scheduler.one_time_alarms):
			state = t.get("state", "active")
			status = " [DIJEDA]" if state == "paused" else ""
			choices.append(f"{idx + 1}. Alarm {t['time_str']}{status}")
		return choices

	def refresh_list(self):
		sel = self.alarmList.GetSelection()
		self.alarmList.Set(self.get_alarm_choices())
		if sel != wx.NOT_FOUND and sel < self.alarmList.GetCount():
			self.alarmList.SetSelection(sel)
		elif self.alarmList.GetCount() > 0:
			self.alarmList.SetSelection(0)
		else:
			import ui
			ui.message("Semua alarm telah dihentikan.")
			self.Destroy()

	def onPauseResume(self, event):
		sel = self.alarmList.GetSelection()
		if sel != wx.NOT_FOUND:
			t = self.scheduler.one_time_alarms[sel]
			if t.get("state") == "paused":
				self.scheduler.resume_one_time_alarm(sel)
			else:
				self.scheduler.pause_one_time_alarm(sel)
			self.refresh_list()

	def onStop(self, event):
		sel = self.alarmList.GetSelection()
		if sel != wx.NOT_FOUND:
			self.scheduler.stop_one_time_alarm(sel)
			self.refresh_list()

	def onNew(self, event):
		self.Destroy()
		import wx
		dlg = OneTimeAlarmDialog(None, self.scheduler)
		dlg.Show()

class HabitTrackerDialog(wx.Dialog):
	def __init__(self, parent, scheduler, habit_manager):
		super().__init__(parent, title="Pelacak Kebiasaan & Status Jadwal (Habit Tracker)", size=(600, 450), style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)
		self.scheduler = scheduler
		self.habit_manager = habit_manager
		self.habit_manager.check_and_reset_streaks()
		
		sizer = wx.BoxSizer(wx.VERTICAL)
		
		info_label = wx.StaticText(self, label="Pilih jadwal aktif hari ini, lalu tekan Enter atau Spasi untuk mengambil tindakan (Selesai/Belum/Tunda):")
		sizer.Add(info_label, 0, wx.ALL, 10)
		
		self.lb_habits = wx.ListBox(self, style=wx.LB_SINGLE)
		self.lb_habits.Bind(wx.EVT_CHAR_HOOK, self.onKeyDown)
		self.lb_habits.Bind(wx.EVT_CONTEXT_MENU, lambda e: self.showContextMenu())
		self.lb_habits.Bind(wx.EVT_LISTBOX_DCLICK, lambda e: self.showContextMenu())
		
		self.active_schedules = self._get_active_schedules_today()
		self._populate_list()
		
		sizer.Add(self.lb_habits, 1, wx.EXPAND | wx.LEFT | wx.RIGHT, 10)
		
		btnSizer = wx.StdDialogButtonSizer()
		self.btnClose = wx.Button(self, wx.ID_CANCEL, label="&Tutup")
		btnSizer.AddButton(self.btnClose)
		btnSizer.Realize()
		sizer.Add(btnSizer, 0, wx.ALIGN_RIGHT | wx.ALL, 15)
		
		self.SetSizer(sizer)
		self.Centre()
		self.lb_habits.SetFocus()

	def _get_active_schedules_today(self):
		if not self.scheduler or not self.scheduler.config:
			return []
			
		schedules = self.scheduler.config.get_schedules()
		active_today = []
		
		import datetime
		now = datetime.datetime.now()
		day_map = {0: "Senin", 1: "Selasa", 2: "Rabu", 3: "Kamis", 4: "Jumat", 5: "Sabtu", 6: "Minggu"}
		current_day_str = day_map[now.weekday()]
		is_weekend = now.weekday() >= 5
		
		for s in schedules:
			if not s.get("active", False):
				continue
			if not s.get("is_habit", True):
				continue
				
			freq = s.get("frequency", "Setiap Hari")
			is_active = False
			
			if freq == "Setiap Hari":
				is_active = True
			elif freq == "Hari Kerja (Senin - Jumat)" and not is_weekend:
				is_active = True
			elif freq == "Akhir Pekan (Sabtu - Minggu)" and is_weekend:
				is_active = True
			elif freq == current_day_str:
				is_active = True
			elif freq.startswith("Sesuaikan Hari"):
				if current_day_str in s.get("custom_days", []):
					is_active = True
			elif freq == "Sekali Waktu (Tanggal Spesifik)":
				if s.get("date") == now.strftime("%Y-%m-%d"):
					is_active = True
					
			if is_active:
				active_today.append(s)
				
		return active_today

	def _get_arrived_count(self, s):
		interval = s.get("interval_hour", 0)
		import datetime
		now = datetime.datetime.now()
		
		if interval == 0:
			sched_h = s.get("hour", 0)
			sched_m = s.get("minute", 0)
			if now.hour > sched_h or (now.hour == sched_h and now.minute >= sched_m):
				return 1
			return 0
			
		start_h = s.get("hour", 0)
		start_m = s.get("minute", 0)
		end_h = s.get("interval_end_hour", 23)
		
		if now.hour < start_h or (now.hour == start_h and now.minute < start_m):
			return 0
			
		elapsed_hours = now.hour - start_h
		if elapsed_hours < 0:
			elapsed_hours += 24
			
		arrived = (elapsed_hours // interval) + 1
		
		target = self._get_target_count(s)
		if arrived > target:
			arrived = target
			
		return arrived

	def _get_target_count(self, s):
		interval = s.get("interval_hour", 0)
		if interval == 0:
			return 1
		start_hour = s.get("hour", 0)
		end_hour = s.get("interval_end_hour", 23)
		
		# e.g. start 08, end 23, interval 2 -> (23 - 8) / 2 = 7 + 1 = 8
		if start_hour <= end_hour:
			return ((end_hour - start_hour) // interval) + 1
		return 1

	def _populate_list(self):
		self.lb_habits.Clear()
		for s in self.active_schedules:
			s_id = s.get("id")
			name = s.get("name", "Jadwal")
			target = self._get_target_count(s)
			completed = self.habit_manager.get_daily_count(s_id)
			
			pct = 0
			if target > 0:
				pct = int((completed / target) * 100)
				if pct > 100: pct = 100
				
			desc = f"{name} - {completed} dari {target} ({pct}%) terselesaikan."
			self.lb_habits.Append(desc, s)

	def onKeyDown(self, event):
		keycode = event.GetKeyCode()
		if keycode in [wx.WXK_SPACE, wx.WXK_RETURN, wx.WXK_NUMPAD_ENTER]:
			self.showContextMenu()
		else:
			event.Skip()
			
	def showContextMenu(self):
		sel = self.lb_habits.GetSelection()
		if sel == wx.NOT_FOUND:
			return
			
		sched = self.lb_habits.GetClientData(sel)
		
		menu = wx.Menu()
		item_done = menu.Append(wx.ID_ANY, "1. Sudah Selesai")
		item_skip = menu.Append(wx.ID_ANY, "2. Belum / Lewati")
		item_snooze = menu.Append(wx.ID_ANY, "3. Tunda (Snooze)...")
		
		self.Bind(wx.EVT_MENU, lambda e: self.onMarkDone(sched, sel), item_done)
		self.Bind(wx.EVT_MENU, lambda e: self.onMarkSkip(sched, sel), item_skip)
		self.Bind(wx.EVT_MENU, lambda e: self.onSnooze(sched, sel), item_snooze)
		
		self.PopupMenu(menu)
		menu.Destroy()

	def onMarkDone(self, sched, index):
		s_id = sched["id"]
		target = self._get_target_count(sched)
		completed = self.habit_manager.get_daily_count(s_id)
		arrived = self._get_arrived_count(sched)
		
		if completed >= target:
			import ui
			ui.message("Jadwal ini sudah mencapai target maksimal untuk hari ini!")
			return
			
		if completed >= arrived:
			import ui
			ui.message("Belum tiba waktunya untuk rutinitas berikutnya. Harap bersabar!")
			return

		new_badge = self.habit_manager.record_completion(sched["id"], sched["name"])
		
		if new_badge:
			# Play level up sound dynamically!
			import ui
			import globalVars
			try:
				import winsound
				sounds_dir = os.path.join(os.path.dirname(__file__), "sounds")
				chime_path = os.path.join(sounds_dir, "chime.wav")
				if os.path.exists(chime_path):
					winsound.PlaySound(chime_path, winsound.SND_FILENAME | winsound.SND_ASYNC)
			except: pass
			
			msg = f"LUAR BIASA! Anda baru saja membuka {new_badge} untuk kebiasaan {sched['name']}!"
			if hasattr(ui, 'message'):
				ui.message(msg)
				
		# Jika sudah selesai, hapus dari tunda (snooze) agar tidak berbunyi lagi
		if hasattr(self, 'scheduler') and self.scheduler and s_id in self.scheduler.daily_overrides:
			del self.scheduler.daily_overrides[s_id]
			if hasattr(self.scheduler, 'config') and self.scheduler.config:
				self.scheduler.config.data["daily_overrides"] = self.scheduler.daily_overrides
				self.scheduler.config.save_data()
			
		self._populate_list()
		self.lb_habits.SetSelection(index)

	def onMarkSkip(self, sched, index):
		import ui
		interval = sched.get("interval_hour", 0)
		if interval == 0:
			import datetime
			now = datetime.datetime.now()
			new_time = now + datetime.timedelta(hours=1)
			if hasattr(self, 'scheduler') and self.scheduler:
				self.scheduler.snooze_schedule(sched["id"], new_time)
			if hasattr(ui, 'message'):
				ui.message(f"Jadwal {sched['name']} ditandai belum. Otomatis ditunda 1 jam ke {new_time.strftime('%H:%M')}.")
		else:
			if hasattr(ui, 'message'):
				ui.message(f"Jadwal {sched['name']} ditandai belum. Jadwal rutin dilewati.")

	def onSnooze(self, sched, index):
		dlg = wx.TextEntryDialog(self, "Masukkan waktu tunda (contoh: +15m, +1j, atau 14:30):", "Tunda Jadwal")
		if dlg.ShowModal() == wx.ID_OK:
			val = dlg.GetValue().strip().lower()
			if val:
				import datetime
				now = datetime.datetime.now()
				new_time = None
				
				if val.startswith("+"):
					import re
					match = re.search(r'\+?(\d+)\s*(m|j|h|menit|jam)', val)
					if match:
						amount = int(match.group(1))
						unit = match.group(2)
						if unit in ['m', 'menit']:
							new_time = now + datetime.timedelta(minutes=amount)
						elif unit in ['j', 'h', 'jam']:
							new_time = now + datetime.timedelta(hours=amount)
							
				if not new_time:
					# Try parse HH:MM
					try:
						parts = val.split(":")
						if len(parts) >= 2:
							h = int(parts[0])
							m = int(parts[1])
							new_time = now.replace(hour=h, minute=m, second=0)
							if new_time < now:
								new_time += datetime.timedelta(days=1)
					except: pass
					
				if new_time:
					# Tell scheduler to inject a snooze
					if self.scheduler:
						self.scheduler.snooze_schedule(sched["id"], new_time)
						import ui
						ui.message(f"Jadwal ditunda hingga {new_time.strftime('%H:%M')}.")
				else:
					import ui
					ui.message("Format waktu tidak dikenali.")
		dlg.Destroy()

class BadgeShowcaseDialog(wx.Dialog):
	def __init__(self, parent, habit_manager):
		super().__init__(parent, title="Pencapaian & Lencana Ketekunan", size=(700, 500), style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)
		self.habit_manager = habit_manager
		self.habit_manager.check_and_reset_streaks()
		
		sizer = wx.BoxSizer(wx.VERTICAL)
		
		sizer.Add(wx.StaticText(self, label="Gunakan panah Atas/Bawah untuk memilih jadwal. Tekan Tab untuk membaca riwayat lencana lengkap."), 0, wx.ALL, 10)
		
		split_sizer = wx.BoxSizer(wx.HORIZONTAL)
		
		self.lb_badges = wx.ListBox(self, style=wx.LB_SINGLE)
		self.lb_badges.Bind(wx.EVT_LISTBOX, self.onSelectionChanged)
		
		self.txt_history = wx.TextCtrl(self, style=wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_RICH2)
		self.txt_history.SetName("Gunakan panah Atas/Bawah untuk memilih jadwal. Tekan Tab untuk membaca riwayat lencana lengkap.")
		self.txt_history.SetToolTip("Gunakan panah Atas/Bawah untuk memilih jadwal. Tekan Tab untuk membaca riwayat lencana lengkap.")
		
		split_sizer.Add(self.lb_badges, 1, wx.EXPAND | wx.ALL, 5)
		split_sizer.Add(self.txt_history, 2, wx.EXPAND | wx.ALL, 5)
		
		sizer.Add(split_sizer, 1, wx.EXPAND | wx.ALL, 5)
		
		btnSizer = wx.StdDialogButtonSizer()
		self.btnClose = wx.Button(self, wx.ID_CANCEL, label="&Tutup")
		btnSizer.AddButton(self.btnClose)
		btnSizer.Realize()
		sizer.Add(btnSizer, 0, wx.ALIGN_RIGHT | wx.ALL, 15)
		
		self.SetSizer(sizer)
		self.Centre()
		
		self._populate_list()

	def _populate_list(self):
		self.lb_badges.Clear()
		habits = self.habit_manager.get_all_habits_summary()
		
		if not habits:
			self.lb_badges.Append("Belum ada data kebiasaan.")
			self.txt_history.SetValue("Belum ada riwayat lencana yang dapat ditampilkan.")
			return
			
		for h in habits:
			self.lb_badges.Append(f"{h['name']} - {h['highest_badge']}", h['id'])
			
		self.lb_badges.SetSelection(0)
		self.onSelectionChanged(None)
		self.lb_badges.SetFocus()

	def onSelectionChanged(self, event):
		sel = self.lb_badges.GetSelection()
		if sel != wx.NOT_FOUND:
			s_id = self.lb_badges.GetClientData(sel)
			if s_id:
				text = self.habit_manager.get_badge_history_text(s_id)
				self.txt_history.SetValue(text)


class LoncengDialog(wx.Dialog):
	def __init__(self, parent, config, audio_manager):
		super().__init__(parent, title="Pengaturan Lonceng Jam Klasik (Grandfather Clock)", size=(500, 400))
		self.config = config
		self.audio_manager = audio_manager
		self.settings = self.config.data.get("lonceng_settings", {
			"enabled": False, "volume": 80, "start_hour": 6, "end_hour": 22,
			"ticking_enabled": False, "ticking_volume": 40
		})
		
		sizer = wx.BoxSizer(wx.VERTICAL)
		
		self.chk_enabled = wx.CheckBox(self, label="&Aktifkan Pengingat Lonceng Klasik")
		self.chk_enabled.SetValue(self.settings.get("enabled", False))
		sizer.Add(self.chk_enabled, 0, wx.ALL, 5)
		
		self.chk_quarter = wx.CheckBox(self, label="Bunyikan juga setiap se&perempat jam (15, 30, 45 menit)")
		self.chk_quarter.SetValue(self.settings.get("quarter_enabled", False))
		sizer.Add(self.chk_quarter, 0, wx.LEFT | wx.RIGHT | wx.BOTTOM, 5)
		
		sizer.Add(wx.StaticText(self, label="&Volume Lonceng Utama:"), 0, wx.ALL, 5)
		self.slider_vol = wx.Slider(self, value=self.settings.get("volume", 80), minValue=0, maxValue=1200, style=wx.SL_HORIZONTAL | wx.SL_AUTOTICKS)
		self.slider_vol.SetName("Volume Lonceng Utama:")
		self.slider_vol.SetToolTip("Volume Lonceng Utama:")
		sizer.Add(self.slider_vol, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 5)
		
		hour_choices = [f"{h:02d}:00" for h in range(24)]
		
		hb_sizer = wx.BoxSizer(wx.HORIZONTAL)
		hb_sizer.Add(wx.StaticText(self, label="Jam &Mulai:"), 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)
		self.cb_start = wx.ComboBox(self, choices=hour_choices, style=wx.CB_READONLY)
		self.cb_start.SetName("Jam Mulai:")
		self.cb_start.SetToolTip("Jam Mulai:")
		self.cb_start.SetSelection(self.settings.get("start_hour", 6))
		hb_sizer.Add(self.cb_start, 1, wx.ALL, 5)
		
		hb_sizer.Add(wx.StaticText(self, label="Jam &Selesai (Tenang):"), 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)
		self.cb_end = wx.ComboBox(self, choices=hour_choices, style=wx.CB_READONLY)
		self.cb_end.SetName("Jam Selesai (Tenang):")
		self.cb_end.SetToolTip("Jam Selesai (Tenang):")
		self.cb_end.SetSelection(self.settings.get("end_hour", 22))
		hb_sizer.Add(self.cb_end, 1, wx.ALL, 5)
		sizer.Add(hb_sizer, 0, wx.EXPAND)
		
		sizer.Add(wx.StaticLine(self), 0, wx.EXPAND | wx.ALL, 10)
		
		self.chk_tick = wx.CheckBox(self, label="Aktifkan &Suara Detik Jam (Ticking) di Latar Belakang")
		self.chk_tick.SetValue(self.settings.get("ticking_enabled", False))
		sizer.Add(self.chk_tick, 0, wx.ALL, 5)
		
		sizer.Add(wx.StaticText(self, label="Volume Suara &Detik:"), 0, wx.ALL, 5)
		self.slider_tick_vol = wx.Slider(self, value=self.settings.get("ticking_volume", 40), minValue=0, maxValue=1200, style=wx.SL_HORIZONTAL | wx.SL_AUTOTICKS)
		self.slider_tick_vol.SetName("Volume Suara Detik:")
		self.slider_tick_vol.SetToolTip("Volume Suara Detik:")
		sizer.Add(self.slider_tick_vol, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 5)
		
		self.btnTest = wx.Button(self, label="&Tes Lonceng Saat Ini")
		self.btnTest.Bind(wx.EVT_BUTTON, self.onTest)
		sizer.Add(self.btnTest, 0, wx.ALL, 10)
		
		btnSizer = wx.StdDialogButtonSizer()
		self.btnOk = wx.Button(self, wx.ID_OK, label="&Simpan")
		self.btnCancel = wx.Button(self, wx.ID_CANCEL, label="&Batal")
		btnSizer.AddButton(self.btnOk)
		btnSizer.AddButton(self.btnCancel)
		btnSizer.Realize()
		self.btnOk.Bind(wx.EVT_BUTTON, self.onSave)
		
		sizer.Add(btnSizer, 0, wx.ALIGN_RIGHT | wx.ALL, 15)
		
		self.SetSizer(sizer)
		self.Centre()

	def onTest(self, evt):
		import datetime
		
		if self.btnTest.GetLabel() == "&Tes Lonceng Saat Ini":
			now = datetime.datetime.now()
			vol = self.slider_vol.GetValue()
			if self.audio_manager:
				self.audio_manager.play_lonceng_sequence(vol, now.hour, test_mode=True)
				import ui
				ui.message("Menguji lonceng...")
			self.btnTest.SetLabel("&Hentikan Tes Lonceng")
			
			# Latar belakang untuk reset nama tombol
			import threading, time, wx
			def monitor_thread():
				time.sleep(2.0)
				while getattr(self.audio_manager, "_is_playing", False):
					time.sleep(0.5)
				try:
					wx.CallAfter(self.btnTest.SetLabel, "&Tes Lonceng Saat Ini")
				except Exception:
					pass
			threading.Thread(target=monitor_thread, daemon=True).start()
		else:
			if self.audio_manager:
				self.audio_manager.stop_sound(stop_alarm=False)
				import ui
				ui.message("Tes lonceng dihentikan.")
			self.btnTest.SetLabel("&Tes Lonceng Saat Ini")

	def onSave(self, evt):
		new_settings = {
			"enabled": self.chk_enabled.GetValue(),
			"quarter_enabled": self.chk_quarter.GetValue(),
			"volume": self.slider_vol.GetValue(),
			"start_hour": self.cb_start.GetSelection(),
			"end_hour": self.cb_end.GetSelection(),
			"ticking_enabled": self.chk_tick.GetValue(),
			"ticking_volume": self.slider_tick_vol.GetValue()
		}
		self.config.data["lonceng_settings"] = new_settings
		self.config.save_data()
		import ui
		ui.message("Pengaturan Lonceng disimpan.")
		self.EndModal(wx.ID_OK)


class TutorialEntryDialog(wx.Dialog):
	def __init__(self, parent):
		super().__init__(parent, title="Pusat Bantuan & Tutorial JadwalKu", size=(400, 200), style=wx.DEFAULT_DIALOG_STYLE)
		sizer = wx.BoxSizer(wx.VERTICAL)
		
		info_label = wx.StaticText(self, label="Bagaimana Anda ingin mempelajari JadwalKu?")
		sizer.Add(info_label, 0, wx.ALL | wx.ALIGN_CENTER_HORIZONTAL, 15)
		
		btn_help = wx.Button(self, label="&1. Buka Panduan Teks Biasa")
		btn_help.Bind(wx.EVT_BUTTON, self.onTextHelp)
		sizer.Add(btn_help, 0, wx.EXPAND | wx.ALL, 10)
		
		btn_sim = wx.Button(self, label="&2. Mulai Tutorial Simulasi Interaktif (Ditutup Sementara)")
		btn_sim.Bind(wx.EVT_BUTTON, self.onSimulation)
		sizer.Add(btn_sim, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 10)
		
		btn_cancel = wx.Button(self, wx.ID_CANCEL, label="&Tutup")
		sizer.Add(btn_cancel, 0, wx.ALIGN_RIGHT | wx.ALL, 10)
		
		self.SetSizer(sizer)
		self.Centre()
		
	def onTextHelp(self, evt):
		self.EndModal(wx.ID_NO)
		
	def onSimulation(self, evt):
		self.EndModal(wx.ID_YES)
