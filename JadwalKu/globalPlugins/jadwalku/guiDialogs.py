# -*- coding: UTF-8 -*-
import wx
import datetime
import logHandler
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
			"=== PANDUAN PENGGUNAAN ADD-ON JADWALKU ===\n\n"
			"1. DAFTAR SHORTCUT UTAMA:\n"
			"- NVDA + / : Masuk ke Mode Perintah JadwalKu.\n\n"
			"2. DAFTAR PERINTAH DALAM MODE JADWALKU (Setelah menekan NVDA + /):\n"
			"- L atau Enter : Buka Dialog Utama Manajemen Jadwal.\n"
			"- 1 : Buka Dialog Pasang Timer Mundur Cepat (Quick Timer dengan detak jam acak di 10 detik terakhir).\n"
			"- 2 : Buka Dialog Pasang Alarm Sekali Pakai (One-Time Alarm).\n"
			"- W atau T : Bacakan jam saat ini dan status pengingat waktu berkala (Time Reminder).\n"
			"- K : Buka Kalender Bulanan & Daftar Tanggal Merah Indonesia.\n"
			"- R : Buka Dialog Kirim Laporan, Kritik, Saran & Bug Fix (Terhubung ke Telegram Bot Aileen).\n"
			"- D : Buka Jam Dunia & Kalkulator Konversi Waktu.\n"
			"- J : Bacakan jadwal agenda terdekat berikutnya hari ini beserta sisa waktunya.\n"
			"- H : Bacakan seluruh daftar agenda aktif hari ini.\n"
			"- A : Check / Uncheck cepat status Aktifkan Pengingat Waktu Berkala.\n"
			"- S : Buka Pengaturan Audio Manager (Speaker & Suara).\n"
			"- M atau P : Buka Pengaturan Mesin TTS Mandiri SAPI 5 untuk notifikasi latar belakang.\n"
			"- G : Bagikan Add-on (Salin tautan unduhan langsung / direct download ke clipboard).\n"
			"- U : Periksa pembaruan terbaru add-on secara langsung dari server.\n"
			"- V : Bacakan versi terkini JadwalKu dan buka dialog catatan riwayat pembaruan (Changelog Read-Only).\n"
			"- Z : Tunda (Snooze) alarm yang sedang berbunyi selama 10 menit ke depan.\n"
			"- Spasi : Hentikan suara notifikasi/chime atau matikan alarm weker yang sedang berdering.\n"
			"- B atau F1 : Buka dialog panduan bantuan ini (Mode Read-Only bisa dinavigasi panah).\n"
			"- Escape : Keluar dari mode perintah JadwalKu.\n\n"
			"3. TIPS FITUR ALARM WEKER & NAVIGASI DI DIALOG UTAMA:\n"
			"- Saat menambah atau mengedit agenda, Anda dapat memilih Mode Pemberitahuan: 'Pemberitahuan Singkat (Chime)' atau 'Alarm Jam Weker'. Jika Anda memilih Alarm Jam Weker, suara akan berdering terus-menerus tanpa henti sampai Anda mematikannya (Spasi) atau menundanya (Z / Alt+T).\n"
			"- Anda juga dapat mengatur pengingat berulang pada agenda (misalnya: tiap 1 jam sekali atau tiap 2 jam sekali untuk pengingat minum/istirahat).\n"
			"- Di dalam daftar agenda (ListBox), Anda dapat menekan tombol Spasi untuk dengan cepat mengaktifkan (Check) atau menonaktifkan (Uncheck) agenda yang dipilih.\n"
			"- Gunakan tombol 'Tes Suara' (Alt + T) saat menambah atau mengedit agenda untuk mendengarkan sampel suara chime/alarm yang Anda pilih.\n"
			"- Gunakan tombol 'Cek Pembaruan...' untuk memeriksa versi terbaru add-on dari server GitHub secara langsung tanpa perlu membuka browser.\n"
			"- Gunakan tombol 'Bagikan Add-on (Copy Link)...' atau shortcut NVDA + / lalu G untuk menyalin tautan unduhan langsung agar teman Anda dapat mengunduh JadwalKu dengan mudah tanpa browser.\n"
			"- Gunakan tombol 'Kirim Laporan & Saran...' atau shortcut NVDA + / lalu K (atau R) untuk mengirimkan ide baru atau melaporkan bug langsung ke Telegram pengembang.\n"
		)
		
		self.textCtrl = wx.TextCtrl(self, value=help_text, style=wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_RICH2 | wx.HSCROLL)
		sizer.Add(self.textCtrl, 1, wx.EXPAND | wx.LEFT | wx.RIGHT, 8)
		
		btnSizer = wx.StdDialogButtonSizer()
		self.btnClose = wx.Button(self, wx.ID_CLOSE, label="&Tutup")
		self.btnClose.Bind(wx.EVT_BUTTON, lambda evt: self.EndModal(wx.ID_CLOSE))
		btnSizer.AddButton(self.btnClose)
		btnSizer.Realize()
		sizer.Add(btnSizer, 0, wx.ALIGN_RIGHT | wx.ALL, 12)
		
		self.SetSizer(sizer)
		self.Centre()
		self.textCtrl.SetFocus()


