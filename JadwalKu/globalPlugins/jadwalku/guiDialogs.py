# -*- coding: UTF-8 -*-
import wx
import datetime
import logHandler
import ui
import gui

class HelpDialog(wx.Dialog):
	def __init__(self, parent):
		super().__init__(parent, title="Panduan & Bantuan JadwalKu", size=(580, 460), style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)
		sizer = wx.BoxSizer(wx.VERTICAL)
		
		info_label = wx.StaticText(self, label="Gunakan Panah Atas/Bawah untuk membaca per baris, atau Panah Kiri/Kanan untuk mengeja teks:")
		sizer.Add(info_label, 0, wx.ALL, 8)
		
		help_text = (
			"=== PANDUAN PENGGUNAAN ADD-ON JADWALKU ===\n\n"
			"1. DAFTAR SHORTCUT UTAMA:\n"
			"- NVDA + Shift + J : Langsung membuka Dialog Utama Manajemen Jadwal & Pengaturan tanpa melalui mode perintah.\n"
			"- NVDA + / : Masuk ke Mode Perintah JadwalKu.\n\n"
			"2. DAFTAR PERINTAH DALAM MODE JADWALKU (Setelah menekan NVDA + /):\n"
			"- L atau Enter : Buka Dialog Utama Manajemen Jadwal.\n"
			"- W atau T : Bacakan jam saat ini dan status pengingat waktu berkala (Time Reminder).\n"
			"- J : Bacakan jadwal agenda terdekat berikutnya hari ini beserta sisa waktunya.\n"
			"- H : Bacakan seluruh daftar agenda aktif hari ini.\n"
			"- A : Check / Uncheck cepat status Aktifkan Pengingat Waktu Berkala.\n"
			"- Spasi : Hentikan suara notifikasi/chime yang sedang berbunyi.\n"
			"- B atau F1 : Buka dialog panduan bantuan ini (Mode Read-Only bisa dinavigasi panah).\n"
			"- Escape : Keluar dari mode perintah JadwalKu.\n\n"
			"3. TIPS NAVIGASI DI DIALOG UTAMA:\n"
			"- Di dalam daftar agenda (ListBox), Anda dapat menekan tombol Spasi untuk dengan cepat mengaktifkan (Check) atau menonaktifkan (Uncheck) agenda yang dipilih.\n"
			"- Gunakan tombol 'Tes Suara' (Alt + T) saat menambah atau mengedit agenda untuk mendengarkan sampel suara chime/alarm yang Anda pilih.\n"
			"- Gunakan tombol 'Cek Pembaruan...' untuk memeriksa versi terbaru add-on dari server GitHub secara langsung tanpa perlu membuka browser.\n"
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
		
		# 2. Frekuensi / Hari
		sizer.Add(wx.StaticText(self, label="&Frekuensi / Hari:"), 0, wx.ALL, 5)
		freq_choices = [
			"Setiap Hari", "Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu",
			"Hari Kerja (Senin - Jumat)", "Akhir Pekan (Sabtu - Minggu)", "Sekali Waktu (Tanggal Spesifik)"
		]
		self.cb_freq = wx.ComboBox(self, choices=freq_choices, style=wx.CB_READONLY)
		current_freq = self.schedule_data.get("frequency", "Setiap Hari")
		if current_freq in freq_choices:
			self.cb_freq.SetValue(current_freq)
		else:
			self.cb_freq.SetSelection(0)
		sizer.Add(self.cb_freq, 0, wx.EXPAND | wx.LEFT | wx.RIGHT, 5)
		
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
		
		# 5. Suara Audio
		sizer.Add(wx.StaticText(self, label="&Suara Chime/Alarm:"), 0, wx.ALL, 5)
		audio_sizer = wx.BoxSizer(wx.HORIZONTAL)
		audio_choices = ["chime.wav (Chime Lembut)", "bell.wav (Bel Singkat)", "alarm.wav (Alarm Nada Dering)", "Tanpa Suara Audio"]
		self.cb_audio = wx.ComboBox(self, choices=audio_choices, style=wx.CB_READONLY)
		cur_audio = self.schedule_data.get("audio_file", "chime.wav")
		if "chime" in cur_audio: self.cb_audio.SetSelection(0)
		elif "bell" in cur_audio: self.cb_audio.SetSelection(1)
		elif "alarm" in cur_audio: self.cb_audio.SetSelection(2)
		else: self.cb_audio.SetSelection(3)
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

	def get_result(self):
		audio_sel = self.cb_audio.GetSelection()
		if audio_sel == 0: audio_file = "chime.wav"; audio_enabled = True
		elif audio_sel == 1: audio_file = "bell.wav"; audio_enabled = True
		elif audio_sel == 2: audio_file = "alarm.wav"; audio_enabled = True
		else: audio_file = ""; audio_enabled = False
		
		return {
			"id": self.schedule_data.get("id", ""),
			"name": self.txt_name.GetValue().strip() or "Agenda Tanpa Nama",
			"frequency": self.cb_freq.GetValue(),
			"date": self.txt_date.GetValue().strip(),
			"hour": int(self.cb_hour.GetValue()),
			"minute": int(self.cb_minute.GetValue()),
			"audio_file": audio_file,
			"audio_enabled": audio_enabled,
			"speech_enabled": self.chk_speech.GetValue(),
			"active": self.chk_active.GetValue(),
			"last_triggered_date": self.schedule_data.get("last_triggered_date", "")
		}

	def onTestSound(self, event):
		if not self.audio_manager:
			return
		sel = self.cb_audio.GetSelection()
		if sel == 0: audio_file = "chime.wav"
		elif sel == 1: audio_file = "bell.wav"
		elif sel == 2: audio_file = "alarm.wav"
		else:
			ui.message("Anda memilih opsi Tanpa Suara Audio.")
			return
		
		ui.message(f"Memutar tes suara: {audio_file}")
		self.audio_manager.play_sound(audio_file)


class TimeReminderDialog(wx.Dialog):
	def __init__(self, parent, time_config=None):
		super().__init__(parent, title="Pengaturan Pengingat Waktu Berkala (Time Reminder)", size=(500, 420), style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)
		self.cfg = time_config or {}
		
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

	def get_result(self):
		idx_int = self.cb_interval.GetSelection()
		idx_mod = self.cb_mode.GetSelection()
		return {
			"enabled": self.chk_enabled.GetValue(),
			"interval": self.interval_values[idx_int if idx_int >= 0 else 4],
			"mode": self.mode_values[idx_mod if idx_mod >= 0 else 0],
			"start_hour": self.cb_start.GetSelection(),
			"end_hour": self.cb_end.GetSelection(),
			"last_triggered_minute": self.cfg.get("last_triggered_minute", "")
		}


class JadwalKuDialog(wx.Dialog):
	def __init__(self, parent, config_manager, audio_manager, updater=None):
		super().__init__(parent, title="JadwalKu - Manajemen Agenda & Pengingat", size=(650, 480), style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)
		self.config = config_manager
		self.audio = audio_manager
		self.updater = updater
		
		sizer = wx.BoxSizer(wx.VERTICAL)
		
		# Judul & petunjuk
		sizer.Add(wx.StaticText(self, label="Daftar Agenda JadwalKu (Tekan Spasi atau tombol Aktifkan untuk Check/Uncheck):"), 0, wx.ALL, 8)
		
		# List box agenda
		self.listBox = wx.ListBox(self, style=wx.LB_SINGLE)
		self.listBox.Bind(wx.EVT_KEY_DOWN, self.onListKeyDown)
		self.listBox.Bind(wx.EVT_LISTBOX_DCLICK, self.onEdit)
		sizer.Add(self.listBox, 1, wx.EXPAND | wx.LEFT | wx.RIGHT, 8)
		
		# Tombol-tombol aksi
		btnSizer1 = wx.BoxSizer(wx.HORIZONTAL)
		self.btnAdd = wx.Button(self, label="&Tambah Jadwal Baru...")
		self.btnAdd.Bind(wx.EVT_BUTTON, self.onAdd)
		btnSizer1.Add(self.btnAdd, 0, wx.ALL, 4)
		
		self.btnEdit = wx.Button(self, label="&Edit Jadwal...")
		self.btnEdit.Bind(wx.EVT_BUTTON, self.onEdit)
		btnSizer1.Add(self.btnEdit, 0, wx.ALL, 4)
		
		self.btnDel = wx.Button(self, label="&Hapus Jadwal")
		self.btnDel.Bind(wx.EVT_BUTTON, self.onDelete)
		btnSizer1.Add(self.btnDel, 0, wx.ALL, 4)
		
		self.btnToggle = wx.Button(self, label="&Check / Uncheck Status")
		self.btnToggle.Bind(wx.EVT_BUTTON, self.onToggleActive)
		btnSizer1.Add(self.btnToggle, 0, wx.ALL, 4)
		sizer.Add(btnSizer1, 0, wx.ALIGN_LEFT | wx.LEFT | wx.RIGHT | wx.TOP, 4)
		
		btnSizer2 = wx.BoxSizer(wx.HORIZONTAL)
		self.btnTimeRemind = wx.Button(self, label="&Pengaturan Pengingat Waktu Berkala...")
		self.btnTimeRemind.Bind(wx.EVT_BUTTON, self.onTimeReminder)
		btnSizer2.Add(self.btnTimeRemind, 0, wx.ALL, 4)
		
		self.btnHelp = wx.Button(self, label="&Bantuan...")
		self.btnHelp.Bind(wx.EVT_BUTTON, self.onHelp)
		btnSizer2.Add(self.btnHelp, 0, wx.ALL, 4)
		
		if self.updater:
			self.btnCheckUp = wx.Button(self, label="&Cek Pembaruan...")
			self.btnCheckUp.Bind(wx.EVT_BUTTON, self.onCheckUpdate)
			btnSizer2.Add(self.btnCheckUp, 0, wx.ALL, 4)
		
		self.btnClose = wx.Button(self, wx.ID_CANCEL, label="&Tutup")
		btnSizer2.Add(self.btnClose, 0, wx.ALL, 4)
		sizer.Add(btnSizer2, 0, wx.ALIGN_RIGHT | wx.ALL, 8)
		
		self.SetSizer(sizer)
		self.Centre()
		self.refreshList()
		self.listBox.SetFocus()

	def refreshList(self, select_index=0):
		self.listBox.Clear()
		self.schedules = self.config.get_schedules()
		for item in self.schedules:
			status_mark = "[V]" if item.get("active", False) else "[ ]"
			time_str = f"{int(item.get('hour', 0)):02d}:{int(item.get('minute', 0)):02d}"
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
			dlg = TimeReminderDialog(self, cfg.copy())
			res = dlg.ShowModal()
			if res == wx.ID_OK:
				updated = dlg.get_result()
				self.config.update_time_reminder_config(updated)
				status = "Aktif" if updated["enabled"] else "Nonaktif"
				ui.message(f"Pengaturan pengingat waktu berkala berhasil disimpan ({status}, tiap {updated['interval']} menit).")
			dlg.Destroy()
		finally:
			gui.mainFrame.postPopup()

	def onCheckUpdate(self, event):
		if self.updater:
			ui.message("Memeriksa pembaruan ke server...")
			self.updater.check_update_manual()

	def onHelp(self, event):
		gui.mainFrame.prePopup()
		try:
			dlg = HelpDialog(self)
			dlg.ShowModal()
			dlg.Destroy()
		finally:
			gui.mainFrame.postPopup()


