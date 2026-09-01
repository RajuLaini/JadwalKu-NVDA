# -*- coding: UTF-8 -*-
import globalPluginHandler
import ui
import gui
import wx
import logHandler
import datetime
import scriptHandler
import api
import os

from .configManager import ConfigManager
from .audioManager import AudioManager
from .ttsManager import TTSManager
from .scheduler import Scheduler
from .guiDialogs import JadwalKuDialog, TimeReminderDialog, HelpDialog, ChangelogDialog, AudioManagerDialog, QuickTimerDialog, OneTimeAlarmDialog, CalendarDialog, WorldClockDialog, TTSManagerDialog, FeedbackDialog, ActiveTimerManagerDialog, ActiveAlarmManagerDialog
from .updateChecker import UpdateChecker
from .statusChecker import get_active_status

_plugin_instance = None

class JadwalKuSettingsPanel(gui.settingsDialogs.SettingsPanel):
	title = "JadwalKu"

	def makeSettings(self, settingsSizer):
		global _plugin_instance
		if not _plugin_instance:
			return
		
		infoLabel = wx.StaticText(self, label="JadwalKu - Pengingat Agenda & Waktu Berkala Aksesibel.\n\nAnda dapat mengelola seluruh jadwal agenda dan pengingat waktu berkala secara detail melalui Dialog Layout Utama JadwalKu, atau menggunakan tombol di bawah ini:")
		settingsSizer.Add(infoLabel, 0, wx.ALL, 8)
		
		btnSizer1 = wx.BoxSizer(wx.HORIZONTAL)
		self.btnOpenLayout = wx.Button(self, label="&Buka Dialog Utama JadwalKu...")
		self.btnOpenLayout.Bind(wx.EVT_BUTTON, self.onOpenLayout)
		btnSizer1.Add(self.btnOpenLayout, 0, wx.ALL, 5)
		
		self.btnOpenTime = wx.Button(self, label="&Pengingat Waktu Berkala...")
		self.btnOpenTime.Bind(wx.EVT_BUTTON, self.onOpenTime)
		btnSizer1.Add(self.btnOpenTime, 0, wx.ALL, 5)
		settingsSizer.Add(btnSizer1, 0, wx.ALL, 2)
		
		btnSizer2 = wx.BoxSizer(wx.HORIZONTAL)
		self.btnOpenAudio = wx.Button(self, label="Pengaturan &Audio Manager (Speaker)...")
		self.btnOpenAudio.Bind(wx.EVT_BUTTON, self.onOpenAudio)
		btnSizer2.Add(self.btnOpenAudio, 0, wx.ALL, 5)
		
		self.btnOpenTTS = wx.Button(self, label="Pengaturan &Mesin TTS Mandiri...")
		self.btnOpenTTS.Bind(wx.EVT_BUTTON, self.onOpenTTS)
		btnSizer2.Add(self.btnOpenTTS, 0, wx.ALL, 5)
		settingsSizer.Add(btnSizer2, 0, wx.ALL, 2)
		
		btnSizer3 = wx.BoxSizer(wx.HORIZONTAL)
		self.btnShare = wx.Button(self, label="&Bagikan Add-on (Salin Link/Undang)...")
		self.btnShare.Bind(wx.EVT_BUTTON, self.onShareAddon)
		btnSizer3.Add(self.btnShare, 0, wx.ALL, 5)
		
		self.btnFeedback = wx.Button(self, label="&Kirim Laporan, Kritik & Saran...")
		self.btnFeedback.Bind(wx.EVT_BUTTON, self.onOpenFeedback)
		btnSizer3.Add(self.btnFeedback, 0, wx.ALL, 5)
		settingsSizer.Add(btnSizer3, 0, wx.ALL, 2)

	def onOpenLayout(self, event):
		global _plugin_instance
		if _plugin_instance:
			wx.CallAfter(_plugin_instance.show_main_dialog)

	def onOpenTime(self, event):
		global _plugin_instance
		if _plugin_instance:
			wx.CallAfter(_plugin_instance.show_time_reminder_dialog)

	def onOpenAudio(self, event):
		global _plugin_instance
		if _plugin_instance:
			wx.CallAfter(_plugin_instance.show_audio_manager_dialog)

	def onOpenTTS(self, event):
		global _plugin_instance
		if _plugin_instance:
			wx.CallAfter(_plugin_instance.show_tts_manager_dialog)

	def onShareAddon(self, event):
		global _plugin_instance
		if _plugin_instance:
			wx.CallAfter(_plugin_instance.share_addon_link)

	def onOpenFeedback(self, event):
		global _plugin_instance
		if _plugin_instance:
			wx.CallAfter(_plugin_instance.show_feedback_dialog)

	def onSave(self):
		pass


