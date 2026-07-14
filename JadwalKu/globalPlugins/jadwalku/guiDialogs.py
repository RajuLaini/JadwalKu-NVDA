# -*- coding: UTF-8 -*-
import wx
import datetime
import logHandler
import ui
import gui
import os

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
			"- J : Bacakan jadwal agenda terdekat berikutnya hari ini beserta sisa waktunya.\n"
			"- H : Bacakan seluruh daftar agenda aktif hari ini.\n"
			"- A : Check / Uncheck cepat status Aktifkan Pengingat Waktu Berkala.\n"
			"- S : Buka Pengaturan Audio Manager (Speaker & Suara).\n"
			"- U : Periksa pembaruan terbaru add-on secara langsung dari server.\n"
			"- Z : Tunda (Snooze) alarm yang sedang berbunyi selama 10 menit ke depan.\n"
			"- Spasi : Hentikan suara notifikasi/chime atau matikan alarm weker yang sedang berdering.\n"
			"- B atau F1 : Buka dialog panduan bantuan ini (Mode Read-Only bisa dinavigasi panah).\n"
			"- Escape : Keluar dari mode perintah JadwalKu.\n\n"
			"3. TIPS FITUR ALARM WEKER & NAVIGASI DI DIALOG UTAMA:\n"
			"- Saat menambah atau mengedit agenda, Anda dapat memilih Mode Pemberitahuan: 'Pemberitahuan Singkat (Chime)' atau 'Alarm Jam Weker'. Jika Anda memilih Alarm Jam Weker, suara akan berdering terus-menerus tanpa henti sampai Anda mematikannya (Spasi) atau menundanya (Z / Alt+T).\n"
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
		
		# 5. Mode Pemberitahuan (Chime vs Alarm Weker)
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
		return {
			"id": self.schedule_data.get("id", ""),
			"name": self.txt_name.GetValue().strip() or "Agenda Tanpa Nama",
			"frequency": self.cb_freq.GetValue(),
			"custom_days": getattr(self, "custom_days", []),
			"date": self.txt_date.GetValue().strip(),
			"hour": int(self.cb_hour.GetValue()),
			"minute": int(self.cb_minute.GetValue()),
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
		
		# 3. Suara Audio
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
		sel = self.cb_audio.GetSelection()
		audio_file = self.audio_files_map[sel] if 0 <= sel < len(self.audio_files_map) else "alarm.wav"
		return {
			"duration": dur,
			"unit": self.cb_unit.GetValue() or "Menit",
			"audio_file": audio_file
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
		
		self.btnAudio = wx.Button(self, label="Pengaturan &Audio Manager (Speaker)...")
		self.btnAudio.Bind(wx.EVT_BUTTON, self.onAudioManager)
		btnSizer2.Add(self.btnAudio, 0, wx.ALL, 4)
		
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