class ChangelogDialog(wx.Dialog):
	def __init__(self, parent):
		super().__init__(parent, title="Catatan Riwayat Pembaruan JadwalKu (Changelog)", size=(620, 500), style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)
		sizer = wx.BoxSizer(wx.VERTICAL)
		
		info_label = wx.StaticText(self, label="Gunakan Panah Atas/Bawah untuk membaca riwayat pembaruan dari versi terbaru hingga terlama:")
		sizer.Add(info_label, 0, wx.ALL, 8)
		
		changelog_text = (
			"=== RIWAYAT PEMBARUAN JADWALKU ===\n\n"
			"--- Versi 1.6.2 (Terbaru - Kustomisasi Format & Gaya Ucapan Pengingat serta Kirim Laporan via Cloudflare Workers) ---\n"
			"* Penyesuaian Format & Gaya Pengucapan Waktu Pengingat (Time Reminder Speech Style & 12/24 Jam): Pada Pengaturan Pengingat Waktu Berkala, kini tersedia pilihan format jam (24 Jam, 12 Jam AM/PM, atau Mengikuti Format NVDA+F12) serta pilihan gaya pengucapan suara (Mulai dari 'Sekarang jam [Jam]:[Menit]', mengikuti persis format & gaya pengucapan NVDA+F12, '[Jam]:[Menit] waktu sekarang', hingga 'Waktu sekarang pukul [Jam]:[Menit]').\n"
			"* Fitur Laporan & Saran Aksesibel via Cloudflare Workers (NVDA + / lalu R): Memungkinkan pengguna mengirimkan permintaan fitur baru, kritik saran, atau melaporkan kesalahan/bug langsung dari dalam add-on JadwalKu ke Bot Telegram pengembang (Aileen Bot) melalui Web API Proxy berkecepatan tinggi yang aman tanpa mengekspos token bot.\n"
			"* Kategori & Sub-Kategori Bug Transparan: Saat melaporkan bug, pengguna dapat memilih sub-fitur spesifik dan memeriksa/mengedit log diagnostik NVDA yang dilampirkan secara transparan.\n"
			"* Pembatasan Pintar & Salin Otomatis: Batas 1 laporan per pengguna per hari (maksimal 10 laporan/hari dari seluruh pengguna). Jika offline atau kuota penuh, laporan otomatis disalin ke clipboard agar tidak ada pesan yang hilang.\n"
			"* Shortcut Kalender Tetap pada Tombol K: Tombol K tetap dipertahankan sebagai shortcut Kalender & Tanggal Merah Indonesia, sementara Kirim Laporan dapat dibuka menggunakan shortcut R (Report) atau dari tombol di Panel Pengaturan NVDA.\n\n"
			"--- Versi 1.6.1 (Terbaru - Fitur Bagikan Add-on Direct Link) ---\n"
			"* Fitur Bagikan Add-on Cepat (Aksesibel via NVDA + / lalu G, atau tombol di Panel Pengaturan NVDA): Menyalin tautan unduhan langsung (direct download link) versi terbaru JadwalKu langsung ke clipboard. Teman yang mengeklik tautan tersebut akan langsung mengunduh file .nvda-addon tanpa perlu menavigasi halaman browser GitHub yang rumit!\n\n"
			"--- Versi 1.6.0 (Mesin Suara TTS Mandiri untuk Notifikasi Latar Belakang) ---\n"
			"* Fitur Mesin TTS Mandiri (Aksesibel via NVDA + / lalu M atau tombol di Tab 2 & Pengingat Waktu): Memungkinkan seluruh pemberitahuan latar belakang (pengingat waktu berkala setiap jam/menit, alarm agenda, quick timer, dan satu kali alarm) dibacakan menggunakan mesin suara SAPI 5 terpisah yang mandiri dan tidak menumpuk dengan suara pembacaan layar NVDA yang sedang aktif!\n"
			"* Pengaturan Suara, Kecepatan & Volume TTS SAPI 5: Pilih suara SAPI 5 yang diinginkan (misal suara Indonesia atau Inggris di sistem), sesuaikan kecepatan (Rate -10 s/d +10) dan volume (0% - 100%) dengan pratinjau tes suara langsung.\n"
			"* Routing Audio Penuh (Audio Device Independent): Suara TTS Mandiri sepenuhnya mengikuti rute perangkat audio (Speaker/Headphone/Virtual Audio Cable) yang dipilih pada Audio Manager JadwalKu, sehingga suara notifikasi tidak bocor ke speaker utama jika diatur ke perangkat lain.\n"
			"* Pengecualian Pintar NVDA + F12: Pengucapan waktu/tanggal manual via NVDA + F12 tetap dibacakan oleh pembaca layar NVDA utama sesuai preferensi pengguna, menjaga pemisahan fungsi yang sempurna.\n\n"
			"--- Versi 1.5.0 (Puncak Spektakuler Waktu, Kalender & Jam Dunia) ---\n"
			"* Fitur Tab 2 Pengaturan Waktu & Kalender (Aksesibel via Shift+Tab dari daftar agenda & Panah Kanan atau Ctrl+Tab): Memungkinkan kostumisasi menyeluruh bagaimana NVDA melaporkan jam dan tanggal.\n"
			"* Penggantian Pintar NVDA + F12: Tekan 1x untuk informasi jam sesuai format (24/12 Jam, pilihan gaya pengucapan, opsi detik). Tekan 2x untuk tanggal lengkap/ringkas. Tekan 3x untuk informasi lengkap beserta hitung mundur sisa hari & jam menuju akhir tahun!\n"
			"* Fitur Kalender & Tanggal Merah (NVDA + / lalu K): Melihat kalender bulanan lengkap dengan deteksi otomatis hari libur nasional Indonesia, serta filter khusus untuk menampilkan seluruh daftar tanggal merah tahun ini.\n"
			"* Fitur Jam Dunia & Konversi Waktu (NVDA + / lalu D): Menampilkan selisih waktu Indonesia (WIB/WITA/WIT) dengan berbagai negara di benua Asia, Eropa, Amerika, Australia, dan Afrika, dilengkapi Kalkulator Konversi Waktu instan.\n\n"
			"--- Versi 1.4.3 ---\n"
			"* Fitur Waktu Selesai Interval (Jam Selesai Perulangan): Pada form tambah/edit jadwal, kini tersedia input 'Waktu Selesai Interval (Jam Selesai Perulangan)' sehingga pengingat berulang (misal minum air atau jam kerja) dapat dibatasi secara otomatis agar berhenti berbunyi setelah jam selesai yang ditentukan.\n"
			"* Dukungan Interval Lintas Malam (Overnight Interval): Sistem mendukung penuh perulangan interval di hari yang sama maupun lintas malam (misal dari jam 20:00 sampai 04:00 pagi).\n\n"
			"--- Versi 1.4.2 ---\n"
			"* Fitur Hitung Mundur Persiapan Quick Timer (NVDA + / lalu 1): Dilengkapi kolom input 'Detik Persiapan Sebelum Mulai' yang menghitung mundur terlebih dahulu, memainkan efek detak jam di 10 detik terakhir dan membacakan angka hitung mundur di 5 detik terakhir (5... 4... 3... 2... 1...).\n"
			"* Pemicu Mulai Timer Utama (Ding Indicator): Ketika waktu persiapan mencapai titik nol, suara Ding (chime.wav) dipicu otomatis sebagai tanda hitung mundur sesungguhnya resmi dimulai.\n"
			"* Revolusi Arsitektur Audio (Single-Open WinMM Relooping Engine): Perpindahan perangkat audio (speaker/headphone pilihan) 100% akurat tanpa macet di default, berulang tanpa batas setiap 2 detik dengan suara utuh tanpa potongan, serta dapat dimatikan seketika via tombol Spasi.\n"
			"* Fitur Pengingat Berulang dalam Form Jadwal: Kini saat membuat atau mengedit agenda, tersedia opsi 'Ulangi Setiap (Interval Jam Sekali)' untuk mengatur pengingat otomatis berulang (misal: setiap 1 jam sekali, 2 jam sekali, dst. untuk pengingat minum atau istirahat mata).\n"
			"* Shortcut Catatan Pembaruan (NVDA + / lalu V): Membacakan versi terkini sekaligus membuka dialog riwayat pembaruan (Changelog) yang dapat dibaca dengan nyaman menggunakan panah.\n\n"
			"--- Versi 1.4.1 ---\n"
			"* Perbaikan sistem Auto Updater agar mendeteksi versi aktif secara dinamis dari manifest dan menghindari permintaan update berulang saat versi terbaru sudah terinstal.\n"
			"* Perbaikan unduhan add-on agar dapat diakses dari repositori publik GitHub tanpa kendala token otentikasi (401 Unauthorized / 404 Not Found).\n"
			"* Perbaikan pemutaran suara hitung mundur timer dan bunyi alarm pada detik ke-0 (overlapping audio/tumpang tindih), memastikan alarm langsung berbunyi dengan lantang tepat saat timer selesai.\n"
			"* Mempertahankan sistem penguat volume audio super (1%-600%) tanpa ketergantungan eksternal.\n\n"
			"--- Versi 1.4.0 ---\n"
			"* Fitur Penguat Volume Audio Super (Up to 600%): Penambahan penguat volume audio internal pada Audio Manager, memungkinkan pengguna memperkeras suara chime/alarm hingga 6 kali lipat dari volume sistem.\n"
			"* Pratinjau Suara Slider Volume: Menggeser slider volume kini langsung memutarkan sampel suara sesuai persentase yang dipilih.\n\n"
			"--- Versi 1.3.3 ---\n"
			"* Fitur Timer Mundur Cepat (Quick Timer - NVDA + / lalu 1): Memungkinkan pemasangan timer berdasarkan detik, menit, atau jam dengan mudah via dropdown.\n"
			"* Efek Suara Detik Hitung Mundur: Pada 10 detik terakhir timer mundur, sistem memutar suara detak jam weker acak dari folder WaitingClock.\n"
			"* Fitur Alarm Sekali Pakai (One-Time Alarm - NVDA + / lalu 2): Pemasangan alarm cepat dengan penentuan jam, menit, detik, pemilihan suara, tes suara, dan fitur tunda (snooze).\n"
			"* Peningkatan stabilitas pemutaran audio dan antarmuka dialog.\n\n"
			"--- Versi 1.3.0 - 1.3.2 ---\n"
			"* Integrasi Sistem Pembaruan Otomatis (Auto-Updater): Pemeriksaan versi terbaru dari server GitHub dan pengunduhan langsung paket add-on.\n"
			"* Penambahan tombol 'Cek Pembaruan...' pada dialog utama dan shortcut cepat NVDA + / lalu U.\n\n"
			"--- Versi 1.2.0 ---\n"
			"* Desain ulang arsitektur Audio Manager menggunakan WinMM (Windows Multimedia API) untuk pemutaran WAV dan MP3 yang sangat ringan dan tidak memblokir suara NVDA.\n"
			"* Fitur Pemilihan Perangkat Audio Output (Speaker/Headphone) pada Audio Manager.\n"
			"* Fitur Pengingat Waktu Berkala (Time Reminder) tiap 15, 30, atau 60 menit dengan lonceng lembut.\n"
			"* Shortcut cepat NVDA + / lalu W/T untuk mengecek jam dan status pengingat.\n\n"
			"--- Versi 1.0.0 (Rilis Awal) ---\n"
			"* Kerangka dasar add-on JadwalKu untuk NVDA dengan manajemen jadwal agenda rutin harian, mingguan, maupun tanggal spesifik.\n"
			"* Pilihan mode pemberitahuan Chime singkat dan Alarm Jam Weker.\n"
			"* Navigasi ramah tuna netra dengan tombol cepat Check/Uncheck status agenda via Spasi di dalam daftar agenda.\n"
		)
		
		self.textCtrl = wx.TextCtrl(self, value=changelog_text, style=wx.TE_MULTILINE | wx.TE_READONLY | wx.TE_RICH2 | wx.HSCROLL)
		sizer.Add(self.textCtrl, 1, wx.EXPAND | wx.LEFT | wx.RIGHT, 8)
		
		btnSizer = wx.StdDialogButtonSizer()
		self.btnClose = wx.Button(self, wx.ID_CLOSE, label="&Tutup")
		self.btnClose.Bind(wx.EVT_BUTTON, lambda evt: self.EndModal(wx.ID_CLOSE))
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
		title_sizer.Add(self.txt_title, 1, wx.EXPAND | wx.ALL, 4)
		sizer.Add(title_sizer, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 6)
		
		# Deskripsi
		sizer.Add(wx.StaticText(self, label="&Deskripsi Lengkap (Tuliskan detail ide permintaan atau kronologi error di sini):"), 0, wx.LEFT | wx.RIGHT | wx.TOP, 8)
		self.txt_desc = wx.TextCtrl(self, style=wx.TE_MULTILINE | wx.TE_RICH2)
		sizer.Add(self.txt_desc, 1, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 8)
		
		# Log Diagnostik (Transparan dan Bisa Diedit)
		self.lbl_logs = wx.StaticText(self, label="&Log Deteksi Otomatis NVDA & JadwalKu (Akan dilampirkan transparan, dapat Anda periksa/edit):")
		sizer.Add(self.lbl_logs, 0, wx.LEFT | wx.RIGHT | wx.TOP, 8)
		self.txt_logs = wx.TextCtrl(self, style=wx.TE_MULTILINE | wx.TE_RICH2 | wx.HSCROLL)
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
		cur_dev = self.config.get_audio_device()
		if cur_dev in device_names:
			self.cb_device.SetValue(cur_dev)
		else:
			self.cb_device.SetSelection(0)
		sizer.Add(self.cb_device, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 6)
		
		self.btnTestDevice = wx.Button(self, label="&Tes Suara di Speaker Ini")
		self.btnTestDevice.Bind(wx.EVT_BUTTON, self.onTestDevice)
		sizer.Add(self.btnTestDevice, 0, wx.ALL, 6)
		
		# 2. Pengaturan Volume Audio (Maksimal 600%)
		cur_vol = self.config.get_audio_volume() if self.config else 100
		self.lbl_volume = wx.StaticText(self, label=f"&Volume Audio Suara ({cur_vol}%):")
		sizer.Add(self.lbl_volume, 0, wx.ALL, 6)
		
		self.slider_volume = wx.Slider(self, value=cur_vol, minValue=1, maxValue=600, style=wx.SL_HORIZONTAL | wx.SL_AUTOTICKS)
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
		btnSizer.AddButton(self.btnOk)
		btnSizer.AddButton(self.btnCancel)
		btnSizer.Realize()
		sizer.Add(btnSizer, 0, wx.ALIGN_RIGHT | wx.ALL, 12)
		
		self.SetSizer(sizer)
		self.Centre()
		self.cb_device.SetFocus()
		self.Bind(wx.EVT_CLOSE, self.onClose)

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
		sizer.Add(self.txt_date, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 5)
		
		# 4. Waktu (Jam & Menit)
		time_sizer = wx.BoxSizer(wx.HORIZONTAL)
		time_sizer.Add(wx.StaticText(self, label="&Jam:"), 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)
		hours = [f"{i:02d}" for i in range(24)]
		self.cb_hour = wx.ComboBox(self, choices=hours, style=wx.CB_READONLY)
		cur_hour = int(self.schedule_data.get("hour", 12))
		self.cb_hour.SetValue(f"{cur_hour:02d}")
		time_sizer.Add(self.cb_hour, 0, wx.ALL, 5)
		
		time_sizer.Add(wx.StaticText(self, label="&Menit:"), 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)
		minutes = [f"{i:02d}" for i in range(60)]
		self.cb_minute = wx.ComboBox(self, choices=minutes, style=wx.CB_READONLY)
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
		return {
			"id": self.schedule_data.get("id", ""),
			"name": self.txt_name.GetValue().strip() or "Agenda Tanpa Nama",
			"frequency": self.cb_freq.GetValue(),
			"custom_days": getattr(self, "custom_days", []),
			"date": self.txt_date.GetValue().strip(),
			"hour": int(self.cb_hour.GetValue()),
			"minute": int(self.cb_minute.GetValue()),
			"interval_hour": interval_val,
			"interval_end_hour": interval_end_val,
			"audio_file": audio_file,
			"audio_enabled": audio_enabled,
			"is_alarm": is_alarm_sel,
			"alarm_mode": self.cb_alarm_mode.GetValue(),
			"speech_enabled": self.chk_speech.GetValue(),
			"active": self.chk_active.GetValue(),
			"last_triggered_date": self.schedule_data.get("last_triggered_date", "")
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
		sizer.Add(self.txt_duration, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 5)
		
		# 2. Satuan Waktu (Dropdown: Detik, Menit, Jam)
		sizer.Add(wx.StaticText(self, label="&Satuan Waktu:"), 0, wx.ALL, 5)
		self.cb_unit = wx.ComboBox(self, choices=["Menit", "Detik", "Jam"], style=wx.CB_READONLY)
		self.cb_unit.SetSelection(0)  # Default ke Menit
		sizer.Add(self.cb_unit, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 5)
		
		# 3. Detik Persiapan Sebelum Mulai (Hitung Mundur Awal)
		sizer.Add(wx.StaticText(self, label="&Detik Persiapan Sebelum Mulai (0 jika langsung):"), 0, wx.ALL, 5)
		self.txt_prep_seconds = wx.TextCtrl(self, value="0")
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
		btnSizer.AddButton(self.btnOk)
		btnSizer.AddButton(self.btnCancel)
		btnSizer.Realize()
		sizer.Add(btnSizer, 0, wx.ALIGN_RIGHT | wx.ALL, 15)
		
		self.SetSizer(sizer)
		self.Centre()
		self.txt_duration.SetFocus()

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
		self.cb_hour.SetValue(f"{now.hour:02d}")
		sizer.Add(self.cb_hour, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 5)
		
		# 2. Dropdown Menit
		sizer.Add(wx.StaticText(self, label="&Menit (00 - 59):"), 0, wx.ALL, 5)
		minutes = [f"{m:02d}" for m in range(60)]
		self.cb_minute = wx.ComboBox(self, choices=minutes, style=wx.CB_READONLY)
		self.cb_minute.SetValue(f"{now.minute:02d}")
		sizer.Add(self.cb_minute, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 5)
		
		# 3. Dropdown Detik
		sizer.Add(wx.StaticText(self, label="&Detik (00 - 59):"), 0, wx.ALL, 5)
		seconds = [f"{s:02d}" for s in range(60)]
		self.cb_second = wx.ComboBox(self, choices=seconds, style=wx.CB_READONLY)
		self.cb_second.SetValue("00")
		sizer.Add(self.cb_second, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 5)
		
		# 4. Mode Alarm / Snooze
		sizer.Add(wx.StaticText(self, label="&Fitur Mode Alarm & Snooze:"), 0, wx.ALL, 5)
		alarm_modes = [
			"Alarm Jam Weker (Berdering Berulang + Fitur Tunda / Snooze 10m)",
			"Pemberitahuan Singkat (Sekali Bunyi / Chime)"
		]
		self.cb_alarm_mode = wx.ComboBox(self, choices=alarm_modes, style=wx.CB_READONLY)
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
		btnSizer.AddButton(self.btnOk)
		btnSizer.AddButton(self.btnCancel)
		btnSizer.Realize()
		sizer.Add(btnSizer, 0, wx.ALIGN_RIGHT | wx.ALL, 15)
		
		self.SetSizer(sizer)
		self.Centre()
		self.cb_hour.SetFocus()

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
		self.slider_rate = wx.Slider(self, value=int(self.cfg.get("rate", 0)), minValue=-10, maxValue=10, style=wx.SL_HORIZONTAL | wx.SL_LABELS)
		sizer.Add(self.slider_rate, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 5)
		
		# Slider Volume
		sizer.Add(wx.StaticText(self, label="&Volume Suara TTS (0% s/d 100%):"), 0, wx.ALL, 5)
		self.slider_volume = wx.Slider(self, value=int(self.cfg.get("volume", 100)), minValue=0, maxValue=100, style=wx.SL_HORIZONTAL | wx.SL_LABELS)
		sizer.Add(self.slider_volume, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 5)
		
		# Tombol Tes Suara
		self.btnTest = wx.Button(self, label="&Tes Suara TTS Mandiri")
		self.btnTest.Bind(wx.EVT_BUTTON, self.onTest)
		sizer.Add(self.btnTest, 0, wx.ALL | wx.ALIGN_CENTER_HORIZONTAL, 10)
		
		# Buttons Simpan & Batal
		btnSizer = wx.StdDialogButtonSizer()
		self.btnOk = wx.Button(self, wx.ID_OK, label="&Simpan")
		self.btnCancel = wx.Button(self, wx.ID_CANCEL, label="&Batal")
		btnSizer.AddButton(self.btnOk)
		btnSizer.AddButton(self.btnCancel)
		btnSizer.Realize()
		sizer.Add(btnSizer, 0, wx.ALIGN_RIGHT | wx.ALL, 15)
		
		self.SetSizer(sizer)
		self.Centre()
		self.chk_enabled.SetFocus()

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
			("Pukul [Jam]:[Menit] tepat (Contoh: Pukul 09:00 tepat / Pukul 09:15)", "pukul_tepat")
		]
		self.speech_style_values = [v for k, v in speech_style_choices]
		self.cb_speech_style = wx.ComboBox(self, choices=[k for k, v in speech_style_choices], style=wx.CB_READONLY)
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
		cur_fmt = self.cfg.get("time_format", "24")
		if cur_fmt in self.format_values:
			self.cb_time_format.SetSelection(self.format_values.index(cur_fmt))
		else:
			self.cb_time_format.SetSelection(0)
		sizer.Add(self.cb_time_format, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 5)
		
		# Jam Mulai & Jam Selesai
		time_sizer = wx.BoxSizer(wx.HORIZONTAL)
		hours = [f"{i:02d}:00" for i in range(24)]
		
		time_sizer.Add(wx.StaticText(self, label="Jam &Mulai Aktif:"), 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)
		self.cb_start = wx.ComboBox(self, choices=hours, style=wx.CB_READONLY)
		self.cb_start.SetSelection(int(self.cfg.get("start_hour", 0)))
		time_sizer.Add(self.cb_start, 0, wx.ALL, 5)
		
		time_sizer.Add(wx.StaticText(self, label="Jam &Selesai Aktif:"), 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)
		self.cb_end = wx.ComboBox(self, choices=hours, style=wx.CB_READONLY)
		self.cb_end.SetSelection(int(self.cfg.get("end_hour", 23)))
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
		btnSizer.AddButton(self.btnOk)
		btnSizer.AddButton(self.btnCancel)
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
			"Waktu sekarang pukul [Jam]:[Menit]:[Detik] (Contoh: Waktu sekarang pukul 09:15:30)"
		]
		self.cb_time_speech_style = wx.ComboBox(self.panel_tab2, choices=time_style_choices, style=wx.CB_READONLY)
		style_map = {"default": 0, "only_time": 1, "prefix_pukul": 2, "with_seconds": 3, "full_seconds": 4}
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
		date_style_map = {"default": 0, "prefix_hari": 1, "numeric": 2, "suffix_hari": 3}
		self.cb_date_speech_style.SetSelection(date_style_map.get(time_cfg.get("date_speech_style", "default"), 0))
		sizer_tab2.Add(self.cb_date_speech_style, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 6)
		
		sizer_tab2.Add(wx.StaticText(self.panel_tab2, label="&Gaya Pengucapan Lengkap & Akhir Tahun (Tekan NVDA+F12 3x):"), 0, wx.LEFT | wx.TOP, 6)
		full_style_choices = [
			"Lengkap dengan sisa hari & jam menuju akhir tahun (Contoh: Kamis, 16 Juli 2026, pukul 09:15. Sisa waktu menuju akhir tahun: 168 hari 14 jam lagi)",
			"Ringkas: Tanggal, waktu, dan sisa hari akhir tahun (Contoh: 16 Juli 2026 09:15. Akhir tahun kurang 168 hari)"
		]
		self.cb_full_speech_style = wx.ComboBox(self.panel_tab2, choices=full_style_choices, style=wx.CB_READONLY)
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
		
		main_sizer.Add(self.notebook, 1, wx.EXPAND | wx.ALL, 6)
		
		bottom_btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
		self.btnClose = wx.Button(self, wx.ID_CANCEL, label="&Tutup Dialog")
		bottom_btn_sizer.Add(self.btnClose, 0, wx.ALL, 6)
		main_sizer.Add(bottom_btn_sizer, 0, wx.ALIGN_RIGHT | wx.RIGHT | wx.BOTTOM, 6)
		
		self.SetSizer(main_sizer)
		self.Centre()
		self.refreshList()
		self.listBox.SetFocus()

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
		t_style_inv = {0: "default", 1: "only_time", 2: "prefix_pukul", 3: "with_seconds", 4: "full_seconds"}
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
		self.cb_month.SetSelection(self.current_month - 1)
		self.cb_month.Bind(wx.EVT_COMBOBOX, self.onMonthYearChanged)
		filter_sizer.Add(self.cb_month, 0, wx.ALL, 4)
		
		filter_sizer.Add(wx.StaticText(self, label="&Tahun:"), 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 4)
		self.years_list = [str(y) for y in range(2024, 2036)]
		self.cb_year = wx.ComboBox(self, choices=self.years_list, style=wx.CB_READONLY)
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
		sizer.Add(btnSizer2, 0, wx.ALIGN_RIGHT | wx.RIGHT | wx.BOTTOM, 6)
		
		self.SetSizer(sizer)
		self.Centre()
		self.refreshMonthCalendar()
		self.listBox.SetFocus()

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
		# Default Jerman jika ada
		jerman_idx = next((i for i, c in enumerate(country_names) if "Jerman" in c), 0)
		self.cb_src_country.SetSelection(jerman_idx)
		self.cb_src_country.Bind(wx.EVT_COMBOBOX, self.onCalculateConversion)
		sizer_v.Add(self.cb_src_country, 0, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 8)
		
		# Jam & Menit Asal
		time_sizer = wx.BoxSizer(wx.HORIZONTAL)
		time_sizer.Add(wx.StaticText(self.panel_conv, label="&Jam di Negara Asal (00-23):"), 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 4)
		self.cb_src_hour = wx.ComboBox(self.panel_conv, choices=[f"{h:02d}" for h in range(24)], style=wx.CB_READONLY)
		self.cb_src_hour.SetSelection(20) # Default Jam 20:00 seperti contoh user
		self.cb_src_hour.Bind(wx.EVT_COMBOBOX, self.onCalculateConversion)
		time_sizer.Add(self.cb_src_hour, 0, wx.ALL, 4)
		
		time_sizer.Add(wx.StaticText(self.panel_conv, label="&Menit:"), 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 4)
		self.cb_src_min = wx.ComboBox(self.panel_conv, choices=[f"{m:02d}" for m in range(60)], style=wx.CB_READONLY)
		self.cb_src_min.SetSelection(0)
		self.cb_src_min.Bind(wx.EVT_COMBOBOX, self.onCalculateConversion)
		time_sizer.Add(self.cb_src_min, 0, wx.ALL, 4)
		sizer_v.Add(time_sizer, 0, wx.LEFT | wx.RIGHT, 8)
		
		# Negara Tujuan
		sizer_v.Add(wx.StaticText(self.panel_conv, label="2. Pilih Negara/Kota &Tujuan Konversi:"), 0, wx.LEFT | wx.TOP, 8)
		self.cb_tgt_country = wx.ComboBox(self.panel_conv, choices=country_names, style=wx.CB_READONLY)
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
		sizer_v.Add(self.txt_result, 1, wx.EXPAND | wx.ALL, 8)
		self.panel_conv.SetSizer(sizer_v)
		
		self.notebook.AddPage(self.panel_clocks, "1. Jam Dunia & Selisih Waktu")
		self.notebook.AddPage(self.panel_conv, "2. Kalkulator Konversi Waktu Antar Negara")
		
		main_sizer = wx.BoxSizer(wx.VERTICAL)
		main_sizer.Add(self.notebook, 1, wx.EXPAND | wx.ALL, 6)
		
		bottom_btn_sizer = wx.BoxSizer(wx.HORIZONTAL)
		self.btnClose = wx.Button(self, wx.ID_CANCEL, label="&Tutup Dialog")
		bottom_btn_sizer.Add(self.btnClose, 0, wx.ALL, 6)
		main_sizer.Add(bottom_btn_sizer, 0, wx.ALIGN_RIGHT | wx.RIGHT | wx.BOTTOM, 6)
		
		self.SetSizer(main_sizer)
		self.Centre()
		self.refreshClocksList()
		self.onCalculateConversion(None, speak=False)
		self.listBox_clocks.SetFocus()

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



