# -*- coding: UTF-8 -*-
import globalPluginHandler
import ui
import gui
import wx
import logHandler
import datetime
import scriptHandler

from .configManager import ConfigManager
from .audioManager import AudioManager
from .scheduler import Scheduler
from .guiDialogs import JadwalKuDialog, TimeReminderDialog, HelpDialog, ChangelogDialog, AudioManagerDialog, QuickTimerDialog, OneTimeAlarmDialog
from .updateChecker import UpdateChecker

_plugin_instance = None

class JadwalKuSettingsPanel(gui.settingsDialogs.SettingsPanel):
	title = "JadwalKu"

	def makeSettings(self, settingsSizer):
		global _plugin_instance
		if not _plugin_instance:
			return
		
		infoLabel = wx.StaticText(self, label="JadwalKu - Pengingat Agenda & Waktu Berkala Aksesibel.\n\nAnda dapat mengelola seluruh jadwal agenda dan pengingat waktu berkala secara detail melalui Dialog Layout Utama JadwalKu, atau menggunakan tombol di bawah ini:")
		settingsSizer.Add(infoLabel, 0, wx.ALL, 8)
		
		btnSizer = wx.BoxSizer(wx.HORIZONTAL)
		self.btnOpenLayout = wx.Button(self, label="&Buka Dialog Utama JadwalKu...")
		self.btnOpenLayout.Bind(wx.EVT_BUTTON, self.onOpenLayout)
		btnSizer.Add(self.btnOpenLayout, 0, wx.ALL, 5)
		
		self.btnOpenTime = wx.Button(self, label="&Pengaturan Pengingat Waktu Berkala...")
		self.btnOpenTime.Bind(wx.EVT_BUTTON, self.onOpenTime)
		btnSizer.Add(self.btnOpenTime, 0, wx.ALL, 5)
		
		self.btnOpenAudio = wx.Button(self, label="Pengaturan &Audio Manager (Speaker)...")
		self.btnOpenAudio.Bind(wx.EVT_BUTTON, self.onOpenAudio)
		btnSizer.Add(self.btnOpenAudio, 0, wx.ALL, 5)
		
		settingsSizer.Add(btnSizer, 0, wx.ALL, 5)

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

	def onSave(self):
		pass


class GlobalPlugin(globalPluginHandler.GlobalPlugin):
	scriptCategory = "JadwalKu"

	def __init__(self):
		super().__init__()
		global _plugin_instance
		_plugin_instance = self
		
		self.config = ConfigManager()
		self.audio = AudioManager(self.config)
		self.scheduler = Scheduler(self.config, self.audio)
		self.scheduler.start()
		
		self.updater = UpdateChecker(self.config, self)
		self.updater.start_auto_check()
		
		self.is_dialog_open = False
		self.switch = False
		
		self.commandLayerGestures = {
			"kb:l": "openLayout",
			"kb:enter": "openLayout",
			"kb:1": "openQuickTimer",
			"kb:2": "openOneTimeAlarm",
			"kb:w": "announceTime",
			"kb:t": "announceTime",
			"kb:j": "nextAgenda",
			"kb:h": "todayAgenda",
			"kb:a": "toggleTimeReminder",
			"kb:s": "openAudioManager",
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
			dlg = JadwalKuDialog(gui.mainFrame, self.config, self.audio, updater=getattr(self, 'updater', None))
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
			dlg = TimeReminderDialog(gui.mainFrame, cfg.copy())
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
			dlg = HelpDialog(gui.mainFrame)
			dlg.ShowModal()
			dlg.Destroy()
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
		description="Mengaktifkan mode perintah JadwalKu (Tekan L Layout, 1 Quick Timer, 2 Alarm Sekali Pakai, W Waktu, J Agenda, V Riwayat, Z Snooze, Spasi Stop)",
		gesture="kb:NVDA+/"
	)
	def script_activateCommandLayer(self, gesture):
		if not self.check_dialog_open():
			return
		self.audio.play_sound("on.wav")
		ui.message("Masuk ke mode JadwalKu. Tekan L untuk Layout, 1 untuk Quick Timer, 2 untuk Alarm Sekali Pakai, V untuk Riwayat Pembaruan, W info waktu, atau B untuk bantuan.")
		self.switch = True

	def script_openLayout(self, gesture):
		wx.CallAfter(self.show_main_dialog)

	def script_openQuickTimer(self, gesture):
		wx.CallAfter(self.show_quick_timer_dialog)

	def script_openOneTimeAlarm(self, gesture):
		wx.CallAfter(self.show_one_time_alarm_dialog)

	def script_openAudioManager(self, gesture):
		wx.CallAfter(self.show_audio_manager_dialog)

	def script_announceTime(self, gesture):
		now = datetime.datetime.now()
		cfg = self.config.get_time_reminder_config()
		status = "aktif" if cfg.get("enabled", False) else "nonaktif"
		interval = cfg.get("interval", 60)
		msg = f"Sekarang jam {now.strftime('%H:%M')}. Pengingat waktu berkala saat ini {status} (tiap {interval} menit)."
		ui.message(msg)

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
				curr_h = h
				while curr_h <= 23:
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
			repeat_str = f" (Tiap {int_h} Jam Sekali)" if int_h > 0 else ""
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
			repeat_str = f" (Tiap {int_h} jam sekali)" if int_h > 0 else ""
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

	def script_showChangelog(self, gesture):
		ui.message("JadwalKu Versi 1.4.2. Membuka riwayat pembaruan (Changelog)...")
		wx.CallAfter(self.show_changelog_dialog)

	def script_exitLayer(self, gesture):
		pass