class GlobalPlugin(globalPluginHandler.GlobalPlugin):
	scriptCategory = "JadwalKu"
	__gestures = {
		"kb:NVDA+/": "activateCommandLayer",
		"kb:NVDA+shift+/": "checkDynamicStatus",
		"kb:NVDA+F12": "reportTimeDate"
	}

	def __init__(self):
		super().__init__()
		global _plugin_instance
		_plugin_instance = self
		
		self.config = ConfigManager()
		self.audio = AudioManager(self.config)
		self.tts = TTSManager(self.config, self.audio)
		self.audio.tts_manager = self.tts
		self.scheduler = Scheduler(self.config, self.audio, self.tts)
		try:
			from globalPlugins.jadwalku.habitManager import HabitManager
			from globalPlugins.jadwalku.configManager import CONFIG_DIR
			self.habit_manager = HabitManager(CONFIG_DIR)
		except Exception as e:
			import logHandler
			logHandler.log.error(f"JadwalKu: Gagal memuat HabitManager: {e}")
			self.habit_manager = None
		
		from . import pomodoro
		self.pomodoro_manager = pomodoro.PomodoroManager(self.audio, self)
		
		self.scheduler.start()
		
		try:
			from .voiceCommandManager import VoiceCommandManager
			self.vc_manager = VoiceCommandManager(self._on_voice_command_triggered)
			vc_cfg = self.config.get_voice_command()
			
			in_dev_name = vc_cfg.get("input_device", "Default (Microsoft Sound Mapper)")
			devs = self.vc_manager.get_input_devices()
			idx = -1
			for d_idx, d_name in devs:
				if d_name == in_dev_name:
					idx = d_idx
					break
			self.vc_manager.set_input_device(idx)
			
			if vc_cfg.get("enabled", False):
				self.vc_manager.start_listening()
		except Exception as e:
			logHandler.log.error(f"JadwalKu: Gagal memuat VoiceCommandManager: {e}")
			self.vc_manager = None
		
		self.updater = UpdateChecker(self.config, self)
		self.updater.start_auto_check()
		
		self.is_dialog_open = False
		self.switch = False
		
		self.commandLayerGestures = {
			"kb:o": "openLayout",
			"kb:enter": "openLayout",
			"kb:1": "openQuickTimer",
			"kb:3": "openPomodoroTimer",
			"kb:2": "openOneTimeAlarm",
			"kb:w": "announceTime",
			"kb:r": "openFeedback",
			"kb:k": "openCalendar",
			"kb:d": "openWorldClock",
			"kb:j": "openHabitTracker",
			"kb:l": "openBadgeShowcase",
			"kb:h": "todayAgenda",
			"kb:a": "toggleTimeReminder",
			"kb:s": "openAudioManager",
			"kb:m": "toggleVoiceCommand",
			"kb:t": "openTTSManager",
			"kb:p": "openLayout",
			"kb:g": "shareAddon",
			"kb:u": "checkUpdate",
			"kb:v": "showChangelog",
			"kb:z": "snoozeAlarm",
			"kb:space": "stopAudio",
			"kb:b": "help",
			"kb:f1": "help",
			"kb:escape": "exitLayer",
		}
		
		# Daftarkan ke NVDASettingsDialog
		try:
			gui.settingsDialogs.NVDASettingsDialog.categoryClasses.append(JadwalKuSettingsPanel)
		except Exception as e:
			logHandler.log.error(f"JadwalKu: Gagal mendaftarkan panel pengaturan: {e}")
			
		# Daftarkan ke Tools Menu NVDA
		try:
			self.menu_item = gui.mainFrame.sysTrayIcon.toolsMenu.Append(wx.ID_ANY, "&JadwalKu - Manajemen Agenda & Pengingat...")
			gui.mainFrame.sysTrayIcon.Bind(wx.EVT_MENU, self.on_tools_menu, self.menu_item)
		except Exception as e:
			logHandler.log.error(f"JadwalKu: Gagal menambah menu ke Tools: {e}")

	def terminate(self):
		global _plugin_instance
		_plugin_instance = None
		
		if getattr(self, 'updater', None):
			self.updater.stop()
		if self.scheduler:
			self.scheduler.stop()
		if self.audio:
			self.audio.stop_sound()
		if getattr(self, 'tts', None):
			self.tts.stop()
			
		try:
			gui.settingsDialogs.NVDASettingsDialog.categoryClasses.remove(JadwalKuSettingsPanel)
		except Exception:
			pass
			
		try:
			if hasattr(self, 'menu_item') and self.menu_item:
				gui.mainFrame.sysTrayIcon.toolsMenu.Remove(self.menu_item)
		except Exception:
			pass
			
		super().terminate()

	def check_dialog_open(self):
		if self.is_dialog_open:
			ui.message("Harap tutup dialog JadwalKu yang sedang terbuka terlebih dahulu.")
			return False
		return True

	def on_tools_menu(self, event):
		wx.CallAfter(self.show_main_dialog)

	def show_main_dialog(self):
		if not self.check_dialog_open():
			return
		self.is_dialog_open = True
		gui.mainFrame.prePopup()
		try:
			dlg = JadwalKuDialog(gui.mainFrame, self.config, self.audio, updater=getattr(self, 'updater', None), tts_manager=getattr(self, 'tts', None))
			dlg.ShowModal()
			dlg.Destroy()
		finally:
			self.is_dialog_open = False
			gui.mainFrame.postPopup()

	def show_time_reminder_dialog(self):
		if not self.check_dialog_open():
			return
		self.is_dialog_open = True
		gui.mainFrame.prePopup()
		try:
			cfg = self.config.get_time_reminder_config()
			dlg = TimeReminderDialog(gui.mainFrame, cfg.copy(), tts_manager=getattr(self, 'tts', None), config_manager=self.config)
			res = dlg.ShowModal()
			if res == wx.ID_OK:
				updated = dlg.get_result()
				self.config.update_time_reminder_config(updated)
				status = "Aktif" if updated["enabled"] else "Nonaktif"
				ui.message(f"Pengaturan pengingat waktu berkala berhasil disimpan ({status}, tiap {updated['interval']} menit).")
			dlg.Destroy()
		finally:
			self.is_dialog_open = False
			gui.mainFrame.postPopup()

	def show_tts_manager_dialog(self):
		if not self.check_dialog_open():
			return
		self.is_dialog_open = True
		gui.mainFrame.prePopup()
		try:
			dlg = TTSManagerDialog(gui.mainFrame, getattr(self, 'tts', None), self.config)
			if dlg.ShowModal() == wx.ID_OK:
				self.config.update_tts_config(dlg.get_result())
				status = "Aktif" if dlg.get_result()["enabled"] else "Nonaktif"
				ui.message(f"Pengaturan TTS Mandiri berhasil disimpan ({status}).")
			dlg.Destroy()
		finally:
			self.is_dialog_open = False
			gui.mainFrame.postPopup()

	def show_audio_manager_dialog(self):
		if not self.check_dialog_open():
			return
		self.is_dialog_open = True
		gui.mainFrame.prePopup()
		try:
			dlg = AudioManagerDialog(gui.mainFrame, self.audio, self.config)
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
			self.is_dialog_open = False
			gui.mainFrame.postPopup()

	def show_help_dialog(self):
		if not self.check_dialog_open():
			return
		self.is_dialog_open = True
		gui.mainFrame.prePopup()
		try:
			from .simulation import start_tutorial
			start_tutorial(gui.mainFrame)
		except Exception as e:
			import traceback
			with open(r"C:\Users\Raju Laini\Documents\Project_Jadwalku\error_log.txt", "w") as f:
				f.write(traceback.format_exc())
			ui.message("Terjadi kesalahan saat membuka bantuan.")
		finally:
			self.is_dialog_open = False
			gui.mainFrame.postPopup()

	def show_changelog_dialog(self):
		if not self.check_dialog_open():
			return
		self.is_dialog_open = True
		gui.mainFrame.prePopup()
		try:
			dlg = ChangelogDialog(gui.mainFrame)
			dlg.ShowModal()
			dlg.Destroy()
		finally:
			self.is_dialog_open = False
			gui.mainFrame.postPopup()

	def share_addon_link(self):
		import gui
		import wx
		import addonHandler
		import api
		dlg = wx.SingleChoiceDialog(gui.mainFrame, "Pilih metode untuk membagikan JadwalKu:", "Bagikan JadwalKu", ["Salin Tautan Unduhan (Direct Link)", "Salin Pesan Undangan (WhatsApp/Medsos)"])
		if dlg.ShowModal() == wx.ID_OK:
			sel = dlg.GetSelection()
			
			try:
				addon = addonHandler.getCodeAddon()
				current_version = addon.manifest['version']
			except Exception:
				current_version = "1.7.0"
				
			url = f"https://github.com/RajuLaini/JadwalKu-NVDA/raw/main/JadwalKu-v{current_version}.nvda-addon"
			if sel == 0:
				text = url
				msg = f"Tautan unduhan langsung JadwalKu v{current_version} berhasil disalin ke clipboard!"
			else:
				text = f"Halo! Ayo coba JadwalKu, Add-on NVDA keren untuk pengingat jadwal, alarm, dan Voice Pack Store!\n\nUnduh versi terbarunya (v{current_version}) langsung di sini:\n{url}"
				msg = "Pesan undangan berhasil disalin! Silakan paste di obrolan WhatsApp atau Medsos teman Anda."
			
			if api.copyToClip(text):
				import ui
				ui.message(msg)
		dlg.Destroy()

	def show_pomodoro_dialog(self):
		if not self.check_dialog_open():
			return
		self.is_dialog_open = True
		gui.mainFrame.prePopup()
		try:
			from . import pomodoro
			dlg = pomodoro.PomodoroTimerDialog(gui.mainFrame, self.pomodoro_manager)
			dlg.ShowModal()
		finally:
			self.is_dialog_open = False
			gui.mainFrame.postPopup()

	def show_quick_timer_dialog(self):
		if not self.check_dialog_open():
			return
		self.is_dialog_open = True
		gui.mainFrame.prePopup()
		try:
			dlg = QuickTimerDialog(gui.mainFrame, audio_manager=self.audio)
			if dlg.ShowModal() == wx.ID_OK:
				res = dlg.get_result()
				if self.scheduler:
					self.scheduler.add_quick_timer(res["duration"], res["unit"], res["audio_file"], prep_seconds=res.get("prep_seconds", 0))
			dlg.Destroy()
		finally:
			self.is_dialog_open = False
			gui.mainFrame.postPopup()

	def show_one_time_alarm_dialog(self):
		if not self.check_dialog_open():
			return
		self.is_dialog_open = True
		gui.mainFrame.prePopup()
		try:
			dlg = OneTimeAlarmDialog(gui.mainFrame, audio_manager=self.audio)
			if dlg.ShowModal() == wx.ID_OK:
				res = dlg.get_result()
				if self.scheduler:
					self.scheduler.add_one_time_alarm(res["hour"], res["minute"], res["second"], res["audio_file"], is_alarm=res["is_alarm"])
			dlg.Destroy()
		finally:
			self.is_dialog_open = False
			gui.mainFrame.postPopup()

	def show_calendar_dialog(self):
		if not self.check_dialog_open():
			return
		self.is_dialog_open = True
		gui.mainFrame.prePopup()
		try:
			dlg = CalendarDialog(gui.mainFrame)
			dlg.ShowModal()
			dlg.Destroy()
		finally:
			self.is_dialog_open = False
			gui.mainFrame.postPopup()

	def show_world_clock_dialog(self):
		if not self.check_dialog_open():
			return
		self.is_dialog_open = True
		gui.mainFrame.prePopup()
		try:
			dlg = WorldClockDialog(gui.mainFrame)
			dlg.ShowModal()
			dlg.Destroy()
		finally:
			self.is_dialog_open = False
			gui.mainFrame.postPopup()

	def show_feedback_dialog(self):
		if not self.check_dialog_open():
			return
		from .reportSender import check_can_send_report
		allowed, reason = check_can_send_report(self.config)
		if not allowed:
			ui.message(reason)
			return
		self.is_dialog_open = True
		gui.mainFrame.prePopup()
		try:
			dlg = FeedbackDialog(gui.mainFrame, self.config)
			dlg.ShowModal()
			dlg.Destroy()
		finally:
			self.is_dialog_open = False
			gui.mainFrame.postPopup()


	def getScript(self, gesture):
		if self.switch:
			script_name = None
			for identifier in gesture.identifiers:
				if identifier in self.commandLayerGestures:
					script_name = "script_" + self.commandLayerGestures[identifier]
					break
			
			if script_name:
				target_script = getattr(self, script_name)
				should_speak = (script_name == "script_exitLayer")
				
				def _wrapped_script(g, _target=target_script, _speak=should_speak):
					self.closeCommandsLayer(speak=_speak)
					wx.CallLater(50, _target, g)
				
				return _wrapped_script
			else:
				self.closeCommandsLayer(speak=True)
		
		return super().getScript(gesture)

	def closeCommandsLayer(self, speak=True):
		if self.switch:
			self.audio.play_sound("off.wav")
		if speak:
			ui.message("Keluar dari mode JadwalKu.")
		self.switch = False

	@scriptHandler.script(
		description="Mengaktifkan mode perintah JadwalKu (Tekan P Pengaturan, T TTS, 1 Quick Timer, 2 Alarm, W Waktu, K Kalender, D Jam Dunia, J Agenda, V Riwayat, Z Snooze, Spasi Stop)",
		gesture="kb:NVDA+/"
	)

	def show_active_timer_dialog(self):
		if not self.check_dialog_open():
			return
		self.is_dialog_open = True
		import gui
		gui.mainFrame.prePopup()
		try:
			dlg = ActiveTimerManagerDialog(gui.mainFrame, self.scheduler)
			dlg.ShowModal()
			dlg.Destroy()
		finally:
			self.is_dialog_open = False
			gui.mainFrame.postPopup()

	def show_active_alarm_dialog(self):
		if not self.check_dialog_open():
			return
		self.is_dialog_open = True
		import gui
		gui.mainFrame.prePopup()
		try:
			dlg = ActiveAlarmManagerDialog(gui.mainFrame, self.scheduler)
			dlg.ShowModal()
			dlg.Destroy()
		finally:
			self.is_dialog_open = False
			gui.mainFrame.postPopup()

	def script_activateCommandLayer(self, gesture):
		if not self.check_dialog_open():
			return
		self.audio.play_sound("on.wav")
		ui.message("Masuk ke mode JadwalKu. Tekan O (atau Enter) untuk Layout, J untuk Pelacak Kebiasaan, L untuk Lencana Ketekunan, 1 Quick Timer, 2 Alarm, 3 Pomodoro Timer, W Waktu, K Kalender, D Jam Dunia, M Microphone, V Riwayat, r untuk laporan, atau B Bantuan.")
		self.switch = True

	
	def script_openHabitTracker(self, gesture):
		if not self.habit_manager:
			ui.message("Sistem Pelacak Kebiasaan gagal dimuat.")
			return
		wx.CallAfter(self.show_habit_tracker_dialog)

	def show_habit_tracker_dialog(self):
		if not self.check_dialog_open():
			return
		self.is_dialog_open = True
		import gui
		gui.mainFrame.prePopup()
		try:
			from .guiDialogs import HabitTrackerDialog
			dlg = HabitTrackerDialog(gui.mainFrame, self.scheduler, self.habit_manager)
			dlg.ShowModal()
			dlg.Destroy()
		finally:
			self.switch = False
			self.is_dialog_open = False
			gui.mainFrame.postPopup()

	def script_openBadgeShowcase(self, gesture):
		if not self.habit_manager:
			ui.message("Sistem Pelacak Kebiasaan gagal dimuat.")
			return
		wx.CallAfter(self.show_badge_showcase_dialog)

	def show_badge_showcase_dialog(self):
		if not self.check_dialog_open():
			return
		self.is_dialog_open = True
		import gui
		gui.mainFrame.prePopup()
		try:
			from .guiDialogs import BadgeShowcaseDialog
			dlg = BadgeShowcaseDialog(gui.mainFrame, self.habit_manager)
			dlg.ShowModal()
			dlg.Destroy()
		finally:
			self.switch = False
			self.is_dialog_open = False
			gui.mainFrame.postPopup()

	def script_openLayout(self, gesture):
		wx.CallAfter(self.show_main_dialog)

	def script_openQuickTimer(self, gesture):
		if getattr(self.scheduler, "quick_timers", []):
			wx.CallAfter(self.show_active_timer_dialog)
		else:
			wx.CallAfter(self.show_quick_timer_dialog)

	def script_openPomodoroTimer(self, gesture):
		wx.CallAfter(self.show_pomodoro_dialog)

	def script_openOneTimeAlarm(self, gesture):
		if getattr(self.scheduler, "one_time_alarms", []):
			wx.CallAfter(self.show_active_alarm_dialog)
		else:
			wx.CallAfter(self.show_one_time_alarm_dialog)

	def script_openCalendar(self, gesture):
		wx.CallAfter(self.show_calendar_dialog)

	def script_openWorldClock(self, gesture):
		wx.CallAfter(self.show_world_clock_dialog)

	def script_openAudioManager(self, gesture):
		wx.CallAfter(self.show_audio_manager_dialog)

	def script_openTTSManager(self, gesture):
		wx.CallAfter(self.show_tts_manager_dialog)

	def format_time_str(self, now, time_settings):
		is_24 = time_settings.get("time_format", "24") == "24"
		style = time_settings.get("time_speech_style", "default")
		inc_sec = time_settings.get("include_seconds", False) or style == "full_seconds" or style == "with_seconds"
		
		if is_24:
			h_str = f"{now.hour:02d}"
			ampm = ""
		else:
			h_12 = now.hour % 12
			if h_12 == 0:
				h_12 = 12
			ampm = " AM" if now.hour < 12 else " PM"
			h_str = f"{h_12:02d}"
		
		m_str = f"{now.minute:02d}"
		s_str = f"{now.second:02d}"
		
		if style == "only_time":
			return f"{h_str}:{m_str}:{s_str}{ampm}" if inc_sec else f"{h_str}:{m_str}{ampm}"
		elif style == "prefix_pukul":
			return f"Waktu sekarang pukul {h_str}:{m_str}:{s_str}{ampm}" if inc_sec else f"Waktu sekarang pukul {h_str}:{m_str}{ampm}"
		elif style == "with_seconds":
			return f"Pukul {h_str}:{m_str}{ampm} lewat {now.second} detik"
		elif style == "full_seconds":
			return f"Waktu sekarang pukul {h_str}:{m_str}:{s_str}{ampm}"
		elif style == "jam_lewat_menit":
			return f"Jam {h_str} lewat {m_str} menit{ampm}"
		elif style == "jam_lewat_menit_detik":
			return f"Jam {h_str} lewat {m_str} menit {s_str} detik{ampm}"
		else:
			# default
			return f"{h_str}:{m_str}:{s_str}{ampm} waktu sekarang" if inc_sec else f"{h_str}:{m_str}{ampm} waktu sekarang"

	def format_date_str(self, now, time_settings):
		day_names = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat", "Sabtu", "Minggu"]
		month_names = ["", "Januari", "Februari", "Maret", "April", "Mei", "Juni", "Juli", "Agustus", "September", "Oktober", "November", "Desember"]
		d_name = day_names[now.weekday()]
		m_name = month_names[now.month]
		
		style = time_settings.get("date_speech_style", "default")
		if style == "prefix_hari":
			return f"Hari {d_name}, tanggal {now.day} bulan {m_name} tahun {now.year}"
		elif style == "numeric":
			return f"{now.day:02d}/{now.month:02d}/{now.year}"
		elif style == "suffix_hari":
			return f"Tanggal {now.day} {m_name} {now.year} hari {d_name}"
		else:
			# default
			return f"{d_name}, {now.day} {m_name} {now.year}"

	def format_full_year_countdown(self, now, time_settings):
		end_y = datetime.datetime(now.year + 1, 1, 1, 0, 0, 0)
		diff = end_y - now
		days_left = diff.days
		hours_left = diff.seconds // 3600
		
		date_s = self.format_date_str(now, time_settings)
		time_s = self.format_time_str(now, time_settings)
		
		style = time_settings.get("full_speech_style", "default")
		if style == "short":
			month_names = ["", "Januari", "Februari", "Maret", "April", "Mei", "Juni", "Juli", "Agustus", "September", "Oktober", "November", "Desember"]
			return f"{now.day} {month_names[now.month]} {now.year} {now.strftime('%H:%M')}. Akhir tahun kurang {days_left} hari {hours_left} jam."
		else:
			return f"{date_s}, {time_s}. Sisa waktu menuju akhir tahun {now.year}: {days_left} hari {hours_left} jam lagi."

	@scriptHandler.script(
		description="Membacakan waktu (1x), tanggal (2x), atau informasi lengkap akhir tahun (3x)",
		gesture="kb:NVDA+F12"
	)
	def script_reportTimeDate(self, gesture):
		time_settings = self.config.get_time_settings()
		if not time_settings.get("override_nvda_f12", True):
			try:
				import globalCommands
				if hasattr(globalCommands, 'commands') and hasattr(globalCommands.commands, 'script_dateTime'):
					globalCommands.commands.script_dateTime(gesture)
					return
			except Exception:
				pass
			if hasattr(gesture, 'send'):
				gesture.send()
			return
		
		repeat_count = scriptHandler.getLastScriptRepeatCount()
		now = datetime.datetime.now()
		if repeat_count == 0:
			msg = self.format_time_str(now, time_settings)
		elif repeat_count == 1:
			msg = self.format_date_str(now, time_settings)
		else:
			msg = self.format_full_year_countdown(now, time_settings)
		
		if hasattr(self, "pomodoro_manager") and self.pomodoro_manager.is_active:
			msg += " " + self.pomodoro_manager.get_status_str()
		
		ui.message(msg)

	def script_announceTime(self, gesture):
		now = datetime.datetime.now()
		time_settings = self.config.get_time_settings()
		time_str = self.format_time_str(now, time_settings)
		
		cfg = self.config.get_time_reminder_config()
		status = "aktif" if cfg.get("enabled", False) else "nonaktif"
		interval = cfg.get("interval", 60)
		status_msg = f"Pengingat waktu berkala saat ini {status} (tiap {interval} menit)."
		
		pomodoro_msg = ""
		if hasattr(self, "pomodoro_manager") and self.pomodoro_manager.is_active:
			pomodoro_msg = " " + self.pomodoro_manager.get_status_str()
			
		full_msg = f"{time_str}. {status_msg}{pomodoro_msg}"
		
		active_vp = cfg.get("active_voice_pack", "")
		mode = cfg.get("mode", "both")
		
		if active_vp:
			import os
			if mode in ("audio", "both"):
				self.audio.play_sound("chime.wav")
						
			is_24 = time_settings.get("time_format", "24") == "24"
			style = time_settings.get("time_speech_style", "default")
			inc_sec = time_settings.get("include_seconds", False) or style == "full_seconds" or style == "with_seconds"
			
			# Buang ":00" agar tidak dibaca "nol" pada menit pas
			clean_str = time_str.lower().replace(":00", " ").replace(":", " ")
			words = clean_str.split()
			vp_files = []
			try:
				from globalPlugins.jadwalku.voicePackManager import VoicePackManager
				vp_mgr = VoicePackManager(os.path.dirname(os.path.abspath(__file__)))
				pack_path = os.path.join(vp_mgr.pack_dir, active_vp)
				if os.path.exists(pack_path):
					temp_dir = vp_mgr.extract_pack_to_temp(pack_path)
					if temp_dir:
						for w in words:
							if w.isdigit():
								w = str(int(w))
							wav_path = os.path.join(temp_dir, f"{w}.wav")
							if os.path.exists(wav_path):
								vp_files.append(wav_path)
							else:
								import logHandler
								logHandler.log.warning(f"JadwalKu VoicePack: Word '{w}' not found in pack, skipping.")
						
						if vp_files:
							import logHandler
							logHandler.log.info(f"JadwalKu DEBUG: vp_files = {vp_files}")
							def delayed_play():
								vp_vol = cfg.get("voice_pack_volume", 100)
								self.audio.play_voice_pack_sequence(vp_files, volume_override=vp_vol)
							wx.CallLater(350 if mode == "both" else 50, delayed_play)
							ui.message(status_msg)
							return
						else:
							import logHandler
							logHandler.log.error(f"JadwalKu DEBUG: No valid words found in {words}")
			except Exception as e:
				import logHandler
				logHandler.log.error(f"JadwalKu DEBUG EXCEPTION: {e}")
				pass
				
		# Fallback
		if hasattr(self, "tts") and self.tts and self.tts.is_enabled():
			self.tts.speak(full_msg)
		else:
			ui.message(full_msg)

	def script_nextAgenda(self, gesture):
		now = datetime.datetime.now()
		schedules = self.config.get_schedules()
		active_schedules = [item for item in schedules if item.get("active", False)]
		
		if not active_schedules:
			ui.message("Tidak ada jadwal agenda yang aktif saat ini.")
			return
		
		# Cari agenda terdekat berikutnya hari ini
		upcoming = []
		for item in active_schedules:
			h = int(item.get("hour", 0))
			m = int(item.get("minute", 0))
			int_h = int(item.get("interval_hour", 0))
			if int_h > 0:
				end_h = int(item.get("interval_end_hour", 23))
				curr_h = h
				if h <= end_h:
					while curr_h <= end_h:
						item_time = now.replace(hour=curr_h, minute=m, second=0, microsecond=0)
						if item_time > now:
							upcoming.append((item_time, item))
						curr_h += int_h
				else:  # Lintas malam
					while curr_h <= 23:
						item_time = now.replace(hour=curr_h, minute=m, second=0, microsecond=0)
						if item_time > now:
							upcoming.append((item_time, item))
						curr_h += int_h
					curr_h = (h + int_h * ((24 - h + int_h - 1) // int_h)) % 24
					while curr_h <= end_h:
						item_time = now.replace(hour=curr_h, minute=m, second=0, microsecond=0)
						if item_time > now:
							upcoming.append((item_time, item))
						curr_h += int_h
			else:
				item_time = now.replace(hour=h, minute=m, second=0, microsecond=0)
				if item_time > now:
					upcoming.append((item_time, item))
		
		if upcoming:
			upcoming.sort(key=lambda x: x[0])
			next_time, next_item = upcoming[0]
			diff_mins = int((next_time - now).total_seconds() / 60)
			if diff_mins >= 60:
				hours_left = diff_mins // 60
				mins_left = diff_mins % 60
				time_left_str = f"{hours_left} jam {mins_left} menit lagi" if mins_left > 0 else f"{hours_left} jam lagi"
			else:
				time_left_str = f"{diff_mins} menit lagi"
			
			int_h = int(next_item.get("interval_hour", 0))
			if int_h > 0:
				end_h = int(next_item.get("interval_end_hour", 23))
				repeat_str = f" (Tiap {int_h} Jam Sekali s.d. Jam {end_h:02d}:00)"
			else:
				repeat_str = ""
			ui.message(f"Jadwal terdekat berikutnya: {next_item.get('name')}{repeat_str} pada jam {next_time.hour:02d}:{next_time.minute:02d} ({time_left_str}).")
		else:
			ui.message("Seluruh jadwal agenda hari ini sudah lewat.")

	def script_todayAgenda(self, gesture):
		schedules = self.config.get_schedules()
		active_schedules = [item for item in schedules if item.get("active", False)]
		
		if not active_schedules:
			ui.message("Tidak ada jadwal agenda yang aktif hari ini.")
			return
		
		msg_lines = ["Daftar Agenda Aktif:"]
		for item in active_schedules:
			h = int(item.get("hour", 0))
			m = int(item.get("minute", 0))
			int_h = int(item.get("interval_hour", 0))
			if int_h > 0:
				end_h = int(item.get("interval_end_hour", 23))
				repeat_str = f" (Tiap {int_h} jam sekali s.d. Jam {end_h:02d}:00)"
			else:
				repeat_str = ""
			msg_lines.append(f"Jam {h:02d}:{m:02d}{repeat_str} - {item.get('name')}")
		
		ui.message(". ".join(msg_lines))

	def script_toggleTimeReminder(self, gesture):
		cfg = self.config.get_time_reminder_config()
		cfg["enabled"] = not cfg.get("enabled", False)
		self.config.update_time_reminder_config(cfg)
		status_str = "diaktifkan" if cfg["enabled"] else "dinonaktifkan"
		ui.message(f"Pengingat waktu berkala tiap {cfg.get('interval', 60)} menit sekarang {status_str}.")

	def script_stopAudio(self, gesture):
		if getattr(self.audio, "is_alarm_ringing", False):
			self.audio.stop_alarm()
		elif self.audio.stop_sound():
			ui.message("Suara notifikasi dihentikan.")

	def script_snoozeAlarm(self, gesture):
		if getattr(self.audio, "is_alarm_ringing", False) or getattr(self.audio, "active_alarm_info", None):
			self.audio.snooze_alarm()
		else:
			ui.message("Tidak ada alarm yang sedang berbunyi untuk ditunda.")

	def script_help(self, gesture):
		wx.CallAfter(self.show_help_dialog)

	def script_checkUpdate(self, gesture):
		if self.updater:
			ui.message("Memeriksa pembaruan JadwalKu ke server...")
			self.updater.check_update_manual()
		else:
			ui.message("Fitur pemeriksa pembaruan tidak aktif.")

	def script_checkDynamicStatus(self, gesture):
		statuses = get_active_status(self.scheduler, self.pomodoro_manager)
		if not statuses:
			ui.message("Tidak ada yang aktif.")
		else:
			for stat in statuses:
				ui.message(stat)

	def script_showChangelog(self, gesture):
		ui.message("JadwalKu Versi 1.6.2. Membuka riwayat pembaruan (Changelog)...")
		wx.CallAfter(self.show_changelog_dialog)

	def script_shareAddon(self, gesture):
		wx.CallAfter(self.share_addon_link)

	def script_openFeedback(self, gesture):
		wx.CallAfter(self.show_feedback_dialog)

	def script_exitLayer(self, gesture):
		pass

	def script_toggleVoiceCommand(self, gesture):
		if not getattr(self, "vc_manager", None):
			ui.message("Modul perintah suara tidak tersedia.")
			return
			
		if not self.vc_manager.is_module_installed():
			ui.message("Modul Perintah Suara belum dipasang. Buka Pengaturan untuk mengunduhnya.")
			return
			
		vc_cfg = self.config.get_voice_command()
		is_enabled = vc_cfg.get("enabled", False)
		
		if is_enabled:
			self.vc_manager.stop_listening()
			vc_cfg["enabled"] = False
			self.config.update_voice_command(vc_cfg)
			ui.message("Pemantauan Mikrofon untuk perintah suara dinonaktifkan.")
		else:
			in_dev_name = vc_cfg.get("input_device", "Default (Microsoft Sound Mapper)")
			devs = self.vc_manager.get_input_devices()
			idx = -1
			for d_idx, d_name in devs:
				if d_name == in_dev_name:
					idx = d_idx
					break
			self.vc_manager.set_input_device(idx)
			
			mic_boost = vc_cfg.get("mic_boost", 100)
			self.vc_manager.mic_boost = mic_boost
			
			if self.vc_manager.start_listening():
				vc_cfg["enabled"] = True
				self.config.update_voice_command(vc_cfg)
				ui.message("Pemantauan Mikrofon untuk perintah suara aktif.")
			else:
				ui.message("Gagal mengaktifkan mikrofon. Pastikan modul terpasang dan mikrofon tersedia.")

	def _on_voice_command_triggered(self):
		import datetime
		now = datetime.datetime.now()
		vc_cfg = self.config.get_voice_command()
		style = vc_cfg.get("speech_style", "jam_lewat_menit")
		
		# Build time string
		h = now.hour
		ampm = ""
		h_str = str(h)
		if self.config.get_time_settings().get("time_format", "24") == "12":
			ampm = " AM" if h < 12 else " PM"
			h = h % 12
			if h == 0: h = 12
			h_str = str(h)
			
		m_str = f"{now.minute:02d}"
		s_str = f"{now.second:02d}"
		
		# Format according to style
		if style == "jam_lewat_menit":
			time_str = f"Jam {h_str} lewat {now.minute} menit{ampm}"
		elif style == "jam_lewat_menit_detik":
			time_str = f"Jam {h_str} lewat {now.minute} menit {now.second} detik{ampm}"
		elif style == "default":
			time_str = f"Sekarang jam {h_str}:{m_str}{ampm}"
		else:
			# Fallback logic to full formatting can be added here, but default is fine
			time_str = f"Pukul {h_str} {now.minute} menit"
			
		# Routing Output
		out_engine = vc_cfg.get("tts_engine", "NVDA Default")
		out_dev = vc_cfg.get("output_device", "Default (Microsoft Sound Mapper)")
		mute_nvda = vc_cfg.get("mute_nvda_fallback", True)
		vc_vol = vc_cfg.get("vc_volume", 100)
		
		# If user wants to mute NVDA and we're not using NVDA Default, skip ui.message
		if not (mute_nvda and out_engine != "NVDA Default"):
			ui.message(time_str)
		else:
			# Just log it or send to braille only, but ui.message does speech+braille.
			# Using braille.handler.message avoids speech if we only want braille, but NVDA might not need it.
			import logHandler
			logHandler.log.info("VC Triggered: " + time_str)
		
		if out_engine == "NVDA Default":
			pass
		elif out_engine == "TTS Standar (SAPI 5)":
			self.tts.speak(time_str, volume_override=vc_vol)
		elif out_engine == "Voice Pack Kustom":
			vp_config = self.config.get_time_reminder_config()
			vp_id = vp_config.get("active_voice_pack", "")
			if vp_id:
				import os
				clean_str = time_str.lower().replace(":00", " ").replace(":", " ")
				words = clean_str.split()
				vp_files = []
				try:
					from globalPlugins.jadwalku.voicePackManager import VoicePackManager
					vp_mgr = VoicePackManager(os.path.dirname(os.path.abspath(__file__)))
					pack_path = os.path.join(vp_mgr.pack_dir, vp_id)
					if os.path.exists(pack_path):
						temp_dir = vp_mgr.extract_pack_to_temp(pack_path)
						if temp_dir:
							for w in words:
								if w.isdigit():
									w = str(int(w))
								wav_path = os.path.join(temp_dir, f"{w}.wav")
								if os.path.exists(wav_path):
									vp_files.append(wav_path)
							
							if vp_files:
								self.audio.play_voice_pack_sequence(vp_files, volume_override=vc_vol)
				except Exception as e:
					import logHandler
					logHandler.log.error(f"JadwalKu: Error playing VC voice pack: {e}")
			else:
				if mute_nvda: ui.message("Tidak ada Voice Pack aktif. " + time_str)
		else:
			pass

	script_toggleVoiceCommand.__doc__ = _("Mengaktifkan atau menonaktifkan pemantauan mikrofon untuk Perintah Suara.")
